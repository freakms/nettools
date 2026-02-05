// DNS Lookup commands - Using Windows nslookup command
use serde::{Deserialize, Serialize};
use super::utils::create_hidden_command;

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
        let args = vec![
            format!("-type={}", record_type),
            domain.clone(),
        ];
        
        let output = Command::new("nslookup")
            .args(&args)
            .output()
            .map_err(|e| format!("Failed to execute nslookup: {}", e))?;
        
        let stdout = String::from_utf8_lossy(&output.stdout);
        
        // Parse nslookup output based on record type
        match record_type.as_str() {
            "A" | "AAAA" => {
                parse_address_records(&stdout, &domain, record_type, &mut records);
            }
            "MX" => {
                parse_mx_records(&stdout, &domain, &mut records);
            }
            "NS" => {
                parse_ns_records(&stdout, &domain, &mut records);
            }
            "TXT" => {
                parse_txt_records(&stdout, &domain, &mut records);
            }
            "CNAME" => {
                parse_cname_records(&stdout, &domain, &mut records);
            }
            _ => {}
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
        let line = line.trim();
        if line.starts_with("Name:") {
            if let Some(name) = line.split(':').nth(1) {
                return Ok(name.trim().to_string());
            }
        }
        if line.contains("name =") {
            if let Some(name) = line.split('=').nth(1) {
                return Ok(name.trim().trim_end_matches('.').to_string());
            }
        }
    }
    
    Err("No PTR record found".to_string())
}

fn parse_address_records(output: &str, domain: &str, record_type: &str, records: &mut Vec<DnsRecord>) {
    let mut in_answer_section = false;
    
    for line in output.lines() {
        let line = line.trim();
        
        // Skip until we get past the server info
        if line.contains("Name:") && line.contains(domain) {
            in_answer_section = true;
            continue;
        }
        
        if in_answer_section && line.starts_with("Address:") {
            if let Some(addr) = line.split(':').nth(1) {
                let addr = addr.trim();
                // Skip server addresses (usually have # port)
                if !addr.contains('#') {
                    let is_ipv6 = addr.contains(':');
                    let matches_type = (record_type == "A" && !is_ipv6) || 
                                       (record_type == "AAAA" && is_ipv6);
                    if matches_type {
                        records.push(DnsRecord {
                            record_type: record_type.to_string(),
                            name: domain.to_string(),
                            value: addr.to_string(),
                            ttl: 300,
                        });
                    }
                }
            }
        }
        
        if line.starts_with("Addresses:") {
            // Multiple addresses on same or following lines
            if let Some(addrs) = line.split(':').nth(1) {
                for addr in addrs.split_whitespace() {
                    let is_ipv6 = addr.contains(':');
                    let matches_type = (record_type == "A" && !is_ipv6) || 
                                       (record_type == "AAAA" && is_ipv6);
                    if matches_type {
                        records.push(DnsRecord {
                            record_type: record_type.to_string(),
                            name: domain.to_string(),
                            value: addr.to_string(),
                            ttl: 300,
                        });
                    }
                }
            }
        }
    }
}

fn parse_mx_records(output: &str, domain: &str, records: &mut Vec<DnsRecord>) {
    for line in output.lines() {
        let line = line.trim();
        if line.contains("mail exchanger") || line.contains("MX preference") {
            // Format: "domain MX preference = X, mail exchanger = host"
            // Or: "MX preference = X, mail exchanger = host"
            if let Some(mx_part) = line.split("mail exchanger").nth(1) {
                let mx_host = mx_part.trim().trim_start_matches('=').trim();
                let priority = line
                    .split("preference")
                    .nth(1)
                    .and_then(|s| s.split(',').next())
                    .and_then(|s| s.trim().trim_start_matches('=').trim().parse::<u16>().ok())
                    .unwrap_or(10);
                
                records.push(DnsRecord {
                    record_type: "MX".to_string(),
                    name: domain.to_string(),
                    value: format!("{} {}", priority, mx_host.trim_end_matches('.')),
                    ttl: 300,
                });
            }
        }
    }
}

fn parse_ns_records(output: &str, domain: &str, records: &mut Vec<DnsRecord>) {
    for line in output.lines() {
        let line = line.trim();
        if line.contains("nameserver") {
            if let Some(ns) = line.split('=').nth(1) {
                records.push(DnsRecord {
                    record_type: "NS".to_string(),
                    name: domain.to_string(),
                    value: ns.trim().trim_end_matches('.').to_string(),
                    ttl: 300,
                });
            }
        }
    }
}

fn parse_txt_records(output: &str, domain: &str, records: &mut Vec<DnsRecord>) {
    for line in output.lines() {
        let line = line.trim();
        if line.contains("text") && line.contains('=') {
            if let Some(txt) = line.split('=').nth(1) {
                let txt_value = txt.trim().trim_matches('"').to_string();
                if !txt_value.is_empty() {
                    records.push(DnsRecord {
                        record_type: "TXT".to_string(),
                        name: domain.to_string(),
                        value: txt_value,
                        ttl: 300,
                    });
                }
            }
        }
    }
}

fn parse_cname_records(output: &str, domain: &str, records: &mut Vec<DnsRecord>) {
    for line in output.lines() {
        let line = line.trim();
        if line.contains("canonical name") || line.contains("CNAME") {
            if let Some(cname) = line.split('=').nth(1) {
                records.push(DnsRecord {
                    record_type: "CNAME".to_string(),
                    name: domain.to_string(),
                    value: cname.trim().trim_end_matches('.').to_string(),
                    ttl: 300,
                });
            }
        }
    }
}
