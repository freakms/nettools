"""
Dashboard UI Module - Redesigned
Clean, information-focused dashboard with network interface details
"""

import customtkinter as ctk
import socket
import platform
import subprocess
import re
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
    
    def create_content(self, parent):
        """Create clean, informative dashboard"""
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
        
        # Stats cards row (4 cards) - Minimal colors
        stats_frame = ctk.CTkFrame(dashboard, fg_color="transparent")
        stats_frame.pack(fill="x", padx=SPACING['xxl'], pady=SPACING['lg'])
        
        # Configure grid
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
        
        # Card 1: System Info
        self._create_info_card(
            stats_frame,
            "System",
            socket.gethostname(),
            platform.system(),
            0, 0
        )
        
        # Card 2: Active Interfaces
        active_count = len([iface for iface in self.network_interfaces if iface.get('status') == 'Up'])
        self._create_info_card(
            stats_frame,
            "Active Interfaces",
            str(active_count),
            f"of {len(self.network_interfaces)} total",
            0, 1
        )
        
        # Card 3: Recent Scans
        recent_scans = len(self.app.scanner.results) if hasattr(self.app, 'scanner') else 0
        self._create_info_card(
            stats_frame,
            "Recent Scans",
            str(recent_scans),
            "results available",
            0, 2
        )
        
        # Card 4: Network Status
        status_text = "Connected" if active_count > 0 else "No Connection"
        self._create_info_card(
            stats_frame,
            "Network Status",
            status_text,
            f"{active_count} interface(s)",
            0, 3
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
    
    def _gather_network_info(self):
        """Gather network interface information using socket and platform commands"""
        self.network_interfaces = []
        
        try:
            system = platform.system()
            
            if system == "Windows":
                # Use ipconfig on Windows
                result = subprocess.run(
                    ['ipconfig', '/all'], 
                    capture_output=True, 
                    text=True,
                    encoding='utf-8',
                    errors='ignore',  # Ignore encoding errors
                    timeout=5
                )
                output = result.stdout
                self._parse_windows_interfaces(output)
            else:
                # Use ip addr on Linux/Mac
                try:
                    result = subprocess.run(['ip', 'addr'], capture_output=True, text=True, timeout=5)
                    output = result.stdout
                    self._parse_linux_interfaces(output)
                except FileNotFoundError:
                    # Fallback to ifconfig if ip command not available
                    result = subprocess.run(['ifconfig'], capture_output=True, text=True, timeout=5)
                    output = result.stdout
                    self._parse_ifconfig_interfaces(output)
        except Exception as e:
            # Fallback to basic socket info
            self._get_basic_network_info()
    
    def _parse_windows_interfaces(self, output):
        """Parse Windows ipconfig output"""
        current_interface = None
        
        for line in output.split('\n'):
            line = line.strip()
            
            if line and not line.startswith(' '):
                # New adapter
                if 'adapter' in line.lower():
                    if current_interface:
                        self.network_interfaces.append(current_interface)
                    current_interface = {
                        'name': line.split(':')[0].strip(),
                        'ipv4': 'N/A',
                        'subnet': 'N/A',
                        'mac': 'N/A',
                        'status': 'Unknown'
                    }
            elif current_interface:
                if 'IPv4 Address' in line:
                    current_interface['ipv4'] = line.split(':')[1].strip().split('(')[0].strip()
                    current_interface['status'] = 'Up'
                elif 'Subnet Mask' in line:
                    current_interface['subnet'] = line.split(':')[1].strip()
                elif 'Physical Address' in line:
                    current_interface['mac'] = line.split(':')[1].strip()
        
        if current_interface:
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
    
    def _create_info_card(self, parent, title, value, subtitle, row, col):
        """Create a clean info card without excessive colors"""
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS['dashboard_card'],
            corner_radius=RADIUS['medium'],
            border_width=1,
            border_color=("gray70", "gray30")
        )
        card.grid(row=row, column=col, padx=SPACING['sm'], pady=SPACING['sm'], sticky="nsew")
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        title_label.pack(pady=(SPACING['md'], SPACING['xs']))
        
        # Value (main info)
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text_primary']
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
            ("Interface", 0.25),
            ("IP Address", 0.25),
            ("Subnet", 0.20),
            ("MAC Address", 0.20),
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
        
        # Interface name
        name_label = ctk.CTkLabel(
            row,
            text=iface['name'][:25],  # Truncate long names
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_primary'],
            anchor="w"
        )
        name_label.pack(side="left", padx=SPACING['sm'], pady=SPACING['sm'], expand=True, fill="x")
        
        # IP Address
        ip_label = ctk.CTkLabel(
            row,
            text=iface['ipv4'],
            font=ctk.CTkFont(size=11, family="Courier New"),
            text_color=COLORS['text_primary'],
            anchor="w"
        )
        ip_label.pack(side="left", padx=SPACING['sm'], expand=True, fill="x")
        
        # Subnet
        subnet_label = ctk.CTkLabel(
            row,
            text=iface['subnet'],
            font=ctk.CTkFont(size=11, family="Courier New"),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        subnet_label.pack(side="left", padx=SPACING['sm'], expand=True, fill="x")
        
        # MAC Address
        mac_label = ctk.CTkLabel(
            row,
            text=iface['mac'],
            font=ctk.CTkFont(size=11, family="Courier New"),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        mac_label.pack(side="left", padx=SPACING['sm'], expand=True, fill="x")
        
        # Status
        status_color = COLORS['success'] if iface['status'] == 'Up' else COLORS['text_secondary']
        status_label = ctk.CTkLabel(
            row,
            text=f"● {iface['status']}",
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
