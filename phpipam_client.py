"""
phpIPAM API Client
Handles communication with phpIPAM REST API
"""

import requests
from typing import Optional, Dict, List, Any
from requests.auth import HTTPBasicAuth
from phpipam_config import PHPIPAMConfig
from datetime import datetime
import urllib3

# Disable SSL warnings for self-signed certificates (only when ssl_verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PHPIPAMClient:
    """Client for interacting with phpIPAM REST API"""
    
    def __init__(self, config: PHPIPAMConfig = None):
        """Initialize phpIPAM client"""
        self.config = config or PHPIPAMConfig()
        self.session = requests.Session()
        self.base_url = self.config.get_phpipam_url()
        self.app_id = self.config.get_app_id()
        self.token: Optional[str] = None
        self.token_expiration: Optional[str] = None
        
        # Load cached token if available
        cached_token, cached_exp = self.config.get_cached_token()
        if cached_token:
            self.token = cached_token
            self.token_expiration = cached_exp
    
    def test_connection(self) -> tuple[bool, str]:
        """Test connection to phpIPAM instance"""
        if not self.config.is_enabled():
            return False, "phpIPAM integration is disabled"
        
        if not self.base_url or not self.app_id:
            return False, "phpIPAM URL or App ID not configured"
        
        try:
            # Try to ping the API
            url = f"{self.base_url}/api/{self.app_id}/user/"
            response = self.session.get(
                url,
                verify=self.config.get_ssl_verify(),
                timeout=5
            )
            
            if response.status_code in [200, 401]:  # 401 means API is reachable
                return True, "Connection successful"
            else:
                return False, f"Unexpected response: {response.status_code}"
        
        except requests.exceptions.SSLError:
            return False, "SSL verification failed. Check certificate or disable SSL verify."
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to phpIPAM server. Check URL."
        except requests.exceptions.Timeout:
            return False, "Connection timeout. Server not responding."
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def authenticate(self) -> tuple[bool, str]:
        """Authenticate with phpIPAM and obtain API token"""
        if not self.config.is_enabled():
            return False, "phpIPAM integration is disabled"
        
        auth_method = self.config.get_auth_method()
        
        try:
            if auth_method == "static":
                # Static token authentication
                token = self.config.get_static_token()
                if not token:
                    return False, "Static token not configured"
                
                self.token = token
                self.token_expiration = "Never (Static Token)"
                return True, "Authenticated with static token"
            
            else:
                # Dynamic authentication
                username = self.config.get_username()
                password = self.config.get_password()
                
                if not username or not password:
                    return False, "Username or password not configured"
                
                auth_url = f"{self.base_url}/api/{self.app_id}/user/"
                
                response = self.session.post(
                    auth_url,
                    auth=HTTPBasicAuth(username, password),
                    headers={"Content-Type": "application/json"},
                    verify=self.config.get_ssl_verify(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.token = data["data"]["token"]
                        self.token_expiration = data["data"]["expires"]
                        
                        # Cache token
                        self.config.set_cached_token(self.token, self.token_expiration)
                        
                        return True, f"Authenticated. Token expires: {self.token_expiration}"
                    else:
                        return False, data.get("message", "Authentication failed")
                else:
                    return False, f"Authentication failed: HTTP {response.status_code}"
        
        except Exception as e:
            return False, f"Authentication error: {str(e)}"
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        retry_auth: bool = True
    ) -> tuple[bool, Any]:
        """Make authenticated API request"""
        
        if not self.config.is_enabled():
            return False, "phpIPAM integration is disabled"
        
        # Ensure we have a token
        if not self.token:
            success, msg = self.authenticate()
            if not success:
                return False, msg
        
        url = f"{self.base_url}/api/{self.app_id}/{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "phpipam-token": self.token
        }
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=headers,
                verify=self.config.get_ssl_verify(),
                timeout=10
            )
            
            # Handle token expiration
            if response.status_code == 401 and retry_auth:
                # Token expired, try re-authenticating
                self.config.clear_cached_token()
                success, msg = self.authenticate()
                if success:
                    # Retry request with new token
                    return self._make_request(method, endpoint, params, json_data, retry_auth=False)
                else:
                    return False, f"Re-authentication failed: {msg}"
            
            # Parse response
            if response.status_code in [200, 201]:
                data = response.json()
                if data.get("success") or response.status_code in [200, 201]:
                    return True, data.get("data", {})
                else:
                    return False, data.get("message", "Unknown error")
            else:
                return False, f"HTTP {response.status_code}: {response.text[:100]}"
        
        except Exception as e:
            return False, f"Request error: {str(e)}"
    
    def search_ip(self, ip_address: str) -> tuple[bool, Any]:
        """Search for IP address in database"""
        endpoint = f"addresses/search/{ip_address}/"
        success, data = self._make_request("GET", endpoint)
        
        if success:
            # Ensure data is a list
            if isinstance(data, dict):
                data = [data] if data else []
            elif not isinstance(data, list):
                data = []
        else:
            data = []
        
        return success, data
    
    def get_all_subnets(self) -> tuple[bool, Any]:
        """Get all subnets"""
        endpoint = "subnets/"
        success, data = self._make_request("GET", endpoint)
        
        if success:
            if isinstance(data, dict):
                data = [data] if data else []
            elif not isinstance(data, list):
                data = []
        else:
            data = []
        
        return success, data
    
    def get_subnet_details(self, subnet_id: int) -> tuple[bool, Any]:
        """Get detailed information about a subnet"""
        endpoint = f"subnets/{subnet_id}/"
        return self._make_request("GET", endpoint)
    
    def get_subnet_addresses(self, subnet_id: int) -> tuple[bool, Any]:
        """Get all IP addresses in a subnet"""
        endpoint = f"subnets/{subnet_id}/addresses/"
        success, data = self._make_request("GET", endpoint)
        
        if success:
            if isinstance(data, dict):
                data = [data] if data else []
            elif not isinstance(data, list):
                data = []
        else:
            data = []
        
        return success, data
    
    def find_first_free_ip(self, subnet_id: int) -> tuple[bool, Any]:
        """Find first available IP in subnet"""
        endpoint = f"addresses/first_free/{subnet_id}/"
        success, data = self._make_request("GET", endpoint)
        
        if success and isinstance(data, dict):
            return True, data.get("data", "")
        else:
            return False, data
    
    def add_ip_address(
        self,
        subnet_id: int,
        ip_address: str,
        hostname: str = "",
        description: str = "",
        mac: str = "",
        owner: str = ""
    ) -> tuple[bool, str]:
        """Add new IP address to subnet"""
        endpoint = "addresses/"
        payload = {
            "subnetId": subnet_id,
            "ip": ip_address
        }
        
        if hostname:
            payload["hostname"] = hostname
        if description:
            payload["description"] = description
        if mac:
            payload["mac"] = mac
        if owner:
            payload["owner"] = owner
        
        success, data = self._make_request("POST", endpoint, json_data=payload)
        
        if success:
            return True, "IP address added successfully"
        else:
            return False, str(data)
    
    def update_ip_address(
        self,
        address_id: int,
        hostname: str = None,
        description: str = None,
        mac: str = None,
        owner: str = None
    ) -> tuple[bool, str]:
        """Update existing IP address"""
        endpoint = f"addresses/{address_id}/"
        payload = {}
        
        if hostname is not None:
            payload["hostname"] = hostname
        if description is not None:
            payload["description"] = description
        if mac is not None:
            payload["mac"] = mac
        if owner is not None:
            payload["owner"] = owner
        
        success, data = self._make_request("PATCH", endpoint, json_data=payload)
        
        if success:
            return True, "IP address updated successfully"
        else:
            return False, str(data)
    
    def delete_ip_address(self, address_id: int) -> tuple[bool, str]:
        """Delete IP address"""
        endpoint = f"addresses/{address_id}/"
        success, data = self._make_request("DELETE", endpoint)
        
        if success:
            return True, "IP address deleted successfully"
        else:
            return False, str(data)
