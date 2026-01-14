// Utility commands
use serde::{Deserialize, Serialize};
use tauri::ClipboardManager;

#[derive(Debug, Serialize, Deserialize)]
pub struct SystemInfo {
    pub os_name: String,
    pub os_version: String,
    pub hostname: String,
    pub username: String,
}

/// Copy text to clipboard
#[tauri::command]
pub fn copy_to_clipboard(app_handle: tauri::AppHandle, text: String) -> Result<(), String> {
    app_handle
        .clipboard_manager()
        .write_text(text)
        .map_err(|e| format!("Failed to copy to clipboard: {}", e))
}

/// Get system information
#[tauri::command]
pub fn get_system_info() -> SystemInfo {
    SystemInfo {
        os_name: std::env::consts::OS.to_string(),
        os_version: "Windows".to_string(), // Would need more detailed implementation
        hostname: hostname::get()
            .map(|h| h.to_string_lossy().to_string())
            .unwrap_or_else(|_| "Unknown".to_string()),
        username: whoami::username(),
    }
}
