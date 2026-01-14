// NetTools Suite - Tauri Backend
// Copyright (c) 2024 frekms

#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

mod commands;

use commands::*;

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            // Scanner commands
            scanner::ping_host,
            scanner::scan_network,
            scanner::get_local_ip,
            // Port scanner commands
            port_scanner::scan_ports,
            port_scanner::scan_single_port,
            // DNS commands
            dns::lookup_dns,
            dns::reverse_lookup,
            // Traceroute commands
            traceroute::run_traceroute,
            // ARP commands
            arp::get_arp_table,
            // Subnet commands
            subnet::calculate_subnet,
            // WHOIS commands
            whois::lookup_whois,
            // SSL commands
            ssl::check_ssl,
            // Hash commands
            hash::generate_hashes,
            hash::hash_file,
            // Password commands
            password::generate_password,
            // Utility commands
            utils::copy_to_clipboard,
            utils::get_system_info,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
