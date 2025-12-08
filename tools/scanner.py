"""
IPv4 Network Scanner Tool
Handles network scanning functionality
"""

import ipaddress
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from pythonping import ping


class IPv4Scanner:
    """IPv4 Network Scanner using ICMP ping"""
    
    def __init__(self):
        self.scanning = False
        self.cancel_flag = False
        self.results = []
        self.progress_callback = None
        self.complete_callback = None
    
    def parse_cidr(self, cidr_input):
        """Parse CIDR notation and return list of host IPs"""
        try:
            network = ipaddress.ip_network(cidr_input, strict=False)
            
            # For /31 and /32, include all addresses
            if network.prefixlen >= 31:
                return [str(ip) for ip in network.hosts()] if network.prefixlen == 31 else [str(network.network_address)]
            
            # For other networks, exclude network and broadcast
            return [str(ip) for ip in network.hosts()]
        except ValueError as e:
            raise ValueError(f"Invalid CIDR format: {e}")
    
    def resolve_hostname(self, ip, timeout=2):
        """Resolve hostname/FQDN for an IP address"""
        try:
            socket.setdefaulttimeout(timeout)
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except (socket.herror, socket.gaierror, socket.timeout):
            return ""
        except Exception:
            return ""
    
    def ping_host(self, ip, timeout_ms, resolve_dns=True):
        """Ping a single host and return result with optional DNS resolution"""
        try:
            response = ping(ip, timeout=timeout_ms/1000, count=1, verbose=False)
            
            # Resolve hostname if requested and host is online
            hostname = ""
            if response.success() and resolve_dns:
                hostname = self.resolve_hostname(ip, timeout=1)
            
            if response.success():
                rtt = response.rtt_avg_ms
                return {
                    'ip': ip,
                    'status': 'Online',
                    'rtt': f"{rtt:.1f}" if rtt else "N/A",
                    'hostname': hostname
                }
            else:
                return {
                    'ip': ip,
                    'status': 'No Response',
                    'rtt': '',
                    'hostname': ''
                }
        except Exception:
            return {
                'ip': ip,
                'status': 'No Response',
                'rtt': '',
                'hostname': ''
            }
    
    def resolve_hostname_to_ip(self, hostname, timeout=2):
        """Resolve hostname/FQDN to IP address"""
        try:
            socket.setdefaulttimeout(timeout)
            ip = socket.gethostbyname(hostname)
            return ip
        except (socket.herror, socket.gaierror, socket.timeout):
            return None
        except Exception:
            return None
    
    def parse_ip_list(self, ip_text, resolve_hostnames=True):
        """Parse IP list from text (supports IPs, CIDR, hostnames, comments)"""
        ip_list = []
        resolved_info = []  # Track what was resolved
        lines = ip_text.strip().split('\n')
        
        for line in lines:
            # Remove comments and whitespace
            line = line.split('#')[0].strip()
            if not line:
                continue
            
            # Try to parse as IP or CIDR first
            try:
                # Check if it's a CIDR
                if '/' in line:
                    network = ipaddress.ip_network(line, strict=False)
                    if network.prefixlen >= 31:
                        ips = [str(ip) for ip in network.hosts()] if network.prefixlen == 31 else [str(network.network_address)]
                    else:
                        ips = [str(ip) for ip in network.hosts()]
                    ip_list.extend(ips)
                    resolved_info.append((line, f"Expanded to {len(ips)} IPs", True))
                else:
                    # Try as single IP address
                    ip = ipaddress.ip_address(line)
                    ip_list.append(str(ip))
                    resolved_info.append((line, str(ip), True))
            except ValueError:
                # Not a valid IP/CIDR, try as hostname
                if resolve_hostnames:
                    resolved_ip = self.resolve_hostname_to_ip(line)
                    if resolved_ip:
                        ip_list.append(resolved_ip)
                        resolved_info.append((line, resolved_ip, True))
                    else:
                        resolved_info.append((line, "Failed to resolve", False))
                else:
                    resolved_info.append((line, "Skipped (not an IP)", False))
        
        return ip_list, resolved_info
    
    def scan_network(self, cidr, aggression='Medium', max_workers=None, resolve_dns=True):
        """Scan network with specified parameters and optional DNS resolution"""
        self.scanning = True
        self.cancel_flag = False
        self.results = []
        
        # Set timeout based on aggression
        timeout_map = {
            'Gentle (longer timeout)': 600,
            'Medium': 300,
            'Aggressive (short timeout)': 150
        }
        timeout_ms = timeout_map.get(aggression, 300)
        
        # Set max workers based on aggression
        worker_map = {
            'Gentle (longer timeout)': 32,
            'Medium': 64,
            'Aggressive (short timeout)': 128
        }
        if max_workers is None:
            max_workers = worker_map.get(aggression, 64)
        
        try:
            ip_list = self.parse_cidr(cidr)
            total = len(ip_list)
            
            if total == 0:
                if self.complete_callback:
                    self.complete_callback([], "No hosts in range")
                return
            
            completed = 0
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_ip = {executor.submit(self.ping_host, ip, timeout_ms, resolve_dns): ip 
                               for ip in ip_list}
                
                for future in as_completed(future_to_ip):
                    if self.cancel_flag:
                        executor.shutdown(wait=False, cancel_futures=True)
                        if self.complete_callback:
                            self.complete_callback(self.results, "Scan cancelled")
                        return
                    
                    result = future.result()
                    self.results.append(result)
                    completed += 1
                    
                    # Update progress
                    if self.progress_callback:
                        self.progress_callback(completed, total, result)
            
            if self.complete_callback:
                self.complete_callback(self.results, "Scan completed")
                
        except Exception as e:
            if self.complete_callback:
                self.complete_callback([], f"Error: {str(e)}")
        finally:
            self.scanning = False
    
    def scan_ip_list(self, ip_list, aggression='Medium', max_workers=None, resolve_dns=True):
        """Scan a list of IP addresses"""
        print(f"Scanner.scan_ip_list called with {len(ip_list)} IPs")
        self.scanning = True
        self.cancel_flag = False
        self.results = []
        
        # Set timeout based on aggression
        timeout_map = {
            'Gentle (longer timeout)': 600,
            'Medium': 300,
            'Aggressive (short timeout)': 150
        }
        timeout_ms = timeout_map.get(aggression, 300)
        print(f"Using timeout: {timeout_ms}ms")
        
        # Set max workers based on aggression
        worker_map = {
            'Gentle (longer timeout)': 32,
            'Medium': 64,
            'Aggressive (short timeout)': 128
        }
        if max_workers is None:
            max_workers = worker_map.get(aggression, 64)
        
        try:
            total = len(ip_list)
            
            if total == 0:
                if self.complete_callback:
                    self.complete_callback([], "No IPs to scan")
                return
            
            completed = 0
            print(f"Creating executor with {max_workers} workers for {total} IPs")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_ip = {executor.submit(self.ping_host, ip, timeout_ms, resolve_dns): ip 
                               for ip in ip_list}
                print(f"Submitted {len(future_to_ip)} tasks")
                
                for future in as_completed(future_to_ip):
                    if self.cancel_flag:
                        executor.shutdown(wait=False, cancel_futures=True)
                        if self.complete_callback:
                            self.complete_callback(self.results, "Scan cancelled")
                        return
                    
                    result = future.result()
                    print(f"Got result for {result.get('ip')}: {result.get('status')}")
                    self.results.append(result)
                    completed += 1
                    
                    # Update progress
                    if self.progress_callback:
                        print(f"Calling progress_callback for {result.get('ip')}")
                        self.progress_callback(completed, total, result)
                    else:
                        print("WARNING: progress_callback is None!")
            
            if self.complete_callback:
                self.complete_callback(self.results, "Scan completed")
                
        except Exception as e:
            if self.complete_callback:
                self.complete_callback([], f"Error: {str(e)}")
        finally:
            self.scanning = False
    
    def cancel_scan(self):
        """Cancel ongoing scan"""
        self.cancel_flag = True
