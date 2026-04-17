// Live Ping Monitor - Real-time continuous ICMP monitoring
// Uses surge-ping instead of ping.exe subprocess for much lower latency
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::net::IpAddr;
use std::sync::Arc;
use std::time::Duration;
use surge_ping::{Client, Config, PingIdentifier, PingSequence, ICMP};
use tokio::sync::Semaphore;

// Max concurrent ICMP pings per batch
const BATCH_CONCURRENT: usize = 50;
// Max hosts the monitor will track
const MAX_MONITOR_HOSTS: usize = 512;
// Same CIDR limits as scanner
const LARGE_NETWORK_THRESHOLD: usize = 256;
const HARD_MAX_HOSTS: usize = 512;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PingDataPoint {
    pub timestamp: u64,
    pub success: bool,
    pub rtt_ms: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResolvedHost {
    pub ip: String,
    pub hostname: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HostStats {
    pub ip: String,
    pub hostname: Option<String>,
    pub status: String, // "online" | "offline" | "unknown"
    pub current_rtt: Option<f64>,
    pub avg_rtt: Option<f64>,
    pub min_rtt: Option<f64>,
    pub max_rtt: Option<f64>,
    pub packet_loss: f64,
    pub total_sent: u32,
    pub total_received: u32,
    pub history: Vec<PingDataPoint>,
}

impl HostStats {
    pub fn new(ip: String, hostname: Option<String>) -> Self {
        Self {
            ip,
            hostname,
            status: "unknown".to_string(),
            current_rtt: None,
            avg_rtt: None,
            min_rtt: None,
            max_rtt: None,
            packet_loss: 0.0,
            total_sent: 0,
            total_received: 0,
            history: Vec::new(),
        }
    }

    pub fn add_result(&mut self, success: bool, rtt_ms: Option<f64>) {
        self.total_sent += 1;

        let timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis() as u64;

        self.history.push(PingDataPoint {
            timestamp,
            success,
            rtt_ms,
        });

        // Keep only last 60 data points (1 minute at 1 ping/sec)
        if self.history.len() > 60 {
            self.history.remove(0);
        }

        if success {
            self.total_received += 1;
            self.current_rtt = rtt_ms;
            self.status = "online".to_string();

            if let Some(rtt) = rtt_ms {
                self.min_rtt = Some(self.min_rtt.map_or(rtt, |m: f64| m.min(rtt)));
                self.max_rtt = Some(self.max_rtt.map_or(rtt, |m: f64| m.max(rtt)));

                let valid_rtts: Vec<f64> = self.history.iter().filter_map(|p| p.rtt_ms).collect();
                if !valid_rtts.is_empty() {
                    self.avg_rtt =
                        Some(valid_rtts.iter().sum::<f64>() / valid_rtts.len() as f64);
                }
            }
        } else {
            self.current_rtt = None;
            self.status = "offline".to_string();
        }

        if self.total_sent > 0 {
            self.packet_loss = ((self.total_sent - self.total_received) as f64
                / self.total_sent as f64)
                * 100.0;
        }
    }
}

// ---------------------------------------------------------------------------
// ICMP helper (reused from scanner logic, self-contained here)
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

/// Hostname → IP (blocking)
fn resolve_to_ip(hostname: &str) -> Option<IpAddr> {
    use std::net::ToSocketAddrs;
    format!("{}:0", hostname)
        .to_socket_addrs()
        .ok()?
        .find(|a| a.is_ipv4())
        .map(|a| a.ip())
}

/// IP → hostname (blocking reverse DNS)
fn reverse_lookup(ip: IpAddr) -> Option<String> {
    dns_lookup::lookup_addr(&ip).ok()
}

// ---------------------------------------------------------------------------
// IP input parser (CIDR / range / single / hostname)
// ---------------------------------------------------------------------------
fn parse_ip_input(input: &str) -> Vec<IpAddr> {
    let input = input.trim();
    let mut ips = Vec::new();

    // CIDR
    if input.contains('/') {
        if let Ok(network) = input.parse::<ipnetwork::Ipv4Network>() {
            let count = network.size() as usize;
            let limit = count.min(HARD_MAX_HOSTS);
            for ip in network.iter().take(limit) {
                ips.push(IpAddr::V4(ip));
            }
        }
        return ips;
    }

    // Range  192.168.1.1-254  or  192.168.1.1-192.168.1.254
    if input.contains('-') {
        let parts: Vec<&str> = input.splitn(2, '-').collect();
        if parts.len() == 2 {
            let start_str = parts[0].trim();
            let end_str = parts[1].trim();

            if let Ok(start_ip) = start_str.parse::<std::net::Ipv4Addr>() {
                let end_ip: Option<std::net::Ipv4Addr> = if end_str.contains('.') {
                    end_str.parse().ok()
                } else {
                    end_str.parse::<u8>().ok().map(|last| {
                        let o = start_ip.octets();
                        std::net::Ipv4Addr::new(o[0], o[1], o[2], last)
                    })
                };

                if let Some(end_ip) = end_ip {
                    let start_u32 = u32::from(start_ip);
                    let end_u32 = u32::from(end_ip);
                    let count = (end_u32.saturating_sub(start_u32) + 1) as usize;
                    let limit = count.min(HARD_MAX_HOSTS);
                    for i in 0..limit {
                        ips.push(IpAddr::V4(std::net::Ipv4Addr::from(start_u32 + i as u32)));
                    }
                }
            }
        }
        return ips;
    }

    // Single IP or hostname
    match input.parse::<IpAddr>() {
        Ok(ip) => ips.push(ip),
        Err(_) => {
            // Hostname – try to resolve synchronously (we're called from a non-async context)
            if let Some(ip) = resolve_to_ip(input) {
                ips.push(ip);
            }
        }
    }

    ips
}

// ---------------------------------------------------------------------------
// Tauri commands
// ---------------------------------------------------------------------------

/// Parse and resolve all hosts from a comma-separated input string.
/// Supports IPs, CIDR, ranges, and hostnames.
#[tauri::command]
pub fn monitor_init_hosts(hosts_input: String) -> Result<Vec<ResolvedHost>, String> {
    let mut results: Vec<ResolvedHost> = Vec::new();
    let mut seen = std::collections::HashSet::new();

    for chunk in hosts_input.split(',') {
        let chunk = chunk.trim();
        if chunk.is_empty() {
            continue;
        }

        // Detect whether the chunk is a hostname (not IP / CIDR / range)
        let is_hostname = chunk.parse::<IpAddr>().is_err()
            && !chunk.contains('/')
            && !chunk.contains('-');

        let ips = parse_ip_input(chunk);

        for ip in ips {
            let ip_str = ip.to_string();
            if seen.contains(&ip_str) {
                continue;
            }
            seen.insert(ip_str.clone());

            // For a hostname input we display it as the hostname label;
            // for IP/CIDR/range we leave hostname as None (resolved later on demand).
            results.push(ResolvedHost {
                ip: ip_str,
                hostname: if is_hostname {
                    Some(chunk.to_string())
                } else {
                    None
                },
            });
        }

        if results.len() >= MAX_MONITOR_HOSTS {
            break;
        }
    }

    results.truncate(MAX_MONITOR_HOSTS);

    // Sort numerically by IP
    results.sort_by(|a, b| {
        let to_u32 = |s: &str| -> u32 {
            s.parse::<IpAddr>()
                .ok()
                .and_then(|a| if let IpAddr::V4(v4) = a { Some(u32::from(v4)) } else { None })
                .unwrap_or(0)
        };
        to_u32(&a.ip).cmp(&to_u32(&b.ip))
    });

    Ok(results)
}

/// Ping a single host and return updated stats.
/// Pass current_stats to preserve history; omit for a fresh entry.
#[tauri::command]
pub async fn monitor_ping_host(ip: String, current_stats: Option<HostStats>) -> HostStats {
    let addr: IpAddr = match ip.parse() {
        Ok(a) => a,
        Err(_) => {
            let mut s = current_stats.unwrap_or_else(|| HostStats::new(ip.clone(), None));
            s.add_result(false, None);
            return s;
        }
    };

    let mut stats = current_stats.unwrap_or_else(|| {
        // First-time entry: attempt a reverse-DNS lookup
        let hostname = tokio::task::block_in_place(|| reverse_lookup(addr));
        HostStats::new(ip.clone(), hostname)
    });

    let (success, rtt) = icmp_ping(addr, 1000).await;
    stats.add_result(success, rtt);
    stats
}

/// Batch ping – all hosts in parallel with a semaphore cap.
/// current_stats_map preserves history between calls.
#[tauri::command]
pub async fn monitor_ping_batch(
    ips: Vec<String>,
    current_stats_map: HashMap<String, HostStats>,
) -> Vec<HostStats> {
    let semaphore = Arc::new(Semaphore::new(BATCH_CONCURRENT.min(ips.len().max(1))));
    let stats_map = Arc::new(current_stats_map);
    let mut handles = Vec::new();

    for ip_str in ips {
        let sem = Arc::clone(&semaphore);
        let map = Arc::clone(&stats_map);

        let handle = tokio::spawn(async move {
            // acquire_owned: permit lives until end of this async block
            let _permit = sem.acquire_owned().await.unwrap();

            let addr: IpAddr = match ip_str.parse() {
                Ok(a) => a,
                Err(_) => {
                    let mut s = map
                        .get(&ip_str)
                        .cloned()
                        .unwrap_or_else(|| HostStats::new(ip_str.clone(), None));
                    s.add_result(false, None);
                    return s;
                }
            };

            let mut stats = map.get(&ip_str).cloned().unwrap_or_else(|| {
                // Resolve hostname once on first encounter
                let hostname = tokio::task::block_in_place(|| reverse_lookup(addr));
                HostStats::new(ip_str.clone(), hostname)
            });

            let (success, rtt) = icmp_ping(addr, 1000).await;
            stats.add_result(success, rtt);
            stats
        });

        handles.push(handle);
    }

    let mut results = Vec::new();
    for handle in handles {
        if let Ok(s) = handle.await {
            results.push(s);
        }
    }
    results
}

/// Reverse-DNS for a single IP (on-demand, e.g. after a host comes online).
#[tauri::command]
pub async fn monitor_resolve_hostname(ip: String) -> Option<String> {
    let addr: IpAddr = ip.parse().ok()?;
    tokio::task::spawn_blocking(move || reverse_lookup(addr))
        .await
        .unwrap_or(None)
}

/// Export monitoring data as plain-text report.
#[tauri::command]
pub fn monitor_export_data(hosts: Vec<HostStats>) -> String {
    let mut lines = Vec::new();

    lines.push("Live Ping Monitor – Export".to_string());
    lines.push("=".repeat(60));
    lines.push(format!(
        "Exportzeit: {}",
        chrono::Local::now().format("%Y-%m-%d %H:%M:%S")
    ));
    lines.push(String::new());

    for host in hosts {
        lines.push(format!("Host: {}", host.ip));
        if let Some(hostname) = &host.hostname {
            lines.push(format!("Hostname: {}", hostname));
        }
        lines.push(format!("Status: {}", host.status));
        lines.push(format!(
            "Ø RTT: {:.1} ms",
            host.avg_rtt.unwrap_or(0.0)
        ));
        lines.push(format!("Min RTT: {:.1} ms", host.min_rtt.unwrap_or(0.0)));
        lines.push(format!("Max RTT: {:.1} ms", host.max_rtt.unwrap_or(0.0)));
        lines.push(format!("Paketverlust: {:.1}%", host.packet_loss));
        lines.push(format!(
            "Pakete: {}/{}",
            host.total_received, host.total_sent
        ));
        lines.push("-".repeat(40));
        lines.push(String::new());
    }

    lines.join("\n")
}
