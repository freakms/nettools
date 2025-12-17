"""
IPv4 Network Scanner Tool
Handles network scanning functionality with enhanced hostname resolution
"""

import ipaddress
import socket
import struct
import time
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed
from pythonping import ping


class IPv4Scanner:
    """IPv4 Network Scanner using ICMP ping with multi-method hostname resolution"""
    
    def __init__(self):
        self.scanning = False
        self.cancel_flag = False
        self.results = []
        self.progress_callback = None
        self.complete_callback = None
        
        # Performance settings
        self._last_progress_time = 0
        self._progress_interval = 0.15  # Minimum seconds between progress updates
        self._progress_count_interval = 20  # Or update every N results
        
        # Hostname resolution settings
        self.use_netbios = True
        self.use_dns = True
        self.use_nbtstat = True
    
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
    
    def resolve_dns(self, ip, timeout=1):
        """Resolve hostname via Reverse DNS lookup"""
        try:
            socket.setdefaulttimeout(timeout)
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except (socket.herror, socket.gaierror, socket.timeout):
            return ""
        except Exception:
            return ""
    
    def resolve_netbios(self, ip, timeout=2):
        """Resolve hostname via NetBIOS Name Service (NBNS) - UDP port 137"""
        try:
            # NetBIOS Name Query packet
            # Transaction ID (2 bytes) + Flags (2 bytes) + Questions (2 bytes) + 
            # Answer RRs (2 bytes) + Authority RRs (2 bytes) + Additional RRs (2 bytes)
            transaction_id = b'\x80\x01'
            flags = b'\x00\x00'  # Standard query
            questions = b'\x00\x01'
            answer_rrs = b'\x00\x00'
            authority_rrs = b'\x00\x00'
            additional_rrs = b'\x00\x00'
            
            # Query for '*' (CKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA) - status query
            # Encoded NetBIOS name for '*' (wildcard)
            query_name = b'\x20CKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x00'
            query_type = b'\x00\x21'  # NBSTAT
            query_class = b'\x00\x01'  # IN
            
            packet = (transaction_id + flags + questions + answer_rrs + 
                     authority_rrs + additional_rrs + query_name + query_type + query_class)
            
            # Send UDP packet to port 137
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            sock.sendto(packet, (ip, 137))
            
            # Receive response
            response, _ = sock.recvfrom(1024)
            sock.close()
            
            # Parse response - name is at offset after header (12 bytes) + query section
            if len(response) > 57:
                # Skip to answer section and find name count
                name_count = response[56]
                if name_count > 0:
                    # Names start at offset 57
                    offset = 57
                    for i in range(name_count):
                        if offset + 18 <= len(response):
                            # NetBIOS name is 15 bytes + 1 byte suffix + 2 bytes flags
                            name_bytes = response[offset:offset + 15]
                            suffix = response[offset + 15]
                            
                            # Decode name (strip padding spaces)
                            try:
                                name = name_bytes.decode('ascii', errors='ignore').strip()
                                # Return workstation name (suffix 0x00) or server name (suffix 0x20)
                                if suffix in (0x00, 0x20) and name and not name.startswith('\x00'):
                                    return name
                            except:
                                pass
                            offset += 18
            return ""
        except (socket.timeout, socket.error, Exception):
            return ""
    
    def resolve_nbtstat(self, ip, timeout=3):
        """Resolve hostname using Windows nbtstat command"""
        if platform.system() != 'Windows':
            return ""
        
        try:
            result = subprocess.run(
                ['nbtstat', '-A', ip],
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0
            )
            
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    # Look for lines with <00> UNIQUE (workstation) or <20> UNIQUE (server)
                    line = line.strip()
                    if '<00>' in line and 'UNIQUE' in line:
                        parts = line.split()
                        if parts:
                            name = parts[0].strip()
                            if name and not name.startswith('_'):
                                return name
                    elif '<20>' in line and 'UNIQUE' in line:
                        parts = line.split()
                        if parts:
                            name = parts[0].strip()
                            if name and not name.startswith('_'):
                                return name
            return ""
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, Exception):
            return ""
    
    def resolve_hostname(self, ip, timeout=1):
        """
        Resolve hostname using multiple methods (like Advanced IP Scanner):
        1. Reverse DNS lookup
        2. NetBIOS Name Service (direct UDP query)
        3. nbtstat command (Windows fallback)
        """
        hostname = ""
        
        # Method 1: Reverse DNS (fastest, works for registered DNS entries)
        if self.use_dns:
            hostname = self.resolve_dns(ip, timeout=0.5)
            if hostname:
                return hostname
        
        # Method 2: NetBIOS Name Service (works for Windows machines in local network)
        if self.use_netbios:
            hostname = self.resolve_netbios(ip, timeout=1)
            if hostname:
                return hostname
        
        # Method 3: nbtstat command (Windows fallback, slower but reliable)
        if self.use_nbtstat and platform.system() == 'Windows':
            hostname = self.resolve_nbtstat(ip, timeout=2)
            if hostname:
                return hostname
        
        return ""
    
    def ping_host(self, ip, timeout_ms, resolve_dns=True):
        """Ping a single host and return result with optional DNS resolution"""
        try:
            response = ping(ip, timeout=timeout_ms/1000, count=1, verbose=False)
            
            # Resolve hostname if requested and host is online
            hostname = ""
            if response.success() and resolve_dns:
                hostname = self.resolve_hostname(ip, timeout=0.5)  # Reduced timeout
            
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
    
    def _should_update_progress(self, completed):
        """Determine if we should fire a progress update (throttled)"""
        current_time = time.time()
        time_elapsed = current_time - self._last_progress_time
        
        # Update if enough time passed OR enough results processed
        if time_elapsed >= self._progress_interval or completed % self._progress_count_interval == 0:
            self._last_progress_time = current_time
            return True
        return False
    
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
        self._last_progress_time = 0
        
        # Set timeout based on aggression
        timeout_map = {
            'Gentle (longer timeout)': 600,
            'Medium': 300,
            'Aggressive (short timeout)': 150
        }
        timeout_ms = int(timeout_map.get(aggression, 300))
        
        # Set max workers based on aggression (increased for better throughput)
        worker_map = {
            'Gentle (longer timeout)': 50,
            'Medium': 100,
            'Aggressive (short timeout)': 150
        }
        if max_workers is None:
            max_workers = int(worker_map.get(aggression, 100))
        
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
                    
                    # Throttled progress update
                    if self.progress_callback and (self._should_update_progress(completed) or completed == total):
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
        self.scanning = True
        self.cancel_flag = False
        self.results = []
        self._last_progress_time = 0
        
        # Set timeout based on aggression
        timeout_map = {
            'Gentle (longer timeout)': 600,
            'Medium': 300,
            'Aggressive (short timeout)': 150
        }
        timeout_ms = int(timeout_map.get(aggression, 300))
        
        # Set max workers based on aggression (increased for better throughput)
        worker_map = {
            'Gentle (longer timeout)': 50,
            'Medium': 100,
            'Aggressive (short timeout)': 150
        }
        if max_workers is None:
            max_workers = int(worker_map.get(aggression, 100))
        
        try:
            total = len(ip_list)
            
            if total == 0:
                if self.complete_callback:
                    self.complete_callback([], "No IPs to scan")
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
                    
                    # Throttled progress update
                    if self.progress_callback and (self._should_update_progress(completed) or completed == total):
                        self.progress_callback(completed, total, result)
            
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
