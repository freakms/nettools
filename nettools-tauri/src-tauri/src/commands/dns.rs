// DNS Lookup commands - Simplified version using system commands
use serde::{Deserialize, Serialize};
use std::process::Command;

#[derive(Debug, Serialize, Deserialize)]
pub struct DnsRecord {
    pub record_type: String,
    pub name: String,
    pub value: String,
    pub ttl: u32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DnsResult {
    pub domain: String,
    pub records: Vec<DnsRecord>,
    pub duration_ms: u64,
}

/// Perform DNS lookup for a domain using nslookup
#[tauri::command]
pub async fn lookup_dns(domain: String, record_types: Vec<String>) -> Result<DnsResult, String> {
    let start = std::time::Instant::now();
    let mut records = Vec::new();
    
    for record_type in &record_types {
        let output = Command::new("nslookup")
            .args(["-type=".to_string() + record_type, domain.clone()])
            .output()
            .map_err(|e| format!("Failed to execute nslookup: {}", e))?;
        
        let stdout = String::from_utf8_lossy(&output.stdout);
        
        // Parse nslookup output
        for line in stdout.lines() {
            let line = line.trim();
            
            // Parse A records
            if record_type == "A" && line.starts_with("Address:") && !line.contains("#") {
                if let Some(ip) = line.split(':').nth(1) {
                    let ip = ip.trim();
                    if !ip.contains("::") { // Skip IPv6
                        records.push(DnsRecord {
                            record_type: "A".to_string(),
                            name: domain.clone(),
                            value: ip.to_string(),
                            ttl: 300,
                        });
                    }
                }
            }
            
            // Parse MX records
            if record_type == "MX" && line.contains("mail exchanger") {
                if let Some(mx) = line.split('=').nth(1) {
                    records.push(DnsRecord {
                        record_type: "MX".to_string(),
                        name: domain.clone(),
                        value: mx.trim().to_string(),
                        ttl: 300,
                    });
                }
            }
            
            // Parse NS records
            if record_type == "NS" && line.contains("nameserver") {
                if let Some(ns) = line.split('=').nth(1) {
                    records.push(DnsRecord {
                        record_type: "NS".to_string(),
                        name: domain.clone(),
                        value: ns.trim().to_string(),
                        ttl: 300,
                    });
                }
            }
            
            // Parse TXT records
            if record_type == "TXT" && line.contains("text") {
                if let Some(txt) = line.split('=').nth(1) {
                    records.push(DnsRecord {
                        record_type: "TXT".to_string(),
                        name: domain.clone(),
                        value: txt.trim().trim_matches('"').to_string(),
                        ttl: 300,
                    });
                }
            }
        }
    }
    
    let duration_ms = start.elapsed().as_millis() as u64;
    
    Ok(DnsResult {
        domain,
        records,
        duration_ms,
    })
}

/// Perform reverse DNS lookup
#[tauri::command]
pub async fn reverse_lookup(ip: String) -> Result<String, String> {
    let output = Command::new("nslookup")
        .arg(&ip)
        .output()
        .map_err(|e| format!("Failed to execute nslookup: {}", e))?;
    
    let stdout = String::from_utf8_lossy(&output.stdout);
    
    for line in stdout.lines() {
        if line.contains("Name:") || line.contains("name =") {
            if let Some(name) = line.split(&[':', '='][..]).last() {
                return Ok(name.trim().to_string());
            }
        }
    }
    
    Err("No PTR record found".to_string())
}
