// ARP Viewer command
use serde::{Deserialize, Serialize};
use super::utils::create_hidden_command;

#[derive(Debug, Serialize, Deserialize)]
pub struct ArpEntry {
    pub ip: String,
    pub mac: String,
    pub interface: String,
    pub entry_type: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ArpResult {
    pub entries: Vec<ArpEntry>,
    pub count: usize,
}

/// Get the ARP table
#[tauri::command]
pub async fn get_arp_table() -> Result<ArpResult, String> {
    let output = create_hidden_command("arp")
        .arg("-a")
        .output()
        .map_err(|e| format!("Failed to execute arp: {}", e))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let entries = parse_arp_output(&stdout);
    let count = entries.len();

    Ok(ArpResult { entries, count })
}

fn parse_arp_output(output: &str) -> Vec<ArpEntry> {
    let mut entries = Vec::new();
    let mut current_interface = String::new();
    
    for line in output.lines() {
        let line = line.trim();
        
        // Check for interface line
        if line.starts_with("Interface:") {
            if let Some(iface) = line.split_whitespace().nth(1) {
                current_interface = iface.to_string();
            }
            continue;
        }
        
        // Skip header lines and empty lines
        if line.is_empty() 
            || line.starts_with("Internet Address")
            || line.starts_with("---")
        {
            continue;
        }
        
        // Parse ARP entry
        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() >= 3 {
            let ip = parts[0].to_string();
            let mac = parts[1].to_string();
            let entry_type = parts[2].to_string();
            
            // Validate MAC address format
            if mac.contains('-') || mac.contains(':') {
                entries.push(ArpEntry {
                    ip,
                    mac,
                    interface: current_interface.clone(),
                    entry_type,
                });
            }
        }
    }
    
    entries
}
