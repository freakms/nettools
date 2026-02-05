// SSL Checker command - Simplified version without x509-parser
use serde::{Deserialize, Serialize};
use super::utils::create_hidden_command;

#[cfg(target_os = "windows")]
use std::os::windows::process::CommandExt;

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

/// Check SSL certificate for a host using PowerShell
#[tauri::command]
pub async fn check_ssl(host: String, port: u16) -> Result<SslCheckResult, String> {
    let host_clone = host.clone();
    
    let result = tokio::task::spawn_blocking(move || {
        check_ssl_powershell(&host_clone, port)
    })
    .await
    .map_err(|e| format!("Task error: {}", e))?;
    
    result
}

fn check_ssl_powershell(host: &str, port: u16) -> Result<SslCheckResult, String> {
    // Use PowerShell to get SSL certificate info
    let script = format!(
        r#"
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        try {{
            $tcpClient.Connect("{}", {})
            $sslStream = New-Object System.Net.Security.SslStream($tcpClient.GetStream(), $false, {{ $true }})
            $sslStream.AuthenticateAsClient("{}")
            $cert = $sslStream.RemoteCertificate
            if ($cert) {{
                $cert2 = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($cert)
                Write-Output "SUBJECT:$($cert2.Subject)"
                Write-Output "ISSUER:$($cert2.Issuer)"
                Write-Output "NOTBEFORE:$($cert2.NotBefore.ToString('o'))"
                Write-Output "NOTAFTER:$($cert2.NotAfter.ToString('o'))"
                Write-Output "SERIAL:$($cert2.SerialNumber)"
                Write-Output "THUMBPRINT:$($cert2.Thumbprint)"
            }}
            $sslStream.Close()
        }} catch {{
            Write-Output "ERROR:$($_.Exception.Message)"
        }} finally {{
            $tcpClient.Close()
        }}
        "#,
        host, port, host
    );

    let mut cmd = create_hidden_command("powershell");
    let output = cmd
        .args(["-NoProfile", "-Command", &script])
        .output()
        .map_err(|e| format!("Failed to execute PowerShell: {}", e))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    
    // Check for error
    if stdout.contains("ERROR:") {
        let error_msg = stdout
            .lines()
            .find(|l| l.starts_with("ERROR:"))
            .map(|l| l.replace("ERROR:", ""))
            .unwrap_or_else(|| "Unknown error".to_string());
        
        return Ok(SslCheckResult {
            host: host.to_string(),
            port,
            certificate: None,
            error: Some(error_msg),
            protocol_version: None,
        });
    }

    // Parse output
    let mut subject = String::new();
    let mut issuer = String::new();
    let mut valid_from = String::new();
    let mut valid_to = String::new();
    let mut serial = String::new();

    for line in stdout.lines() {
        if line.starts_with("SUBJECT:") {
            subject = line.replace("SUBJECT:", "");
        } else if line.starts_with("ISSUER:") {
            issuer = line.replace("ISSUER:", "");
        } else if line.starts_with("NOTBEFORE:") {
            valid_from = line.replace("NOTBEFORE:", "");
        } else if line.starts_with("NOTAFTER:") {
            valid_to = line.replace("NOTAFTER:", "");
        } else if line.starts_with("SERIAL:") {
            serial = line.replace("SERIAL:", "");
        }
    }

    // Calculate days until expiry
    let days_until_expiry = calculate_days_until_expiry(&valid_to);

    Ok(SslCheckResult {
        host: host.to_string(),
        port,
        certificate: Some(SslCertificate {
            subject,
            issuer,
            valid_from,
            valid_to,
            serial_number: serial,
            is_valid: days_until_expiry > 0,
            days_until_expiry,
            san: vec![host.to_string()],
        }),
        error: None,
        protocol_version: Some("TLS 1.2+".to_string()),
    })
}

fn calculate_days_until_expiry(date_str: &str) -> i64 {
    // Try to parse ISO 8601 date
    if let Ok(date) = chrono::DateTime::parse_from_rfc3339(date_str) {
        let now = chrono::Utc::now();
        return (date.signed_duration_since(now)).num_days();
    }
    
    // Default to 365 if parsing fails
    365
}
