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
    
    @staticmethod
    def lookup(domain, lookup_type='dns'):
        """
        Perform single MXToolbox lookup
        
        Args:
            domain (str): Domain name to lookup
            lookup_type (str): Type of lookup (dns, mx, a, ns, txt, soa, etc.)
            
        Returns:
            dict: MXToolbox results
        """
        try:
            headers = {
                'Authorization': MXTOOLBOX_API_KEY,
                'Accept': 'application/json',
                'User-Agent': 'NetTools/1.0'
            }
            
            url = f"{MXToolbox.API_BASE}/{lookup_type}/{domain}"
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 401:
                return {"success": False, "error": "Invalid API key.", "domain": domain}
            if response.status_code == 403:
                return {"success": False, "error": "API limit exceeded (63/day).", "domain": domain}
            if response.status_code == 429:
                return {"success": False, "error": "Rate limit exceeded.", "domain": domain}
            if response.status_code != 200:
                return {"success": False, "error": f"HTTP {response.status_code}", "domain": domain}
            
            return {"success": True, "data": response.json(), "domain": domain}
            
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timed out.", "domain": domain}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Network error: {str(e)}", "domain": domain}
        except Exception as e:
            return {"success": False, "error": f"Error: {str(e)}", "domain": domain}
    
    @staticmethod
    def full_dns_check(domain):
        """
        Perform comprehensive DNS check by querying multiple record types.
        Uses 4 API calls: dns (for NS+diagnostics), a, mx, txt
        
        Args:
            domain (str): Domain name to lookup
            
        Returns:
            dict: Combined DNS results with all record types
        """
        results = {
            "success": True,
            "domain": domain,
            "dns_records": {
                "a": [],
                "aaaa": [],
                "mx": [],
                "ns": [],
                "txt": [],
                "soa": []
            },
            "diagnostics": {
                "passed": [],
                "warnings": [],
                "errors": []
            },
            "statistics": {},
            "reporting_nameserver": "",
            "api_calls_used": 0
        }
        
        errors = []
        
        # 1. DNS check (gets NS records + diagnostics) - 1 API call
        dns_result = MXToolbox.lookup(domain, 'dns')
        results["api_calls_used"] += 1
        
        if dns_result.get("success"):
            data = dns_result.get("data", {})
            results["reporting_nameserver"] = data.get("ReportingNameServer", "")
            
            # Parse NS records from Information
            for info in data.get("Information", []):
                if info.get("Type") == "NS":
                    ns_record = MXToolbox._parse_ns_record(info)
                    if ns_record:
                        results["dns_records"]["ns"].append(ns_record)
            
            # Parse diagnostics
            for item in data.get("Passed", []):
                results["diagnostics"]["passed"].append({
                    "name": item.get("Name", ""),
                    "info": item.get("Info", "")
                })
            
            for item in data.get("Warnings", []):
                results["diagnostics"]["warnings"].append({
                    "name": item.get("Name", ""),
                    "info": item.get("Info", ""),
                    "details": item.get("AdditionalInfo", [])
                })
            
            for item in data.get("Failed", []):
                results["diagnostics"]["errors"].append({
                    "name": item.get("Name", ""),
                    "info": item.get("Info", ""),
                    "details": item.get("AdditionalInfo", [])
                })
        else:
            errors.append(f"DNS check: {dns_result.get('error', 'Unknown error')}")
        
        # 2. A record lookup - 1 API call
        a_result = MXToolbox.lookup(domain, 'a')
        results["api_calls_used"] += 1
        
        if a_result.get("success"):
            for info in a_result.get("data", {}).get("Information", []):
                a_record = MXToolbox._parse_a_record(info)
                if a_record:
                    if info.get("IsIpV6") == "True":
                        results["dns_records"]["aaaa"].append(a_record)
                    else:
                        results["dns_records"]["a"].append(a_record)
        else:
            errors.append(f"A record: {a_result.get('error', 'Unknown error')}")
        
        # 3. MX record lookup - 1 API call
        mx_result = MXToolbox.lookup(domain, 'mx')
        results["api_calls_used"] += 1
        
        if mx_result.get("success"):
            for info in mx_result.get("data", {}).get("Information", []):
                mx_record = MXToolbox._parse_mx_record(info)
                if mx_record:
                    results["dns_records"]["mx"].append(mx_record)
        else:
            errors.append(f"MX record: {mx_result.get('error', 'Unknown error')}")
        
        # 4. TXT record lookup - 1 API call
        txt_result = MXToolbox.lookup(domain, 'txt')
        results["api_calls_used"] += 1
        
        if txt_result.get("success"):
            for info in txt_result.get("data", {}).get("Information", []):
                txt_record = MXToolbox._parse_txt_record(info)
                if txt_record:
                    results["dns_records"]["txt"].append(txt_record)
        else:
            errors.append(f"TXT record: {txt_result.get('error', 'Unknown error')}")
        
        # Calculate statistics
        results["statistics"] = {
            "a_records": len(results["dns_records"]["a"]),
            "aaaa_records": len(results["dns_records"]["aaaa"]),
            "mx_records": len(results["dns_records"]["mx"]),
            "ns_records": len(results["dns_records"]["ns"]),
            "txt_records": len(results["dns_records"]["txt"]),
            "passed_checks": len(results["diagnostics"]["passed"]),
            "warnings": len(results["diagnostics"]["warnings"]),
            "errors": len(results["diagnostics"]["errors"])
        }
        
        # Set overall success based on whether we got any data
        total_records = sum([
            results["statistics"]["a_records"],
            results["statistics"]["mx_records"],
            results["statistics"]["ns_records"]
        ])
        
        if total_records == 0 and errors:
            results["success"] = False
            results["error"] = "; ".join(errors)
        elif errors:
            results["partial_errors"] = errors
        
        return results
    
    @staticmethod
    def _parse_ns_record(info):
        """Parse NS record from API response"""
        domain_name = info.get("Domain Name", "")
        ip_address = info.get("IP Address", "")
        ttl = info.get("TTL", "")
        status = info.get("Status", "").replace("[", "").replace("]", "")
        
        # Parse ASN info
        asn_info = ""
        asn_raw = info.get("Asn", "[]")
        try:
            asn_data = json.loads(asn_raw) if isinstance(asn_raw, str) else asn_raw
            if asn_data and len(asn_data) > 0:
                asn_info = f"{asn_data[0].get('asname', '')} (AS{asn_data[0].get('asn', '')})"
        except (json.JSONDecodeError, TypeError, IndexError):
            pass
        
        if domain_name:
            return {
                "ns": domain_name,
                "ip": ip_address,
                "ttl": ttl,
                "status": status,
                "asn": asn_info
            }
        return None
    
    @staticmethod
    def _parse_a_record(info):
        """Parse A/AAAA record from API response"""
        domain_name = info.get("Domain Name", "")
        ip_address = info.get("IP Address", "")
        ttl = info.get("TTL", "")
        is_ipv6 = info.get("IsIpV6", "False") == "True"
        
        # Parse ASN info
        asn_info = ""
        asn_raw = info.get("Asn", "[]")
        try:
            asn_data = json.loads(asn_raw) if isinstance(asn_raw, str) else asn_raw
            if asn_data and len(asn_data) > 0:
                asn_info = f"{asn_data[0].get('asname', '')} (AS{asn_data[0].get('asn', '')})"
        except (json.JSONDecodeError, TypeError, IndexError):
            pass
        
        if ip_address:
            return {
                "host": domain_name,
                "ip": ip_address,
                "ttl": ttl,
                "asn": asn_info,
                "ipv6": is_ipv6
            }
        return None
    
    @staticmethod
    def _parse_mx_record(info):
        """Parse MX record from API response"""
        hostname = info.get("Hostname", "")
        ip_address = info.get("IP Address", "")
        preference = info.get("Pref", "")
        ttl = info.get("TTL", "")
        is_ipv6 = info.get("IsIpV6", "False") == "True"
        
        # Parse ASN info
        asn_info = ""
        asn_raw = info.get("Asn", "[]")
        try:
            asn_data = json.loads(asn_raw) if isinstance(asn_raw, str) else asn_raw
            if asn_data and len(asn_data) > 0:
                asn_info = f"{asn_data[0].get('asname', '')} (AS{asn_data[0].get('asn', '')})"
        except (json.JSONDecodeError, TypeError, IndexError):
            pass
        
        if hostname:
            return {
                "mx": hostname,
                "ip": ip_address,
                "preference": preference,
                "ttl": ttl,
                "asn": asn_info,
                "ipv6": is_ipv6
            }
        return None
    
    @staticmethod
    def _parse_txt_record(info):
        """Parse TXT record from API response"""
        # TXT records might have different format
        record_text = info.get("Record", "") or info.get("Info", "") or info.get("TXT", "")
        ttl = info.get("TTL", "")
        
        if record_text:
            return {
                "txt": record_text,
                "ttl": ttl
            }
        return None
    
    @staticmethod
    def is_available():
        """Check if MXToolbox API is accessible"""
        try:
            headers = {
                'Authorization': MXTOOLBOX_API_KEY,
                'Accept': 'application/json'
            }
            response = requests.get(
                f"{MXToolbox.API_BASE}/dns/example.com",
                headers=headers,
                timeout=5
            )
            return response.status_code in [200, 401, 403]
        except Exception:
            return False
