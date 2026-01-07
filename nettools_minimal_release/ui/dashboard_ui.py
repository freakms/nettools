"""
Dashboard UI Module - Redesigned
Clean, information-focused dashboard with network interface details
"""

import customtkinter as ctk
import socket
import platform
import subprocess
import re
import threading
import urllib.request
import json
from design_constants import COLORS, SPACING, RADIUS, FONTS


class DashboardUI:
    """Dashboard page UI implementation - Redesigned for clarity and information"""
    
    def __init__(self, app):
        """
        Initialize Dashboard UI
        
        Args:
            app: Reference to main NetToolsApp instance
        """
        self.app = app
        self.network_interfaces = []
        self.external_ip = "Loading..."
        self.external_ip_info = {}
    
    def create_content(self, parent):
        """Create clean, informative dashboard"""
        self.parent = parent
        
        # Main dashboard container
        dashboard = ctk.CTkScrollableFrame(
            parent,
            fg_color=COLORS['dashboard_bg'],
            corner_radius=0
        )
        dashboard.pack(fill="both", expand=True)
        
        # Header section - Simple and clean
        header_frame = ctk.CTkFrame(dashboard, fg_color="transparent")
        header_frame.pack(fill="x", padx=SPACING['xxl'], pady=(SPACING['xxl'], SPACING['lg']))
        
        title = ctk.CTkLabel(
            header_frame,
            text="Network Overview",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS['text_primary']
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            header_frame,
            text="System and network interface information",
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_secondary']
        )
        subtitle.pack(anchor="w", pady=(3, 0))
        
        # Gather network information
        self._gather_network_info()
        
        # Stats cards row (5 cards) - Added External IP
        stats_frame = ctk.CTkFrame(dashboard, fg_color="transparent")
        stats_frame.pack(fill="x", padx=SPACING['xxl'], pady=SPACING['lg'])
        
        # Configure grid for 5 cards
        for i in range(5):
            stats_frame.grid_columnconfigure(i, weight=1)
        
        # Card 1: External IP (NEW)
        self.external_ip_card = self._create_info_card(
            stats_frame,
            "🌐 External IP",
            "Loading...",
            "Fetching...",
            0, 0,
            highlight=True
        )
        
        # Card 2: System Info
        self._create_info_card(
            stats_frame,
            "💻 System",
            socket.gethostname(),
            platform.system(),
            0, 1
        )
        
        # Card 3: Active Interfaces
        active_count = len([iface for iface in self.network_interfaces if iface.get('status') == 'Up'])
        self._create_info_card(
            stats_frame,
            "📡 Interfaces",
            str(active_count),
            f"of {len(self.network_interfaces)} total",
            0, 2
        )
        
        # Card 4: Recent Scans
        recent_scans = len(self.app.scanner.results) if hasattr(self.app, 'scanner') else 0
        self._create_info_card(
            stats_frame,
            "📊 Recent Scans",
            str(recent_scans),
            "results available",
            0, 3
        )
        
        # Card 5: Network Status
        status_text = "Connected" if active_count > 0 else "Offline"
        self._create_info_card(
            stats_frame,
            "🔌 Status",
            status_text,
            f"{active_count} active",
            0, 4
        )
        
        # Main content area (2 columns)
        content_frame = ctk.CTkFrame(dashboard, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=SPACING['xxl'], pady=SPACING['md'])
        
        content_frame.grid_columnconfigure(0, weight=2)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Left column - Network Interfaces Table
        left_col = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING['md']))
        
        self._create_network_interfaces_section(left_col)
        
        # Right column - Recent Activity
        right_col = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew")
        
        self._create_recent_activity_section(right_col)
        self._create_system_info_section(right_col)
        
        # Fetch external IP in background
        self._fetch_external_ip()
    
    def _fetch_external_ip(self):
        """Fetch external IP address in background thread"""
        def fetch():
            try:
                # Try multiple services for reliability
                services = [
                    ("https://api.ipify.org?format=json", "ip"),
                    ("https://ipinfo.io/json", "ip"),
                    ("https://api.myip.com", "ip"),
                ]
                
                ip = None
                info = {}
                
                for url, key in services:
                    try:
                        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=5) as response:
                            data = json.loads(response.read().decode())
                            ip = data.get(key)
                            
                            # Get additional info if available (from ipinfo.io)
                            if 'city' in data:
                                info['city'] = data.get('city', '')
                                info['region'] = data.get('region', '')
                                info['country'] = data.get('country', '')
                                info['org'] = data.get('org', '')
                            
                            if ip:
                                break
                    except:
                        continue
                
                if ip:
                    self.external_ip = ip
                    self.external_ip_info = info
                    
                    # Update UI
                    location = ""
                    if info.get('city'):
                        location = f"{info.get('city', '')}, {info.get('country', '')}"
                    elif info.get('org'):
                        location = info.get('org', '')[:30]
                    else:
                        location = "Internet"
                    
                    self.app.after(0, lambda ip=ip, loc=location: self._update_external_ip_card(ip, loc))
                else:
                    self.app.after(0, lambda: self._update_external_ip_card("Unavailable", "Could not fetch"))
                    
            except Exception as ex:
                error_msg = str(ex)[:20]
                self.app.after(0, lambda msg=error_msg: self._update_external_ip_card("Error", msg))
        
        thread = threading.Thread(target=fetch, daemon=True)
        thread.start()
    
    def _update_external_ip_card(self, ip, subtitle):
        """Update the external IP card with fetched data"""
        if hasattr(self, 'external_ip_value_label'):
            self.external_ip_value_label.configure(text=ip)
        if hasattr(self, 'external_ip_subtitle_label'):
            self.external_ip_subtitle_label.configure(text=subtitle)
    
    def _gather_network_info(self):
        """Gather network interface information using socket and platform commands"""
        self.network_interfaces = []
        
        try:
            system = platform.system()
            
            if system == "Windows":
                # Use ipconfig on Windows with proper encoding for German characters
                result = subprocess.run(
                    ['ipconfig', '/all'], 
                    capture_output=True, 
                    text=True,
                    encoding='cp1252',  # Windows-1252 for proper German characters
                    errors='replace',  # Replace errors instead of failing
                    timeout=5
                )
                output = result.stdout
                self._parse_windows_interfaces(output)
            else:
                # Use ip addr on Linux/Mac
                try:
                    result = subprocess.run(
                        ['ip', 'addr'], 
                        capture_output=True, 
                        text=True,
                        encoding='utf-8',
                        errors='ignore',
                        timeout=5
                    )
                    output = result.stdout
                    self._parse_linux_interfaces(output)
                except FileNotFoundError:
                    # Fallback to ifconfig if ip command not available
                    result = subprocess.run(
                        ['ifconfig'], 
                        capture_output=True, 
                        text=True,
                        encoding='utf-8',
                        errors='ignore',
                        timeout=5
                    )
                    output = result.stdout
                    self._parse_ifconfig_interfaces(output)
        except Exception as e:
            # Fallback to basic socket info
            self._get_basic_network_info()
    
    def _parse_windows_interfaces(self, output):
        """Parse Windows ipconfig output (supports English and German)"""
        current_interface = None
        
        # Patterns for both English and German Windows
        adapter_patterns = [
            'adapter',           # English
            'Adapter',           # English
            '-Adapter',          # German: "Ethernet-Adapter", "Drahtlos-LAN-Adapter"
        ]
        
        disconnected_patterns = [
            'media disconnected',    # English
            'Medium getrennt',       # German
            'Medienstatus',          # German (when followed by getrennt)
        ]
        
        for line in output.split('\n'):
            line_stripped = line.strip()
            
            # Check for new adapter section
            # Adapter lines are NOT indented and contain adapter type + name
            is_adapter_line = False
            if line and not line.startswith(' ') and not line.startswith('\t'):
                for pattern in adapter_patterns:
                    if pattern.lower() in line.lower() and ':' in line:
                        is_adapter_line = True
                        break
            
            if is_adapter_line:
                # Save previous interface if it has an IP
                if current_interface and current_interface['ipv4'] != 'N/A':
                    self.network_interfaces.append(current_interface)
                
                # Extract adapter name - everything before the last colon
                adapter_name = line.rsplit(':', 1)[0].strip()
                
                current_interface = {
                    'name': adapter_name,
                    'ipv4': 'N/A',
                    'subnet': 'N/A',
                    'gateway': 'N/A',
                    'mac': 'N/A',
                    'dns': 'N/A',
                    'status': 'Down'
                }
                continue
            
            # Parse interface details if we have a current interface
            if current_interface and line_stripped:
                line_lower = line_stripped.lower()
                
                # Check for disconnected status
                for pattern in disconnected_patterns:
                    if pattern.lower() in line_lower:
                        current_interface['status'] = 'Down'
                
                # Parse IPv4 Address (English and German)
                # English: "IPv4 Address. . . . . . . . . . . : 192.168.1.1"
                # German: "IPv4-Adresse  . . . . . . . . . . : 192.168.3.72(Bevorzugt)"
                if 'ipv4' in line_lower and ':' in line_stripped:
                    parts = line_stripped.split(':', 1)
                    if len(parts) > 1:
                        ip = parts[1].strip()
                        # Remove "(Preferred)" or "(Bevorzugt)" suffix
                        ip = ip.split('(')[0].strip()
                        if ip and ip != 'N/A':
                            current_interface['ipv4'] = ip
                            current_interface['status'] = 'Up'
                
                # Parse Subnet Mask (English and German)
                # English: "Subnet Mask . . . . . . . . . . . : 255.255.255.0"
                # German: "Subnetzmaske  . . . . . . . . . . : 255.255.255.0"
                if ('subnet' in line_lower or 'subnetz' in line_lower) and ':' in line_stripped:
                    parts = line_stripped.split(':', 1)
                    if len(parts) > 1:
                        current_interface['subnet'] = parts[1].strip()
                
                # Parse Default Gateway (English and German)
                # English: "Default Gateway . . . . . . . . . : 192.168.1.1"
                # German: "Standardgateway . . . . . . . . . : 192.168.3.1"
                if ('gateway' in line_lower or 'standardgateway' in line_lower) and ':' in line_stripped:
                    parts = line_stripped.split(':', 1)
                    if len(parts) > 1:
                        gw = parts[1].strip()
                        if gw:
                            current_interface['gateway'] = gw
                
                # Parse Physical/MAC Address (English and German)
                # English: "Physical Address. . . . . . . . . : AA-BB-CC-DD-EE-FF"
                # German: "Physische Adresse . . . . . . . . : AA-BB-CC-DD-EE-FF"
                if ('physical' in line_lower or 'physische' in line_lower) and ':' in line_stripped:
                    parts = line_stripped.split(':', 1)
                    if len(parts) > 1:
                        mac = parts[1].strip()
                        if mac and len(mac) >= 17:  # MAC address is at least 17 chars (AA-BB-CC-DD-EE-FF)
                            current_interface['mac'] = mac
                
                # Parse DNS Server (English and German)
                # English: "DNS Servers . . . . . . . . . . . : 8.8.8.8"
                # German: "DNS-Server  . . . . . . . . . . . : 192.168.178.7"
                if 'dns' in line_lower and ('server' in line_lower) and ':' in line_stripped:
                    parts = line_stripped.split(':', 1)
                    if len(parts) > 1:
                        dns = parts[1].strip()
                        if dns:
                            current_interface['dns'] = dns
        
        # Add last interface if it has an IP
        if current_interface and current_interface['ipv4'] != 'N/A':
            self.network_interfaces.append(current_interface)
    
    def _parse_linux_interfaces(self, output):
        """Parse Linux ip addr output"""
        current_interface = None
        
        for line in output.split('\n'):
            if re.match(r'^\d+:', line):
                # New interface
                if current_interface:
                    self.network_interfaces.append(current_interface)
                
                parts = line.split(':')
                name = parts[1].strip()
                status = 'Up' if 'UP' in line else 'Down'
                
                current_interface = {
                    'name': name,
                    'ipv4': 'N/A',
                    'subnet': 'N/A',
                    'mac': 'N/A',
                    'status': status
                }
            elif current_interface:
                if 'inet ' in line and not 'inet6' in line:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        addr_parts = parts[1].split('/')
                        current_interface['ipv4'] = addr_parts[0]
                        if len(addr_parts) > 1:
                            current_interface['subnet'] = f"/{addr_parts[1]}"
                elif 'link/ether' in line:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        current_interface['mac'] = parts[1]
        
        if current_interface:
            self.network_interfaces.append(current_interface)
    
    def _parse_ifconfig_interfaces(self, output):
        """Parse ifconfig output (fallback)"""
        current_interface = None
        
        for line in output.split('\n'):
            if line and not line.startswith(' ') and not line.startswith('\t'):
                # New interface
                if current_interface:
                    self.network_interfaces.append(current_interface)
                
                name = line.split(':')[0].strip()
                status = 'Up' if 'UP' in line else 'Down'
                
                current_interface = {
                    'name': name,
                    'ipv4': 'N/A',
                    'subnet': 'N/A',
                    'mac': 'N/A',
                    'status': status
                }
            elif current_interface:
                if 'inet ' in line:
                    parts = line.strip().split()
                    for i, part in enumerate(parts):
                        if part == 'inet' and i + 1 < len(parts):
                            current_interface['ipv4'] = parts[i + 1]
                        elif part == 'netmask' and i + 1 < len(parts):
                            current_interface['subnet'] = parts[i + 1]
                elif 'ether' in line:
                    parts = line.strip().split()
                    for i, part in enumerate(parts):
                        if part == 'ether' and i + 1 < len(parts):
                            current_interface['mac'] = parts[i + 1]
        
        if current_interface:
            self.network_interfaces.append(current_interface)
    
    def _get_basic_network_info(self):
        """Fallback: Get basic network info using socket"""
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            
            self.network_interfaces.append({
                'name': 'Primary',
                'ipv4': ip_address,
                'subnet': 'N/A',
                'mac': 'N/A',
                'status': 'Up'
            })
        except:
            self.network_interfaces.append({
                'name': 'Unknown',
                'ipv4': 'N/A',
                'subnet': 'N/A',
                'mac': 'N/A',
                'status': 'Down'
            })
    
    def _create_info_card(self, parent, title, value, subtitle, row, col, highlight=False):
        """Create a clean info card without excessive colors"""
        # Use highlight color for special cards (like External IP)
        border_color = COLORS['electric_violet'] if highlight else ("gray70", "gray30")
        
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS['dashboard_card'],
            corner_radius=RADIUS['medium'],
            border_width=2 if highlight else 1,
            border_color=border_color
        )
        card.grid(row=row, column=col, padx=SPACING['sm'], pady=SPACING['sm'], sticky="nsew")
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold" if highlight else "normal"),
            text_color=COLORS['electric_violet'] if highlight else COLORS['text_secondary']
        )
        title_label.pack(pady=(SPACING['md'], SPACING['xs']))
        
        # Value (main info)
        value_color = COLORS['neon_cyan'] if highlight else COLORS['text_primary']
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=18 if highlight else 20, weight="bold"),
            text_color=value_color
        )
        value_label.pack()
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            card,
            text=subtitle,
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary']
        )
        subtitle_label.pack(pady=(SPACING['xs'], SPACING['md']))
        
        # Store references for External IP card
        if highlight:
            self.external_ip_value_label = value_label
            self.external_ip_subtitle_label = subtitle_label
        
        return card
    
    def _create_network_interfaces_section(self, parent):
        """Create network interfaces information table"""
        section = ctk.CTkFrame(
            parent,
            fg_color=COLORS['dashboard_card'],
            corner_radius=RADIUS['medium']
        )
        section.pack(fill="both", expand=True, pady=(0, SPACING['md']))
        
        # Section header
        header = ctk.CTkLabel(
            section,
            text="Network Interfaces",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary'],
            anchor="w"
        )
        header.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['md']))
        
        # Table header
        table_header = ctk.CTkFrame(section, fg_color=("gray85", "gray20"))
        table_header.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        headers = [
            ("Interface", 0.22),
            ("IP Address", 0.18),
            ("Gateway", 0.15),
            ("Subnet", 0.15),
            ("MAC", 0.20),
            ("Status", 0.10)
        ]
        
        for header_text, weight in headers:
            label = ctk.CTkLabel(
                table_header,
                text=header_text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS['text_secondary']
            )
            label.pack(side="left", padx=SPACING['sm'], pady=SPACING['xs'], expand=True, fill="x")
            if weight:
                label.configure(anchor="w")
        
        # Table rows
        if self.network_interfaces:
            for iface in self.network_interfaces:
                self._create_interface_row(section, iface)
        else:
            # Empty state
            empty_label = ctk.CTkLabel(
                section,
                text="No network interfaces detected",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_secondary']
            )
            empty_label.pack(pady=SPACING['xxl'])
        
        # Add spacing at bottom
        ctk.CTkLabel(section, text="", height=SPACING['md']).pack()
    
    def _create_interface_row(self, parent, iface):
        """Create a row for interface information"""
        row = ctk.CTkFrame(
            parent,
            fg_color=("gray90", "gray17"),
            corner_radius=RADIUS['small']
        )
        row.pack(fill="x", padx=SPACING['lg'], pady=SPACING['xs'])
        
        # Interface name (truncate if too long)
        name = iface.get('name', 'Unknown')
        if len(name) > 22:
            name = name[:20] + "..."
        
        name_label = ctk.CTkLabel(
            row,
            text=name,
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_primary'],
            anchor="w"
        )
        name_label.pack(side="left", padx=SPACING['sm'], pady=SPACING['sm'], expand=True, fill="x")
        
        # IP Address
        ip_label = ctk.CTkLabel(
            row,
            text=iface.get('ipv4', 'N/A'),
            font=ctk.CTkFont(size=11, family="Courier New"),
            text_color=COLORS['text_primary'],
            anchor="w"
        )
        ip_label.pack(side="left", padx=SPACING['sm'], expand=True, fill="x")
        
        # Gateway
        gateway = iface.get('gateway', 'N/A')
        if not gateway or gateway == '':
            gateway = 'N/A'
        gateway_label = ctk.CTkLabel(
            row,
            text=gateway,
            font=ctk.CTkFont(size=11, family="Courier New"),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        gateway_label.pack(side="left", padx=SPACING['sm'], expand=True, fill="x")
        
        # Subnet
        subnet_label = ctk.CTkLabel(
            row,
            text=iface.get('subnet', 'N/A'),
            font=ctk.CTkFont(size=11, family="Courier New"),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        subnet_label.pack(side="left", padx=SPACING['sm'], expand=True, fill="x")
        
        # MAC Address
        mac_label = ctk.CTkLabel(
            row,
            text=iface.get('mac', 'N/A'),
            font=ctk.CTkFont(size=11, family="Courier New"),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        mac_label.pack(side="left", padx=SPACING['sm'], expand=True, fill="x")
        
        # Status
        status = iface.get('status', 'Down')
        status_color = COLORS['success'] if status == 'Up' else COLORS['text_secondary']
        status_label = ctk.CTkLabel(
            row,
            text=f"● {status}",
            font=ctk.CTkFont(size=11),
            text_color=status_color,
            anchor="w"
        )
        status_label.pack(side="left", padx=SPACING['sm'])
    
    def _create_recent_activity_section(self, parent):
        """Create recent scans activity section"""
        section = ctk.CTkFrame(
            parent,
            fg_color=COLORS['dashboard_card'],
            corner_radius=RADIUS['medium']
        )
        section.pack(fill="x", pady=(0, SPACING['md']))
        
        # Section header
        header = ctk.CTkLabel(
            section,
            text="Recent Activity",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary'],
            anchor="w"
        )
        header.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['md']))
        
        # Check if there are any scans
        if hasattr(self.app, 'scanner') and len(self.app.scanner.results) > 0:
            results_preview = self.app.scanner.results[:5]  # Show last 5
            
            for result in results_preview:
                item_frame = ctk.CTkFrame(
                    section,
                    fg_color=("gray90", "gray17"),
                    corner_radius=RADIUS['small']
                )
                item_frame.pack(fill="x", padx=SPACING['lg'], pady=SPACING['xs'])
                
                # IP
                ip_label = ctk.CTkLabel(
                    item_frame,
                    text=result.get('ip', 'N/A'),
                    font=ctk.CTkFont(size=11, family="Courier New"),
                    text_color=COLORS['text_primary']
                )
                ip_label.pack(side="left", padx=SPACING['md'], pady=SPACING['sm'])
                
                # Status
                status = result.get('status', 'Unknown')
                status_color = COLORS['success'] if status == 'Online' else COLORS['text_secondary']
                status_label = ctk.CTkLabel(
                    item_frame,
                    text=f"● {status}",
                    font=ctk.CTkFont(size=10),
                    text_color=status_color
                )
                status_label.pack(side="left", padx=SPACING['sm'])
                
                # RTT
                if result.get('rtt'):
                    rtt_label = ctk.CTkLabel(
                        item_frame,
                        text=f"{result.get('rtt')} ms",
                        font=ctk.CTkFont(size=10),
                        text_color=COLORS['text_secondary']
                    )
                    rtt_label.pack(side="right", padx=SPACING['md'])
        else:
            # Empty state
            empty_label = ctk.CTkLabel(
                section,
                text="No recent scans\nUse IPv4 Scanner to begin",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_secondary'],
                justify="center"
            )
            empty_label.pack(pady=SPACING['xl'])
        
        # Add spacing at bottom
        ctk.CTkLabel(section, text="", height=SPACING['sm']).pack()
    
    def _create_system_info_section(self, parent):
        """Create system information section"""
        section = ctk.CTkFrame(
            parent,
            fg_color=COLORS['dashboard_card'],
            corner_radius=RADIUS['medium']
        )
        section.pack(fill="x")
        
        # Section header
        header = ctk.CTkLabel(
            section,
            text="System Information",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary'],
            anchor="w"
        )
        header.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['md']))
        
        # Info rows
        info_items = [
            ("Hostname", socket.gethostname()),
            ("Operating System", f"{platform.system()} {platform.release()}"),
            ("Architecture", platform.machine()),
            ("Python Version", platform.python_version())
        ]
        
        for label_text, value_text in info_items:
            item_frame = ctk.CTkFrame(section, fg_color="transparent")
            item_frame.pack(fill="x", padx=SPACING['lg'], pady=SPACING['xs'])
            
            label = ctk.CTkLabel(
                item_frame,
                text=label_text + ":",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_secondary'],
                anchor="w"
            )
            label.pack(side="left", fill="x", expand=True)
            
            value = ctk.CTkLabel(
                item_frame,
                text=value_text,
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_primary'],
                anchor="e"
            )
            value.pack(side="right")
        
        # Add spacing at bottom
        ctk.CTkLabel(section, text="", height=SPACING['md']).pack()
