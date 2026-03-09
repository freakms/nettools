// Live Ping Monitor - Real-time continuous ping monitoring
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::net::IpAddr;
use std::sync::{Arc, Mutex};
use super::utils::create_hidden_command;

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
    pub status: String, // "online", "offline", "unknown"
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
                // Update min/max
                self.min_rtt = Some(self.min_rtt.map_or(rtt, |m| m.min(rtt)));
                self.max_rtt = Some(self.max_rtt.map_or(rtt, |m| m.max(rtt)));

                // Calculate average from history
                let valid_rtts: Vec<f64> = self.history
                    .iter()
                    .filter_map(|p| p.rtt_ms)
                    .collect();
                
                if !valid_rtts.is_empty() {
                    self.avg_rtt = Some(valid_rtts.iter().sum::<f64>() / valid_rtts.len() as f64);
                }
            }
        } else {
            self.current_rtt = None;
            self.status = "offline".to_string();
        }

        // Calculate packet loss
        if self.total_sent > 0 {
            self.packet_loss = ((self.total_sent - self.total_received) as f64 / self.total_sent as f64) * 100.0;
        }
    }
}

pub struct MonitorState {
    pub hosts: HashMap<String, HostStats>,
    pub is_running: bool,
}

impl MonitorState {
    pub fn new() -> Self {
        Self {
            hosts: HashMap::new(),
            is_running: false,
        }
    }
}

pub type SharedMonitorState = Arc<Mutex<MonitorState>>;

/// Parse IP input (single IP, range, or CIDR) into list of IPs
fn parse_ip_input(input: &str) -> Vec<String> {
    let mut ips = Vec::new();
    let input = input.trim();

    // Check for CIDR notation (e.g., 192.168.1.0/24)
    if input.contains('/') {
        if let Ok(network) = input.parse::<ipnetwork::Ipv4Network>() {
            // Limit to 256 hosts for safety
            let count = network.size();
            if count <= 256 {
                for ip in network.iter() {
                    ips.push(ip.to_string());
                }
            } else {
                // For larger networks, take first 256
                for (i, ip) in network.iter().enumerate() {
                    if i >= 256 {
                        break;
                    }
                    ips.push(ip.to_string());
                }
            }
        }
        return ips;
    }

    // Check for range notation (e.g., 192.168.1.1-254 or 192.168.1.1-192.168.1.254)
    if input.contains('-') {
        let parts: Vec<&str> = input.split('-').collect();
        if parts.len() == 2 {
            let start = parts[0].trim();
            let end = parts[1].trim();

            // Check if end is just a number (short range format)
            if !end.contains('.') {
                // Short format: 192.168.1.1-254
                if let Some(last_dot) = start.rfind('.') {
                    let prefix = &start[..=last_dot];
                    if let (Ok(start_num), Ok(end_num)) = (
                        start[last_dot + 1..].parse::<u8>(),
                        end.parse::<u8>(),
                    ) {
                        for i in start_num..=end_num {
                            ips.push(format!("{}{}", prefix, i));
                        }
                    }
                }
            } else {
                // Full format: 192.168.1.1-192.168.1.254
                if let (Ok(start_ip), Ok(end_ip)) = (
                    start.parse::<std::net::Ipv4Addr>(),
                    end.parse::<std::net::Ipv4Addr>(),
                ) {
                    let start_u32 = u32::from(start_ip);
                    let end_u32 = u32::from(end_ip);
                    
                    // Limit range
                    let count = end_u32.saturating_sub(start_u32) + 1;
                    let max_count = count.min(256);
                    
                    for i in 0..max_count {
                        let ip = std::net::Ipv4Addr::from(start_u32 + i);
                        ips.push(ip.to_string());
                    }
                }
            }
        }
        return ips;
    }

    // Single IP or hostname
    // If it's a hostname (not a valid IP), resolve to IP via DNS
    if input.parse::<IpAddr>().is_err() {
        use std::net::ToSocketAddrs;
        if let Ok(mut addrs) = format!("{}:0", input).to_socket_addrs() {
            if let Some(addr) = addrs.next() {
                ips.push(addr.ip().to_string());
                return ips;
            }
        }
        // Fallback: use the hostname as-is if DNS resolution fails
        ips.push(input.to_string());
    } else {
        ips.push(input.to_string());
    }
    ips
}

/// Single ping to a host - fast timeout for monitoring
fn ping_host(ip: &str) -> (bool, Option<f64>) {
    #[cfg(target_os = "windows")]
    let output = create_hidden_command("ping")
        .args(["-n", "1", "-w", "500", ip])
        .output();

    #[cfg(not(target_os = "windows"))]
    let output = create_hidden_command("ping")
        .args(["-c", "1", "-W", "1", ip])
        .output();

    match output {
        Ok(output) => {
            let stdout = String::from_utf8_lossy(&output.stdout);
            
            if output.status.success() || stdout.contains("TTL=") || stdout.contains("ttl=") {
                // Try to extract RTT
                let rtt = extract_rtt(&stdout);
                (true, rtt)
            } else {
                (false, None)
            }
        }
        Err(_) => (false, None),
    }
}

/// Extract RTT from ping output
fn extract_rtt(output: &str) -> Option<f64> {
    // Windows German format: "Antwort von x.x.x.x: Bytes=32 Zeit=1ms TTL=64" or "Zeit<1ms"
    // Windows English format: "Reply from x.x.x.x: bytes=32 time=1ms TTL=64"
    // Linux format: "64 bytes from x.x.x.x: icmp_seq=1 ttl=64 time=0.123 ms"
    
    // Try German format first (Zeit= or Zeit<)
    if let Some(time_pos) = output.find("Zeit=").or_else(|| output.find("Zeit<")) {
        let after_time = &output[time_pos + 5..];
        let time_str: String = after_time.chars()
            .skip_while(|c| *c == '<')
            .take_while(|c| c.is_numeric() || *c == '.')
            .collect();
        if let Ok(rtt) = time_str.parse::<f64>() {
            return Some(rtt);
        }
    }
    
    // Try English format (time= or time<)
    if let Some(time_pos) = output.find("time=").or_else(|| output.find("time<")) {
        let after_time = &output[time_pos + 5..];
        let time_str: String = after_time.chars()
            .skip_while(|c| *c == '<')
            .take_while(|c| c.is_numeric() || *c == '.')
            .collect();
        if let Ok(rtt) = time_str.parse::<f64>() {
            return Some(rtt);
        }
    }
    
    // Fallback for "time<1ms" or "Zeit<1ms"
    if output.contains("time<1ms") || output.contains("Zeit<1ms") {
        return Some(0.5);
    }
    
    None
}

/// Resolve hostname for an IP
fn resolve_hostname(ip: &str) -> Option<String> {
    // Try DNS reverse lookup via nslookup
    if let Ok(_addr) = ip.parse::<IpAddr>() {
        #[cfg(target_os = "windows")]
        {
            if let Ok(output) = create_hidden_command("nslookup")
                .arg(ip)
                .output()
            {
                let stdout = String::from_utf8_lossy(&output.stdout);
                let lines: Vec<&str> = stdout.lines().collect();
                
                // nslookup output has server info first, then result
                // We need to skip the DNS server section and find "Name:" in the answer
                let mut found_answer = false;
                for line in &lines {
                    let trimmed = line.trim();
                    
                    // Skip empty lines
                    if trimmed.is_empty() {
                        found_answer = true; // After first empty line, we're in the answer section
                        continue;
                    }
                    
                    // Look for "Name:" or "Name =" in the answer section
                    if found_answer {
                        if let Some(pos) = trimmed.find("Name:").or_else(|| trimmed.find("name:")) {
                            let name = trimmed[pos + 5..].trim();
                            if !name.is_empty() && name != ip {
                                return Some(name.to_string());
                            }
                        }
                        if let Some(pos) = trimmed.find("name =").or_else(|| trimmed.find("Name =")) {
                            let name = trimmed[pos + 6..].trim().trim_end_matches('.');
                            if !name.is_empty() && name != ip {
                                return Some(name.to_string());
                            }
                        }
                    }
                }
                
                // Fallback: also try "Name:" anywhere in output (some DNS servers differ)
                for line in &lines {
                    let trimmed = line.trim();
                    if trimmed.starts_with("Name:") || trimmed.starts_with("name:") {
                        let name = trimmed.split(':').nth(1).unwrap_or("").trim();
                        if !name.is_empty() && name != ip {
                            return Some(name.to_string());
                        }
                    }
                }
            }
        }
        
        #[cfg(not(target_os = "windows"))]
        {
            if let Ok(output) = create_hidden_command("host")
                .arg(ip)
                .output()
            {
                let stdout = String::from_utf8_lossy(&output.stdout);
                if let Some(line) = stdout.lines().next() {
                    if line.contains("pointer") {
                        let parts: Vec<&str> = line.split("pointer").collect();
                        if parts.len() >= 2 {
                            return Some(parts[1].trim().trim_end_matches('.').to_string());
                        }
                    }
                }
            }
        }
    }
    
    None
}

/// Initialize hosts for monitoring - resolves hostnames to IPs
#[tauri::command]
pub fn monitor_init_hosts(hosts_input: String) -> Result<Vec<ResolvedHost>, String> {
    let mut results = Vec::new();
    let mut seen_ips = std::collections::HashSet::new();
    
    for input in hosts_input.split(',') {
        let input = input.trim();
        if input.is_empty() { continue; }
        
        // Check if input is a hostname
        let is_hostname = input.parse::<IpAddr>().is_err() 
            && !input.contains('/') 
            && !input.contains('-');
        
        let ips = parse_ip_input(input);
        
        for ip in ips {
            if seen_ips.contains(&ip) { continue; }
            seen_ips.insert(ip.clone());
            
            results.push(ResolvedHost {
                ip: ip.clone(),
                hostname: if is_hostname { Some(input.to_string()) } else { None },
            });
        }
    }
    
    // Sort by IP numerically
    results.sort_by(|a, b| {
        let parse_ip = |ip: &str| -> u32 {
            ip.split('.').filter_map(|s| s.parse::<u32>().ok()).fold(0u32, |acc, o| (acc << 8) | o)
        };
        parse_ip(&a.ip).cmp(&parse_ip(&b.ip))
    });
    
    if results.len() > 512 {
        results.truncate(512);
    }
    
    Ok(results)
}

/// Ping a single host and return updated stats
#[tauri::command]
pub fn monitor_ping_host(ip: String, current_stats: Option<HostStats>) -> HostStats {
    let mut stats = current_stats.unwrap_or_else(|| {
        let hostname = resolve_hostname(&ip);
        HostStats::new(ip.clone(), hostname)
    });
    
    let (success, rtt) = ping_host(&ip);
    stats.add_result(success, rtt);
    
    stats
}

/// Batch ping hosts in parallel - limited concurrency for performance
#[tauri::command]
pub async fn monitor_ping_batch(
    ips: Vec<String>,
    current_stats_map: std::collections::HashMap<String, HostStats>,
) -> Vec<HostStats> {
    use std::sync::Arc;
    use tokio::sync::Semaphore;

    // Max 15 concurrent ping processes to avoid overloading Windows
    let max_concurrent = 15.min(ips.len().max(1));
    let semaphore = Arc::new(Semaphore::new(max_concurrent));
    let stats_map = Arc::new(current_stats_map);
    
    let mut handles = Vec::new();
    
    for ip in ips {
        let sem = Arc::clone(&semaphore);
        let map = Arc::clone(&stats_map);
        
        let handle = tokio::task::spawn_blocking(move || {
            let _permit = sem.try_acquire();
            
            let mut stats = map.get(&ip).cloned().unwrap_or_else(|| {
                HostStats::new(ip.clone(), None)
            });
            
            let (success, rtt) = ping_host(&ip);
            stats.add_result(success, rtt);
            stats
        });
        handles.push(handle);
    }
    
    let mut results = Vec::new();
    for handle in handles {
        if let Ok(stats) = handle.await {
            results.push(stats);
        }
    }
    results
}

/// Get hostname for an IP
#[tauri::command]
pub fn monitor_resolve_hostname(ip: String) -> Option<String> {
    resolve_hostname(&ip)
}

/// Export monitoring data
#[tauri::command]
pub fn monitor_export_data(hosts: Vec<HostStats>) -> String {
    let mut lines = Vec::new();
    
    lines.push("Live Ping Monitor - Export".to_string());
    lines.push("=".repeat(60));
    lines.push(format!("Export Time: {}", chrono::Local::now().format("%Y-%m-%d %H:%M:%S")));
    lines.push(String::new());
    
    for host in hosts {
        lines.push(format!("Host: {}", host.ip));
        if let Some(hostname) = &host.hostname {
            lines.push(format!("Hostname: {}", hostname));
        }
        lines.push(format!("Status: {}", host.status));
        lines.push(format!("Average RTT: {:.1} ms", host.avg_rtt.unwrap_or(0.0)));
        lines.push(format!("Min RTT: {:.1} ms", host.min_rtt.unwrap_or(0.0)));
        lines.push(format!("Max RTT: {:.1} ms", host.max_rtt.unwrap_or(0.0)));
        lines.push(format!("Packet Loss: {:.1}%", host.packet_loss));
        lines.push(format!("Packets: {}/{}", host.total_received, host.total_sent));
        lines.push("-".repeat(40));
        lines.push(String::new());
    }
    
    lines.join("\n")
}
