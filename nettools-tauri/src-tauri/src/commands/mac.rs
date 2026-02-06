// MAC Address Formatter command
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::Duration;

#[derive(Debug, Serialize, Deserialize)]
pub struct MacFormats {
    pub colon_upper: String,    // AA:BB:CC:DD:EE:FF
    pub colon_lower: String,    // aa:bb:cc:dd:ee:ff
    pub hyphen_upper: String,   // AA-BB-CC-DD-EE-FF
    pub hyphen_lower: String,   // aa-bb-cc-dd-ee-ff
    pub dot_upper: String,      // AABB.CCDD.EEFF
    pub dot_lower: String,      // aabb.ccdd.eeff
    pub no_separator: String,   // AABBCCDDEEFF
    pub cisco: String,          // aabb.ccdd.eeff
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MacResult {
    pub original: String,
    pub formats: MacFormats,
    pub vendor: Option<String>,
    pub is_valid: bool,
}

// Common OUI (Organizationally Unique Identifier) database
fn get_oui_database() -> HashMap<&'static str, &'static str> {
    let mut db = HashMap::new();
    // Common vendors
    db.insert("00:00:0C", "Cisco Systems");
    db.insert("00:01:42", "Cisco Systems");
    db.insert("00:1A:A0", "Dell Inc.");
    db.insert("00:14:22", "Dell Inc.");
    db.insert("00:50:56", "VMware");
    db.insert("00:0C:29", "VMware");
    db.insert("00:15:5D", "Microsoft Hyper-V");
    db.insert("00:03:FF", "Microsoft");
    db.insert("00:0D:3A", "Microsoft Azure");
    db.insert("00:1C:42", "Parallels");
    db.insert("08:00:27", "Oracle VirtualBox");
    db.insert("52:54:00", "QEMU/KVM");
    db.insert("00:16:3E", "Xen");
    db.insert("00:1A:4A", "Qumranet (KVM)");
    db.insert("AC:DE:48", "Private (LAA)");
    db.insert("00:25:90", "Super Micro Computer");
    db.insert("00:30:48", "Supermicro");
    db.insert("D4:BE:D9", "Dell Inc.");
    db.insert("B8:AC:6F", "Dell Inc.");
    db.insert("34:17:EB", "Dell Inc.");
    db.insert("00:1E:67", "Intel Corporate");
    db.insert("00:1F:3C", "Intel Corporate");
    db.insert("00:22:FA", "Intel Corporate");
    db.insert("3C:FD:FE", "Intel Corporate");
    db.insert("A4:BF:01", "Intel Corporate");
    db.insert("00:24:D7", "Intel Corporate");
    db.insert("00:1B:21", "Intel Corporate");
    db.insert("00:13:20", "Intel Corporate");
    db.insert("00:02:B3", "Intel Corporate");
    db.insert("00:AA:00", "Intel Corporate");
    db.insert("00:25:00", "Apple, Inc.");
    db.insert("00:1E:C2", "Apple, Inc.");
    db.insert("00:23:6C", "Apple, Inc.");
    db.insert("00:25:BC", "Apple, Inc.");
    db.insert("28:CF:DA", "Apple, Inc.");
    db.insert("3C:15:C2", "Apple, Inc.");
    db.insert("70:CD:60", "Apple, Inc.");
    db.insert("98:01:A7", "Apple, Inc.");
    db.insert("AC:BC:32", "Apple, Inc.");
    db.insert("00:17:F2", "Apple, Inc.");
    db.insert("00:1F:F3", "Apple, Inc.");
    db.insert("58:55:CA", "Apple, Inc.");
    db.insert("60:03:08", "Apple, Inc.");
    db.insert("78:CA:39", "Apple, Inc.");
    db.insert("00:26:B0", "Apple, Inc.");
    db.insert("00:26:BB", "Apple, Inc.");
    db.insert("F0:B4:79", "HP Inc.");
    db.insert("00:1E:0B", "HP Inc.");
    db.insert("00:21:5A", "HP Inc.");
    db.insert("00:25:B3", "HP Inc.");
    db.insert("2C:27:D7", "HP Inc.");
    db.insert("38:63:BB", "HP Inc.");
    db.insert("00:30:6E", "HP Inc.");
    db.insert("00:17:A4", "HP Inc.");
    db.insert("00:14:38", "HP Inc.");
    db.insert("00:0B:CD", "HP Inc.");
    db.insert("08:00:09", "HP Inc.");
    db.insert("EC:B1:D7", "HP Inc.");
    db.insert("00:1A:6B", "Universal Global Scientific Industrial");
    db.insert("00:E0:4C", "Realtek Semiconductor");
    db.insert("52:54:AB", "Realtek (QEMU)");
    db.insert("00:0A:CD", "Sunrich Technology");
    db.insert("00:1D:7D", "Giga-Byte Technology");
    db.insert("50:E5:49", "GIGA-BYTE Technology");
    db.insert("1C:83:41", "GIGA-BYTE Technology");
    db.insert("00:1E:8C", "ASUSTek Computer");
    db.insert("00:1A:92", "ASUSTek Computer");
    db.insert("00:15:F2", "ASUSTek Computer");
    db.insert("00:13:D4", "ASUSTek Computer");
    db.insert("00:0E:A6", "ASUSTek Computer");
    db.insert("BC:EE:7B", "ASUSTek Computer");
    db.insert("00:22:15", "ASUSTek Computer");
    db.insert("00:24:8C", "ASUSTek Computer");
    db.insert("20:CF:30", "ASUSTek Computer");
    db.insert("30:85:A9", "ASUSTek Computer");
    db.insert("54:04:A6", "ASUSTek Computer");
    db.insert("60:45:BD", "Microsoft");
    db.insert("7C:1E:52", "Microsoft");
    db.insert("28:18:78", "Microsoft");
    db.insert("00:1D:D8", "Microsoft");
    db.insert("B4:0E:DE", "Samsung Electronics");
    db.insert("00:12:47", "Samsung Electronics");
    db.insert("00:15:99", "Samsung Electronics");
    db.insert("00:16:32", "Samsung Electronics");
    db.insert("00:17:D5", "Samsung Electronics");
    db.insert("00:1A:8A", "Samsung Electronics");
    db.insert("00:21:19", "Samsung Electronics");
    db.insert("00:23:39", "Samsung Electronics");
    db.insert("00:24:54", "Samsung Electronics");
    db.insert("00:25:66", "Samsung Electronics");
    db.insert("00:26:37", "Samsung Electronics");
    db.insert("5C:0A:5B", "Samsung Electronics");
    db.insert("84:25:DB", "Samsung Electronics");
    db.insert("90:18:7C", "Samsung Electronics");
    db.insert("A8:F2:74", "Samsung Electronics");
    db.insert("BC:44:86", "Samsung Electronics");
    db.insert("C4:73:1E", "Samsung Electronics");
    db.insert("E4:7C:F9", "Samsung Electronics");
    db.insert("F8:D0:BD", "Samsung Electronics");
    db.insert("CC:07:AB", "Samsung Electronics");
    db
}

/// Parse a MAC address from various formats and return normalized bytes
fn parse_mac(mac: &str) -> Option<[u8; 6]> {
    // Remove common separators and whitespace
    let clean: String = mac
        .chars()
        .filter(|c| c.is_ascii_hexdigit())
        .collect();
    
    if clean.len() != 12 {
        return None;
    }
    
    let mut bytes = [0u8; 6];
    for i in 0..6 {
        bytes[i] = u8::from_str_radix(&clean[i*2..i*2+2], 16).ok()?;
    }
    
    Some(bytes)
}

/// Lookup vendor from OUI
fn lookup_vendor(bytes: &[u8; 6]) -> Option<String> {
    let oui = format!("{:02X}:{:02X}:{:02X}", bytes[0], bytes[1], bytes[2]);
    let db = get_oui_database();
    db.get(oui.as_str()).map(|s| s.to_string())
}

/// Format MAC address
#[tauri::command]
pub fn format_mac(mac: String) -> MacResult {
    let bytes = match parse_mac(&mac) {
        Some(b) => b,
        None => {
            return MacResult {
                original: mac,
                formats: MacFormats {
                    colon_upper: String::new(),
                    colon_lower: String::new(),
                    hyphen_upper: String::new(),
                    hyphen_lower: String::new(),
                    dot_upper: String::new(),
                    dot_lower: String::new(),
                    no_separator: String::new(),
                    cisco: String::new(),
                },
                vendor: None,
                is_valid: false,
            };
        }
    };
    
    let colon_upper = format!(
        "{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}",
        bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5]
    );
    
    let colon_lower = format!(
        "{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}",
        bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5]
    );
    
    let hyphen_upper = format!(
        "{:02X}-{:02X}-{:02X}-{:02X}-{:02X}-{:02X}",
        bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5]
    );
    
    let hyphen_lower = format!(
        "{:02x}-{:02x}-{:02x}-{:02x}-{:02x}-{:02x}",
        bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5]
    );
    
    let dot_upper = format!(
        "{:02X}{:02X}.{:02X}{:02X}.{:02X}{:02X}",
        bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5]
    );
    
    let dot_lower = format!(
        "{:02x}{:02x}.{:02x}{:02x}.{:02x}{:02x}",
        bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5]
    );
    
    let no_separator = format!(
        "{:02X}{:02X}{:02X}{:02X}{:02X}{:02X}",
        bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5]
    );
    
    let vendor = lookup_vendor(&bytes);
    
    MacResult {
        original: mac,
        formats: MacFormats {
            colon_upper,
            colon_lower: colon_lower.clone(),
            hyphen_upper,
            hyphen_lower,
            dot_upper,
            dot_lower: dot_lower.clone(),
            no_separator,
            cisco: dot_lower,
        },
        vendor,
        is_valid: true,
    }
}

/// Lookup MAC vendor from macvendors.com API (using reqwest with HTTPS)
#[tauri::command]
pub async fn lookup_mac_vendor(mac: String) -> Result<String, String> {
    let bytes = parse_mac(&mac).ok_or("Invalid MAC address")?;
    
    // First try local database
    if let Some(vendor) = lookup_vendor(&bytes) {
        return Ok(vendor);
    }
    
    let oui = format!("{:02X}:{:02X}:{:02X}", bytes[0], bytes[1], bytes[2]);
    let url = format!("https://api.macvendors.com/{}", oui);
    
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(10))
        .build()
        .map_err(|e| format!("HTTP-Client Fehler: {}", e))?;
    
    let response = client
        .get(&url)
        .header("User-Agent", "NetTools/1.0")
        .send()
        .await
        .map_err(|e| format!("API-Anfrage fehlgeschlagen: {}", e))?;
    
    match response.status().as_u16() {
        200 => {
            let body = response.text().await
                .map_err(|e| format!("Antwort lesen fehlgeschlagen: {}", e))?;
            let body = body.trim().to_string();
            if body.is_empty() || body.contains("Not Found") {
                Ok("Unbekannter Hersteller".to_string())
            } else {
                Ok(body)
            }
        }
        404 => Ok("Unbekannter Hersteller".to_string()),
        429 => Err("Rate Limit erreicht. Bitte später erneut versuchen.".to_string()),
        status => Err(format!("API-Fehler: HTTP {}", status)),
    }
}
