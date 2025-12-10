"""
DNS Lookup Module
Performs DNS lookups (forward and reverse) with custom DNS server support
"""

import socket
import ipaddress
import subprocess
import platform


# Common DNS servers for quick selection
COMMON_DNS_SERVERS = {
    "system": ("System Default", None),
    "google": ("Google DNS", "8.8.8.8"),
    "google_secondary": ("Google DNS Secondary", "8.8.4.4"),
    "cloudflare": ("Cloudflare DNS", "1.1.1.1"),
    "cloudflare_secondary": ("Cloudflare DNS Secondary", "1.0.0.1"),
    "quad9": ("Quad9 DNS", "9.9.9.9"),
    "opendns": ("OpenDNS", "208.67.222.222"),
    "opendns_secondary": ("OpenDNS Secondary", "208.67.220.220"),
}


class DNSLookup:
    """DNS lookup utility for forward and reverse queries"""
    
    @staticmethod
    def lookup(query, dns_server="system"):
        """
        Perform DNS lookup
        
        Args:
            query (str): Hostname or IP address to lookup
            dns_server (str): DNS server to use ("system" for default or IP address)
            
        Returns:
            dict: Lookup results
        """
        # Determine if query is IP or hostname
        try:
            ipaddress.ip_address(query)
            is_ip = True
        except ValueError:
            is_ip = False
        
        if is_ip:
            # Reverse lookup (IP to hostname)
            return DNSLookup._reverse_lookup(query, dns_server)
        else:
            # Forward lookup (hostname to IP)
            return DNSLookup._forward_lookup(query, dns_server)
    
    @staticmethod
    def _get_dns_server_info(dns_server):
        """Get DNS server display name and IP"""
        if dns_server == "system" or dns_server is None:
            return "System Default", None
        
        # Check if it's a known DNS server key
        if dns_server in COMMON_DNS_SERVERS:
            return COMMON_DNS_SERVERS[dns_server]
        
        # It's a custom IP address
        return dns_server, dns_server
    
    @staticmethod
    def _reverse_lookup(ip, dns_server="system"):
        """
        Perform reverse DNS lookup (IP to hostname)
        
        Args:
            ip (str): IP address
            dns_server (str): DNS server to use
            
        Returns:
            dict: Lookup results
        """
        dns_name, dns_ip = DNSLookup._get_dns_server_info(dns_server)
        
        try:
            if dns_ip:
                # Use custom DNS server via nslookup/dig for reverse lookup
                return DNSLookup._reverse_lookup_custom(ip, dns_ip, dns_name)
            else:
                # Use system DNS
                hostname = socket.gethostbyaddr(ip)[0]
                return {
                    "type": "Reverse Lookup (PTR)",
                    "query": ip,
                    "result": hostname,
                    "dns_server": dns_name,
                    "success": True
                }
        except socket.herror:
            return {
                "type": "Reverse Lookup (PTR)",
                "query": ip,
                "result": "No hostname found",
                "dns_server": dns_name,
                "success": False
            }
        except Exception as e:
            return {
                "type": "Reverse Lookup (PTR)",
                "query": ip,
                "result": f"Error: {str(e)}",
                "dns_server": dns_name,
                "success": False
            }
    
    @staticmethod
    def _reverse_lookup_custom(ip, dns_server_ip, dns_name):
        """Reverse lookup using custom DNS server"""
        try:
            if platform.system() == "Windows":
                cmd = ['nslookup', ip, dns_server_ip]
            else:
                cmd = ['dig', f'@{dns_server_ip}', '-x', ip, '+short']
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8',
                errors='ignore'
            )
            
            hostname = None
            if platform.system() == "Windows":
                # Parse nslookup output for PTR
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Name:' in line or 'name =' in line.lower():
                        if 'Name:' in line:
                            hostname = line.split('Name:')[1].strip()
                        else:
                            hostname = line.split('=')[1].strip().rstrip('.')
                        break
            else:
                # Parse dig output
                output = result.stdout.strip()
                if output:
                    hostname = output.split('\n')[0].rstrip('.')
            
            if hostname:
                return {
                    "type": "Reverse Lookup (PTR)",
                    "query": ip,
                    "result": hostname,
                    "dns_server": f"{dns_name} ({dns_server_ip})",
                    "success": True
                }
            else:
                return {
                    "type": "Reverse Lookup (PTR)",
                    "query": ip,
                    "result": "No hostname found",
                    "dns_server": f"{dns_name} ({dns_server_ip})",
                    "success": False
                }
        except subprocess.TimeoutExpired:
            return {
                "type": "Reverse Lookup (PTR)",
                "query": ip,
                "result": "DNS query timed out",
                "dns_server": f"{dns_name} ({dns_server_ip})",
                "success": False
            }
        except Exception as e:
            return {
                "type": "Reverse Lookup (PTR)",
                "query": ip,
                "result": f"Error: {str(e)}",
                "dns_server": f"{dns_name} ({dns_server_ip})",
                "success": False
            }
    
    @staticmethod
    def _forward_lookup(hostname, dns_server="system"):
        """
        Perform forward DNS lookup (hostname to IP)
        
        Args:
            hostname (str): Hostname to resolve
            dns_server (str): DNS server to use
            
        Returns:
            dict: Lookup results
        """
        dns_name, dns_ip = DNSLookup._get_dns_server_info(dns_server)
        
        try:
            if dns_ip:
                # Use custom DNS server
                return DNSLookup._forward_lookup_custom(hostname, dns_ip, dns_name)
            else:
                # Use system DNS
                ip_addresses = socket.gethostbyname_ex(hostname)[2]
                return {
                    "type": "Forward Lookup (A)",
                    "query": hostname,
                    "result": ip_addresses,
                    "dns_server": dns_name,
                    "success": True
                }
        except socket.gaierror:
            return {
                "type": "Forward Lookup (A)",
                "query": hostname,
                "result": "Hostname not found",
                "dns_server": dns_name,
                "success": False
            }
        except Exception as e:
            return {
                "type": "Forward Lookup (A)",
                "query": hostname,
                "result": f"Error: {str(e)}",
                "dns_server": dns_name,
                "success": False
            }
    
    @staticmethod
    def _forward_lookup_custom(hostname, dns_server_ip, dns_name):
        """
        Lookup using custom DNS server via nslookup/dig
        
        Args:
            hostname (str): Hostname to resolve
            dns_server_ip (str): DNS server IP address
            dns_name (str): Display name for DNS server
            
        Returns:
            dict: Lookup results
        """
        try:
            if platform.system() == "Windows":
                cmd = ['nslookup', hostname, dns_server_ip]
            else:
                cmd = ['dig', f'@{dns_server_ip}', hostname, '+short']
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8',
                errors='ignore'
            )
            
            ips = []
            if platform.system() == "Windows":
                # Parse nslookup output
                lines = result.stdout.split('\n')
                in_answer_section = False
                for line in lines:
                    # Skip the DNS server's own address
                    if 'Server:' in line or 'Address:' in line and dns_server_ip in line:
                        continue
                    # Look for answer section
                    if 'Name:' in line and hostname.lower() in line.lower():
                        in_answer_section = True
                        continue
                    if in_answer_section and 'Address:' in line:
                        ip = line.split('Address:')[1].strip()
                        if ip and ip != dns_server_ip:
                            # Handle IPv6 and IPv4
                            ip = ip.split('%')[0]  # Remove scope ID if present
                            ips.append(ip)
                    elif in_answer_section and 'Addresses:' in line:
                        # Multiple addresses on same line
                        addrs = line.split('Addresses:')[1].strip()
                        for ip in addrs.split(','):
                            ip = ip.strip().split('%')[0]
                            if ip and ip != dns_server_ip:
                                ips.append(ip)
                
                # Fallback: look for any Address lines after the server info
                if not ips:
                    found_server = False
                    for line in lines:
                        if 'Server:' in line:
                            found_server = True
                            continue
                        if found_server and 'Address:' in line:
                            if dns_server_ip in line:
                                continue  # Skip server's address
                            ip = line.split('Address:')[1].strip().split('%')[0]
                            if ip:
                                ips.append(ip)
            else:
                # Parse dig output
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line and not line.startswith(';'):
                        ips.append(line)
            
            if ips:
                return {
                    "type": "Forward Lookup (A/AAAA)",
                    "query": hostname,
                    "result": ips,
                    "dns_server": f"{dns_name} ({dns_server_ip})",
                    "success": True
                }
            else:
                return {
                    "type": "Forward Lookup (A)",
                    "query": hostname,
                    "result": "No IP addresses found",
                    "dns_server": f"{dns_name} ({dns_server_ip})",
                    "success": False
                }
        except subprocess.TimeoutExpired:
            return {
                "type": "Forward Lookup (A)",
                "query": hostname,
                "result": "DNS query timed out",
                "dns_server": f"{dns_name} ({dns_server_ip})",
                "success": False
            }
        except Exception as e:
            return {
                "type": "Forward Lookup (A)",
                "query": hostname,
                "result": f"Error: {str(e)}",
                "dns_server": f"{dns_name} ({dns_server_ip})",
                "success": False
            }
    
    @staticmethod
    def get_all_records(hostname, dns_server="system"):
        """
        Get multiple record types for a hostname
        
        Args:
            hostname (str): Hostname to query
            dns_server (str): DNS server to use
            
        Returns:
            dict: Results with multiple record types
        """
        dns_name, dns_ip = DNSLookup._get_dns_server_info(dns_server)
        server_to_use = dns_ip if dns_ip else None
        
        results = {
            "hostname": hostname,
            "dns_server": f"{dns_name}" + (f" ({dns_ip})" if dns_ip else ""),
            "records": {}
        }
        
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME']
        
        for record_type in record_types:
            try:
                records = DNSLookup._query_record_type(hostname, record_type, server_to_use)
                if records:
                    results["records"][record_type] = records
            except Exception:
                pass
        
        return results
    
    @staticmethod
    def _query_record_type(hostname, record_type, dns_server_ip=None):
        """Query specific DNS record type"""
        try:
            if platform.system() == "Windows":
                if dns_server_ip:
                    cmd = ['nslookup', '-type=' + record_type, hostname, dns_server_ip]
                else:
                    cmd = ['nslookup', '-type=' + record_type, hostname]
            else:
                if dns_server_ip:
                    cmd = ['dig', f'@{dns_server_ip}', hostname, record_type, '+short']
                else:
                    cmd = ['dig', hostname, record_type, '+short']
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
                encoding='utf-8',
                errors='ignore'
            )
            
            records = []
            if platform.system() == "Windows":
                # Parse Windows nslookup output
                lines = result.stdout.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    # Skip server info
                    if 'Server:' in line or (dns_server_ip and dns_server_ip in line):
                        continue
                    # Extract record data based on type
                    if record_type == 'MX' and 'mail exchanger' in line.lower():
                        records.append(line)
                    elif record_type == 'NS' and 'nameserver' in line.lower():
                        records.append(line.split('=')[-1].strip())
                    elif record_type == 'TXT' and 'text' in line.lower():
                        records.append(line.split('=')[-1].strip().strip('"'))
                    elif record_type in ['A', 'AAAA'] and 'Address:' in line:
                        addr = line.split('Address:')[1].strip()
                        if addr and (dns_server_ip is None or addr != dns_server_ip):
                            records.append(addr)
            else:
                # Parse dig output
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line and not line.startswith(';'):
                        records.append(line)
            
            return records
        except Exception:
            return []
    
    @staticmethod
    def validate_query(query):
        """
        Validate DNS query (hostname or IP)
        
        Args:
            query (str): Query to validate
            
        Returns:
            tuple: (is_valid, query_type) where query_type is "ip" or "hostname"
        """
        if not query or not query.strip():
            return False, None
        
        # Check if it's an IP address
        try:
            ipaddress.ip_address(query.strip())
            return True, "ip"
        except ValueError:
            pass
        
        # Check if it looks like a valid hostname
        # Basic validation - could be more strict
        if len(query.strip()) > 0 and '.' in query:
            return True, "hostname"
        
        return False, None
    
    @staticmethod
    def validate_dns_server(dns_server):
        """
        Validate DNS server IP address
        
        Args:
            dns_server (str): DNS server to validate
            
        Returns:
            bool: True if valid IP address
        """
        if dns_server == "system" or dns_server in COMMON_DNS_SERVERS:
            return True
        
        try:
            ipaddress.ip_address(dns_server.strip())
            return True
        except ValueError:
            return False
