// Port Scanner commands
use serde::{Deserialize, Serialize};
use std::net::{SocketAddr, TcpStream};
use std::time::Duration;

#[derive(Debug, Serialize, Deserialize)]
pub struct PortResult {
    pub port: u16,
    pub status: String, // "open", "closed", "filtered"
    pub service: Option<String>,
    pub banner: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct PortScanResult {
    pub target: String,
    pub results: Vec<PortResult>,
    pub open_ports: usize,
    pub duration_ms: u64,
}

// Common ports and their services
const COMMON_PORTS: &[(u16, &str)] = &[
    (20, "FTP-DATA"),
    (21, "FTP"),
    (22, "SSH"),
    (23, "Telnet"),
    (25, "SMTP"),
    (53, "DNS"),
    (80, "HTTP"),
    (110, "POP3"),
    (111, "RPC"),
    (135, "MSRPC"),
    (139, "NetBIOS"),
    (143, "IMAP"),
    (443, "HTTPS"),
    (445, "SMB"),
    (993, "IMAPS"),
    (995, "POP3S"),
    (1433, "MSSQL"),
    (1521, "Oracle"),
    (3306, "MySQL"),
    (3389, "RDP"),
    (5432, "PostgreSQL"),
    (5900, "VNC"),
    (6379, "Redis"),
    (8080, "HTTP-ALT"),
    (8443, "HTTPS-ALT"),
    (27017, "MongoDB"),
];

/// Scan a single port on a target
#[tauri::command]
pub async fn scan_single_port(target: String, port: u16, timeout_ms: u32) -> Result<PortResult, String> {
    let addr = format!("{}:{}", target, port);
    let socket_addr: SocketAddr = addr
        .parse()
        .map_err(|_| format!("Invalid address: {}", addr))?;
    
    let timeout = Duration::from_millis(timeout_ms as u64);
    
    let status = match TcpStream::connect_timeout(&socket_addr, timeout) {
        Ok(_stream) => "open",
        Err(e) => {
            if e.kind() == std::io::ErrorKind::TimedOut {
                "filtered"
            } else {
                "closed"
            }
        }
    };
    
    let service = get_service_name(port);
    
    Ok(PortResult {
        port,
        status: status.to_string(),
        service,
        banner: None, // Banner grabbing can be added later
    })
}

/// Scan multiple ports on a target
#[tauri::command]
pub async fn scan_ports(
    target: String,
    ports: Vec<u16>,
    timeout_ms: u32,
) -> Result<PortScanResult, String> {
    let start = std::time::Instant::now();
    
    let mut results = Vec::new();
    let mut handles = Vec::new();
    
    // Scan ports in parallel
    for port in ports {
        let target_clone = target.clone();
        let handle = tokio::spawn(async move {
            scan_single_port(target_clone, port, timeout_ms).await
        });
        handles.push(handle);
    }
    
    for handle in handles {
        if let Ok(Ok(result)) = handle.await {
            results.push(result);
        }
    }
    
    // Sort by port number
    results.sort_by_key(|r| r.port);
    
    let open_ports = results.iter().filter(|r| r.status == "open").count();
    let duration_ms = start.elapsed().as_millis() as u64;

    Ok(PortScanResult {
        target,
        results,
        open_ports,
        duration_ms,
    })
}

fn get_service_name(port: u16) -> Option<String> {
    COMMON_PORTS
        .iter()
        .find(|(p, _)| *p == port)
        .map(|(_, name)| name.to_string())
}
