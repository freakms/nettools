// WHOIS Lookup command
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct WhoisResult {
    pub domain: String,
    pub registrar: Option<String>,
    pub creation_date: Option<String>,
    pub expiration_date: Option<String>,
    pub name_servers: Vec<String>,
    pub status: Vec<String>,
    pub raw_data: String,
}

/// Perform WHOIS lookup for a domain
#[tauri::command]
pub async fn lookup_whois(domain: String) -> Result<WhoisResult, String> {
    let whois_server = determine_whois_server(&domain);
    let domain_clone = domain.clone();
    
    let output = tokio::task::spawn_blocking(move || {
        use std::io::{Read, Write};
        use std::net::TcpStream;
        use std::time::Duration;
        
        let mut stream = TcpStream::connect(format!("{}:43", whois_server))
            .map_err(|e| format!("Failed to connect to WHOIS server: {}", e))?;
        
        stream.set_read_timeout(Some(Duration::from_secs(10))).ok();
        stream.set_write_timeout(Some(Duration::from_secs(5))).ok();
        
        stream.write_all(format!("{}\r\n", domain_clone).as_bytes())
            .map_err(|e| format!("Failed to send query: {}", e))?;
        
        let mut response = String::new();
        stream.read_to_string(&mut response)
            .map_err(|e| format!("Failed to read response: {}", e))?;
        
        Ok::<String, String>(response)
    })
    .await
    .map_err(|e| format!("Task error: {}", e))??;

    let result = parse_whois_output(&domain, &output);
    
    Ok(result)
}

fn determine_whois_server(domain: &str) -> &'static str {
    let tld = domain.rsplit('.').next().unwrap_or("");
    
    match tld.to_lowercase().as_str() {
        "com" | "net" => "whois.verisign-grs.com",
        "org" => "whois.pir.org",
        "de" => "whois.denic.de",
        "uk" | "co.uk" => "whois.nic.uk",
        "io" => "whois.nic.io",
        "me" => "whois.nic.me",
        "eu" => "whois.eu",
        "info" => "whois.afilias.net",
        "biz" => "whois.biz",
        _ => "whois.iana.org",
    }
}

fn parse_whois_output(domain: &str, output: &str) -> WhoisResult {
    let mut registrar = None;
    let mut creation_date = None;
    let mut expiration_date = None;
    let mut name_servers = Vec::new();
    let mut status = Vec::new();
    
    for line in output.lines() {
        let line = line.trim();
        let lower = line.to_lowercase();
        
        if lower.starts_with("registrar:") {
            registrar = Some(line.split(':').skip(1).collect::<Vec<_>>().join(":").trim().to_string());
        } else if lower.contains("creation date") || lower.contains("created:") || lower.contains("registered:") {
            creation_date = Some(line.split(':').skip(1).collect::<Vec<_>>().join(":").trim().to_string());
        } else if lower.contains("expir") && lower.contains("date") {
            expiration_date = Some(line.split(':').skip(1).collect::<Vec<_>>().join(":").trim().to_string());
        } else if lower.starts_with("name server:") || lower.starts_with("nserver:") {
            let ns = line.split(':').skip(1).collect::<Vec<_>>().join(":").trim().to_string();
            if !ns.is_empty() {
                name_servers.push(ns);
            }
        } else if lower.starts_with("status:") || lower.starts_with("domain status:") {
            let s = line.split(':').skip(1).collect::<Vec<_>>().join(":").trim().to_string();
            if !s.is_empty() {
                status.push(s);
            }
        }
    }
    
    WhoisResult {
        domain: domain.to_string(),
        registrar,
        creation_date,
        expiration_date,
        name_servers,
        status,
        raw_data: output.to_string(),
    }
}
