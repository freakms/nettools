// DNS Lookup commands - Updated for Tauri 2.x
use serde::{Deserialize, Serialize};
use hickory_resolver::config::*;
use hickory_resolver::Resolver;

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

/// Perform DNS lookup for a domain
#[tauri::command]
pub async fn lookup_dns(domain: String, record_types: Vec<String>) -> Result<DnsResult, String> {
    let start = std::time::Instant::now();
    
    let resolver = Resolver::new(ResolverConfig::default(), ResolverOpts::default())
        .map_err(|e| format!("Failed to create resolver: {}", e))?;
    
    let mut records = Vec::new();
    
    for record_type in &record_types {
        match record_type.as_str() {
            "A" => {
                if let Ok(response) = resolver.lookup_ip(&domain) {
                    for ip in response.iter() {
                        if ip.is_ipv4() {
                            records.push(DnsRecord {
                                record_type: "A".to_string(),
                                name: domain.clone(),
                                value: ip.to_string(),
                                ttl: 300, // Default TTL
                            });
                        }
                    }
                }
            }
            "AAAA" => {
                if let Ok(response) = resolver.lookup_ip(&domain) {
                    for ip in response.iter() {
                        if ip.is_ipv6() {
                            records.push(DnsRecord {
                                record_type: "AAAA".to_string(),
                                name: domain.clone(),
                                value: ip.to_string(),
                                ttl: 300,
                            });
                        }
                    }
                }
            }
            "MX" => {
                if let Ok(response) = resolver.mx_lookup(&domain) {
                    for mx in response.iter() {
                        records.push(DnsRecord {
                            record_type: "MX".to_string(),
                            name: domain.clone(),
                            value: format!("{} {}", mx.preference(), mx.exchange()),
                            ttl: 300,
                        });
                    }
                }
            }
            "NS" => {
                if let Ok(response) = resolver.ns_lookup(&domain) {
                    for ns in response.iter() {
                        records.push(DnsRecord {
                            record_type: "NS".to_string(),
                            name: domain.clone(),
                            value: ns.to_string(),
                            ttl: 300,
                        });
                    }
                }
            }
            "TXT" => {
                if let Ok(response) = resolver.txt_lookup(&domain) {
                    for txt in response.iter() {
                        let txt_data: String = txt.iter()
                            .map(|d| String::from_utf8_lossy(d).to_string())
                            .collect::<Vec<_>>()
                            .join("");
                        records.push(DnsRecord {
                            record_type: "TXT".to_string(),
                            name: domain.clone(),
                            value: txt_data,
                            ttl: 300,
                        });
                    }
                }
            }
            "SOA" => {
                if let Ok(response) = resolver.soa_lookup(&domain) {
                    for soa in response.iter() {
                        records.push(DnsRecord {
                            record_type: "SOA".to_string(),
                            name: domain.clone(),
                            value: format!(
                                "{} {} {} {} {} {} {}",
                                soa.mname(),
                                soa.rname(),
                                soa.serial(),
                                soa.refresh(),
                                soa.retry(),
                                soa.expire(),
                                soa.minimum()
                            ),
                            ttl: 300,
                        });
                    }
                }
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
    let resolver = Resolver::new(ResolverConfig::default(), ResolverOpts::default())
        .map_err(|e| format!("Failed to create resolver: {}", e))?;
    
    let ip_addr: std::net::IpAddr = ip
        .parse()
        .map_err(|_| "Invalid IP address".to_string())?;
    
    let response = resolver
        .reverse_lookup(ip_addr)
        .map_err(|e| format!("Reverse lookup failed: {}", e))?;
    
    response
        .iter()
        .next()
        .map(|name| name.to_string())
        .ok_or_else(|| "No PTR record found".to_string())
}
