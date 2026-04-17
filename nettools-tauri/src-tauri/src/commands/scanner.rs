// Scanner commands - ICMP-based, no ping.exe subprocess
// Uses surge-ping for raw ICMP (fast, no admin required on Windows 8+)
use serde::{Deserialize, Serialize};
use std::net::{IpAddr, ToSocketAddrs};
use std::sync::Arc;
use std::time::Duration;
use surge_ping::{Client, Config, PingIdentifier, PingSequence, ICMP};
use tokio::sync::Semaphore;

// Threshold above which a warning is emitted to the frontend
const LARGE_NETWORK_THRESHOLD: usize = 1024;
// Max hosts we will ever scan in one call (prevents /8 accidents)
const HARD_MAX_HOSTS: usize = 65536;
// Concurrent ICMP pings – much higher than the old ping.exe approach
const MAX_CONCURRENT: usize = 300;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct PingResult {
    pub ip: String,
    pub hostname: Option<String>,
    pub status: String, // "online" | "offline" | "timeout"
    pub rtt: Option<f64>,
    pub ttl: Option<u8>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ScanResult {
    pub results: Vec<PingResult>,
    pub total_hosts: usize,
    pub responding_hosts: usize,
    pub duration_ms: u64,
    pub warning: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ScanProgress {
    pub completed: usize,
    pub total: usize,
    pub latest: Option<PingResult>,
}

// ---------------------------------------------------------------------------
// ICMP ping – single host, no subprocess
// ---------------------------------------------------------------------------
async fn icmp_ping(ip: IpAddr, timeout_ms: u32) -> (bool, Option<f64>) {
    let config = Config::builder()
        .kind(match ip {
            IpAddr::V4(_) => ICMP::V4,
            IpAddr::V6(_) => ICMP::V6,
        })
        .build();

    let client = match Client::new(&config) {
        Ok(c) => c,
        Err(_) => return (false, None),
    };

    let mut pinger = client
        .pinger(ip, PingIdentifier(rand::random()))
        .await;
    pinger.timeout(Duration::from_millis(timeout_ms as u64));

    match pinger.ping(PingSequence(0), &[0u8; 8]).await {
        Ok((_, rtt)) => (true, Some(rtt.as_secs_f64() * 1000.0)),
        Err(_) => (false, None),
    }
}

// ---------------------------------------------------------------------------
// DNS helpers
// ---------------------------------------------------------------------------

/// Resolve a hostname to its first IPv4 address (blocking, run in spawn_blocking)
fn resolve_to_ip(hostname: &str) -> Option<IpAddr> {
    format!("{}:0", hostname)
        .to_socket_addrs()
        .ok()?
        .find(|a| a.is_ipv4())
        .map(|a| a.ip())
}

/// Reverse-DNS: IP → hostname (blocking)
fn reverse_lookup(ip: IpAddr) -> Option<String> {
    // dns_lookup::lookup_addr is the cleanest cross-platform API,
    // but we avoid an extra dep by using ToSocketAddrs trick.
    // Instead we rely on the dns-lookup crate added to Cargo.toml.
    dns_lookup::lookup_addr(&ip).ok()
}

// ---------------------------------------------------------------------------
// Input parsing
// ---------------------------------------------------------------------------

/// Returned by parse_target – carries both the IP list and any warning.
pub struct ParsedTarget {
    pub ips: Vec<IpAddr>,
    pub warning: Option<String>,
}

pub fn parse_target(target: &str) -> Result<ParsedTarget, String> {
    let target = target.trim();
    let mut ips: Vec<IpAddr> = Vec::new();
    let mut warning: Option<String> = None;

    if target.contains('/') {
        // CIDR notation
        let network: ipnetwork::IpNetwork = target
            .parse()
            .map_err(|e| format!("Ungültige CIDR-Notation: {}", e))?;

        let total = match network {
            ipnetwork::IpNetwork::V4(n) => n.size() as usize,
            ipnetwork::IpNetwork::V6(_) => HARD_MAX_HOSTS + 1,
        };

        if total > HARD_MAX_HOSTS {
            return Err(format!(
                "Netzwerk zu groß: {} Hosts. Maximum ist {}. \
                 Bitte kleineres CIDR verwenden (z.B. /16 statt /8).",
                total, HARD_MAX_HOSTS
            ));
        }

        if total > LARGE_NETWORK_THRESHOLD {
            warning = Some(format!(
                "Großes Netzwerk: {} Hosts werden gescannt. \
                 Das kann mehrere Minuten dauern.",
                total
            ));
        }

        for ip in network.iter() {
            ips.push(ip);
        }
    } else if target.contains('-') {
        // Range: 192.168.1.1-254  OR  192.168.1.1-192.168.1.254
        let parts: Vec<&str> = target.splitn(2, '-').collect();
        let start_str = parts[0].trim();
        let end_str = parts[1].trim();

        let start_ip: std::net::Ipv4Addr = start_str
            .parse()
            .map_err(|_| format!("Ungültige Start-IP: {}", start_str))?;

        // End can be a full IP or just the last octet
        let end_ip: std::net::Ipv4Addr = if end_str.contains('.') {
            end_str
                .parse()
                .map_err(|_| format!("Ungültige End-IP: {}", end_str))?
        } else {
            let last: u8 = end_str
                .parse()
                .map_err(|_| format!("Ungültiges End-Oktet: {}", end_str))?;
            let octs = start_ip.octets();
            std::net::Ipv4Addr::new(octs[0], octs[1], octs[2], last)
        };

        let start_u32 = u32::from(start_ip);
        let end_u32 = u32::from(end_ip);

        if end_u32 < start_u32 {
            return Err("End-IP ist kleiner als Start-IP".to_string());
        }

        let count = (end_u32 - start_u32 + 1) as usize;
        if count > HARD_MAX_HOSTS {
            return Err(format!(
                "Range zu groß: {} Hosts. Maximum ist {}.",
                count, HARD_MAX_HOSTS
            ));
        }
        if count > LARGE_NETWORK_THRESHOLD {
            warning = Some(format!(
                "Großer Bereich: {} Hosts werden gescannt.",
                count
            ));
        }

        for offset in 0..count {
            let ip = std::net::Ipv4Addr::from(start_u32 + offset as u32);
            ips.push(IpAddr::V4(ip));
        }
    } else {
        // Single IP or hostname
        match target.parse::<IpAddr>() {
            Ok(ip) => ips.push(ip),
            Err(_) => {
                // It's a hostname – resolve it
                let hostname = target.to_string();
                let resolved = tokio::task::block_in_place(|| resolve_to_ip(&hostname));
                match resolved {
                    Some(ip) => ips.push(ip),
                    None => return Err(format!("Hostname '{}' konnte nicht aufgelöst werden", target)),
                }
            }
        }
    }

    Ok(ParsedTarget { ips, warning })
}

// ---------------------------------------------------------------------------
// Tauri commands
// ---------------------------------------------------------------------------

/// Ping a single host (IP or hostname). Resolves hostname → IP automatically.
#[tauri::command]
pub async fn ping_host(ip: String, timeout_ms: u32) -> Result<PingResult, String> {
    let input = ip.trim().to_string();

    // Resolve hostname if needed
    let (addr, display_hostname) = match input.parse::<IpAddr>() {
        Ok(a) => (a, None),
        Err(_) => {
            let h = input.clone();
            let resolved = tokio::task::spawn_blocking(move || resolve_to_ip(&h))
                .await
                .map_err(|e| format!("Task-Fehler: {}", e))?;
            match resolved {
                Some(a) => (a, Some(input.clone())),
                None => return Err(format!("Hostname '{}' konnte nicht aufgelöst werden", input)),
            }
        }
    };

    let (alive, rtt) = icmp_ping(addr, timeout_ms).await;

    Ok(PingResult {
        ip: addr.to_string(),
        hostname: display_hostname,
        status: if alive { "online" } else { "offline" }.to_string(),
        rtt,
        ttl: None, // TTL not exposed by surge-ping
    })
}

/// Ping + reverse-DNS hostname lookup (slightly slower).
#[tauri::command]
pub async fn ping_host_with_hostname(ip: String, timeout_ms: u32) -> Result<PingResult, String> {
    let mut result = ping_host(ip, timeout_ms).await?;

    if result.status == "online" && result.hostname.is_none() {
        let addr: IpAddr = result.ip.parse().unwrap();
        result.hostname = tokio::task::spawn_blocking(move || reverse_lookup(addr))
            .await
            .unwrap_or(None);
    }

    Ok(result)
}

/// Scan a network range. Emits "scan-progress" events while running.
/// Returns a warning string for large networks instead of refusing.
#[tauri::command]
pub async fn scan_network(
    app: tauri::AppHandle,
    target: String,
    timeout_ms: u32,
    only_responding: bool,
) -> Result<ScanResult, String> {
    use tauri::Emitter;

    let start = std::time::Instant::now();

    let parsed = parse_target(&target)?;
    let ips = parsed.ips;
    let warning = parsed.warning.clone();
    let total_hosts = ips.len();

    let semaphore = Arc::new(Semaphore::new(MAX_CONCURRENT.min(total_hosts.max(1))));
    let app_handle = app.clone();
    let total_for_progress = total_hosts;

    // Shared counter for progress events
    let completed = Arc::new(std::sync::atomic::AtomicUsize::new(0));

    let mut handles = Vec::with_capacity(total_hosts);

    for ip in ips {
        let sem = Arc::clone(&semaphore);
        let completed_ref = Arc::clone(&completed);
        let app_ref = app_handle.clone();

        let handle = tokio::spawn(async move {
            // acquire_owned keeps the permit alive for the full duration of the ping
            let _permit = sem.acquire_owned().await.unwrap();

            let (alive, rtt) = icmp_ping(ip, timeout_ms).await;

            let result = PingResult {
                ip: ip.to_string(),
                hostname: None,
                status: if alive { "online" } else { "offline" }.to_string(),
                rtt,
                ttl: None,
            };

            // Emit progress (best-effort, ignore errors)
            let done = completed_ref.fetch_add(1, std::sync::atomic::Ordering::Relaxed) + 1;
            // Throttle: emit every 10 results or when finished
            if done % 10 == 0 || done == total_for_progress {
                let _ = app_ref.emit(
                    "scan-progress",
                    ScanProgress {
                        completed: done,
                        total: total_for_progress,
                        latest: Some(result.clone()),
                    },
                );
            }

            result
        });
        handles.push(handle);
    }

    let mut results = Vec::with_capacity(total_hosts);
    for handle in handles {
        if let Ok(result) = handle.await {
            if !only_responding || result.status == "online" {
                results.push(result);
            }
        }
    }

    // Sort by IP numerically
    results.sort_by(|a, b| {
        let to_u32 = |ip: &str| -> u32 {
            ip.parse::<IpAddr>()
                .ok()
                .and_then(|a| if let IpAddr::V4(v4) = a { Some(u32::from(v4)) } else { None })
                .unwrap_or(0)
        };
        to_u32(&a.ip).cmp(&to_u32(&b.ip))
    });

    let responding_hosts = results.iter().filter(|r| r.status == "online").count();
    let duration_ms = start.elapsed().as_millis() as u64;

    Ok(ScanResult {
        results,
        total_hosts,
        responding_hosts,
        duration_ms,
        warning,
    })
}

/// Resolve a single IP to its hostname (reverse DNS).
#[tauri::command]
pub async fn resolve_hostname(ip: String) -> Result<Option<String>, String> {
    let addr: IpAddr = ip.parse().map_err(|_| format!("Ungültige IP: {}", ip))?;
    Ok(tokio::task::spawn_blocking(move || reverse_lookup(addr))
        .await
        .unwrap_or(None))
}

/// Batch reverse-DNS resolution for a list of IPs (limited concurrency).
#[tauri::command]
pub async fn resolve_hostnames_batch(
    ips: Vec<String>,
) -> Result<Vec<(String, Option<String>)>, String> {
    let semaphore = Arc::new(Semaphore::new(20));
    let mut handles = Vec::new();

    for ip_str in ips {
        let sem = Arc::clone(&semaphore);
        let handle = tokio::spawn(async move {
            let _permit = sem.acquire_owned().await.unwrap();
            let addr: Option<IpAddr> = ip_str.parse().ok();
            let hostname = match addr {
                Some(a) => tokio::task::spawn_blocking(move || reverse_lookup(a))
                    .await
                    .unwrap_or(None),
                None => None,
            };
            (ip_str, hostname)
        });
        handles.push(handle);
    }

    let mut results = Vec::new();
    for handle in handles {
        if let Ok(r) = handle.await {
            results.push(r);
        }
    }
    Ok(results)
}

/// Get the local machine's primary IPv4 address.
#[tauri::command]
pub fn get_local_ip() -> Result<String, String> {
    // Connect a UDP socket (no actual traffic) to determine outbound interface
    let socket = std::net::UdpSocket::bind("0.0.0.0:0")
        .map_err(|e| format!("Socket-Fehler: {}", e))?;
    socket
        .connect("8.8.8.8:80")
        .map_err(|e| format!("Connect-Fehler: {}", e))?;
    let addr = socket
        .local_addr()
        .map_err(|e| format!("Adress-Fehler: {}", e))?;
    Ok(addr.ip().to_string())
}
