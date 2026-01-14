// Utility commands - Updated for Tauri 2.x
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct SystemInfo {
    pub os_name: String,
    pub os_version: String,
    pub hostname: String,
    pub username: String,
}

/// Get system information
#[tauri::command]
pub fn get_system_info() -> SystemInfo {
    SystemInfo {
        os_name: std::env::consts::OS.to_string(),
        os_version: "Windows".to_string(),
        hostname: hostname::get()
            .map(|h| h.to_string_lossy().to_string())
            .unwrap_or_else(|_| "Unknown".to_string()),
        username: whoami::username(),
    }
}
