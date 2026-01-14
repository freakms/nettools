// SSL Checker command
use serde::{Deserialize, Serialize};
use native_tls::TlsConnector;
use std::net::TcpStream;
use x509_parser::prelude::*;
use chrono::{DateTime, Utc, NaiveDateTime};

#[derive(Debug, Serialize, Deserialize)]
pub struct SslCertificate {
    pub subject: String,
    pub issuer: String,
    pub valid_from: String,
    pub valid_to: String,
    pub serial_number: String,
    pub signature_algorithm: String,
    pub is_valid: bool,
    pub days_until_expiry: i64,
    pub san: Vec<String>, // Subject Alternative Names
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
        .danger_accept_invalid_certs(true) // We want to inspect even invalid certs
        .build()
        .map_err(|e| format!("Failed to create TLS connector: {}", e))?;

    let addr = format!("{}:{}", host, port);
    let stream = TcpStream::connect(&addr)
        .map_err(|e| format!("Failed to connect: {}", e))?;

    let tls_stream = connector
        .connect(host, stream)
        .map_err(|e| format!("TLS handshake failed: {}", e))?;

    // Get peer certificate
    let cert = tls_stream
        .peer_certificate()
        .map_err(|e| format!("Failed to get certificate: {}", e))?
        .ok_or_else(|| "No certificate presented".to_string())?;

    let cert_der = cert.to_der()
        .map_err(|e| format!("Failed to encode certificate: {}", e))?;

    // Parse certificate using x509-parser
    let (_, parsed_cert) = X509Certificate::from_der(&cert_der)
        .map_err(|e| format!("Failed to parse certificate: {}", e))?;

    let subject = parsed_cert.subject().to_string();
    let issuer = parsed_cert.issuer().to_string();
    
    let valid_from = parsed_cert.validity().not_before.to_rfc2822();
    let valid_to = parsed_cert.validity().not_after.to_rfc2822();
    
    let serial = parsed_cert.raw_serial_as_string();
    let sig_algo = parsed_cert.signature_algorithm.algorithm.to_string();
    
    // Calculate days until expiry
    let not_after = parsed_cert.validity().not_after.timestamp();
    let now = Utc::now().timestamp();
    let days_until_expiry = (not_after - now) / 86400;
    
    // Check validity
    let is_valid = parsed_cert.validity().is_valid();
    
    // Extract SANs
    let mut san = Vec::new();
    if let Ok(Some(ext)) = parsed_cert.subject_alternative_name() {
        for name in ext.value.general_names.iter() {
            match name {
                GeneralName::DNSName(dns) => san.push(dns.to_string()),
                GeneralName::IPAddress(ip) => san.push(format!("{:?}", ip)),
                _ => {}
            }
        }
    }

    Ok(SslCheckResult {
        host: host.to_string(),
        port,
        certificate: Some(SslCertificate {
            subject,
            issuer,
            valid_from,
            valid_to,
            serial_number: serial,
            signature_algorithm: sig_algo,
            is_valid,
            days_until_expiry,
            san,
        }),
        error: None,
        protocol_version: Some("TLS 1.2+".to_string()),
    })
}
