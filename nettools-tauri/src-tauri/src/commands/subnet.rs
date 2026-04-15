// Subnet Calculator command
use serde::{Deserialize, Serialize};
use ipnetwork::IpNetwork;
use std::net::Ipv4Addr;

#[derive(Debug, Serialize, Deserialize)]
pub struct SubnetInfo {
    pub network: String,
    pub broadcast: String,
    pub netmask: String,
    pub wildcard_mask: String,
    pub first_host: String,
    pub last_host: String,
    pub total_hosts: u32,
    pub usable_hosts: u32,
    pub cidr: u8,
    pub ip_class: String,
    pub is_private: bool,
}

/// Calculate subnet information from CIDR notation
#[tauri::command]
pub fn calculate_subnet(cidr: String) -> Result<SubnetInfo, String> {
    let network: IpNetwork = cidr
        .parse()
        .map_err(|e| format!("Invalid CIDR notation: {}", e))?;
    
    match network {
        IpNetwork::V4(net) => {
            let network_addr = net.network();
            let broadcast = net.broadcast();
            let prefix = net.prefix();
            
            // Calculate netmask
            let mask_bits = !((1u32 << (32 - prefix)) - 1);
            let netmask = Ipv4Addr::from(mask_bits);
            
            // Calculate wildcard mask
            let wildcard_bits = (1u32 << (32 - prefix)) - 1;
            let wildcard = Ipv4Addr::from(wildcard_bits);
            
            // Calculate hosts
            let total_hosts = if prefix >= 31 {
                2u32.pow((32 - prefix) as u32)
            } else {
                2u32.pow((32 - prefix) as u32)
            };
            
            let usable_hosts = if prefix >= 31 {
                total_hosts
            } else {
                total_hosts.saturating_sub(2)
            };
            
            // First and last usable host
            let first_host = if prefix >= 31 {
                network_addr
            } else {
                Ipv4Addr::from(u32::from(network_addr) + 1)
            };
            
            let last_host = if prefix >= 31 {
                broadcast
            } else {
                Ipv4Addr::from(u32::from(broadcast) - 1)
            };
            
            // Determine IP class
            let first_octet = network_addr.octets()[0];
            let ip_class = match first_octet {
                0..=127 => "A",
                128..=191 => "B",
                192..=223 => "C",
                224..=239 => "D (Multicast)",
                240..=255 => "E (Reserved)",
            };
            
            // Check if private
            let is_private = network_addr.is_private();
            
            Ok(SubnetInfo {
                network: network_addr.to_string(),
                broadcast: broadcast.to_string(),
                netmask: netmask.to_string(),
                wildcard_mask: wildcard.to_string(),
                first_host: first_host.to_string(),
                last_host: last_host.to_string(),
                total_hosts,
                usable_hosts,
                cidr: prefix,
                ip_class: ip_class.to_string(),
                is_private,
            })
        }
        IpNetwork::V6(_) => {
            Err("IPv6 subnet calculation not yet supported".to_string())
        }
    }
}
