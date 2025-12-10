"""
DNSDumpster API Integration
Domain reconnaissance and subdomain enumeration
Uses official DNSDumpster API
"""

import requests
import json
import os


def get_api_key():
    """
    Get DNSDumpster API key from config file or environment variable.
    Priority: Environment variable > Config file > Hardcoded default
    """
    # Check environment variable first
    env_key = os.environ.get('DNSDUMPSTER_API_KEY')
    if env_key:
        return env_key
    
    # Try to read from config file
    config_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'api_keys.json'),
        os.path.join(os.path.dirname(__file__), 'api_keys.json'),
        'api_keys.json'
    ]
    
    for config_path in config_paths:
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    key = config.get('dnsdumpster_api_key')
                    if key:
                        return key
        except (json.JSONDecodeError, IOError):
            continue
    
    # Fallback to hardcoded key
    return "b77d2fa35f30f2b4fea96ee709d9141e61f6d1002ee47f1d0209776546589116"


# Load API key on module import
DNSDUMPSTER_API_KEY = get_api_key()


class DNSDumpster:
    """DNSDumpster API for domain reconnaissance"""
    
    API_URL = "https://api.dnsdumpster.com/domain/"
    
    @staticmethod
    def lookup(domain):
        """
        Perform DNSDumpster lookup for a domain using official API
        
        Args:
            domain (str): Domain name to lookup (e.g., example.com)
            
        Returns:
            dict: DNSDumpster results including subdomains, DNS records, etc.
        """
        try:
            headers = {
                'X-API-Key': DNSDUMPSTER_API_KEY,
                'Accept': 'application/json',
                'User-Agent': 'NetTools/1.0'
            }
            
            url = f"{DNSDumpster.API_URL}{domain}"
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 401:
                return {
                    "success": False,
                    "error": "Invalid API key. Please check your DNSDumpster API key.",
                    "domain": domain
                }
            
            if response.status_code == 403:
                return {
                    "success": False,
                    "error": "API access forbidden. Your account may have reached its limit.",
                    "domain": domain
                }
            
            if response.status_code == 404:
                return {
                    "success": False,
                    "error": f"No data found for domain: {domain}",
                    "domain": domain
                }
            
            if response.status_code == 429:
                return {
                    "success": False,
                    "error": "Rate limit exceeded. Please wait before making more requests.",
                    "domain": domain
                }
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"API returned HTTP {response.status_code}",
                    "domain": domain
                }
            
            # Parse JSON response
            data = response.json()
            
            # Transform API response to our format
            results = DNSDumpster._parse_api_response(data, domain)
            results["success"] = True
            results["domain"] = domain
            
            return results
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timed out. DNSDumpster API might be slow.",
                "domain": domain
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "domain": domain
            }
        except ValueError as e:
            return {
                "success": False,
                "error": f"Invalid JSON response: {str(e)}",
                "domain": domain
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "domain": domain
            }
    
    @staticmethod
    def _parse_api_response(data, domain):
        """Parse DNSDumpster API JSON response"""
        results = {
            "dns_records": {
                "host": [],
                "mx": [],
                "txt": [],
                "ns": []
            },
            "subdomains": [],
            "statistics": {}
        }
        
        try:
            # Parse DNS records section
            dns = data.get("dns", {})
            
            # A Records (Host records)
            a_records = dns.get("a", [])
            if isinstance(a_records, list):
                for record in a_records:
                    if isinstance(record, dict):
                        host = record.get("host", "") or record.get("name", "")
                        ip = record.get("ip", "") or record.get("address", "")
                        provider = record.get("provider", "") or record.get("asn", {}).get("name", "Unknown")
                        
                        if host and ip:
                            results["dns_records"]["host"].append({
                                "host": host,
                                "ip": ip,
                                "provider": str(provider)
                            })
                            
                            # Add to subdomains if it's a subdomain
                            if host != domain and domain in host:
                                results["subdomains"].append(host)
            
            # MX Records
            mx_records = dns.get("mx", [])
            if isinstance(mx_records, list):
                for record in mx_records:
                    if isinstance(record, dict):
                        mx = record.get("host", "") or record.get("exchange", "")
                        ip = record.get("ip", "") or record.get("address", "")
                        provider = record.get("provider", "") or record.get("asn", {}).get("name", "Unknown")
                        priority = record.get("priority", "")
                        
                        if mx:
                            mx_entry = {
                                "mx": mx,
                                "ip": str(ip),
                                "provider": str(provider)
                            }
                            if priority:
                                mx_entry["priority"] = priority
                            results["dns_records"]["mx"].append(mx_entry)
            
            # NS Records
            ns_records = dns.get("ns", [])
            if isinstance(ns_records, list):
                for record in ns_records:
                    if isinstance(record, dict):
                        ns = record.get("host", "") or record.get("nameserver", "")
                        ip = record.get("ip", "") or record.get("address", "")
                        
                        if ns:
                            results["dns_records"]["ns"].append({
                                "ns": ns,
                                "ip": str(ip) if ip else "N/A"
                            })
            
            # TXT Records
            txt_records = dns.get("txt", [])
            if isinstance(txt_records, list):
                for record in txt_records:
                    if isinstance(record, str):
                        results["dns_records"]["txt"].append(record)
                    elif isinstance(record, dict):
                        txt = record.get("value", "") or record.get("txt", "")
                        if txt:
                            results["dns_records"]["txt"].append(txt)
            
            # Parse subdomains/hosts section (might be separate from DNS)
            hosts = data.get("hosts", []) or data.get("subdomains", [])
            if isinstance(hosts, list):
                for host_entry in hosts:
                    if isinstance(host_entry, dict):
                        hostname = host_entry.get("host", "") or host_entry.get("name", "")
                        ip = host_entry.get("ip", "") or host_entry.get("address", "")
                        provider = host_entry.get("provider", "") or host_entry.get("asn", {}).get("name", "Unknown")
                        
                        if hostname:
                            # Add to host records if not already there
                            existing_hosts = [h["host"] for h in results["dns_records"]["host"]]
                            if hostname not in existing_hosts and ip:
                                results["dns_records"]["host"].append({
                                    "host": hostname,
                                    "ip": ip,
                                    "provider": str(provider)
                                })
                            
                            # Add to subdomains
                            if hostname != domain and domain in hostname:
                                if hostname not in results["subdomains"]:
                                    results["subdomains"].append(hostname)
                    elif isinstance(host_entry, str):
                        if host_entry != domain and domain in host_entry:
                            if host_entry not in results["subdomains"]:
                                results["subdomains"].append(host_entry)
            
            # Statistics
            results["statistics"]["total_hosts"] = len(results["dns_records"]["host"])
            results["statistics"]["total_subdomains"] = len(results["subdomains"])
            results["statistics"]["mx_records"] = len(results["dns_records"]["mx"])
            results["statistics"]["ns_records"] = len(results["dns_records"]["ns"])
            results["statistics"]["txt_records"] = len(results["dns_records"]["txt"])
            
            # Sort subdomains
            results["subdomains"] = sorted(list(set(results["subdomains"])))
            
        except Exception as e:
            results["parse_error"] = str(e)
        
        return results
    
    @staticmethod
    def is_available():
        """Check if DNSDumpster API is accessible"""
        try:
            headers = {
                'X-API-Key': DNSDUMPSTER_API_KEY,
                'Accept': 'application/json'
            }
            response = requests.get(
                f"{DNSDumpster.API_URL}example.com",
                headers=headers,
                timeout=5
            )
            # 200 or 401 means API is reachable
            return response.status_code in [200, 401, 403]
        except Exception:
            return False
