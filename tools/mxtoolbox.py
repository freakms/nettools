"""
MXToolbox API Integration
DNS lookup and domain diagnostics
"""

import requests
import json
import os


def get_api_key():
    """
    Get MXToolbox API key from config file or environment variable.
    """
    # Check environment variable first
    env_key = os.environ.get('MXTOOLBOX_API_KEY')
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
                    key = config.get('mxtoolbox_api_key')
                    if key:
                        return key
        except (json.JSONDecodeError, IOError):
            continue
    
    # Fallback to hardcoded key
    return "211424db-fd37-4862-b402-8fd5ba5cfb7f"


# Load API key on module import
MXTOOLBOX_API_KEY = get_api_key()


class MXToolbox:
    """MXToolbox API for DNS lookups and domain diagnostics"""
    
    API_BASE = "https://mxtoolbox.com/api/v1/Lookup"
    
    # Available lookup types
    LOOKUP_TYPES = {
        'dns': 'dns',           # Full DNS check
        'mx': 'mx',             # MX records
        'a': 'a',               # A records
        'aaaa': 'aaaa',         # AAAA records (IPv6)
        'ns': 'ns',             # Name servers
        'soa': 'soa',           # SOA record
        'txt': 'txt',           # TXT records
        'cname': 'cname',       # CNAME records
        'ptr': 'ptr',           # PTR (reverse DNS)
        'spf': 'spf',           # SPF record check
        'dmarc': 'dmarc',       # DMARC record check
    }
    
    @staticmethod
    def lookup(domain, lookup_type='dns'):
        """
        Perform MXToolbox lookup for a domain
        
        Args:
            domain (str): Domain name to lookup (e.g., example.com)
            lookup_type (str): Type of lookup (dns, mx, a, ns, txt, etc.)
            
        Returns:
            dict: MXToolbox results
        """
        try:
            # Validate lookup type
            if lookup_type not in MXToolbox.LOOKUP_TYPES:
                lookup_type = 'dns'
            
            headers = {
                'Authorization': MXTOOLBOX_API_KEY,
                'Accept': 'application/json',
                'User-Agent': 'NetTools/1.0'
            }
            
            # Build URL: /api/v1/Lookup/{type}/{domain}
            url = f"{MXToolbox.API_BASE}/{lookup_type}/{domain}"
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 401:
                return {
                    "success": False,
                    "error": "Invalid API key. Please check your MXToolbox API key.",
                    "domain": domain
                }
            
            if response.status_code == 403:
                return {
                    "success": False,
                    "error": "API access forbidden. You may have exceeded your daily limit (63 queries).",
                    "domain": domain
                }
            
            if response.status_code == 404:
                return {
                    "success": False,
                    "error": f"Lookup type '{lookup_type}' not found or domain invalid.",
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
                    "error": f"API returned HTTP {response.status_code}: {response.text[:200]}",
                    "domain": domain
                }
            
            # Parse JSON response
            data = response.json()
            
            # Transform API response to our format
            results = MXToolbox._parse_response(data, domain, lookup_type)
            results["success"] = True
            results["domain"] = domain
            results["lookup_type"] = lookup_type
            
            return results
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timed out. MXToolbox API might be slow.",
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
    def full_dns_check(domain):
        """
        Perform comprehensive DNS check (uses 'dns' lookup type)
        This is the main method for full domain reconnaissance.
        """
        return MXToolbox.lookup(domain, 'dns')
    
    @staticmethod
    def _parse_response(data, domain, lookup_type):
        """Parse MXToolbox API response"""
        results = {
            "dns_records": {
                "a": [],
                "aaaa": [],
                "mx": [],
                "ns": [],
                "txt": [],
                "soa": [],
                "cname": []
            },
            "information": [],
            "passed": [],
            "warnings": [],
            "errors": [],
            "statistics": {},
            "raw_data": data  # Keep raw data for debugging
        }
        
        try:
            # Parse Information section (contains DNS records)
            info_list = data.get("Information", [])
            for info in info_list:
                if isinstance(info, dict):
                    info_text = info.get("Info", "") or info.get("Information", "")
                    info_type = info.get("Type", "").lower()
                    
                    # Parse the info text to extract records
                    record = MXToolbox._parse_info_record(info, info_type, domain)
                    if record:
                        results["information"].append(record)
                        
                        # Categorize by record type
                        if info_type in results["dns_records"]:
                            results["dns_records"][info_type].append(record)
                        elif 'mx' in info_type.lower():
                            results["dns_records"]["mx"].append(record)
                        elif 'ns' in info_type.lower() or 'nameserver' in info_type.lower():
                            results["dns_records"]["ns"].append(record)
                        elif 'txt' in info_type.lower() or 'spf' in info_type.lower():
                            results["dns_records"]["txt"].append(record)
                        elif 'a record' in info_text.lower() or info_type == 'a':
                            results["dns_records"]["a"].append(record)
            
            # Parse Passed checks
            passed_list = data.get("Passed", [])
            for item in passed_list:
                if isinstance(item, dict):
                    results["passed"].append({
                        "info": item.get("Info", ""),
                        "name": item.get("Name", ""),
                        "additional": item.get("AdditionalInfo", "")
                    })
            
            # Parse Warnings
            warning_list = data.get("Warnings", [])
            for item in warning_list:
                if isinstance(item, dict):
                    results["warnings"].append({
                        "info": item.get("Info", ""),
                        "name": item.get("Name", ""),
                        "additional": item.get("AdditionalInfo", "")
                    })
            
            # Parse Failed/Errors
            failed_list = data.get("Failed", [])
            for item in failed_list:
                if isinstance(item, dict):
                    results["errors"].append({
                        "info": item.get("Info", ""),
                        "name": item.get("Name", ""),
                        "additional": item.get("AdditionalInfo", "")
                    })
            
            # Get command/query info
            results["command"] = data.get("Command", "")
            results["command_argument"] = data.get("CommandArgument", domain)
            results["is_transitioned"] = data.get("IsTransitioned", False)
            results["dns_service_provider"] = data.get("DnsServiceProvider", "")
            results["mx_rep"] = data.get("MxRep", 0)
            results["email_service_provider"] = data.get("EmailServiceProvider", "")
            results["related_lookups"] = data.get("RelatedLookups", [])
            
            # Calculate statistics
            results["statistics"] = {
                "total_records": len(results["information"]),
                "passed_checks": len(results["passed"]),
                "warnings": len(results["warnings"]),
                "errors": len(results["errors"]),
                "a_records": len(results["dns_records"]["a"]),
                "mx_records": len(results["dns_records"]["mx"]),
                "ns_records": len(results["dns_records"]["ns"]),
                "txt_records": len(results["dns_records"]["txt"])
            }
            
        except Exception as e:
            results["parse_error"] = str(e)
        
        return results
    
    @staticmethod
    def _parse_info_record(info, info_type, domain):
        """Parse individual info record from MXToolbox response"""
        record = {
            "type": info_type.upper() if info_type else "INFO",
            "info": info.get("Info", "") or info.get("Information", ""),
            "domain": info.get("Domain", domain),
            "ip_address": info.get("IPAddress", ""),
            "name": info.get("Name", ""),
            "additional_info": info.get("AdditionalInfo", ""),
            "ttl": info.get("TTL", ""),
            "status": info.get("Status", ""),
            "priority": info.get("Priority", ""),
        }
        
        # Clean up empty values
        record = {k: v for k, v in record.items() if v}
        
        return record if record.get("info") or record.get("ip_address") else None
    
    @staticmethod
    def is_available():
        """Check if MXToolbox API is accessible"""
        try:
            headers = {
                'Authorization': MXTOOLBOX_API_KEY,
                'Accept': 'application/json'
            }
            # Test with example.com (free lookup)
            response = requests.get(
                f"{MXToolbox.API_BASE}/dns/example.com",
                headers=headers,
                timeout=5
            )
            return response.status_code in [200, 401, 403]
        except Exception:
            return False
