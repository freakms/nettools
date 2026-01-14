// Password Generator command
use serde::{Deserialize, Serialize};
use rand::Rng;
use rand::seq::SliceRandom;

#[derive(Debug, Serialize, Deserialize)]
pub struct PasswordOptions {
    pub length: usize,
    pub uppercase: bool,
    pub lowercase: bool,
    pub numbers: bool,
    pub symbols: bool,
    pub exclude_ambiguous: bool, // Exclude 0, O, l, 1, etc.
}

#[derive(Debug, Serialize, Deserialize)]
pub struct PasswordResult {
    pub password: String,
    pub strength: String,
    pub entropy_bits: f64,
}

const UPPERCASE: &str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const LOWERCASE: &str = "abcdefghijklmnopqrstuvwxyz";
const NUMBERS: &str = "0123456789";
const SYMBOLS: &str = "!@#$%^&*()_+-=[]{}|;:,.<>?";
const AMBIGUOUS: &str = "0O1lI";

/// Generate a secure password
#[tauri::command]
pub fn generate_password(options: PasswordOptions) -> Result<PasswordResult, String> {
    let mut charset = String::new();
    let mut required_chars = Vec::new();
    let mut rng = rand::thread_rng();
    
    if options.uppercase {
        let chars: String = if options.exclude_ambiguous {
            UPPERCASE.chars().filter(|c| !AMBIGUOUS.contains(*c)).collect()
        } else {
            UPPERCASE.to_string()
        };
        if let Some(c) = chars.chars().collect::<Vec<_>>().choose(&mut rng) {
            required_chars.push(*c);
        }
        charset.push_str(&chars);
    }
    
    if options.lowercase {
        let chars: String = if options.exclude_ambiguous {
            LOWERCASE.chars().filter(|c| !AMBIGUOUS.contains(*c)).collect()
        } else {
            LOWERCASE.to_string()
        };
        if let Some(c) = chars.chars().collect::<Vec<_>>().choose(&mut rng) {
            required_chars.push(*c);
        }
        charset.push_str(&chars);
    }
    
    if options.numbers {
        let chars: String = if options.exclude_ambiguous {
            NUMBERS.chars().filter(|c| !AMBIGUOUS.contains(*c)).collect()
        } else {
            NUMBERS.to_string()
        };
        if let Some(c) = chars.chars().collect::<Vec<_>>().choose(&mut rng) {
            required_chars.push(*c);
        }
        charset.push_str(&chars);
    }
    
    if options.symbols {
        if let Some(c) = SYMBOLS.chars().collect::<Vec<_>>().choose(&mut rng) {
            required_chars.push(*c);
        }
        charset.push_str(SYMBOLS);
    }
    
    if charset.is_empty() {
        return Err("At least one character type must be selected".to_string());
    }
    
    let charset_chars: Vec<char> = charset.chars().collect();
    let charset_len = charset_chars.len();
    
    // Generate password
    let remaining_length = options.length.saturating_sub(required_chars.len());
    let mut password: Vec<char> = required_chars;
    
    for _ in 0..remaining_length {
        let idx = rng.gen_range(0..charset_len);
        password.push(charset_chars[idx]);
    }
    
    // Shuffle the password
    password.shuffle(&mut rng);
    
    let password_str: String = password.iter().collect();
    
    // Calculate entropy
    let entropy_bits = (options.length as f64) * (charset_len as f64).log2();
    
    // Determine strength
    let strength = if entropy_bits < 28.0 {
        "Sehr schwach"
    } else if entropy_bits < 36.0 {
        "Schwach"
    } else if entropy_bits < 60.0 {
        "Mittel"
    } else if entropy_bits < 128.0 {
        "Stark"
    } else {
        "Sehr stark"
    };
    
    Ok(PasswordResult {
        password: password_str,
        strength: strength.to_string(),
        entropy_bits,
    })
}
