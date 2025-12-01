"""
phpIPAM Configuration Management
Handles settings and secure credential storage for phpIPAM integration
"""

import json
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
import base64


class PHPIPAMConfig:
    """Manage phpIPAM configuration with secure credential storage"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".nettools"
        self.config_file = self.config_dir / "phpipam_config.json"
        self.key_file = self.config_dir / "phpipam.key"
        self.config = self.load_config()
    
    def ensure_encryption_key(self):
        """Ensure encryption key exists"""
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)
        
        if not self.key_file.exists():
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key
        else:
            with open(self.key_file, 'rb') as f:
                return f.read()
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt a sensitive value"""
        if not value:
            return ""
        key = self.ensure_encryption_key()
        cipher = Fernet(key)
        encrypted = cipher.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a sensitive value"""
        if not encrypted_value:
            return ""
        try:
            key = self.ensure_encryption_key()
            cipher = Fernet(key)
            encrypted_bytes = base64.b64decode(encrypted_value.encode())
            decrypted = cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return ""
    
    def load_config(self) -> dict:
        """Load configuration from file"""
        if not self.config_file.exists():
            return self.get_default_config()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return self.get_default_config()
    
    def get_default_config(self) -> dict:
        """Get default configuration"""
        return {
            "enabled": False,
            "phpipam_url": "",
            "app_id": "",
            "auth_method": "dynamic",  # "dynamic" or "static"
            "username": "",
            "password": "",  # Encrypted
            "static_token": "",  # Encrypted
            "ssl_verify": True,
            "cached_token": "",
            "token_expiration": ""
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            if not self.config_dir.exists():
                self.config_dir.mkdir(parents=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def is_enabled(self) -> bool:
        """Check if phpIPAM integration is enabled"""
        return self.config.get("enabled", False)
    
    def get_phpipam_url(self) -> str:
        """Get phpIPAM base URL"""
        return self.config.get("phpipam_url", "")
    
    def get_app_id(self) -> str:
        """Get phpIPAM application ID"""
        return self.config.get("app_id", "")
    
    def get_auth_method(self) -> str:
        """Get authentication method"""
        return self.config.get("auth_method", "dynamic")
    
    def get_username(self) -> str:
        """Get username for dynamic auth"""
        return self.config.get("username", "")
    
    def get_password(self) -> str:
        """Get decrypted password"""
        encrypted = self.config.get("password", "")
        return self.decrypt_value(encrypted) if encrypted else ""
    
    def get_static_token(self) -> str:
        """Get decrypted static token"""
        encrypted = self.config.get("static_token", "")
        return self.decrypt_value(encrypted) if encrypted else ""
    
    def get_ssl_verify(self) -> bool:
        """Get SSL verification setting"""
        return self.config.get("ssl_verify", True)
    
    def update_config(
        self,
        enabled: bool,
        phpipam_url: str,
        app_id: str,
        auth_method: str,
        username: str = "",
        password: str = "",
        static_token: str = "",
        ssl_verify: bool = True
    ):
        """Update configuration with new values"""
        self.config["enabled"] = enabled
        self.config["phpipam_url"] = phpipam_url.rstrip("/")
        self.config["app_id"] = app_id
        self.config["auth_method"] = auth_method
        self.config["username"] = username
        self.config["ssl_verify"] = ssl_verify
        
        # Encrypt sensitive data
        if password:
            self.config["password"] = self.encrypt_value(password)
        if static_token:
            self.config["static_token"] = self.encrypt_value(static_token)
        
        return self.save_config()
    
    def clear_cached_token(self):
        """Clear cached authentication token"""
        self.config["cached_token"] = ""
        self.config["token_expiration"] = ""
        self.save_config()
    
    def set_cached_token(self, token: str, expiration: str):
        """Cache authentication token"""
        self.config["cached_token"] = token
        self.config["token_expiration"] = expiration
        self.save_config()
    
    def get_cached_token(self) -> tuple:
        """Get cached token and expiration"""
        return (
            self.config.get("cached_token", ""),
            self.config.get("token_expiration", "")
        )
