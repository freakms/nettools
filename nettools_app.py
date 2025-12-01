#!/usr/bin/env python3
"""
NetTools Suite - IPv4 Scanner & MAC Formatter
Author: Malte Schad
Version: 1.0.0

Modern desktop application for network utilities.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress
import csv
import re
import sys
from datetime import datetime
from pathlib import Path
import platform
import os
from pythonping import ping
from PIL import Image, ImageDraw
import io
import json

# Application metadata
APP_NAME = "NetTools Suite"
APP_VERSION = "1.2.1"
APP_COMPANY = "Malte Schad"

# Configure CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ScanManager:
    """Manage saved scans for comparison"""
    
    def __init__(self):
        self.history_dir = Path.home() / ".nettools"
        self.scans_file = self.history_dir / "scans.json"
        self.max_scans = 20
        self.scans = self.load_scans()
    
    def load_scans(self):
        """Load saved scans from file"""
        if not self.history_dir.exists():
            self.history_dir.mkdir(parents=True)
        
        if self.scans_file.exists():
            try:
                with open(self.scans_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return []
    
    def save_scans(self):
        """Save scans to file"""
        try:
            with open(self.scans_file, 'w', encoding='utf-8') as f:
                json.dump(self.scans, f, indent=2)
        except Exception as e:
            print(f"Could not save scans: {e}")
    
    def add_scan(self, cidr, results):
        """Add a scan result"""
        scan = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "cidr": cidr,
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "total": len(results),
                "online": sum(1 for r in results if r["status"] == "Online"),
                "offline": sum(1 for r in results if r["status"] == "Offline")
            }
        }
        
        self.scans.insert(0, scan)
        self.scans = self.scans[:self.max_scans]
        self.save_scans()
        return scan["id"]
    
    def get_scans(self, cidr=None):
        """Get saved scans, optionally filtered by CIDR"""
        if cidr:
            return [s for s in self.scans if s["cidr"] == cidr]
        return self.scans
    
    def get_scan_by_id(self, scan_id):
        """Get a specific scan by ID"""
        for scan in self.scans:
            if scan["id"] == scan_id:
                return scan
        return None
    
    def compare_scans(self, scan1_id, scan2_id):
        """Compare two scans and return differences"""
        scan1 = self.get_scan_by_id(scan1_id)
        scan2 = self.get_scan_by_id(scan2_id)
        
        if not scan1 or not scan2:
            return None
        
        # Create IP lookup dictionaries
        ips1 = {r["ip"]: r for r in scan1["results"]}
        ips2 = {r["ip"]: r for r in scan2["results"]}
        
        # Find differences
        all_ips = sorted(set(ips1.keys()) | set(ips2.keys()), key=lambda ip: tuple(map(int, ip.split('.'))))
        
        comparison = []
        for ip in all_ips:
            if ip in ips1 and ip in ips2:
                # IP exists in both scans
                if ips1[ip]["status"] == ips2[ip]["status"]:
                    comparison.append({
                        "ip": ip,
                        "change": "unchanged",
                        "scan1_status": ips1[ip]["status"],
                        "scan2_status": ips2[ip]["status"],
                        "scan1_rtt": ips1[ip].get("rtt"),
                        "scan2_rtt": ips2[ip].get("rtt")
                    })
                else:
                    comparison.append({
                        "ip": ip,
                        "change": "changed",
                        "scan1_status": ips1[ip]["status"],
                        "scan2_status": ips2[ip]["status"],
                        "scan1_rtt": ips1[ip].get("rtt"),
                        "scan2_rtt": ips2[ip].get("rtt")
                    })
            elif ip in ips2:
                # New in scan2
                comparison.append({
                    "ip": ip,
                    "change": "new",
                    "scan1_status": "N/A",
                    "scan2_status": ips2[ip]["status"],
                    "scan1_rtt": None,
                    "scan2_rtt": ips2[ip].get("rtt")
                })
            else:
                # Missing in scan2
                comparison.append({
                    "ip": ip,
                    "change": "missing",
                    "scan1_status": ips1[ip]["status"],
                    "scan2_status": "N/A",
                    "scan1_rtt": ips1[ip].get("rtt"),
                    "scan2_rtt": None
                })
        
        return {
            "scan1": scan1,
            "scan2": scan2,
            "comparison": comparison,
            "summary": {
                "new": sum(1 for c in comparison if c["change"] == "new"),
                "missing": sum(1 for c in comparison if c["change"] == "missing"),
                "changed": sum(1 for c in comparison if c["change"] == "changed"),
                "unchanged": sum(1 for c in comparison if c["change"] == "unchanged")
            }
        }


class HistoryManager:
    """Manage history of scans and MAC addresses"""
    
    def __init__(self):
        self.history_dir = Path.home() / ".nettools"
        self.history_file = self.history_dir / "history.json"
        self.max_items = 10
        self.history = self.load_history()
    
    def load_history(self):
        """Load history from file"""
        if not self.history_dir.exists():
            self.history_dir.mkdir(parents=True)
        
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {"recent_cidrs": [], "recent_macs": []}
    
    def save_history(self):
        """Save history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Could not save history: {e}")
    
    def add_cidr(self, cidr):
        """Add CIDR to history"""
        if not cidr or cidr.strip() == "":
            return
        
        cidr = cidr.strip()
        
        # Remove if already exists (to move to top)
        self.history["recent_cidrs"] = [
            item for item in self.history["recent_cidrs"]
            if item["cidr"] != cidr
        ]
        
        # Add to beginning
        self.history["recent_cidrs"].insert(0, {
            "cidr": cidr,
            "timestamp": datetime.now().isoformat(),
            "count": 1
        })
        
        # Keep only max_items
        self.history["recent_cidrs"] = self.history["recent_cidrs"][:self.max_items]
        
        self.save_history()
    
    def add_mac(self, mac):
        """Add MAC to history"""
        if not mac or mac.strip() == "":
            return
        
        mac = mac.strip().upper()
        
        # Remove if already exists
        self.history["recent_macs"] = [
            item for item in self.history["recent_macs"]
            if item["mac"] != mac
        ]
        
        # Add to beginning
        self.history["recent_macs"].insert(0, {
            "mac": mac,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only max_items
        self.history["recent_macs"] = self.history["recent_macs"][:self.max_items]
        
        self.save_history()
    
    def get_recent_cidrs(self):
        """Get list of recent CIDRs"""
        return [item["cidr"] for item in self.history["recent_cidrs"]]
    
    def get_recent_macs(self):
        """Get list of recent MACs"""
        return [item["mac"] for item in self.history["recent_macs"]]
    
    def clear_cidr_history(self):
        """Clear CIDR history"""
        self.history["recent_cidrs"] = []
        self.save_history()
    
    def clear_mac_history(self):
        """Clear MAC history"""
        self.history["recent_macs"] = []
        self.save_history()


class NetworkIcon:
    """Generate custom network icon"""
    
    @staticmethod
    def create_icon(size=256):
        """Create network topology icon"""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Colors
        fg_color = (80, 80, 80)
        bg_color = (235, 235, 235)
        device_color = (210, 210, 210)
        
        # Main router/switch box
        pad = int(size * 0.12)
        box_size = size - 2 * pad
        corner = int(box_size * 0.15)
        
        # Draw rounded rectangle for main device
        draw.rounded_rectangle(
            [pad, pad, pad + box_size, pad + box_size],
            radius=corner,
            fill=bg_color,
            outline=fg_color,
            width=3
        )
        
        # Draw monitor/screen on top
        monitor_w = int(box_size * 0.65)
        monitor_h = int(box_size * 0.32)
        mx = pad + (box_size - monitor_w) // 2
        my = pad + 2
        draw.rectangle([mx, my, mx + monitor_w, my + monitor_h], 
                      fill=device_color, outline=fg_color, width=2)
        
        # Draw stand
        stand_h = int(box_size * 0.08)
        sx = mx + (monitor_w - stand_h) // 2
        sy = my + monitor_h + 2
        draw.rectangle([sx, sy, sx + stand_h, sy + stand_h], fill=fg_color)
        
        # Draw vertical line from stand
        line_x = sx + stand_h // 2
        line_y1 = sy + stand_h
        line_y2 = line_y1 + 12
        draw.line([line_x, line_y1, line_x, line_y2], fill=fg_color, width=3)
        
        # Draw connected devices (3 squares)
        sq_size = int(box_size * 0.18)
        gap = int(box_size * 0.06)
        total_width = 3 * sq_size + 2 * gap
        start_x = line_x - total_width // 2
        sq_y = line_y2 + 10
        
        for i in range(3):
            x = start_x + i * (sq_size + gap)
            # Draw device square
            draw.rectangle([x, sq_y, x + sq_size, sq_y + sq_size],
                          fill=device_color, outline=fg_color, width=2)
            
            # Draw connection line from device to hub
            center_x = x + sq_size // 2
            draw.line([center_x, sq_y, center_x, sq_y - 10], 
                     fill=fg_color, width=2)
            draw.line([line_x, line_y2 + 1, center_x, sq_y - 10],
                     fill=fg_color, width=2)
        
        return img


class IPScanner:
    """IPv4 Network Scanner with CIDR support"""
    
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
    
    def ping_host(self, ip, timeout_ms):
        """Ping a single host and return result"""
        try:
            response = ping(ip, timeout=timeout_ms/1000, count=1, verbose=False)
            
            if response.success():
                rtt = response.rtt_avg_ms
                return {
                    'ip': ip,
                    'status': 'Online',
                    'rtt': f"{rtt:.1f}" if rtt else "N/A"
                }
            else:
                return {
                    'ip': ip,
                    'status': 'No Response',
                    'rtt': ''
                }
        except Exception:
            return {
                'ip': ip,
                'status': 'No Response',
                'rtt': ''
            }
    
    def scan_network(self, cidr, aggression='Medium', max_workers=None):
        """Scan network with specified parameters"""
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
                future_to_ip = {executor.submit(self.ping_host, ip, timeout_ms): ip 
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
    
    def cancel_scan(self):
        """Cancel ongoing scan"""
        self.cancel_flag = True


class OUILookup:
    """OUI Vendor Lookup"""
    
    _database = None
    
    @classmethod
    def load_database(cls):
        """Load OUI database from file"""
        if cls._database is not None:
            return cls._database
        
        try:
            # Handle both development and PyInstaller bundled environments
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                bundle_dir = Path(sys._MEIPASS)
            else:
                # Running as script
                bundle_dir = Path(__file__).parent
            
            db_path = bundle_dir / "oui_database.json"
            
            if db_path.exists():
                with open(db_path, 'r', encoding='utf-8') as f:
                    cls._database = json.load(f)
            else:
                print(f"OUI database not found at: {db_path}")
                cls._database = {}
        except Exception as e:
            print(f"Could not load OUI database: {e}")
            cls._database = {}
        
        return cls._database
    
    @classmethod
    def lookup_vendor(cls, mac):
        """Lookup vendor from MAC address"""
        if cls._database is None:
            cls.load_database()
        
        # Extract OUI (first 3 bytes)
        # MAC can be in any format, so we normalize it first
        hex_only = re.sub(r'[^0-9A-Fa-f]', '', mac).upper()
        
        if len(hex_only) < 6:
            return "Unknown"
        
        # Format as XX:XX:XX
        oui = ':'.join([hex_only[i:i+2] for i in range(0, 6, 2)])
        
        return cls._database.get(oui, "Unknown Vendor")


class MACFormatter:
    """MAC Address Formatter"""
    
    @staticmethod
    def validate_mac(mac_input):
        """Validate MAC address input"""
        # Check for invalid characters first
        if re.search(r'[^0-9A-Fa-f:\-\s]', mac_input):
            return None, "Invalid characters! Allowed: 0-9, A-F, '-', ':', and spaces"
        
        # Remove valid separators and spaces
        hex_only = re.sub(r'[^0-9A-Fa-f]', '', mac_input)
        
        if len(hex_only) != 12:
            return None, f"Invalid MAC: {len(hex_only)} hex characters (expected: 12)"
        
        return hex_only.upper(), None
    
    @staticmethod
    def format_mac(hex_mac):
        """Format MAC address in different styles"""
        formats = {
            'plain': hex_mac,
            'colon': ':'.join([hex_mac[i:i+2] for i in range(0, 12, 2)]),
            'dash_4': '-'.join([hex_mac[i:i+4] for i in range(0, 12, 4)]),
            'dash_2': '-'.join([hex_mac[i:i+2] for i in range(0, 12, 2)])
        }
        return formats
    
    @staticmethod
    def generate_switch_commands(formats):
        """Generate vendor-specific switch commands"""
        commands = {
            'EXTREME': f"show fdb {formats['colon']}",
            'Huawei': f"display mac-address {formats['dash_4']}",
            'Huawei Access-User': f"display access-user mac-address {formats['dash_4']}",
            'Dell': f"show mac address-table address {formats['colon']}"
        }
        return commands


class NetToolsApp(ctk.CTk):
    """Main Application Window"""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title(f"{APP_NAME} - {APP_COMPANY}")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Set icon
        try:
            icon_img = NetworkIcon.create_icon(256)
            # Save temporarily for tkinter
            icon_path = Path("temp_icon.png")
            icon_img.save(icon_path)
            self.iconphoto(True, ctk.CTkImage(light_image=icon_img, size=(32, 32))._light_image)
            if icon_path.exists():
                icon_path.unlink()
        except Exception:
            pass
        
        # Initialize scanner
        self.scanner = IPScanner()
        self.scan_thread = None
        
        # Initialize history manager
        self.history = HistoryManager()
        
        # Initialize scan manager
        self.scan_manager = ScanManager()
        
        # Load OUI database
        self.oui_database = self.load_oui_database()
        
        # Base window size for scaling calculations
        self.base_width = 1200
        self.base_height = 800
        self.current_scale = 1.0
        
        # Store font references for scaling
        self.base_font_size = 11
        self.title_font_size = 24
        self.subtitle_font_size = 12
        self.label_font_size = 12
        
        # Create UI
        self.create_sidebar()
        self.create_main_content()
        self.create_status_bar()
        
        # Bind keyboard shortcuts
        self.bind('<Return>', self.on_enter_key)
        self.bind('<Control-e>', self.export_csv)
        
        # Bind window resize for auto-scaling
        self.bind('<Configure>', self.on_window_resize)
    
    def load_oui_database(self):
        """Load OUI database from JSON file"""
        try:
            # Handle both development and PyInstaller bundled environments
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                bundle_dir = Path(sys._MEIPASS)
            else:
                # Running as script
                bundle_dir = Path(__file__).parent
            
            oui_path = bundle_dir / "oui_database.json"
            
            if oui_path.exists():
                with open(oui_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"OUI database not found at: {oui_path}")
        except Exception as e:
            print(f"Could not load OUI database: {e}")
        return {}
    
    def lookup_vendor(self, mac_address):
        """Lookup vendor from MAC address OUI"""
        if not mac_address or len(mac_address) < 8:
            return "Unknown"
        
        # Extract OUI (first 3 octets) and normalize format
        # Handle different MAC formats
        cleaned_mac = mac_address.replace(':', '').replace('-', '').replace('.', '').upper()
        
        if len(cleaned_mac) >= 6:
            # Format as XX:XX:XX for lookup
            oui = f"{cleaned_mac[0:2]}:{cleaned_mac[2:4]}:{cleaned_mac[4:6]}"
            vendor = self.oui_database.get(oui, "Unknown Vendor")
            return vendor
        
        return "Unknown"
        
    def create_sidebar(self):
        """Create modern sidebar navigation"""
        # Sidebar frame
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)
        
        # Logo/Title section
        logo_frame = ctk.CTkFrame(self.sidebar, height=100, corner_radius=0, fg_color="transparent")
        logo_frame.pack(fill="x", padx=0, pady=0)
        logo_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            logo_frame,
            text="NetTools",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(padx=20, pady=(25, 5))
        
        subtitle_label = ctk.CTkLabel(
            logo_frame,
            text="Professional Suite",
            font=ctk.CTkFont(size=13)
        )
        subtitle_label.pack(padx=20, pady=(0, 10))
        
        # Separator
        separator = ctk.CTkFrame(self.sidebar, height=2, corner_radius=0)
        separator.pack(fill="x", padx=10, pady=10)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("scanner", "🔍  IPv4 Scanner", "Scan network for active hosts"),
            ("mac", "🏷️  MAC Formatter", "Format and analyze MAC addresses"),
            ("compare", "📊  Scan Comparison", "Compare network scan results"),
        ]
        
        self.current_page = "scanner"
        
        for page_id, label, tooltip in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                command=lambda p=page_id: self.switch_page(p),
                height=50,
                corner_radius=8,
                anchor="w",
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30")
            )
            btn.pack(fill="x", padx=10, pady=5)
            self.nav_buttons[page_id] = btn
        
        # Update initial button state
        self.nav_buttons["scanner"].configure(fg_color=("gray75", "gray25"))
        
        # Spacer to push theme selector to bottom
        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)
        
        # Theme selector at bottom
        theme_frame = ctk.CTkFrame(self.sidebar, corner_radius=0, fg_color="transparent")
        theme_frame.pack(fill="x", padx=10, pady=20)
        
        theme_label = ctk.CTkLabel(theme_frame, text="Theme", font=ctk.CTkFont(size=12))
        theme_label.pack(pady=(0, 5))
        
        self.theme_selector = ctk.CTkOptionMenu(
            theme_frame,
            values=["Dark", "Light"],
            command=self.change_theme,
            width=220,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=13)
        )
        self.theme_selector.pack()
        self.theme_selector.set("Dark")
    
    def switch_page(self, page_id):
        """Switch between pages with smooth transition"""
        if page_id == self.current_page:
            return
        
        # Update button states
        for btn_id, btn in self.nav_buttons.items():
            if btn_id == page_id:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")
        
        # Hide all pages
        for page in self.pages.values():
            page.pack_forget()
        
        # Show selected page
        self.pages[page_id].pack(fill="both", expand=True, padx=0, pady=0)
        self.current_page = page_id
        
        # Update status bar based on page
        if page_id == "scanner":
            self.status_label.configure(text="Ready to scan network")
        elif page_id == "mac":
            self.status_label.configure(text="Ready to format MAC address")
        elif page_id == "compare":
            self.status_label.configure(text="Compare network scans")
    
    def create_main_content(self):
        """Create main content area with pages"""
        # Main content frame
        self.main_content = ctk.CTkFrame(self, corner_radius=0)
        self.main_content.pack(side="right", fill="both", expand=True, padx=0, pady=0)
        
        # Create pages dictionary
        self.pages = {}
        
        # Create scanner page
        self.pages["scanner"] = ctk.CTkFrame(self.main_content, corner_radius=0)
        self.create_scanner_content(self.pages["scanner"])
        
        # Create MAC formatter page
        self.pages["mac"] = ctk.CTkFrame(self.main_content, corner_radius=0)
        self.create_mac_content(self.pages["mac"])
        
        # Create comparison page
        self.pages["compare"] = ctk.CTkFrame(self.main_content, corner_radius=0)
    
    def create_scanner_content(self, parent):
        """Create IPv4 Scanner page content"""
        # Input section
        input_frame = ctk.CTkFrame(parent)
        input_frame.pack(fill="x", padx=15, pady=15)
        
        # CIDR input
        cidr_label = ctk.CTkLabel(input_frame, text="IPv4 / CIDR:", font=ctk.CTkFont(size=12))
        cidr_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.cidr_entry = ctk.CTkEntry(input_frame, placeholder_text="e.g., 192.168.1.0/24")
        self.cidr_entry.grid(row=0, column=1, padx=(15, 5), pady=15, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)
        self.cidr_entry.bind('<KeyRelease>', self.update_host_count)
        
        # History button for CIDR
        self.cidr_history_btn = ctk.CTkButton(
            input_frame,
            text="⏱",
            width=35,
            command=self.show_cidr_history,
            font=ctk.CTkFont(size=16)
        )
        self.cidr_history_btn.grid(row=0, column=2, padx=(0, 15), pady=15)
        
        self.host_count_label = ctk.CTkLabel(input_frame, text="", font=ctk.CTkFont(size=11))
        self.host_count_label.grid(row=0, column=3, padx=15, pady=15, sticky="w")
        
        # Aggression selector
        aggro_label = ctk.CTkLabel(input_frame, text="Aggressiveness:", font=ctk.CTkFont(size=12))
        aggro_label.grid(row=1, column=0, padx=15, pady=15, sticky="w")
        
        self.aggro_selector = ctk.CTkOptionMenu(
            input_frame,
            values=["Gentle (longer timeout)", "Medium", "Aggressive (short timeout)"]
        )
        self.aggro_selector.set("Medium")
        self.aggro_selector.grid(row=1, column=1, padx=15, pady=15, sticky="ew")
        
        # Scan buttons
        button_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        button_frame.grid(row=0, column=3, rowspan=2, padx=15, pady=15, sticky="e")
        input_frame.grid_columnconfigure(3, weight=1)
        
        self.start_scan_btn = ctk.CTkButton(
            button_frame,
            text="Start Scan",
            command=self.start_scan,
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.start_scan_btn.pack(side="left", padx=5)
        
        self.cancel_scan_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel_scan,
            width=100,
            height=35,
            state="disabled",
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        self.cancel_scan_btn.pack(side="left", padx=5)
        
        # Options section
        options_frame = ctk.CTkFrame(parent)
        options_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.only_responding_check = ctk.CTkCheckBox(
            options_frame,
            text="Show only responding hosts",
            command=self.filter_results
        )
        self.only_responding_check.select()  # Check by default
        self.only_responding_check.pack(side="left", padx=15, pady=15)
        
        self.show_all_btn = ctk.CTkButton(
            options_frame,
            text="Show All Addresses",
            command=self.show_all_addresses,
            width=160
        )
        self.show_all_btn.pack(side="left", padx=(10, 15), pady=15)
        
        self.export_btn = ctk.CTkButton(
            options_frame,
            text="Export as CSV (Ctrl+E)",
            command=self.export_csv,
            width=200,
            state="disabled"
        )
        self.export_btn.pack(side="right", padx=15, pady=15)
        
        self.compare_btn = ctk.CTkButton(
            options_frame,
            text="Compare Scans",
            command=self.show_scan_comparison,
            width=160,
            state="disabled"
        )
        self.compare_btn.pack(side="right", padx=(0, 10), pady=15)
        
        # Results section
        results_frame = ctk.CTkFrame(parent)
        results_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Results header
        header_frame = ctk.CTkFrame(results_frame, height=40)
        header_frame.pack(fill="x", padx=2, pady=2)
        header_frame.pack_propagate(False)
        
        headers = [("●", 50), ("IP Address", 250), ("Status", 200), ("Response (ms)", 150)]
        for text, width in headers:
            label = ctk.CTkLabel(
                header_frame,
                text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=width
            )
            label.pack(side="left", padx=5, pady=5)
        
        # Scrollable results
        self.results_scrollable = ctk.CTkScrollableFrame(results_frame)
        self.results_scrollable.pack(fill="both", expand=True, padx=2, pady=(0, 2))
        
        self.result_rows = []
    
    def create_mac_content(self, parent):
        """Create MAC Formatter page content"""
        # Input section (stays at top, not scrollable)
        input_frame = ctk.CTkFrame(parent)
        input_frame.pack(fill="x", padx=15, pady=15)
        
        mac_label = ctk.CTkLabel(
            input_frame,
            text="Enter MAC Address:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        mac_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Frame for MAC entry and history button
        mac_entry_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        mac_entry_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        self.mac_entry = ctk.CTkEntry(
            mac_entry_frame,
            placeholder_text="e.g., AA:BB:CC:DD:EE:FF or AABBCCDDEEFF",
            height=40
        )
        self.mac_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.mac_entry.bind('<KeyRelease>', self.update_mac_formats)
        
        # History button for MAC
        self.mac_history_btn = ctk.CTkButton(
            mac_entry_frame,
            text="⏱",
            width=40,
            height=40,
            command=self.show_mac_history,
            font=ctk.CTkFont(size=16)
        )
        self.mac_history_btn.pack(side="left")
        
        self.mac_warning_label = ctk.CTkLabel(
            input_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#dc3545"
        )
        self.mac_warning_label.pack(anchor="w", padx=15, pady=(0, 5))
        
        # Vendor information display
        self.vendor_label = ctk.CTkLabel(
            input_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#28a745"
        )
        self.vendor_label.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Scrollable content area for formats and commands
        self.mac_scrollable = ctk.CTkScrollableFrame(parent)
        self.mac_scrollable.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # MAC Formats section (inside scrollable area)
        self.formats_frame = ctk.CTkFrame(self.mac_scrollable)
        self.formats_frame.pack(fill="x", padx=5, pady=(10, 15))
        
        formats_title = ctk.CTkLabel(
            self.formats_frame,
            text="Standard MAC Formats",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        formats_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        format_labels = [
            "Format 1 (Plain):",
            "Format 2 (Colon):",
            "Format 3 (Dash-4):",
            "Format 4 (Dash-2):"
        ]
        
        self.format_entries = []
        for label_text in format_labels:
            row_frame = ctk.CTkFrame(self.formats_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=15, pady=4)
            
            label = ctk.CTkLabel(row_frame, text=label_text, width=150, anchor="w")
            label.pack(side="left", padx=(0, 10))
            
            entry = ctk.CTkEntry(row_frame, height=32)
            entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=2)
            entry.configure(state="readonly")
            self.format_entries.append(entry)
            
            copy_btn = ctk.CTkButton(
                row_frame,
                text="Copy",
                width=80,
                command=lambda e=entry: self.copy_to_clipboard(e)
            )
            copy_btn.pack(side="left")
        
        self.formats_frame.pack_configure(pady=(0, 10))
        
        # Switch Commands section (inside scrollable area)
        self.commands_frame = ctk.CTkFrame(self.mac_scrollable)
        self.commands_frame.pack(fill="x", padx=5, pady=(0, 15))
        
        commands_title = ctk.CTkLabel(
            self.commands_frame,
            text="Switch Commands",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        commands_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        command_labels = [
            "EXTREME CLI:",
            "Huawei CLI:",
            "Huawei Access-User CLI:",
            "Dell CLI:"
        ]
        
        self.command_textboxes = []
        for label_text in command_labels:
            row_frame = ctk.CTkFrame(self.commands_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=15, pady=4)
            
            label = ctk.CTkLabel(row_frame, text=label_text, width=200, anchor="w")
            label.pack(side="left", padx=(0, 10))
            
            textbox = ctk.CTkTextbox(row_frame, height=35, wrap="word")
            textbox.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=2)
            textbox.configure(state="disabled")
            self.command_textboxes.append(textbox)
            
            copy_btn = ctk.CTkButton(
                row_frame,
                text="Copy",
                width=80,
                command=lambda tb=textbox: self.copy_textbox_to_clipboard(tb)
            )
            copy_btn.pack(side="left")
        
        self.commands_visible = True
    
    def create_comparison_content(self, parent):
        """Create Scan Comparison page content"""
        # Title
        title_label = ctk.CTkLabel(
            parent,
            text="Network Scan Comparison",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(padx=20, pady=(20, 10))
        
        # Description
        desc_label = ctk.CTkLabel(
            parent,
            text="Compare two network scans to see what devices have appeared, disappeared, or changed status.",
            font=ctk.CTkFont(size=12)
        )
        desc_label.pack(padx=20, pady=(0, 20))
        
        # Comparison button
        compare_btn = ctk.CTkButton(
            parent,
            text="Open Scan Comparison Tool",
            command=self.show_scan_comparison,
            width=250,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        compare_btn.pack(pady=20)
        self.create_comparison_content(self.pages["compare"])
        
        # Show initial page (scanner)
        self.pages["scanner"].pack(fill="both", expand=True, padx=0, pady=0)
    def create_tabs(self):
        """Create tabbed interface"""
        self.tabview = ctk.CTkTabview(self, command=self.on_tab_change)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        self.tab_scanner = self.tabview.add("IPv4 Scanner")
        self.tab_mac = self.tabview.add("MAC Formatter")
        
        # Create tab content
        self.create_scanner_tab()
        self.create_mac_tab()
    
    def create_scanner_tab(self):
        """Create IPv4 Scanner tab"""
        # Input section
        input_frame = ctk.CTkFrame(self.tab_scanner)
        input_frame.pack(fill="x", padx=15, pady=15)
        
        # CIDR input
        cidr_label = ctk.CTkLabel(input_frame, text="IPv4 / CIDR:", font=ctk.CTkFont(size=12))
        cidr_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.cidr_entry = ctk.CTkEntry(input_frame, placeholder_text="e.g., 192.168.1.0/24")
        self.cidr_entry.grid(row=0, column=1, padx=(15, 5), pady=15, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)
        self.cidr_entry.bind('<KeyRelease>', self.update_host_count)
        
        # History button for CIDR
        self.cidr_history_btn = ctk.CTkButton(
            input_frame,
            text="⏱",
            width=35,
            command=self.show_cidr_history,
            font=ctk.CTkFont(size=16)
        )
        self.cidr_history_btn.grid(row=0, column=2, padx=(0, 15), pady=15)
        
        self.host_count_label = ctk.CTkLabel(input_frame, text="", font=ctk.CTkFont(size=11))
        self.host_count_label.grid(row=0, column=3, padx=15, pady=15, sticky="w")
        
        # Aggression selector
        aggro_label = ctk.CTkLabel(input_frame, text="Aggressiveness:", font=ctk.CTkFont(size=12))
        aggro_label.grid(row=1, column=0, padx=15, pady=15, sticky="w")
        
        self.aggro_selector = ctk.CTkOptionMenu(
            input_frame,
            values=["Gentle (longer timeout)", "Medium", "Aggressive (short timeout)"]
        )
        self.aggro_selector.set("Medium")
        self.aggro_selector.grid(row=1, column=1, padx=15, pady=15, sticky="ew")
        
        # Scan buttons
        button_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        button_frame.grid(row=0, column=3, rowspan=2, padx=15, pady=15, sticky="e")
        input_frame.grid_columnconfigure(3, weight=1)
        
        self.start_scan_btn = ctk.CTkButton(
            button_frame,
            text="Start Scan",
            command=self.start_scan,
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.start_scan_btn.pack(side="left", padx=5)
        
        self.cancel_scan_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel_scan,
            width=100,
            height=35,
            state="disabled",
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        self.cancel_scan_btn.pack(side="left", padx=5)
        
        # Options section
        options_frame = ctk.CTkFrame(self.tab_scanner)
        options_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.only_responding_check = ctk.CTkCheckBox(
            options_frame,
            text="Show only responding hosts",
            command=self.filter_results
        )
        self.only_responding_check.select()  # Check by default
        self.only_responding_check.pack(side="left", padx=15, pady=15)
        
        self.show_all_btn = ctk.CTkButton(
            options_frame,
            text="Show All Addresses",
            command=self.show_all_addresses,
            width=160
        )
        self.show_all_btn.pack(side="left", padx=(10, 15), pady=15)
        
        self.export_btn = ctk.CTkButton(
            options_frame,
            text="Export as CSV (Ctrl+E)",
            command=self.export_csv,
            width=200,
            state="disabled"
        )
        self.export_btn.pack(side="right", padx=15, pady=15)
        
        self.compare_btn = ctk.CTkButton(
            options_frame,
            text="Compare Scans",
            command=self.show_scan_comparison,
            width=160,
            state="disabled"
        )
        self.compare_btn.pack(side="right", padx=(0, 10), pady=15)
        
        # Results section
        results_frame = ctk.CTkFrame(self.tab_scanner)
        results_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Results header
        header_frame = ctk.CTkFrame(results_frame, height=40)
        header_frame.pack(fill="x", padx=2, pady=2)
        header_frame.pack_propagate(False)
        
        headers = [("●", 50), ("IP Address", 250), ("Status", 200), ("Response (ms)", 150)]
        for text, width in headers:
            label = ctk.CTkLabel(
                header_frame,
                text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=width
            )
            label.pack(side="left", padx=5, pady=5)
        
        # Scrollable results
        self.results_scrollable = ctk.CTkScrollableFrame(results_frame)
        self.results_scrollable.pack(fill="both", expand=True, padx=2, pady=(0, 2))
        
        self.result_rows = []
    
    def create_mac_tab(self):
        """Create MAC Formatter tab"""
        # Input section (stays at top, not scrollable)
        input_frame = ctk.CTkFrame(self.tab_mac)
        input_frame.pack(fill="x", padx=15, pady=15)
        
        mac_label = ctk.CTkLabel(
            input_frame,
            text="Enter MAC Address:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        mac_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Frame for MAC entry and history button
        mac_entry_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        mac_entry_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        self.mac_entry = ctk.CTkEntry(
            mac_entry_frame,
            placeholder_text="e.g., AA:BB:CC:DD:EE:FF or AABBCCDDEEFF",
            height=40
        )
        self.mac_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.mac_entry.bind('<KeyRelease>', self.update_mac_formats)
        
        # History button for MAC
        self.mac_history_btn = ctk.CTkButton(
            mac_entry_frame,
            text="⏱",
            width=40,
            height=40,
            command=self.show_mac_history,
            font=ctk.CTkFont(size=16)
        )
        self.mac_history_btn.pack(side="left")
        
        self.mac_warning_label = ctk.CTkLabel(
            input_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#dc3545"
        )
        self.mac_warning_label.pack(anchor="w", padx=15, pady=(0, 5))
        
        # Vendor information display
        self.vendor_label = ctk.CTkLabel(
            input_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#28a745"
        )
        self.vendor_label.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Scrollable content area for formats and commands
        self.mac_scrollable = ctk.CTkScrollableFrame(self.tab_mac)
        self.mac_scrollable.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # MAC Formats section (inside scrollable area)
        self.formats_frame = ctk.CTkFrame(self.mac_scrollable)
        self.formats_frame.pack(fill="x", padx=5, pady=(10, 15))
        
        formats_title = ctk.CTkLabel(
            self.formats_frame,
            text="Standard MAC Formats",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        formats_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        format_labels = [
            "Format 1 (Plain):",
            "Format 2 (Colon):",
            "Format 3 (Dash-4):",
            "Format 4 (Dash-2):"
        ]
        
        self.format_entries = []
        for label_text in format_labels:
            row_frame = ctk.CTkFrame(self.formats_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=15, pady=4)
            
            label = ctk.CTkLabel(row_frame, text=label_text, width=150, anchor="w")
            label.pack(side="left", padx=(0, 10))
            
            entry = ctk.CTkEntry(row_frame, height=32)
            entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=2)
            entry.configure(state="readonly")
            self.format_entries.append(entry)
            
            copy_btn = ctk.CTkButton(
                row_frame,
                text="Copy",
                width=80,
                command=lambda e=entry: self.copy_to_clipboard(e)
            )
            copy_btn.pack(side="left")
        
        self.formats_frame.pack_configure(pady=(0, 10))
        
        # Switch Commands section (inside scrollable area)
        self.commands_frame = ctk.CTkFrame(self.mac_scrollable)
        self.commands_frame.pack(fill="x", padx=5, pady=(0, 15))
        
        commands_title = ctk.CTkLabel(
            self.commands_frame,
            text="Switch Commands",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        commands_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        command_labels = [
            "EXTREME CLI:",
            "Huawei CLI:",
            "Huawei Access-User CLI:",
            "Dell CLI:"
        ]
        
        self.command_textboxes = []
        for label_text in command_labels:
            row_frame = ctk.CTkFrame(self.commands_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=15, pady=4)
            
            label = ctk.CTkLabel(row_frame, text=label_text, width=200, anchor="w")
            label.pack(side="left", padx=(0, 10))
            
            textbox = ctk.CTkTextbox(row_frame, height=35, wrap="word")
            textbox.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=2)
            textbox.configure(state="disabled")
            self.command_textboxes.append(textbox)
            
            copy_btn = ctk.CTkButton(
                row_frame,
                text="Copy",
                width=80,
                command=lambda tb=textbox: self.copy_textbox_to_clipboard(tb)
            )
            copy_btn.pack(side="left")
        
        self.commands_visible = True
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = ctk.CTkFrame(self, height=35, corner_radius=0)
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready.",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(side="left", padx=15, pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=200)
        self.progress_bar.pack(side="left", padx=15, pady=5)
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()  # Hide initially
        
        copyright_label = ctk.CTkLabel(
            status_frame,
            text=f"© {APP_COMPANY}",
            font=ctk.CTkFont(size=10)
        )
        copyright_label.pack(side="right", padx=15, pady=5)
    
    def change_theme(self, theme):
        """Change application theme"""
        ctk.set_appearance_mode(theme)
    
    def update_host_count(self, event=None):
        """Update host count label based on CIDR input"""
        cidr = self.cidr_entry.get().strip()
        if not cidr:
            self.host_count_label.configure(text="")
            return
        
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            if network.prefixlen >= 31:
                count = 2 if network.prefixlen == 31 else 1
            else:
                count = network.num_addresses - 2  # Exclude network and broadcast
            self.host_count_label.configure(text=f"Hosts in range: {count:,}")
        except ValueError:
            self.host_count_label.configure(text="")
    
    def start_scan(self):
        """Start network scan"""
        cidr = self.cidr_entry.get().strip()
        
        if not cidr:
            messagebox.showinfo(
                "Information",
                "Please enter an IPv4 address in CIDR format."
            )
            return
        
        # Check for large scans
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            if network.prefixlen < 20:  # /19 or larger
                host_count = network.num_addresses - 2 if network.prefixlen < 31 else network.num_addresses
                answer = messagebox.askyesno(
                    "Large Scan Warning",
                    f"This range contains {host_count:,} hosts. The scan may take a long time. Continue?"
                )
                if not answer:
                    return
        except ValueError:
            pass
        
        # Save to history
        self.history.add_cidr(cidr)
        
        # Clear previous results
        for row in self.result_rows:
            row.destroy()
        self.result_rows = []
        
        # Update UI
        self.start_scan_btn.configure(state="disabled")
        self.cancel_scan_btn.configure(state="normal")
        self.export_btn.configure(state="disabled")
        self.progress_bar.pack(side="left", padx=15, pady=5)
        self.progress_bar.set(0)
        
        # Set callbacks
        self.scanner.progress_callback = self.on_scan_progress
        self.scanner.complete_callback = self.on_scan_complete
        
        # Start scan in thread
        aggression = self.aggro_selector.get()
        self.scan_thread = threading.Thread(
            target=self.scanner.scan_network,
            args=(cidr, aggression),
            daemon=True
        )
        self.scan_thread.start()
        
        self.status_label.configure(text="Scan running...")
    
    def cancel_scan(self):
        """Cancel ongoing scan"""
        self.scanner.cancel_scan()
        self.status_label.configure(text="Cancelling scan...")
        self.cancel_scan_btn.configure(state="disabled")
    
    def on_scan_progress(self, completed, total, result):
        """Handle scan progress update"""
        self.after(0, self._update_scan_progress, completed, total, result)
    
    def _update_scan_progress(self, completed, total, result):
        """Update scan progress in main thread"""
        # Update progress bar
        progress = completed / total if total > 0 else 0
        self.progress_bar.set(progress)
        self.status_label.configure(text=f"Scan running... ({completed} / {total})")
        
        # Add result row
        self.add_result_row(result)
    
    def on_scan_complete(self, results, message):
        """Handle scan completion"""
        self.after(0, self._finalize_scan, results, message)
    
    def _finalize_scan(self, results, message):
        """Finalize scan in main thread"""
        self.start_scan_btn.configure(state="normal")
        self.cancel_scan_btn.configure(state="disabled")
        
        if len(results) > 0:
            self.export_btn.configure(state="normal")
            self.compare_btn.configure(state="normal")
            
            # Save scan for comparison
            cidr = self.cidr_entry.get().strip()
            scan_id = self.scan_manager.add_scan(cidr, results)
            self.status_label.configure(text=f"{message} (Saved as {scan_id})")
        else:
            self.status_label.configure(text=message)
        
        self.filter_results()
    
    def add_result_row(self, result):
        """Add a result row to the display"""
        row_frame = ctk.CTkFrame(self.results_scrollable, height=35)
        row_frame.pack(fill="x", padx=2, pady=1)
        row_frame.pack_propagate(False)
        
        # Status dot
        status_color = "#4CAF50" if result['status'] == 'Online' else "#8C8C8C"
        dot_label = ctk.CTkLabel(
            row_frame,
            text="●",
            font=ctk.CTkFont(size=16),
            text_color=status_color,
            width=50
        )
        dot_label.pack(side="left", padx=5)
        
        # IP Address
        ip_label = ctk.CTkLabel(row_frame, text=result['ip'], width=250, anchor="w")
        ip_label.pack(side="left", padx=5)
        
        # Status
        status_label = ctk.CTkLabel(row_frame, text=result['status'], width=200, anchor="w")
        status_label.pack(side="left", padx=5)
        
        # RTT
        rtt_label = ctk.CTkLabel(row_frame, text=result['rtt'], width=150, anchor="w")
        rtt_label.pack(side="left", padx=5)
        
        # Store reference
        row_frame.result_data = result
        self.result_rows.append(row_frame)
    
    def filter_results(self, event=None):
        """Filter displayed results"""
        only_responding = self.only_responding_check.get()
        
        for row in self.result_rows:
            if only_responding and row.result_data['status'] != 'Online':
                row.pack_forget()
            else:
                row.pack(fill="x", padx=2, pady=1)
    
    def show_all_addresses(self):
        """Show all addresses (uncheck the filter)"""
        self.only_responding_check.deselect()
        self.filter_results()
    
    def export_csv(self, event=None):
        """Export results to CSV"""
        if not self.scanner.results:
            messagebox.showinfo("Information", "No data to export.")
            return
        
        # Get desktop path
        desktop = Path.home() / "Desktop"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"NetToolsScan_{timestamp}.csv"
        default_path = desktop / default_filename
        
        # Ask for save location
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=desktop,
            initialfile=default_filename
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['ip', 'status', 'rtt'])
                writer.writeheader()
                writer.writerows(self.scanner.results)
            
            messagebox.showinfo(
                "Export Successful",
                f"CSV successfully exported to:\n{filepath}"
            )
        except Exception as e:
            messagebox.showerror(
                "Export Error",
                f"Error exporting CSV: {str(e)}"
            )
    
    def update_mac_formats(self, event=None):
        """Update MAC address formats"""
        mac_input = self.mac_entry.get()
        
        if not mac_input:
            self.mac_warning_label.configure(text="")
            self.vendor_label.configure(text="")
            for entry in self.format_entries:
                entry.configure(state="normal")
                entry.delete(0, 'end')
                entry.configure(state="readonly")
            for textbox in self.command_textboxes:
                textbox.configure(state="normal")
                textbox.delete("1.0", 'end')
                textbox.configure(state="disabled")
            return
        
        hex_mac, error = MACFormatter.validate_mac(mac_input)
        
        if error:
            self.mac_warning_label.configure(text=error)
            self.vendor_label.configure(text="")
            for entry in self.format_entries:
                entry.configure(state="normal")
                entry.delete(0, 'end')
                entry.configure(state="readonly")
            for textbox in self.command_textboxes:
                textbox.configure(state="normal")
                textbox.delete("1.0", 'end')
                textbox.configure(state="disabled")
            return
        
        self.mac_warning_label.configure(text="")
        
        # Lookup and display vendor
        vendor = self.lookup_vendor(hex_mac)
        if vendor and vendor != "Unknown Vendor":
            self.vendor_label.configure(text=f"🏢 Vendor: {vendor}")
        else:
            self.vendor_label.configure(text="🏢 Vendor: Unknown")
        
        # Save to history (only when valid)
        self.history.add_mac(hex_mac)
        
        # Update formats
        formats = MACFormatter.format_mac(hex_mac)
        format_values = [
            formats['plain'],
            formats['colon'],
            formats['dash_4'],
            formats['dash_2']
        ]
        
        for entry, value in zip(self.format_entries, format_values):
            entry.configure(state="normal")
            entry.delete(0, 'end')
            entry.insert(0, value)
            entry.configure(state="readonly")
        
        # Update commands
        commands = MACFormatter.generate_switch_commands(formats)
        command_values = [
            commands['EXTREME'],
            commands['Huawei'],
            commands['Huawei Access-User'],
            commands['Dell']
        ]
        
        for textbox, value in zip(self.command_textboxes, command_values):
            textbox.configure(state="normal")
            textbox.delete("1.0", 'end')
            textbox.insert("1.0", value)
            
            # Auto-adjust height based on content lines
            # Count newlines in text to determine height needed
            lines = value.count('\n') + 1
            if lines > 1:
                new_height = min(35 + (lines - 1) * 20, 80)  # Max 80px height
                textbox.configure(height=new_height)
            else:
                textbox.configure(height=35)  # Single line height
            
            textbox.configure(state="disabled")
    
    def copy_to_clipboard(self, entry):
        """Copy entry content to clipboard"""
        text = entry.get()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.status_label.configure(text="Copied to clipboard!")
            self.after(2000, lambda: self.status_label.configure(text="Ready."))
    
    def copy_textbox_to_clipboard(self, textbox):
        """Copy textbox content to clipboard"""
        text = textbox.get("1.0", 'end-1c')
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.status_label.configure(text="Copied to clipboard!")
            self.after(2000, lambda: self.status_label.configure(text="Ready."))
    
    def on_window_resize(self, event):
        """Handle window resize for auto-scaling"""
        # Only process resize events for the main window
        if event.widget != self:
            return
        
        # Calculate scale factor based on window size
        new_width = event.width
        new_height = event.height
        
        # Calculate scale (min 0.75, max 1.8)
        width_scale = new_width / self.base_width
        height_scale = new_height / self.base_height
        new_scale = min(width_scale, height_scale)
        new_scale = max(0.75, min(1.8, new_scale))
        
        # Only update if scale changed significantly (avoid too many updates)
        if abs(new_scale - self.current_scale) > 0.08:
            self.current_scale = new_scale
            self.update_fonts_and_sizes()
    
    def update_fonts_and_sizes(self):
        """Update fonts and widget sizes based on current scale"""
        try:
            # Calculate scaled font sizes
            scaled_base = max(9, int(self.base_font_size * self.current_scale))
            scaled_title = max(18, int(self.title_font_size * self.current_scale))
            scaled_subtitle = max(10, int(self.subtitle_font_size * self.current_scale))
            scaled_label = max(10, int(self.label_font_size * self.current_scale))
            
            # Update header fonts
            for widget in self.winfo_children():
                self.update_widget_fonts(widget, scaled_base, scaled_label)
                
        except Exception as e:
            pass  # Silently ignore scaling errors
    
    def update_widget_fonts(self, widget, base_size, label_size):
        """Recursively update fonts for all widgets"""
        try:
            if isinstance(widget, ctk.CTkLabel):
                current_font = widget.cget("font")
                if current_font:
                    if isinstance(current_font, ctk.CTkFont):
                        if current_font.cget("size") >= 14:
                            # Large labels (titles)
                            widget.configure(font=ctk.CTkFont(size=label_size + 2, weight=current_font.cget("weight")))
                        else:
                            # Normal labels
                            widget.configure(font=ctk.CTkFont(size=label_size, weight=current_font.cget("weight")))
            elif isinstance(widget, (ctk.CTkEntry, ctk.CTkTextbox)):
                # Scale entry and textbox fonts
                widget.configure(font=ctk.CTkFont(size=base_size))
            elif isinstance(widget, ctk.CTkButton):
                # Scale button fonts
                widget.configure(font=ctk.CTkFont(size=base_size))
            
            # Recursively update children
            for child in widget.winfo_children():
                self.update_widget_fonts(child, base_size, label_size)
        except:
            pass
    
    # Old tab-based methods removed - now using sidebar navigation
    
    def show_cidr_history(self):
        """Show CIDR history dropdown"""
        recent_cidrs = self.history.get_recent_cidrs()
        
        if not recent_cidrs:
            messagebox.showinfo("History", "No recent scans in history.")
            return
        
        # Create popup window
        history_window = ctk.CTkToplevel(self)
        history_window.title("Recent Scans")
        history_window.geometry("400x350")
        history_window.transient(self)
        history_window.grab_set()
        
        # Center window
        history_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - history_window.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - history_window.winfo_height()) // 2
        history_window.geometry(f"+{x}+{y}")
        
        # Title
        title_label = ctk.CTkLabel(
            history_window,
            text="Recent Scans (Click to use)",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(padx=20, pady=(20, 10))
        
        # Scrollable frame for history items
        scroll_frame = ctk.CTkScrollableFrame(history_window)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Add each history item as a button
        for cidr in recent_cidrs:
            btn = ctk.CTkButton(
                scroll_frame,
                text=cidr,
                command=lambda c=cidr: self.select_cidr_from_history(c, history_window),
                height=35,
                anchor="w"
            )
            btn.pack(fill="x", pady=3)
        
        # Bottom buttons
        button_frame = ctk.CTkFrame(history_window, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear History",
            command=lambda: self.clear_cidr_history(history_window),
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        clear_btn.pack(side="left", padx=(0, 10))
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            command=history_window.destroy
        )
        close_btn.pack(side="left")
    
    def select_cidr_from_history(self, cidr, window):
        """Select CIDR from history"""
        self.cidr_entry.delete(0, 'end')
        self.cidr_entry.insert(0, cidr)
        self.update_host_count()
        window.destroy()
    
    def clear_cidr_history(self, window):
        """Clear CIDR history"""
        result = messagebox.askyesno(
            "Clear History",
            "Are you sure you want to clear all scan history?"
        )
        if result:
            self.history.clear_cidr_history()
            window.destroy()
            messagebox.showinfo("History", "Scan history cleared.")
    
    def show_mac_history(self):
        """Show MAC history dropdown"""
        recent_macs = self.history.get_recent_macs()
        
        if not recent_macs:
            messagebox.showinfo("History", "No recent MAC addresses in history.")
            return
        
        # Create popup window
        history_window = ctk.CTkToplevel(self)
        history_window.title("Recent MAC Addresses")
        history_window.geometry("450x350")
        history_window.transient(self)
        history_window.grab_set()
        
        # Center window
        history_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - history_window.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - history_window.winfo_height()) // 2
        history_window.geometry(f"+{x}+{y}")
        
        # Title
        title_label = ctk.CTkLabel(
            history_window,
            text="Recent MAC Addresses (Click to use)",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(padx=20, pady=(20, 10))
        
        # Scrollable frame for history items
        scroll_frame = ctk.CTkScrollableFrame(history_window)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Add each history item as a button
        for mac in recent_macs:
            btn = ctk.CTkButton(
                scroll_frame,
                text=mac,
                command=lambda m=mac: self.select_mac_from_history(m, history_window),
                height=35,
                anchor="w"
            )
            btn.pack(fill="x", pady=3)
        
        # Bottom buttons
        button_frame = ctk.CTkFrame(history_window, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear History",
            command=lambda: self.clear_mac_history(history_window),
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        clear_btn.pack(side="left", padx=(0, 10))
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            command=history_window.destroy
        )
        close_btn.pack(side="left")
    
    def select_mac_from_history(self, mac, window):
        """Select MAC from history"""
        self.mac_entry.delete(0, 'end')
        self.mac_entry.insert(0, mac)
        self.update_mac_formats()
        window.destroy()
    
    def clear_mac_history(self, window):
        """Clear MAC history"""
        result = messagebox.askyesno(
            "Clear History",
            "Are you sure you want to clear all MAC history?"
        )
        if result:
            self.history.clear_mac_history()
            window.destroy()
            messagebox.showinfo("History", "MAC history cleared.")
    
    def show_scan_comparison(self):
        """Show scan comparison window"""
        scans = self.scan_manager.get_scans()
        
        if len(scans) < 2:
            messagebox.showinfo("Scan Comparison", "You need at least 2 saved scans to compare. Run more scans first.")
            return
        
        # Create comparison window
        comp_window = ctk.CTkToplevel(self)
        comp_window.title("Scan Comparison")
        comp_window.geometry("900x700")
        comp_window.transient(self)
        comp_window.grab_set()
        
        # Center window
        comp_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - comp_window.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - comp_window.winfo_height()) // 2
        comp_window.geometry(f"+{x}+{y}")
        
        # Title
        title_label = ctk.CTkLabel(
            comp_window,
            text="Compare Network Scans",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(padx=20, pady=(20, 10))
        
        # Selection frame
        select_frame = ctk.CTkFrame(comp_window)
        select_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Prepare scan options
        scan_options = [f"{s['id']} - {s['cidr']} ({s['summary']['online']}/{s['summary']['total']} online)" for s in scans]
        
        # Scan 1 selection
        scan1_label = ctk.CTkLabel(select_frame, text="Scan 1:", font=ctk.CTkFont(size=12, weight="bold"))
        scan1_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        scan1_var = ctk.StringVar(value=scan_options[0])
        scan1_menu = ctk.CTkOptionMenu(select_frame, variable=scan1_var, values=scan_options, width=400)
        scan1_menu.grid(row=0, column=1, padx=10, pady=10)
        
        # Scan 2 selection
        scan2_label = ctk.CTkLabel(select_frame, text="Scan 2:", font=ctk.CTkFont(size=12, weight="bold"))
        scan2_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        scan2_var = ctk.StringVar(value=scan_options[-1] if len(scan_options) > 1 else scan_options[0])
        scan2_menu = ctk.CTkOptionMenu(select_frame, variable=scan2_var, values=scan_options, width=400)
        scan2_menu.grid(row=1, column=1, padx=10, pady=10)
        
        # Results area
        results_frame = ctk.CTkFrame(comp_window)
        results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        results_scroll = ctk.CTkScrollableFrame(results_frame)
        results_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        results_label = ctk.CTkLabel(
            results_scroll,
            text="Select two scans and click 'Compare' to see differences",
            font=ctk.CTkFont(size=12)
        )
        results_label.pack(pady=50)
        
        def do_comparison():
            """Perform the comparison"""
            # Get selected scan IDs
            scan1_id = scan1_var.get().split(" - ")[0]
            scan2_id = scan2_var.get().split(" - ")[0]
            
            if scan1_id == scan2_id:
                messagebox.showwarning("Same Scan", "Please select two different scans to compare.")
                return
            
            # Perform comparison
            comparison_result = self.scan_manager.compare_scans(scan1_id, scan2_id)
            
            if not comparison_result:
                messagebox.showerror("Error", "Could not load scan data.")
                return
            
            # Clear results
            for widget in results_scroll.winfo_children():
                widget.destroy()
            
            # Summary
            summary_frame = ctk.CTkFrame(results_scroll)
            summary_frame.pack(fill="x", padx=5, pady=10)
            
            summary_title = ctk.CTkLabel(
                summary_frame,
                text="Summary",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            summary_title.pack(pady=(10, 5))
            
            summary = comparison_result["summary"]
            summary_text = f"✅ Unchanged: {summary['unchanged']}  |  "
            summary_text += f"🆕 New: {summary['new']}  |  "
            summary_text += f"❌ Missing: {summary['missing']}  |  "
            summary_text += f"🔄 Changed: {summary['changed']}"
            
            summary_label = ctk.CTkLabel(
                summary_frame,
                text=summary_text,
                font=ctk.CTkFont(size=12)
            )
            summary_label.pack(pady=(0, 10))
            
            # Details header
            details_header = ctk.CTkFrame(results_scroll)
            details_header.pack(fill="x", padx=5, pady=5)
            
            headers = [
                ("Change", 100),
                ("IP Address", 150),
                ("Scan 1 Status", 150),
                ("Scan 2 Status", 150),
                ("Scan 1 RTT", 120),
                ("Scan 2 RTT", 120)
            ]
            
            for text, width in headers:
                label = ctk.CTkLabel(
                    details_header,
                    text=text,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    width=width
                )
                label.pack(side="left", padx=5)
            
            # Details rows
            for item in comparison_result["comparison"]:
                # Skip unchanged if there are too many
                if item["change"] == "unchanged" and summary["unchanged"] > 50:
                    # Only show first 10 unchanged
                    continue
                
                row_frame = ctk.CTkFrame(results_scroll)
                row_frame.pack(fill="x", padx=5, pady=2)
                
                # Change indicator
                change_icons = {
                    "unchanged": "✅",
                    "new": "🆕",
                    "missing": "❌",
                    "changed": "🔄"
                }
                change_colors = {
                    "unchanged": "#4CAF50",
                    "new": "#2196F3",
                    "missing": "#dc3545",
                    "changed": "#FF9800"
                }
                
                change_label = ctk.CTkLabel(
                    row_frame,
                    text=change_icons.get(item["change"], "?"),
                    width=100,
                    text_color=change_colors.get(item["change"], "#FFFFFF")
                )
                change_label.pack(side="left", padx=5)
                
                # IP
                ip_label = ctk.CTkLabel(row_frame, text=item["ip"], width=150)
                ip_label.pack(side="left", padx=5)
                
                # Scan 1 Status
                s1_label = ctk.CTkLabel(row_frame, text=item["scan1_status"], width=150)
                s1_label.pack(side="left", padx=5)
                
                # Scan 2 Status
                s2_label = ctk.CTkLabel(row_frame, text=item["scan2_status"], width=150)
                s2_label.pack(side="left", padx=5)
                
                # Scan 1 RTT
                s1_rtt = item["scan1_rtt"] if item["scan1_rtt"] else "-"
                s1_rtt_label = ctk.CTkLabel(row_frame, text=s1_rtt, width=120)
                s1_rtt_label.pack(side="left", padx=5)
                
                # Scan 2 RTT
                s2_rtt = item["scan2_rtt"] if item["scan2_rtt"] else "-"
                s2_rtt_label = ctk.CTkLabel(row_frame, text=s2_rtt, width=120)
                s2_rtt_label.pack(side="left", padx=5)
        
        def export_comparison():
            """Export comparison to file"""
            scan1_id = scan1_var.get().split(" - ")[0]
            scan2_id = scan2_var.get().split(" - ")[0]
            
            if scan1_id == scan2_id:
                messagebox.showwarning("Same Scan", "Please select two different scans to compare.")
                return
            
            comparison_result = self.scan_manager.compare_scans(scan1_id, scan2_id)
            if not comparison_result:
                messagebox.showerror("Error", "Could not load scan data.")
                return
            
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"comparison_{scan1_id}_vs_{scan2_id}.csv"
            )
            
            if filename:
                try:
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Change', 'IP Address', 'Scan 1 Status', 'Scan 2 Status', 'Scan 1 RTT', 'Scan 2 RTT'])
                        
                        for item in comparison_result["comparison"]:
                            writer.writerow([
                                item["change"],
                                item["ip"],
                                item["scan1_status"],
                                item["scan2_status"],
                                item["scan1_rtt"] or "-",
                                item["scan2_rtt"] or "-"
                            ])
                    
                    messagebox.showinfo("Success", f"Comparison exported to:\n{filename}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not export comparison:\n{str(e)}")
        
        # Action buttons
        button_frame = ctk.CTkFrame(comp_window)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        compare_btn = ctk.CTkButton(
            button_frame,
            text="Compare",
            command=do_comparison,
            width=150
        )
        compare_btn.pack(side="left", padx=(0, 10))
        
        export_btn = ctk.CTkButton(
            button_frame,
            text="Export Comparison",
            command=export_comparison,
            width=150
        )
        export_btn.pack(side="left", padx=(0, 10))
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            command=comp_window.destroy,
            width=100
        )
        close_btn.pack(side="right")
    
    def on_enter_key(self, event):
        """Handle Enter key press"""
        if self.current_page == "scanner":
            if self.start_scan_btn.cget("state") == "normal":
                self.start_scan()
        elif self.current_page == "mac":
            if self.format_entries[0].get():
                self.copy_to_clipboard(self.format_entries[0])


if __name__ == "__main__":
    app = NetToolsApp()
    app.mainloop()
