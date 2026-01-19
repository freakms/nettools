// API Tester / HTTP Request command
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Serialize, Deserialize)]
pub struct ApiResponse {
    pub status: u16,
    pub status_text: String,
    pub headers: HashMap<String, String>,
    pub body: String,
    pub duration_ms: u64,
}

/// Send an HTTP request
#[tauri::command]
pub async fn send_http_request(
    method: String,
    url: String,
    headers: HashMap<String, String>,
    body: Option<String>,
) -> Result<ApiResponse, String> {
    let start = std::time::Instant::now();
    
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(30))
        .danger_accept_invalid_certs(true)
        .build()
        .map_err(|e| format!("Failed to create client: {}", e))?;

    let mut request = match method.to_uppercase().as_str() {
        "GET" => client.get(&url),
        "POST" => client.post(&url),
        "PUT" => client.put(&url),
        "DELETE" => client.delete(&url),
        "PATCH" => client.patch(&url),
        "HEAD" => client.head(&url),
        _ => return Err(format!("Unsupported method: {}", method)),
    };

    // Add headers
    for (key, value) in &headers {
        request = request.header(key, value);
    }

    // Add body if present
    if let Some(body_content) = body {
        request = request.body(body_content);
    }

    let response = request
        .send()
        .await
        .map_err(|e| format!("Request failed: {}", e))?;

    let status = response.status().as_u16();
    let status_text = response.status().canonical_reason().unwrap_or("Unknown").to_string();

    // Collect response headers
    let mut resp_headers = HashMap::new();
    for (key, value) in response.headers() {
        if let Ok(v) = value.to_str() {
            resp_headers.insert(key.to_string(), v.to_string());
        }
    }

    let body = response
        .text()
        .await
        .map_err(|e| format!("Failed to read response body: {}", e))?;

    let duration_ms = start.elapsed().as_millis() as u64;

    Ok(ApiResponse {
        status,
        status_text,
        headers: resp_headers,
        body,
        duration_ms,
    })
}
