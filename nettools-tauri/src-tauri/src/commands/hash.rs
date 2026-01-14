// Hash Generator command
use serde::{Deserialize, Serialize};
use sha2::{Sha256, Sha512, Digest};
use sha1::Sha1;
use md5::Md5;
use std::fs::File;
use std::io::Read;

#[derive(Debug, Serialize, Deserialize)]
pub struct HashResult {
    pub input: String,
    pub input_type: String, // "text" or "file"
    pub md5: String,
    pub sha1: String,
    pub sha256: String,
    pub sha512: String,
}

/// Generate hash values for text input
#[tauri::command]
pub fn generate_hashes(text: String) -> HashResult {
    let bytes = text.as_bytes();
    
    HashResult {
        input: if text.len() > 100 { 
            format!("{}...", &text[..100]) 
        } else { 
            text 
        },
        input_type: "text".to_string(),
        md5: format!("{:x}", Md5::digest(bytes)),
        sha1: format!("{:x}", Sha1::digest(bytes)),
        sha256: format!("{:x}", Sha256::digest(bytes)),
        sha512: format!("{:x}", Sha512::digest(bytes)),
    }
}

/// Generate hash values for a file
#[tauri::command]
pub fn hash_file(path: String) -> Result<HashResult, String> {
    let mut file = File::open(&path)
        .map_err(|e| format!("Failed to open file: {}", e))?;
    
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)
        .map_err(|e| format!("Failed to read file: {}", e))?;
    
    Ok(HashResult {
        input: path,
        input_type: "file".to_string(),
        md5: format!("{:x}", Md5::digest(&buffer)),
        sha1: format!("{:x}", Sha1::digest(&buffer)),
        sha256: format!("{:x}", Sha256::digest(&buffer)),
        sha512: format!("{:x}", Sha512::digest(&buffer)),
    })
}
