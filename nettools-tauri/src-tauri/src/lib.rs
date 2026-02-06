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
            scanner::ping_host_with_hostname,
            scanner::scan_network,
            scanner::resolve_hostname,
            scanner::resolve_hostnames_batch,
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
            // MAC commands
            mac::format_mac,
            mac::lookup_mac_vendor,
            // API Tester commands
            api_tester::send_http_request,
            // Live Monitor commands
            live_monitor::monitor_init_hosts,
            live_monitor::monitor_ping_host,
            live_monitor::monitor_resolve_hostname,
            live_monitor::monitor_export_data,
            // Utility commands
            utils::get_system_info,
            // Network Profile commands
            network_profile::get_network_adapters,
            network_profile::enable_adapter,
            network_profile::disable_adapter,
            network_profile::apply_network_profile,
            network_profile::get_hosts_file,
            network_profile::update_hosts_file,
            network_profile::get_computer_name,
            network_profile::set_computer_name,
            network_profile::flush_dns_cache,
            network_profile::renew_dhcp,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
