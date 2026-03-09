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

    // Windows console output may use OEM codepage (CP850/437) instead of UTF-8
    // from_utf8_lossy handles invalid UTF-8 with replacement chars
    let stdout_utf8 = String::from_utf8_lossy(&output.stdout);
    
    // Also try to decode as raw bytes for pattern matching (handles garbled umlauts)
    let stdout = decode_windows_output(&output.stdout, &stdout_utf8);
    
    let hops = parse_traceroute_output(&stdout);
    
    let duration_ms = start.elapsed().as_millis() as u64;

    Ok(TracerouteResult {
        target,
        hops,
        duration_ms,
    })
}

/// Decode Windows console output - handle OEM codepage issues
fn decode_windows_output(raw: &[u8], utf8_fallback: &str) -> String {
    // Try to decode as Windows-1252 (common Western European codepage)
    let mut result = String::with_capacity(raw.len());
    for &byte in raw {
        match byte {
            0x00..=0x7F => result.push(byte as char),
            0xFC => result.push('ü'), // ü in CP1252/CP850
            0xDC => result.push('Ü'), // Ü
            0xE4 => result.push('ä'), // ä
            0xC4 => result.push('Ä'), // Ä
            0xF6 => result.push('ö'), // ö
            0xD6 => result.push('Ö'), // Ö
            0xDF => result.push('ß'), // ß
            0x81 => result.push('ü'), // ü in CP850
            0x84 => result.push('ä'), // ä in CP850
            0x94 => result.push('ö'), // ö in CP850
            0x8E => result.push('Ä'), // Ä in CP850
            0x99 => result.push('Ö'), // Ö in CP850
            0x9A => result.push('Ü'), // Ü in CP850
            0xE1 => result.push('ß'), // ß in CP850
            _ => result.push(byte as char),
        }
    }
    
    // If result seems valid, use it; otherwise fallback
    if result.contains("Trace") || result.contains("Routenverfolgung") || result.contains("Hop") {
        result
    } else {
        utf8_fallback.to_string()
    }
}

fn parse_traceroute_output(output: &str) -> Vec<TracerouteHop> {
    let mut hops = Vec::new();
    
    for line in output.lines() {
        let line = line.trim();
        
        // Skip header lines (English and German)
        if line.is_empty() 
            || line.starts_with("Tracing") 
            || line.starts_with("Routenverfolgung")
            || line.starts_with("over a maximum")
            || line.starts_with("über maximal")
            || line.starts_with("Trace complete")
            || line.starts_with("Ablaufverfolgung")
        {
            continue;
        }
        
        // Parse hop line
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
    
    // Check for timeout line (English and German variants)
    if line.contains("Request timed out") 
        || line.contains("* * *") 
        || line.contains("Zeitüberschreitung")
        || line.contains("berschreitung")  // fallback for garbled ü
        || line.contains("Allgemein")
    {
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
