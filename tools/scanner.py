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
    
    def resolve_netbios_raw(self, ip, timeout=2):
        """
        Resolve hostname via NetBIOS Name Service (NBNS) - UDP port 137
        Sends a NetBIOS Node Status Request to get the computer name
        """
        try:
            # Build NetBIOS Node Status Request packet
            # This is a NBSTAT query for the wildcard name '*'
            
            # Header
            transaction_id = b'\x80\x94'  # Random transaction ID
            flags = b'\x00\x00'  # Standard query, no recursion
            qdcount = b'\x00\x01'  # 1 question
            ancount = b'\x00\x00'  # 0 answers
            nscount = b'\x00\x00'  # 0 authority
            arcount = b'\x00\x00'  # 0 additional
            
            # Question section - encoded '*' name for NBSTAT query
            # NetBIOS first-level encoding of '*' padded to 16 chars
            # '*' = 0x2A, padded with spaces (0x20) to 16 bytes
            # First-level encoding: each nibble + 'A' (0x41)
            # '*' (0x2A) -> 'C' 'K' (0x43, 0x4B)
            # ' ' (0x20) -> 'C' 'A' (0x43, 0x41)
            encoded_name = b'\x20'  # Length 32
            encoded_name += b'CKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'  # Encoded '*' + 15 spaces
            encoded_name += b'\x00'  # Name terminator
            
            qtype = b'\x00\x21'   # NBSTAT (Node Status)
            qclass = b'\x00\x01'  # IN (Internet)
            
            packet = (transaction_id + flags + qdcount + ancount + 
                     nscount + arcount + encoded_name + qtype + qclass)
            
            # Send UDP packet
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            sock.sendto(packet, (ip, 137))
            
            # Receive response
            response, _ = sock.recvfrom(2048)
            sock.close()
            
            # Parse the response
            if len(response) < 57:
                return ""
            
            # The response format:
            # - 12 bytes header
            # - Question section (copy of request)
            # - Answer section with node status
            
            # Find the number of names in the response
            # This is after the header (12) + question section (~38 bytes) + answer header (~12 bytes)
            # Look for the name count byte
            
            # Skip to after the question section
            # The name count is typically at offset 56 or thereabouts
            pos = 56
            if pos >= len(response):
                return ""
            
            num_names = response[pos]
            pos += 1
            
            # Parse each name entry (18 bytes each: 15 name + 1 suffix + 2 flags)
            for _ in range(num_names):
                if pos + 18 > len(response):
                    break
                
                name_bytes = response[pos:pos + 15]
                suffix = response[pos + 15]
                # flags = response[pos + 16:pos + 18]  # Not needed
                pos += 18
                
                # Decode the name
                try:
                    name = name_bytes.decode('ascii', errors='ignore').rstrip()
                    # suffix 0x00 = Workstation, 0x20 = Server
                    # We want the workstation or server name, not group names
                    if suffix in (0x00, 0x20) and name and len(name) > 0:
                        # Skip names starting with special chars
                        if not name.startswith(('_', '~', '\x01', '\x00')):
                            return name
                except Exception:
                    continue
            
            return ""
        except socket.timeout:
            return ""
        except Exception:
            return ""
    
    def resolve_nbtstat(self, ip, timeout=3):
        """Resolve hostname using Windows nbtstat command"""
        if platform.system() != 'Windows':
            return ""
        
        try:
            # Use CREATE_NO_WINDOW flag on Windows
            startupinfo = None
            creationflags = 0
            if platform.system() == 'Windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creationflags = subprocess.CREATE_NO_WINDOW
            
            result = subprocess.run(
                ['nbtstat', '-A', ip],
                capture_output=True,
                timeout=timeout,
                startupinfo=startupinfo,
                creationflags=creationflags
            )
            
            # Decode output, handling different encodings
            output = ""
            for encoding in ['utf-8', 'cp850', 'cp1252', 'latin-1']:
                try:
                    output = result.stdout.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if output:
                lines = output.split('\n')
                for line in lines:
                    line = line.strip()
                    # Look for lines with <00> UNIQUE (workstation) or <20> UNIQUE (server)
                    if '<00>' in line and 'UNIQUE' in line.upper():
                        parts = line.split()
                        if parts:
                            name = parts[0].strip()
                            if name and not name.startswith(('_', '~')):
                                return name
                    elif '<20>' in line and 'UNIQUE' in line.upper():
                        parts = line.split()
                        if parts:
                            name = parts[0].strip()
                            if name and not name.startswith(('_', '~')):
                                return name
            return ""
        except subprocess.TimeoutExpired:
            return ""
        except Exception:
            return ""
    
    def resolve_ping_a(self, ip, timeout=2):
        """Resolve hostname using Windows 'ping -a' command (reverse DNS via ping)"""
        if platform.system() != 'Windows':
            return ""
        
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            result = subprocess.run(
                ['ping', '-a', '-n', '1', '-w', str(int(timeout * 1000)), ip],
                capture_output=True,
                timeout=timeout + 1,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            output = ""
            for encoding in ['utf-8', 'cp850', 'cp1252', 'latin-1']:
                try:
                    output = result.stdout.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if output:
                # Look for pattern: "Pinging hostname [ip]" or "Ping wird ausgeführt für hostname [ip]"
                lines = output.split('\n')
                for line in lines:
                    if '[' in line and ']' in line:
                        # Extract hostname before [ip]
                        import re
                        # Match: "Pinging hostname [ip]" - extract hostname
                        match = re.search(r'(?:Pinging|Ping\s+\S+\s+\S+\s+für)\s+(\S+)\s+\[', line, re.IGNORECASE)
                        if match:
                            hostname = match.group(1)
                            if hostname and hostname != ip:
                                return hostname
            return ""
        except Exception:
            return ""
    
    def resolve_powershell_dns(self, ip, timeout=3):
        """Resolve hostname using PowerShell Resolve-DnsName (Windows)"""
        if platform.system() != 'Windows':
            return ""
        
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            # Use PowerShell to do a PTR lookup
            cmd = f'powershell -NoProfile -Command "(Resolve-DnsName -Name {ip} -DnsOnly -ErrorAction SilentlyContinue).NameHost"'
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                timeout=timeout,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            output = ""
            for encoding in ['utf-8', 'cp850', 'cp1252', 'latin-1']:
                try:
                    output = result.stdout.decode(encoding).strip()
                    break
                except UnicodeDecodeError:
                    continue
            
            if output and output != ip and not output.startswith('Resolve-'):
                return output
            return ""
        except Exception:
            return ""
    
    def resolve_smb_hostname(self, ip, timeout=2):
        """
        Resolve hostname via SMB/CIFS on port 445.
        This works even when NetBIOS is disabled.
        Connects to SMB port and extracts hostname from negotiation.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, 445))
            
            # SMB Negotiate Protocol Request
            # This is a minimal SMB1 negotiate request that will get a response with the server name
            smb_negotiate = bytes([
                # NetBIOS Session Service header
                0x00,  # Message type: Session message
                0x00, 0x00, 0x85,  # Length (133 bytes)
                
                # SMB Header
                0xFF, 0x53, 0x4D, 0x42,  # Server Component: SMB
                0x72,  # SMB Command: Negotiate Protocol (0x72)
                0x00, 0x00, 0x00, 0x00,  # NT Status: Success
                0x18,  # Flags
                0x53, 0xC8,  # Flags2
                0x00, 0x00,  # Process ID High
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # Signature
                0x00, 0x00,  # Reserved
                0x00, 0x00,  # Tree ID
                0x00, 0x00,  # Process ID
                0x00, 0x00,  # User ID
                0x00, 0x00,  # Multiplex ID
                
                # Negotiate Protocol Request
                0x00,  # Word Count
                0x62, 0x00,  # Byte Count (98 bytes)
                
                # Dialects
                0x02, 0x50, 0x43, 0x20, 0x4E, 0x45, 0x54, 0x57,  # PC NETWORK PROGRAM 1.0
                0x4F, 0x52, 0x4B, 0x20, 0x50, 0x52, 0x4F, 0x47,
                0x52, 0x41, 0x4D, 0x20, 0x31, 0x2E, 0x30, 0x00,
                0x02, 0x4C, 0x41, 0x4E, 0x4D, 0x41, 0x4E, 0x31,  # LANMAN1.0
                0x2E, 0x30, 0x00,
                0x02, 0x57, 0x69, 0x6E, 0x64, 0x6F, 0x77, 0x73,  # Windows for Workgroups 3.1a
                0x20, 0x66, 0x6F, 0x72, 0x20, 0x57, 0x6F, 0x72,
                0x6B, 0x67, 0x72, 0x6F, 0x75, 0x70, 0x73, 0x20,
                0x33, 0x2E, 0x31, 0x61, 0x00,
                0x02, 0x4C, 0x4D, 0x31, 0x2E, 0x32, 0x58, 0x30,  # LM1.2X002
                0x30, 0x32, 0x00,
                0x02, 0x4C, 0x41, 0x4E, 0x4D, 0x41, 0x4E, 0x32,  # LANMAN2.1
                0x2E, 0x31, 0x00,
                0x02, 0x4E, 0x54, 0x20, 0x4C, 0x4D, 0x20, 0x30,  # NT LM 0.12
                0x2E, 0x31, 0x32, 0x00,
            ])
            
            sock.send(smb_negotiate)
            response = sock.recv(1024)
            sock.close()
            
            # Parse SMB response for server name
            # The server name is in the negotiate response, but it's complex to parse
            # A simpler approach: the response often contains the hostname in plain text
            if len(response) > 50:
                # Look for readable hostname in response
                try:
                    # Try to find hostname pattern in response
                    text = response.decode('utf-16-le', errors='ignore')
                    # Look for sequences that look like hostnames
                    import re
                    matches = re.findall(r'([A-Za-z][A-Za-z0-9\-]{1,15})', text)
                    for match in matches:
                        if len(match) > 2 and match.upper() not in ('SMB', 'NTLM', 'LAN', 'WINDOWS'):
                            return match.upper()
                except Exception:
                    pass
            
            return ""
        except (socket.timeout, socket.error, ConnectionRefusedError):
            return ""
        except Exception:
            return ""
    
    def resolve_net_view(self, ip, timeout=3):
        """
        Resolve hostname using 'net view' command (Windows).
        This queries SMB shares and often returns the computer name.
        """
        if platform.system() != 'Windows':
            return ""
        
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            result = subprocess.run(
                ['net', 'view', f'\\\\{ip}'],
                capture_output=True,
                timeout=timeout,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Even if net view fails, the error message often contains the hostname
            output = ""
            for encoding in ['utf-8', 'cp850', 'cp1252', 'latin-1']:
                try:
                    output = (result.stdout.decode(encoding) + result.stderr.decode(encoding)).strip()
                    break
                except UnicodeDecodeError:
                    continue
            
            if output:
                # Look for patterns like "Shared resources at \\HOSTNAME" or error with hostname
                import re
                # Pattern for shared resources
                match = re.search(r'\\\\([A-Za-z0-9\-_]+)', output)
                if match:
                    hostname = match.group(1)
                    if hostname and hostname != ip:
                        return hostname
            return ""
        except Exception:
            return ""
    
    def resolve_wmi(self, ip, timeout=5):
        """
        Resolve hostname using WMI (Windows Management Instrumentation).
        Requires WMI access to the remote machine.
        """
        if platform.system() != 'Windows':
            return ""
        
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            # Use WMIC to query computer name
            cmd = f'wmic /node:"{ip}" computersystem get name /value'
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                timeout=timeout,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            output = ""
            for encoding in ['utf-8', 'cp850', 'cp1252', 'latin-1']:
                try:
                    output = result.stdout.decode(encoding).strip()
                    break
                except UnicodeDecodeError:
                    continue
            
            if output:
                # Parse "Name=HOSTNAME" format
                import re
                match = re.search(r'Name=([A-Za-z0-9\-_]+)', output, re.IGNORECASE)
                if match:
                    return match.group(1)
            return ""
        except Exception:
            return ""
    
    def resolve_hostname(self, ip, timeout=1):
        """
        Resolve hostname using multiple methods (like Advanced IP Scanner):
        1. Reverse DNS lookup (socket.gethostbyaddr)
        2. Windows ping -a (reverse DNS via ping)
        3. PowerShell Resolve-DnsName (Windows)
        4. NetBIOS Name Service (direct UDP query to port 137)
        5. nbtstat command (Windows - most reliable for local Windows machines)
        """
        hostname = ""
        
        # Method 1: Reverse DNS (fastest, works for registered DNS entries)
        if self.use_dns:
            hostname = self.resolve_dns(ip, timeout=0.5)
            if hostname:
                return hostname
        
        # Method 2: ping -a on Windows (another way to do reverse DNS)
        if self.use_dns and platform.system() == 'Windows':
            hostname = self.resolve_ping_a(ip, timeout=1)
            if hostname:
                return hostname
        
        # Method 3: PowerShell Resolve-DnsName (Windows - can use LLMNR)
        if self.use_dns and platform.system() == 'Windows':
            hostname = self.resolve_powershell_dns(ip, timeout=2)
            if hostname:
                return hostname
        
        # Method 4: NetBIOS Name Service (works for Windows machines in local network)
        if self.use_netbios:
            hostname = self.resolve_netbios_raw(ip, timeout=1)
            if hostname:
                return hostname
        
        # Method 5: nbtstat command (Windows - slower but reliable)
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
