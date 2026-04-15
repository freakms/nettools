// Network Profile Manager - Windows network adapter management
use serde::{Deserialize, Serialize};
use super::utils::create_hidden_command;
use std::fs;
use std::path::Path;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NetworkAdapter {
    pub name: String,
    pub description: String,
    pub status: String,
    pub mac_address: Option<String>,
    pub ip_address: Option<String>,
    pub subnet_mask: Option<String>,
    pub gateway: Option<String>,
    pub dns_servers: Vec<String>,
    pub dhcp_enabled: bool,
    pub speed: Option<String>,
    pub adapter_type: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NetworkProfile {
    pub id: String,
    pub name: String,
    pub adapter_name: String,
    pub use_dhcp: bool,
    pub ip_address: Option<String>,
    pub subnet_mask: Option<String>,
    pub gateway: Option<String>,
    pub dns_primary: Option<String>,
    pub dns_secondary: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct HostsEntry {
    pub ip: String,
    pub hostname: String,
    pub comment: Option<String>,
}

/// Get all network adapters
#[tauri::command]
pub async fn get_network_adapters() -> Result<Vec<NetworkAdapter>, String> {
    // Use PowerShell to get detailed adapter info
    let script = r#"
        Get-NetAdapter | ForEach-Object {
            $adapter = $_
            $config = Get-NetIPConfiguration -InterfaceIndex $adapter.ifIndex -ErrorAction SilentlyContinue
            $ipv4 = Get-NetIPAddress -InterfaceIndex $adapter.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue | Select-Object -First 1
            $dns = Get-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
            
            [PSCustomObject]@{
                Name = $adapter.Name
                Description = $adapter.InterfaceDescription
                Status = $adapter.Status
                MacAddress = $adapter.MacAddress
                Speed = if($adapter.LinkSpeed) { $adapter.LinkSpeed } else { $null }
                MediaType = $adapter.MediaType
                IPAddress = if($ipv4) { $ipv4.IPAddress } else { $null }
                PrefixLength = if($ipv4) { $ipv4.PrefixLength } else { $null }
                Gateway = if($config.IPv4DefaultGateway) { $config.IPv4DefaultGateway.NextHop } else { $null }
                DnsServers = if($dns) { $dns.ServerAddresses -join ',' } else { '' }
                DhcpEnabled = (Get-NetIPInterface -InterfaceIndex $adapter.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue).Dhcp -eq 'Enabled'
            } | ConvertTo-Json -Compress
        }
    "#;

    let output = create_hidden_command("powershell")
        .args(["-NoProfile", "-Command", script])
        .output()
        .map_err(|e| format!("Failed to execute PowerShell: {}", e))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let mut adapters = Vec::new();

    for line in stdout.lines() {
        let line = line.trim();
        if line.starts_with('{') {
            if let Ok(json) = serde_json::from_str::<serde_json::Value>(line) {
                let prefix_length = json.get("PrefixLength").and_then(|v| v.as_u64()).unwrap_or(24);
                let subnet_mask = prefix_to_subnet(prefix_length as u8);
                
                let dns_str = json.get("DnsServers").and_then(|v| v.as_str()).unwrap_or("");
                let dns_servers: Vec<String> = dns_str.split(',')
                    .map(|s| s.trim().to_string())
                    .filter(|s| !s.is_empty())
                    .collect();

                adapters.push(NetworkAdapter {
                    name: json.get("Name").and_then(|v| v.as_str()).unwrap_or("").to_string(),
                    description: json.get("Description").and_then(|v| v.as_str()).unwrap_or("").to_string(),
                    status: json.get("Status").and_then(|v| v.as_str()).unwrap_or("Unknown").to_string(),
                    mac_address: json.get("MacAddress").and_then(|v| v.as_str()).map(|s| s.to_string()),
                    ip_address: json.get("IPAddress").and_then(|v| v.as_str()).map(|s| s.to_string()),
                    subnet_mask: Some(subnet_mask),
                    gateway: json.get("Gateway").and_then(|v| v.as_str()).map(|s| s.to_string()),
                    dns_servers,
                    dhcp_enabled: json.get("DhcpEnabled").and_then(|v| v.as_bool()).unwrap_or(true),
                    speed: json.get("Speed").and_then(|v| v.as_str()).map(|s| s.to_string()),
                    adapter_type: json.get("MediaType").and_then(|v| v.as_str()).unwrap_or("Unknown").to_string(),
                });
            }
        }
    }

    Ok(adapters)
}

/// Enable a network adapter (requires admin)
#[tauri::command]
pub async fn enable_adapter(adapter_name: String) -> Result<String, String> {
    let script = format!(r#"Enable-NetAdapter -Name "{}" -Confirm:$false"#, adapter_name);
    
    let output = create_hidden_command("powershell")
        .args(["-NoProfile", "-Command", &script])
        .output()
        .map_err(|e| format!("Failed to execute PowerShell: {}", e))?;

    if output.status.success() {
        Ok(format!("Adapter '{}' aktiviert", adapter_name))
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        if stderr.contains("Access") || stderr.contains("Administrator") {
            Err("Administrator-Rechte erforderlich. Bitte App als Admin starten.".to_string())
        } else {
            Err(format!("Fehler: {}", stderr))
        }
    }
}

/// Disable a network adapter (requires admin)
#[tauri::command]
pub async fn disable_adapter(adapter_name: String) -> Result<String, String> {
    let script = format!(r#"Disable-NetAdapter -Name "{}" -Confirm:$false"#, adapter_name);
    
    let output = create_hidden_command("powershell")
        .args(["-NoProfile", "-Command", &script])
        .output()
        .map_err(|e| format!("Failed to execute PowerShell: {}", e))?;

    if output.status.success() {
        Ok(format!("Adapter '{}' deaktiviert", adapter_name))
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        if stderr.contains("Access") || stderr.contains("Administrator") {
            Err("Administrator-Rechte erforderlich. Bitte App als Admin starten.".to_string())
        } else {
            Err(format!("Fehler: {}", stderr))
        }
    }
}

/// Apply network profile to adapter (requires admin)
#[tauri::command]
pub async fn apply_network_profile(profile: NetworkProfile) -> Result<String, String> {
    let mut commands = Vec::new();

    if profile.use_dhcp {
        // Enable DHCP
        commands.push(format!(
            r#"Set-NetIPInterface -InterfaceAlias "{}" -Dhcp Enabled"#,
            profile.adapter_name
        ));
        commands.push(format!(
            r#"Set-DnsClientServerAddress -InterfaceAlias "{}" -ResetServerAddresses"#,
            profile.adapter_name
        ));
    } else {
        // Static IP configuration
        if let (Some(ip), Some(subnet)) = (&profile.ip_address, &profile.subnet_mask) {
            let prefix = subnet_to_prefix(subnet);
            
            // Remove existing IP first
            commands.push(format!(
                r#"Remove-NetIPAddress -InterfaceAlias "{}" -Confirm:$false -ErrorAction SilentlyContinue"#,
                profile.adapter_name
            ));
            
            // Add new IP
            let mut ip_cmd = format!(
                r#"New-NetIPAddress -InterfaceAlias "{}" -IPAddress "{}" -PrefixLength {}"#,
                profile.adapter_name, ip, prefix
            );
            
            if let Some(gw) = &profile.gateway {
                if !gw.is_empty() {
                    ip_cmd.push_str(&format!(r#" -DefaultGateway "{}""#, gw));
                }
            }
            commands.push(ip_cmd);
        }

        // Set DNS servers
        let mut dns_servers = Vec::new();
        if let Some(dns1) = &profile.dns_primary {
            if !dns1.is_empty() {
                dns_servers.push(format!(r#""{}""#, dns1));
            }
        }
        if let Some(dns2) = &profile.dns_secondary {
            if !dns2.is_empty() {
                dns_servers.push(format!(r#""{}""#, dns2));
            }
        }
        
        if !dns_servers.is_empty() {
            commands.push(format!(
                r#"Set-DnsClientServerAddress -InterfaceAlias "{}" -ServerAddresses {}"#,
                profile.adapter_name,
                dns_servers.join(",")
            ));
        }
    }

    let script = commands.join("; ");
    
    let output = create_hidden_command("powershell")
        .args(["-NoProfile", "-Command", &script])
        .output()
        .map_err(|e| format!("Failed to execute PowerShell: {}", e))?;

    if output.status.success() {
        Ok(format!("Profil '{}' angewendet", profile.name))
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        if stderr.contains("Access") || stderr.contains("Administrator") || stderr.contains("denied") {
            Err("Administrator-Rechte erforderlich. Bitte App als Admin starten.".to_string())
        } else {
            Err(format!("Fehler: {}", stderr))
        }
    }
}

/// Get hosts file content
#[tauri::command]
pub async fn get_hosts_file() -> Result<Vec<HostsEntry>, String> {
    let hosts_path = r"C:\Windows\System32\drivers\etc\hosts";
    
    let content = fs::read_to_string(hosts_path)
        .map_err(|e| format!("Hosts-Datei konnte nicht gelesen werden: {}", e))?;

    let mut entries = Vec::new();
    
    for line in content.lines() {
        let line = line.trim();
        
        // Skip empty lines and comments
        if line.is_empty() || line.starts_with('#') {
            continue;
        }

        // Parse entry
        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() >= 2 {
            let ip = parts[0].to_string();
            let hostname = parts[1].to_string();
            let comment = if parts.len() > 2 {
                Some(parts[2..].join(" "))
            } else {
                None
            };

            entries.push(HostsEntry { ip, hostname, comment });
        }
    }

    Ok(entries)
}

/// Update hosts file (requires admin)
#[tauri::command]
pub async fn update_hosts_file(entries: Vec<HostsEntry>) -> Result<String, String> {
    let hosts_path = r"C:\Windows\System32\drivers\etc\hosts";
    
    // Read existing content to preserve comments
    let existing = fs::read_to_string(hosts_path).unwrap_or_default();
    
    let mut new_content = String::new();
    
    // Preserve header comments
    for line in existing.lines() {
        if line.starts_with('#') {
            new_content.push_str(line);
            new_content.push('\n');
        } else {
            break;
        }
    }
    
    // Add default header if none exists
    if new_content.is_empty() {
        new_content.push_str("# Hosts file managed by NetTools\n");
        new_content.push_str("# localhost entries\n");
        new_content.push_str("127.0.0.1       localhost\n");
        new_content.push_str("::1             localhost\n\n");
        new_content.push_str("# Custom entries\n");
    }
    
    // Add entries
    for entry in entries {
        let line = if let Some(comment) = entry.comment {
            format!("{}\t{}\t# {}\n", entry.ip, entry.hostname, comment)
        } else {
            format!("{}\t{}\n", entry.ip, entry.hostname)
        };
        new_content.push_str(&line);
    }

    // Write using PowerShell to handle admin rights
    let escaped_content = new_content.replace("\"", "`\"").replace("\n", "`n");
    let script = format!(
        r#"Set-Content -Path "{}" -Value "{}" -Encoding ASCII"#,
        hosts_path, escaped_content
    );
    
    let output = create_hidden_command("powershell")
        .args(["-NoProfile", "-Command", &script])
        .output()
        .map_err(|e| format!("Failed to execute PowerShell: {}", e))?;

    if output.status.success() {
        Ok("Hosts-Datei aktualisiert".to_string())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        if stderr.contains("Access") || stderr.contains("denied") {
            Err("Administrator-Rechte erforderlich. Bitte App als Admin starten.".to_string())
        } else {
            Err(format!("Fehler: {}", stderr))
        }
    }
}

/// Get computer name
#[tauri::command]
pub async fn get_computer_name() -> Result<String, String> {
    let output = create_hidden_command("hostname")
        .output()
        .map_err(|e| format!("Failed to get hostname: {}", e))?;

    let name = String::from_utf8_lossy(&output.stdout).trim().to_string();
    Ok(name)
}

/// Set computer name (requires admin + restart)
#[tauri::command]
pub async fn set_computer_name(new_name: String) -> Result<String, String> {
    // Validate name
    if new_name.is_empty() || new_name.len() > 15 {
        return Err("Computer-Name muss 1-15 Zeichen lang sein".to_string());
    }

    if !new_name.chars().all(|c| c.is_alphanumeric() || c == '-') {
        return Err("Computer-Name darf nur Buchstaben, Zahlen und Bindestriche enthalten".to_string());
    }

    let script = format!(
        r#"Rename-Computer -NewName "{}" -Force"#,
        new_name
    );
    
    let output = create_hidden_command("powershell")
        .args(["-NoProfile", "-Command", &script])
        .output()
        .map_err(|e| format!("Failed to execute PowerShell: {}", e))?;

    if output.status.success() {
        Ok("Computer-Name geändert. Neustart erforderlich!".to_string())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        if stderr.contains("Access") || stderr.contains("Administrator") {
            Err("Administrator-Rechte erforderlich. Bitte App als Admin starten.".to_string())
        } else {
            Err(format!("Fehler: {}", stderr))
        }
    }
}

/// Flush DNS cache
#[tauri::command]
pub async fn flush_dns_cache() -> Result<String, String> {
    let output = create_hidden_command("ipconfig")
        .arg("/flushdns")
        .output()
        .map_err(|e| format!("Failed to flush DNS: {}", e))?;

    if output.status.success() {
        Ok("DNS-Cache geleert".to_string())
    } else {
        Err("Fehler beim Leeren des DNS-Cache".to_string())
    }
}

/// Release and renew DHCP
#[tauri::command]
pub async fn renew_dhcp(adapter_name: String) -> Result<String, String> {
    // Release
    let release = create_hidden_command("ipconfig")
        .args(["/release", &adapter_name])
        .output()
        .map_err(|e| format!("Failed to release: {}", e))?;

    // Renew
    let renew = create_hidden_command("ipconfig")
        .args(["/renew", &adapter_name])
        .output()
        .map_err(|e| format!("Failed to renew: {}", e))?;

    if renew.status.success() {
        Ok("DHCP erneuert".to_string())
    } else {
        let stderr = String::from_utf8_lossy(&renew.stderr);
        Err(format!("Fehler: {}", stderr))
    }
}

// Helper functions
fn prefix_to_subnet(prefix: u8) -> String {
    let mask: u32 = if prefix == 0 {
        0
    } else {
        !0u32 << (32 - prefix)
    };
    
    format!(
        "{}.{}.{}.{}",
        (mask >> 24) & 255,
        (mask >> 16) & 255,
        (mask >> 8) & 255,
        mask & 255
    )
}

fn subnet_to_prefix(subnet: &str) -> u8 {
    let parts: Vec<u8> = subnet.split('.')
        .filter_map(|s| s.parse().ok())
        .collect();
    
    if parts.len() != 4 {
        return 24; // default
    }
    
    let mask: u32 = ((parts[0] as u32) << 24) 
        | ((parts[1] as u32) << 16) 
        | ((parts[2] as u32) << 8) 
        | (parts[3] as u32);
    
    mask.count_ones() as u8
}
