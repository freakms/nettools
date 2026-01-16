// SSL Checker command - Simplified version
use serde::{Deserialize, Serialize};
use native_tls::TlsConnector;
use std::net::TcpStream;

#[derive(Debug, Serialize, Deserialize)]
pub struct SslCertificate {
    pub subject: String,
    pub issuer: String,
    pub valid_from: String,
    pub valid_to: String,
    pub serial_number: String,
    pub is_valid: bool,
    pub days_until_expiry: i64,
    pub san: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SslCheckResult {
    pub host: String,
    pub port: u16,
    pub certificate: Option<SslCertificate>,
    pub error: Option<String>,
    pub protocol_version: Option<String>,
}

/// Check SSL certificate for a host
#[tauri::command]
pub async fn check_ssl(host: String, port: u16) -> Result<SslCheckResult, String> {
    let host_clone = host.clone();
    
    let result = tokio::task::spawn_blocking(move || {
        check_ssl_sync(&host_clone, port)
    })
    .await
    .map_err(|e| format!("Task error: {}", e))?;
    
    result
}

fn check_ssl_sync(host: &str, port: u16) -> Result<SslCheckResult, String> {
    let connector = TlsConnector::builder()
        .danger_accept_invalid_certs(true)
        .build()
        .map_err(|e| format!("Failed to create TLS connector: {}", e))?;

    let addr = format!("{}:{}", host, port);
    let stream = TcpStream::connect(&addr)
        .map_err(|e| format!("Failed to connect: {}", e))?;

    let tls_stream = connector
        .connect(host, stream)
        .map_err(|e| format!("TLS handshake failed: {}", e))?;

    // Get peer certificate
    if let Some(cert) = tls_stream
        .peer_certificate()
        .map_err(|e| format!("Failed to get certificate: {}", e))? 
    {
        let cert_der = cert.to_der()
            .map_err(|e| format!("Failed to encode certificate: {}", e))?;

        // Parse with x509-parser
        let (_, parsed) = x509_parser::parse_x509_certificate(&cert_der)
            .map_err(|e| format!("Failed to parse certificate: {:?}", e))?;

        let subject = parsed.subject().to_string();
        let issuer = parsed.issuer().to_string();
        
        let valid_from = parsed.validity().not_before.to_rfc2822()
            .unwrap_or_else(|_| "Unknown".to_string());
        let valid_to = parsed.validity().not_after.to_rfc2822()
            .unwrap_or_else(|_| "Unknown".to_string());
        
        // Serial as hex string
        let serial = parsed.raw_serial()
            .iter()
            .map(|b| format!("{:02X}", b))
            .collect::<Vec<_>>()
            .join(":");
        
        // Calculate days until expiry
        let not_after = parsed.validity().not_after.timestamp();
        let now = std::time::SystemTime::now()
            .duration_since(std::time::SystemTime::UNIX_EPOCH)
            .unwrap()
            .as_secs() as i64;
        let days_until_expiry = (not_after - now) / 86400;
        
        let is_valid = parsed.validity().is_valid();
        
        // Extract SANs
        let mut san = Vec::new();
        if let Ok(Some(ext)) = parsed.subject_alternative_name() {
            for name in ext.value.general_names.iter() {
                match name {
                    x509_parser::prelude::GeneralName::DNSName(dns) => {
                        san.push(dns.to_string())
                    },
                    _ => {}
                }
            }
        }

        return Ok(SslCheckResult {
            host: host.to_string(),
            port,
            certificate: Some(SslCertificate {
                subject,
                issuer,
                valid_from,
                valid_to,
                serial_number: serial,
                is_valid,
                days_until_expiry,
                san,
            }),
            error: None,
            protocol_version: Some("TLS 1.2+".to_string()),
        });
    }

    Ok(SslCheckResult {
        host: host.to_string(),
        port,
        certificate: None,
        error: Some("No certificate found".to_string()),
        protocol_version: None,
    })
}
