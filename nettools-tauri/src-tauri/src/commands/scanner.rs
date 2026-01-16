// Scanner commands for network host discovery
use serde::{Deserialize, Serialize};
use std::process::Command;

#[derive(Debug, Serialize, Deserialize)]
pub struct PingResult {
    pub ip: String,
    pub hostname: Option<String>,
    pub status: String,
    pub rtt: Option<f64>,
    pub ttl: Option<u8>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ScanResult {
    pub results: Vec<PingResult>,
    pub total_hosts: usize,
    pub responding_hosts: usize,
    pub duration_ms: u64,
}

/// Ping a single host
#[tauri::command]
pub async fn ping_host(ip: String, timeout_ms: u32) -> Result<PingResult, String> {
    let output = Command::new("ping")
        .args(["-n", "1", "-w", &timeout_ms.to_string(), &ip])
        .output()
        .map_err(|e| format!("Failed to execute ping: {}", e))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    
    let status = if output.status.success() && stdout.contains("TTL=") {
        "online"
    } else if stdout.contains("Request timed out") || stdout.contains("100% loss") {
        "timeout"
    } else {
        "offline"
    };

    let rtt = extract_rtt(&stdout);
    let ttl = extract_ttl(&stdout);
    let hostname = get_hostname(&ip).ok();

    Ok(PingResult {
        ip,
        hostname,
        status: status.to_string(),
        rtt,
        ttl,
    })
}

/// Scan a network range
#[tauri::command]
pub async fn scan_network(
    target: String,
    timeout_ms: u32,
    only_responding: bool,
) -> Result<ScanResult, String> {
    let start = std::time::Instant::now();
    let ips = parse_target(&target)?;
    let total_hosts = ips.len();
    
    let mut results = Vec::new();
    let mut handles = Vec::new();
    
    for ip in ips {
        let ip_clone = ip.clone();
        let handle = tokio::spawn(async move {
            ping_host(ip_clone, timeout_ms).await
        });
        handles.push(handle);
    }
    
    for handle in handles {
        if let Ok(Ok(result)) = handle.await {
            if !only_responding || result.status == "online" {
                results.push(result);
            }
        }
    }

    let responding_hosts = results.iter().filter(|r| r.status == "online").count();
    let duration_ms = start.elapsed().as_millis() as u64;

    Ok(ScanResult {
        results,
        total_hosts,
        responding_hosts,
        duration_ms,
    })
}

/// Get the local machine's IP address
#[tauri::command]
pub fn get_local_ip() -> Result<String, String> {
    let output = Command::new("ipconfig")
        .output()
        .map_err(|e| format!("Failed to execute ipconfig: {}", e))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    
    for line in stdout.lines() {
        if line.contains("IPv4") && line.contains(":") {
            if let Some(ip) = line.split(':').nth(1) {
                let ip = ip.trim();
                if !ip.starts_with("127.") {
                    return Ok(ip.to_string());
                }
            }
        }
    }
    
    Err("Could not determine local IP address".to_string())
}

fn parse_target(target: &str) -> Result<Vec<String>, String> {
    let mut ips = Vec::new();
    
    if target.contains('/') {
        let network: ipnetwork::IpNetwork = target
            .parse()
            .map_err(|e| format!("Invalid CIDR notation: {}", e))?;
        
        for ip in network.iter() {
            ips.push(ip.to_string());
        }
    } else if target.contains('-') {
        let parts: Vec<&str> = target.split('.').collect();
        if parts.len() == 4 {
            let range_parts: Vec<&str> = parts[3].split('-').collect();
            if range_parts.len() == 2 {
                let start: u8 = range_parts[0].parse().map_err(|_| "Invalid range start")?;
                let end: u8 = range_parts[1].parse().map_err(|_| "Invalid range end")?;
                let base = format!("{}.{}.{}.", parts[0], parts[1], parts[2]);
                
                for i in start..=end {
                    ips.push(format!("{}{}", base, i));
                }
            }
        }
    } else {
        ips.push(target.to_string());
    }
    
    Ok(ips)
}

fn extract_rtt(output: &str) -> Option<f64> {
    for line in output.lines() {
        if let Some(idx) = line.find("time=") {
            let rest = &line[idx + 5..];
            if let Some(end) = rest.find("ms") {
                if let Ok(rtt) = rest[..end].parse::<f64>() {
                    return Some(rtt);
                }
            }
        } else if line.contains("time<1ms") {
            return Some(0.5);
        }
    }
    None
}

fn extract_ttl(output: &str) -> Option<u8> {
    for line in output.lines() {
        if let Some(idx) = line.find("TTL=") {
            let rest = &line[idx + 4..];
            let ttl_str: String = rest.chars().take_while(|c| c.is_ascii_digit()).collect();
            if let Ok(ttl) = ttl_str.parse::<u8>() {
                return Some(ttl);
            }
        }
    }
    None
}

fn get_hostname(ip: &str) -> Result<String, String> {
    let output = Command::new("nslookup")
        .arg(ip)
        .output()
        .map_err(|e| format!("nslookup failed: {}", e))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    
    for line in stdout.lines() {
        if line.contains("Name:") {
            if let Some(name) = line.split(':').nth(1) {
                return Ok(name.trim().to_string());
            }
        }
    }
    
    Err("Hostname not found".to_string())
}
