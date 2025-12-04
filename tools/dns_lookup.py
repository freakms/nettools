"""
DNS Lookup Module
Performs DNS lookups (forward and reverse)
"""

import socket
import ipaddress
import subprocess
import platform


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
        results = {}
        
        # Determine if query is IP or hostname
        try:
            ipaddress.ip_address(query)
            is_ip = True
        except:
            is_ip = False
        
        if is_ip:
            # Reverse lookup (IP to hostname)
            return DNSLookup._reverse_lookup(query)
        else:
            # Forward lookup (hostname to IP)
            return DNSLookup._forward_lookup(query, dns_server)
    
    @staticmethod
    def _reverse_lookup(ip):
        """
        Perform reverse DNS lookup (IP to hostname)
        
        Args:
            ip (str): IP address
            
        Returns:
            dict: Lookup results
        """
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return {
                "type": "Reverse Lookup",
                "query": ip,
                "result": hostname,
                "success": True
            }
        except socket.herror:
            return {
                "type": "Reverse Lookup",
                "query": ip,
                "result": "No hostname found",
                "success": False
            }
        except Exception as e:
            return {
                "type": "Reverse Lookup",
                "query": ip,
                "result": f"Error: {str(e)}",
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
        try:
            if dns_server != "system":
                # Use custom DNS server
                return DNSLookup._lookup_with_custom_dns(hostname, dns_server)
            else:
                # Use system DNS
                ip_addresses = socket.gethostbyname_ex(hostname)[2]
                return {
                    "type": "Forward Lookup",
                    "query": hostname,
                    "result": ip_addresses,
                    "dns_server": "System Default",
                    "success": True
                }
        except socket.gaierror:
            return {
                "type": "Forward Lookup",
                "query": hostname,
                "result": "Hostname not found",
                "success": False
            }
        except Exception as e:
            return {
                "type": "Forward Lookup",
                "query": hostname,
                "result": f"Error: {str(e)}",
                "success": False
            }
    
    @staticmethod
    def _lookup_with_custom_dns(hostname, dns_server):
        """
        Lookup using custom DNS server via nslookup/dig
        
        Args:
            hostname (str): Hostname to resolve
            dns_server (str): DNS server IP address
            
        Returns:
            dict: Lookup results
        """
        try:
            if platform.system() == "Windows":
                cmd = f'nslookup {hostname} {dns_server}'
            else:
                cmd = f'dig @{dns_server} {hostname} +short'
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )
            
            if platform.system() == "Windows":
                # Parse nslookup output
                lines = result.stdout.split('\n')
                ips = []
                for line in lines:
                    if 'Address:' in line and dns_server not in line:
                        ip = line.split('Address:')[1].strip()
                        if ip:
                            ips.append(ip)
                
                if ips:
                    return {
                        "type": "Forward Lookup",
                        "query": hostname,
                        "result": ips,
                        "dns_server": dns_server,
                        "success": True
                    }
                else:
                    return {
                        "type": "Forward Lookup",
                        "query": hostname,
                        "result": "No IP addresses found",
                        "success": False
                    }
            else:
                # Parse dig output
                ips = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                if ips:
                    return {
                        "type": "Forward Lookup",
                        "query": hostname,
                        "result": ips,
                        "dns_server": dns_server,
                        "success": True
                    }
                else:
                    return {
                        "type": "Forward Lookup",
                        "query": hostname,
                        "result": "No IP addresses found",
                        "success": False
                    }
        except Exception as e:
            return {
                "type": "Forward Lookup",
                "query": hostname,
                "result": f"Error: {str(e)}",
                "success": False
            }
    
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
        except:
            pass
        
        # Check if it looks like a valid hostname
        # Basic validation - could be more strict
        if len(query.strip()) > 0 and '.' in query:
            return True, "hostname"
        
        return False, None
