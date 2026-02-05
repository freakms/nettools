// Traceroute command
use serde::{Deserialize, Serialize};
use super::utils::create_hidden_command;

#[derive(Debug, Serialize, Deserialize)]
pub struct TracerouteHop {
    pub hop: u8,
    pub ip: Option<String>,
    pub hostname: Option<String>,
    pub rtt1: Option<f64>,
    pub rtt2: Option<f64>,
    pub rtt3: Option<f64>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TracerouteResult {
    pub target: String,
    pub hops: Vec<TracerouteHop>,
    pub duration_ms: u64,
}

/// Run traceroute to a target
#[tauri::command]
pub async fn run_traceroute(target: String, max_hops: u8) -> Result<TracerouteResult, String> {
    let start = std::time::Instant::now();
    
    // Use Windows tracert command
    let output = create_hidden_command("tracert")
        .args(["-h", &max_hops.to_string(), "-w", "1000", &target])
        .output()
        .map_err(|e| format!("Failed to execute tracert: {}", e))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let hops = parse_traceroute_output(&stdout);
    
    let duration_ms = start.elapsed().as_millis() as u64;

    Ok(TracerouteResult {
        target,
        hops,
        duration_ms,
    })
}

fn parse_traceroute_output(output: &str) -> Vec<TracerouteHop> {
    let mut hops = Vec::new();
    
    for line in output.lines() {
        let line = line.trim();
        
        // Skip header lines
        if line.is_empty() 
            || line.starts_with("Tracing") 
            || line.starts_with("over a maximum")
            || line.starts_with("Trace complete")
        {
            continue;
        }
        
        // Parse hop line (e.g., "  1    <1 ms    <1 ms    <1 ms  192.168.1.1")
        if let Some(hop) = parse_hop_line(line) {
            hops.push(hop);
        }
    }
    
    hops
}

fn parse_hop_line(line: &str) -> Option<TracerouteHop> {
    let parts: Vec<&str> = line.split_whitespace().collect();
    
    if parts.is_empty() {
        return None;
    }
    
    // First part should be hop number
    let hop_num: u8 = parts.get(0)?.parse().ok()?;
    
    // Check for timeout line
    if line.contains("Request timed out") || line.contains("* * *") {
        return Some(TracerouteHop {
            hop: hop_num,
            ip: None,
            hostname: None,
            rtt1: None,
            rtt2: None,
            rtt3: None,
        });
    }
    
    // Parse RTT values and IP
    let mut rtts = Vec::new();
    let mut ip = None;
    let mut hostname = None;
    
    for (i, part) in parts.iter().enumerate().skip(1) {
        if *part == "ms" {
            // Previous part was RTT value
            if i > 1 {
                let rtt_str = parts[i - 1];
                if rtt_str == "<1" {
                    rtts.push(0.5);
                } else if let Ok(rtt) = rtt_str.parse::<f64>() {
                    rtts.push(rtt);
                }
            }
        } else if part.contains('.') || part.contains(':') {
            // This might be an IP address
            if part.chars().all(|c| c.is_digit(10) || c == '.' || c == ':') {
                ip = Some(part.to_string());
            }
        } else if part.contains('[') && part.contains(']') {
            // IP in brackets [x.x.x.x]
            let clean_ip = part.trim_matches(|c| c == '[' || c == ']');
            ip = Some(clean_ip.to_string());
        } else if !part.contains('[') && hostname.is_none() && ip.is_none() {
            // Could be hostname
            if part.contains('.') || part.len() > 5 {
                hostname = Some(part.to_string());
            }
        }
    }
    
    Some(TracerouteHop {
        hop: hop_num,
        ip,
        hostname,
        rtt1: rtts.get(0).copied(),
        rtt2: rtts.get(1).copied(),
        rtt3: rtts.get(2).copied(),
    })
}
