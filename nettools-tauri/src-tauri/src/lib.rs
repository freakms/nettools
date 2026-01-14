// NetTools Suite - Tauri 2.x Backend
// Copyright (c) 2024 frekms

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;

use commands::*;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_clipboard_manager::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_os::init())
        .plugin(tauri_plugin_process::init())
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
            utils::get_system_info,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
