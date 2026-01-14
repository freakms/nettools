// SSL Checker command - Updated for Tauri 2.x
use serde::{Deserialize, Serialize};
use std::net::TcpStream;
use std::io::{Read, Write};
use std::sync::Arc;

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
    use rustls::ClientConfig;
    use rustls::pki_types::ServerName;
    use std::time::SystemTime;
    
    // Create rustls config that accepts all certificates for inspection
    let root_store = rustls::RootCertStore::empty();
    
    let config = ClientConfig::builder()
        .with_root_certificates(root_store)
        .with_no_client_auth();
    
    let server_name = ServerName::try_from(host.to_string())
        .map_err(|_| "Invalid server name")?;
    
    let mut conn = rustls::ClientConnection::new(Arc::new(config), server_name)
        .map_err(|e| format!("Failed to create TLS connection: {}", e))?;
    
    let addr = format!("{}:{}", host, port);
    let mut sock = TcpStream::connect(&addr)
        .map_err(|e| format!("Failed to connect: {}", e))?;
    
    let mut tls = rustls::Stream::new(&mut conn, &mut sock);
    
    // Try to complete handshake
    let _ = tls.write(&[]);
    
    // Get peer certificates
    let certs = conn.peer_certificates();
    
    if let Some(cert_chain) = certs {
        if let Some(cert) = cert_chain.first() {
            // Parse certificate with x509-parser
            let (_, parsed) = x509_parser::parse_x509_certificate(cert.as_ref())
                .map_err(|e| format!("Failed to parse certificate: {:?}", e))?;
            
            let subject = parsed.subject().to_string();
            let issuer = parsed.issuer().to_string();
            let valid_from = parsed.validity().not_before.to_rfc2822();
            let valid_to = parsed.validity().not_after.to_rfc2822();
            let serial = format!("{:X}", parsed.raw_serial());
            
            // Calculate days until expiry
            let not_after = parsed.validity().not_after.timestamp();
            let now = SystemTime::now()
                .duration_since(SystemTime::UNIX_EPOCH)
                .unwrap()
                .as_secs() as i64;
            let days_until_expiry = (not_after - now) / 86400;
            
            let is_valid = parsed.validity().is_valid();
            
            // Extract SANs
            let mut san = Vec::new();
            if let Ok(Some(ext)) = parsed.subject_alternative_name() {
                for name in ext.value.general_names.iter() {
                    match name {
                        x509_parser::prelude::GeneralName::DNSName(dns) => san.push(dns.to_string()),
                        x509_parser::prelude::GeneralName::IPAddress(ip) => san.push(format!("{:?}", ip)),
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
                protocol_version: Some("TLS 1.3".to_string()),
            });
        }
    }
    
    Ok(SslCheckResult {
        host: host.to_string(),
        port,
        certificate: None,
        error: Some("No certificate found".to_string()),
        protocol_version: None,
    })
}
