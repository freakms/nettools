// Hash Generator command
use serde::{Deserialize, Serialize};
use sha2::{Sha256, Sha512, Digest};
use sha1::Sha1;
use std::fs::File;
use std::io::Read;

#[derive(Debug, Serialize, Deserialize)]
pub struct HashResult {
    pub input: String,
    pub input_type: String,
    pub md5: String,
    pub sha1: String,
    pub sha256: String,
    pub sha512: String,
}

/// Generate hash values for text input
#[tauri::command]
pub fn generate_hashes(text: String) -> HashResult {
    let bytes = text.as_bytes();
    
    // MD5 using md5 crate
    let md5_hash = format!("{:x}", md5::compute(bytes));
    
    // SHA1
    let mut sha1_hasher = Sha1::new();
    sha1_hasher.update(bytes);
    let sha1_hash = format!("{:x}", sha1_hasher.finalize());
    
    // SHA256
    let mut sha256_hasher = Sha256::new();
    sha256_hasher.update(bytes);
    let sha256_hash = format!("{:x}", sha256_hasher.finalize());
    
    // SHA512
    let mut sha512_hasher = Sha512::new();
    sha512_hasher.update(bytes);
    let sha512_hash = format!("{:x}", sha512_hasher.finalize());
    
    HashResult {
        input: if text.len() > 100 { 
            format!("{}...", &text[..100]) 
        } else { 
            text 
        },
        input_type: "text".to_string(),
        md5: md5_hash,
        sha1: sha1_hash,
        sha256: sha256_hash,
        sha512: sha512_hash,
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
    
    let md5_hash = format!("{:x}", md5::compute(&buffer));
    
    let mut sha1_hasher = Sha1::new();
    sha1_hasher.update(&buffer);
    let sha1_hash = format!("{:x}", sha1_hasher.finalize());
    
    let mut sha256_hasher = Sha256::new();
    sha256_hasher.update(&buffer);
    let sha256_hash = format!("{:x}", sha256_hasher.finalize());
    
    let mut sha512_hasher = Sha512::new();
    sha512_hasher.update(&buffer);
    let sha512_hash = format!("{:x}", sha512_hasher.finalize());
    
    Ok(HashResult {
        input: path,
        input_type: "file".to_string(),
        md5: md5_hash,
        sha1: sha1_hash,
        sha256: sha256_hash,
        sha512: sha512_hash,
    })
}
