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
import subprocess
import socket
try:
    import telnetlib
    TELNETLIB_AVAILABLE = True
except ImportError:
    TELNETLIB_AVAILABLE = False
from datetime import datetime
from pathlib import Path
import platform
import os
from pythonping import ping
from PIL import Image, ImageDraw
import io
import json
import xml.etree.ElementTree as ET

# Design system and UI components
from design_constants import COLORS, SPACING, RADIUS, FONTS, BUTTON_SIZES
from ui_components import (
    StyledCard, StyledButton, StyledEntry, SectionTitle, SubTitle,
    ResultRow, StatusBadge, SectionSeparator, LoadingSpinner, InfoBox, DataGrid
)

# phpIPAM integration
try:
    from phpipam_config import PHPIPAMConfig
    from phpipam_client import PHPIPAMClient
    PHPIPAM_AVAILABLE = True
except ImportError:
    PHPIPAM_AVAILABLE = False
    print("phpIPAM modules not found. Integration will be disabled.")

# Application metadata
APP_NAME = "NetTools Suite"
APP_VERSION = "1.11.0"
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


class NetworkProfileManager:
    """Manage network interface profiles"""
    
    def __init__(self):
        self.history_dir = Path.home() / ".nettools"
        self.profiles_file = self.history_dir / "network_profiles.json"
        self.profiles = self.load_profiles()
    
    def load_profiles(self):
        """Load saved profiles from file"""
        if not self.history_dir.exists():
            self.history_dir.mkdir(parents=True)
        
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return []
    
    def save_profiles(self):
        """Save profiles to file"""
        try:
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(self.profiles, f, indent=2)
        except Exception as e:
            print(f"Could not save profiles: {e}")
    
    def add_profile(self, name, interfaces):
        """Add a new profile"""
        profile = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "name": name,
            "interfaces": interfaces,
            "created": datetime.now().isoformat()
        }
        
        self.profiles.append(profile)
        self.save_profiles()
        return profile["id"]
    
    def delete_profile(self, profile_id):
        """Delete a profile by ID"""
        self.profiles = [p for p in self.profiles if p["id"] != profile_id]
        self.save_profiles()
    
    def get_profile(self, profile_id):
        """Get a specific profile by ID"""
        for profile in self.profiles:
            if profile["id"] == profile_id:
                return profile
        return None


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
        
        # Initialize network profile manager
        self.profile_manager = NetworkProfileManager()
        
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
        
        # Create UI (order matters: status bar must be packed before main content)
        self.create_sidebar()
        self.create_status_bar()
        self.create_main_content()
        
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
        
        # Navigation buttons (reordered for better workflow)
        self.nav_buttons = {}
        nav_items = [
            ("scanner", "🔍  IPv4 Scanner", "Scan network for active hosts"),
            ("portscan", "🔌  Port Scanner", "Scan for open ports on hosts"),
            ("traceroute", "🛣  Traceroute & Pathping", "Trace network path to host"),
            ("dns", "🌐  DNS Lookup", "Resolve hostnames and IP addresses"),
            ("mac", "🏷  MAC Formatter", "Format and analyze MAC addresses"),
            ("compare", "📊  Scan Comparison", "Compare network scan results"),
            ("profiles", "⚙  Network Profiles", "Manage network interface profiles"),
            ("subnet", "🔢  Subnet Calculator", "Calculate subnet information"),
            ("phpipam", "📡  phpIPAM", "Manage IP addresses with phpIPAM"),
        ]
        
        self.current_page = "scanner"
        
        for page_id, label, tooltip in nav_items:
            # Split emoji and text for better alignment
            parts = label.split("  ", 1)
            if len(parts) == 2:
                emoji, text = parts
                # Pad emoji to fixed width using spaces for alignment
                # Emojis are typically 2 characters wide, pad to align text
                display_text = f"{emoji}    {text}"
            else:
                display_text = label
            
            # Simple button approach - no complex layering
            btn = ctk.CTkButton(
                self.sidebar,
                text=display_text,
                command=lambda p=page_id: self.switch_page(p),
                height=50,
                corner_radius=8,
                anchor="w",
                font=ctk.CTkFont(size=14, weight="bold", family="Segoe UI"),
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
        """Switch between pages with lazy loading"""
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
        
        # Lazy load page content if not already loaded
        if page_id not in self.pages_loaded:
            if page_id not in self.pages:
                self.pages[page_id] = ctk.CTkFrame(self.main_content, corner_radius=0)
            
            # Load page content based on page_id
            if page_id == "mac":
                self.create_mac_content(self.pages[page_id])
            elif page_id == "compare":
                self.create_comparison_content(self.pages[page_id])
            elif page_id == "profiles":
                self.create_profiles_content(self.pages[page_id])
            elif page_id == "portscan":
                self.create_portscan_content(self.pages[page_id])
            elif page_id == "traceroute":
                self.create_traceroute_content(self.pages[page_id])
            elif page_id == "dns":
                self.create_dns_content(self.pages[page_id])
            elif page_id == "subnet":
                self.create_subnet_content(self.pages[page_id])
            elif page_id == "phpipam":
                self.create_phpipam_content(self.pages[page_id])
            
            self.pages_loaded[page_id] = True
        
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
        elif page_id == "profiles":
            self.status_label.configure(text="Manage network interface profiles")
        elif page_id == "portscan":
            self.status_label.configure(text="Scan for open ports on target hosts")
        elif page_id == "traceroute":
            self.status_label.configure(text="Trace network path and analyze latency to target host")
        elif page_id == "dns":
            self.status_label.configure(text="Resolve hostnames and IP addresses")
        elif page_id == "subnet":
            self.status_label.configure(text="Calculate subnet information from CIDR")
        elif page_id == "phpipam":
            self.status_label.configure(text="Manage IP addresses with phpIPAM")
    
    def create_main_content(self):
        """Create main content area with pages (lazy loading for faster startup)"""
        # Main content frame
        self.main_content = ctk.CTkFrame(self, corner_radius=0)
        self.main_content.pack(side="right", fill="both", expand=True, padx=0, pady=0)
        
        # Create pages dictionary (empty frames, content loaded on demand)
        self.pages = {}
        self.pages_loaded = {}  # Track which pages have been loaded
        
        # Pre-create only the scanner page for fast initial display
        self.pages["scanner"] = ctk.CTkFrame(self.main_content, corner_radius=0)
        self.create_scanner_content(self.pages["scanner"])
        self.pages_loaded["scanner"] = True
        
        # Show the initial page (scanner)
        self.pages["scanner"].pack(fill="both", expand=True, padx=0, pady=0)
    
    def create_scanner_content(self, parent):
        """Create IPv4 Scanner page content"""
        # Input section with styled card
        input_card = StyledCard(parent)
        input_card.pack(fill="x", padx=SPACING['lg'], pady=SPACING['lg'])
        
        # CIDR input
        cidr_label = ctk.CTkLabel(
            input_card,
            text="IPv4 / CIDR:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        cidr_label.grid(row=0, column=0, padx=SPACING['md'], pady=SPACING['md'], sticky="w")
        
        self.cidr_entry = StyledEntry(
            input_card,
            placeholder_text="e.g., 192.168.1.0/24"
        )
        self.cidr_entry.grid(row=0, column=1, padx=(SPACING['md'], SPACING['xs']), pady=SPACING['md'], sticky="ew")
        input_card.grid_columnconfigure(1, weight=1)
        self.cidr_entry.bind('<KeyRelease>', self.update_host_count)
        
        # History button for CIDR
        self.cidr_history_btn = StyledButton(
            input_card,
            text="⏱",
            size="small",
            variant="neutral",
            command=self.show_cidr_history
        )
        self.cidr_history_btn.grid(row=0, column=2, padx=(0, SPACING['md']), pady=SPACING['md'])
        
        self.host_count_label = SubTitle(
            input_card,
            text=""
        )
        self.host_count_label.grid(row=0, column=3, padx=SPACING['md'], pady=SPACING['md'], sticky="w")
        
        # Aggression selector
        aggro_label = ctk.CTkLabel(input_card, text="Aggressiveness:", font=ctk.CTkFont(size=FONTS['body']))
        aggro_label.grid(row=1, column=0, padx=SPACING['md'], pady=SPACING['md'], sticky="w")
        
        self.aggro_selector = ctk.CTkOptionMenu(
            input_card,
            values=["Gentle (longer timeout)", "Medium", "Aggressive (short timeout)"]
        )
        self.aggro_selector.set("Medium")
        self.aggro_selector.grid(row=1, column=1, padx=SPACING['md'], pady=SPACING['md'], sticky="ew")
        
        # Scan buttons
        button_frame = ctk.CTkFrame(input_card, fg_color="transparent")
        button_frame.grid(row=0, column=3, rowspan=2, padx=SPACING['md'], pady=SPACING['md'], sticky="e")
        input_card.grid_columnconfigure(3, weight=1)
        
        self.start_scan_btn = StyledButton(
            button_frame,
            text="▶ Start Scan",
            command=self.start_scan,
            size="medium",
            variant="primary"
        )
        self.start_scan_btn.pack(side="left", padx=SPACING['xs'])
        
        self.cancel_scan_btn = StyledButton(
            button_frame,
            text="⏹ Cancel",
            command=self.cancel_scan,
            size="medium",
            variant="danger",
            state="disabled"
        )
        self.cancel_scan_btn.pack(side="left", padx=SPACING['xs'])
        
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
        
        self.show_all_btn = StyledButton(
            options_frame,
            text="👁 Show All Addresses",
            command=self.show_all_addresses,
            size="large",
            variant="neutral"
        )
        self.show_all_btn.pack(side="left", padx=(SPACING['sm'], SPACING['md']), pady=SPACING['md'])
        
        self.export_btn = StyledButton(
            options_frame,
            text="📤 Export Results (Ctrl+E)",
            command=self.export_csv,
            size="xlarge",
            variant="success",
            state="disabled"
        )
        self.export_btn.pack(side="right", padx=SPACING['md'], pady=SPACING['md'])
        
        self.compare_btn = StyledButton(
            options_frame,
            text="📊 Compare Scans",
            command=self.show_scan_comparison,
            size="large",
            variant="primary",
            state="disabled"
        )
        self.compare_btn.pack(side="right", padx=(0, SPACING['sm']), pady=SPACING['md'])
        
        # Results section with StyledCard
        results_card = StyledCard(parent)
        results_card.pack(fill="both", expand=True, padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Results header with primary color
        header_frame = ctk.CTkFrame(
            results_card,
            height=45,
            corner_radius=RADIUS['medium'],
            fg_color=COLORS['primary']
        )
        header_frame.pack(fill="x", padx=SPACING['xs'], pady=SPACING['xs'])
        header_frame.pack_propagate(False)
        
        headers = [("●", 50), ("IP Address", 250), ("Status", 200), ("Response (ms)", 150)]
        for text, width in headers:
            label = ctk.CTkLabel(
                header_frame,
                text=text,
                font=ctk.CTkFont(size=FONTS['body'], weight="bold"),
                text_color="white",
                width=width
            )
            label.pack(side="left", padx=SPACING['sm'], pady=SPACING['sm'])
        
        # Scrollable results
        self.results_scrollable = ctk.CTkScrollableFrame(results_card)
        self.results_scrollable.pack(fill="both", expand=True, padx=SPACING['xs'], pady=(0, SPACING['xs']))
        
        self.result_rows = []
    
    def create_mac_content(self, parent):
        """Create MAC Formatter page content"""
        # Input section with styled card
        input_card = StyledCard(parent)
        input_card.pack(fill="x", padx=SPACING['lg'], pady=SPACING['lg'])
        
        mac_label = ctk.CTkLabel(
            input_card,
            text="Enter MAC Address:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        mac_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        # Frame for MAC entry and history button
        mac_entry_frame = ctk.CTkFrame(input_card, fg_color="transparent")
        mac_entry_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        self.mac_entry = StyledEntry(
            mac_entry_frame,
            placeholder_text="e.g., AA:BB:CC:DD:EE:FF or AABBCCDDEEFF"
        )
        self.mac_entry.pack(side="left", fill="x", expand=True, padx=(0, SPACING['xs']))
        self.mac_entry.bind('<KeyRelease>', self.update_mac_formats)
        
        # History button for MAC
        self.mac_history_btn = StyledButton(
            mac_entry_frame,
            text="⏱",
            size="small",
            variant="neutral",
            command=self.show_mac_history
        )
        self.mac_history_btn.pack(side="left")
        
        self.mac_warning_label = ctk.CTkLabel(
            input_card,
            text="",
            font=ctk.CTkFont(size=FONTS['small']),
            text_color=COLORS['danger']
        )
        self.mac_warning_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        # Vendor information display
        self.vendor_label = ctk.CTkLabel(
            input_card,
            text="",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold"),
            text_color=COLORS['success']
        )
        self.vendor_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Scrollable content area for formats and commands
        self.mac_scrollable = ctk.CTkScrollableFrame(parent)
        self.mac_scrollable.pack(fill="both", expand=True, padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # MAC Formats section with styled card
        self.formats_frame = StyledCard(self.mac_scrollable)
        self.formats_frame.pack(fill="x", padx=SPACING['xs'], pady=(SPACING['md'], SPACING['lg']))
        
        formats_title = SectionTitle(
            self.formats_frame,
            text="Standard MAC Formats"
        )
        formats_title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['md']))
        
        format_labels = [
            "Format 1 (Plain):",
            "Format 2 (Colon):",
            "Format 3 (Dash-4):",
            "Format 4 (Dash-2):"
        ]
        
        self.format_entries = []
        for label_text in format_labels:
            row_frame = ctk.CTkFrame(self.formats_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=SPACING['lg'], pady=SPACING['xs'])
            
            label = ctk.CTkLabel(
                row_frame,
                text=label_text,
                width=150,
                anchor="w",
                font=ctk.CTkFont(size=FONTS['body'])
            )
            label.pack(side="left", padx=(0, SPACING['md']))
            
            entry = StyledEntry(row_frame)
            entry.pack(side="left", fill="x", expand=True, padx=(0, SPACING['md']))
            entry.configure(state="readonly")
            self.format_entries.append(entry)
            
            copy_btn = StyledButton(
                row_frame,
                text="Copy",
                size="small",
                variant="neutral",
                command=lambda e=entry: self.copy_to_clipboard(e)
            )
            copy_btn.pack(side="left")
        
        # Switch Commands section with styled card
        self.commands_frame = StyledCard(self.mac_scrollable)
        self.commands_frame.pack(fill="x", padx=SPACING['xs'], pady=(0, SPACING['lg']))
        
        commands_title = SectionTitle(
            self.commands_frame,
            text="Switch Commands"
        )
        commands_title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['md']))
        
        command_labels = [
            "EXTREME CLI:",
            "Huawei CLI:",
            "Huawei Access-User CLI:",
            "Dell CLI:"
        ]
        
        self.command_textboxes = []
        for label_text in command_labels:
            row_frame = ctk.CTkFrame(self.commands_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=SPACING['lg'], pady=SPACING['xs'])
            
            label = ctk.CTkLabel(
                row_frame,
                text=label_text,
                width=200,
                anchor="w",
                font=ctk.CTkFont(size=FONTS['body'])
            )
            label.pack(side="left", padx=(0, SPACING['md']))
            
            textbox = ctk.CTkTextbox(
                row_frame,
                height=35,
                wrap="word",
                font=ctk.CTkFont(size=FONTS['body']),
                corner_radius=RADIUS['medium']
            )
            textbox.pack(side="left", fill="x", expand=True, padx=(0, SPACING['md']))
            textbox.configure(state="disabled")
            self.command_textboxes.append(textbox)
            
            copy_btn = StyledButton(
                row_frame,
                text="Copy",
                size="small",
                variant="neutral",
                command=lambda tb=textbox: self.copy_textbox_to_clipboard(tb)
            )
            copy_btn.pack(side="left")
        
        # Add bottom padding
        padding_frame = ctk.CTkFrame(self.commands_frame, fg_color="transparent", height=SPACING['md'])
        padding_frame.pack()
        
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
    
    def create_profiles_content(self, parent):
        """Create Network Profiles page content"""
        # Scrollable content area
        scrollable = ctk.CTkScrollableFrame(parent)
        scrollable.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            scrollable,
            text="Network Profile Manager",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 5))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            scrollable,
            text="Manage network interface configurations and quick-switch profiles",
            font=ctk.CTkFont(size=12)
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Admin warning if not admin
        if not self.is_admin():
            warning_frame = ctk.CTkFrame(scrollable, fg_color=("#FFC107", "#FF6F00"), corner_radius=8)
            warning_frame.pack(fill="x", pady=(0, 15))
            
            warning_label = ctk.CTkLabel(
                warning_frame,
                text="⚠️ Administrator privileges required to change network settings",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("black", "white")
            )
            warning_label.pack(pady=10)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            scrollable,
            text="🔄 Refresh Interfaces",
            command=self.refresh_interfaces,
            width=200,
            height=42,
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"]
        )
        refresh_btn.pack(pady=(0, 15))
        
        # Current Interfaces Section
        interfaces_title = ctk.CTkLabel(
            scrollable,
            text="Network Interfaces (Current Status)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        interfaces_title.pack(pady=(10, 10), anchor="w")
        
        # Frame to hold interface cards
        self.interfaces_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        self.interfaces_frame.pack(fill="x", pady=(0, 20))
        
        # Separator
        separator = ctk.CTkFrame(scrollable, height=2, fg_color=("gray70", "gray30"))
        separator.pack(fill="x", pady=20)
        
        # Saved Profiles Section
        profiles_title = ctk.CTkLabel(
            scrollable,
            text="Saved Profiles",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        profiles_title.pack(pady=(0, 10), anchor="w")
        
        # New profile button
        new_profile_btn = ctk.CTkButton(
            scrollable,
            text="➕ Create New Profile",
            command=self.create_new_profile,
            width=220,
            height=42,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"]
        )
        new_profile_btn.pack(pady=(0, 15))
        
        # Frame to hold profile cards
        self.profiles_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        self.profiles_frame.pack(fill="x")
        
        # Load initial data
        self.refresh_interfaces()
        self.refresh_profiles()
    
    def create_portscan_content(self, parent):
        """Create Port Scanner page content"""
        # Scrollable content area
        scrollable = ctk.CTkScrollableFrame(parent)
        scrollable.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            scrollable,
            text="Port Scanner",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 5))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            scrollable,
            text="Scan for open ports on target hosts using multiple methods",
            font=ctk.CTkFont(size=12)
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Input section
        input_frame = ctk.CTkFrame(scrollable, corner_radius=8)
        input_frame.pack(fill="x", pady=(0, 15))
        
        # Target host
        target_label = ctk.CTkLabel(
            input_frame,
            text="Target Host:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        target_label.pack(pady=(15, 5), padx=15, anchor="w")
        
        target_info = ctk.CTkLabel(
            input_frame,
            text="Enter IP address or hostname (e.g., 192.168.1.1 or example.com)",
            font=ctk.CTkFont(size=10),
            text_color=("gray60", "gray40")
        )
        target_info.pack(pady=(0, 5), padx=15, anchor="w")
        
        self.port_target_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="192.168.1.1 or example.com",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.port_target_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        # Port selection
        port_label = ctk.CTkLabel(
            input_frame,
            text="Port Selection:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        port_label.pack(pady=(0, 5), padx=15, anchor="w")
        
        # Port mode selection
        self.port_mode_var = ctk.StringVar(value="common")
        
        port_mode_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        port_mode_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        common_radio = ctk.CTkRadioButton(
            port_mode_frame,
            text="Common Ports (21,22,23,25,80,443,3389,...)",
            variable=self.port_mode_var,
            value="common",
            command=self.update_port_mode,
            font=ctk.CTkFont(size=11)
        )
        common_radio.pack(anchor="w", pady=2)
        
        range_radio = ctk.CTkRadioButton(
            port_mode_frame,
            text="Port Range (e.g., 1-1000)",
            variable=self.port_mode_var,
            value="range",
            command=self.update_port_mode,
            font=ctk.CTkFont(size=11)
        )
        range_radio.pack(anchor="w", pady=2)
        
        custom_radio = ctk.CTkRadioButton(
            port_mode_frame,
            text="Custom Ports (comma-separated, e.g., 80,443,8080)",
            variable=self.port_mode_var,
            value="custom",
            command=self.update_port_mode,
            font=ctk.CTkFont(size=11)
        )
        custom_radio.pack(anchor="w", pady=2)
        
        # Port input (changes based on mode)
        self.port_input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Will scan common ports",
            height=40,
            font=ctk.CTkFont(size=13),
            state="disabled"
        )
        self.port_input_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        # Scan method
        method_label = ctk.CTkLabel(
            input_frame,
            text="Scan Method:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        method_label.pack(pady=(0, 5), padx=15, anchor="w")
        
        self.scan_method_var = ctk.StringVar(value="socket")
        
        method_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        method_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        socket_radio = ctk.CTkRadioButton(
            method_frame,
            text="Socket Scan (Fast, recommended)",
            variable=self.scan_method_var,
            value="socket",
            font=ctk.CTkFont(size=11)
        )
        socket_radio.pack(anchor="w", pady=2)
        
        if TELNETLIB_AVAILABLE:
            telnet_radio = ctk.CTkRadioButton(
                method_frame,
                text="Telnet Test (Connection-based)",
                variable=self.scan_method_var,
                value="telnet",
                font=ctk.CTkFont(size=11)
            )
            telnet_radio.pack(anchor="w", pady=2)
        
        if platform.system() == "Windows":
            powershell_radio = ctk.CTkRadioButton(
                method_frame,
                text="PowerShell Test-NetConnection (Most reliable on Windows)",
                variable=self.scan_method_var,
                value="powershell",
                font=ctk.CTkFont(size=11)
            )
            powershell_radio.pack(anchor="w", pady=2)
        
        # Scan buttons
        button_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 15))
        
        self.port_scan_btn = ctk.CTkButton(
            button_frame,
            text="▶ Start Port Scan",
            command=self.start_port_scan,
            width=200,
            height=48,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"]
        )
        self.port_scan_btn.pack(side="left", padx=(0, 10))
        
        self.port_cancel_btn = ctk.CTkButton(
            button_frame,
            text="⏹ Cancel",
            command=self.cancel_port_scan,
            width=130,
            height=48,
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled",
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"]
        )
        self.port_cancel_btn.pack(side="left")
        
        self.port_export_btn = ctk.CTkButton(
            button_frame,
            text="📤 Export Results",
            command=self.export_port_scan,
            width=180,
            height=48,
            font=ctk.CTkFont(size=14),
            state="disabled",
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"]
        )
        self.port_export_btn.pack(side="left", padx=(10, 0))
        
        # Progress
        self.port_progress_label = ctk.CTkLabel(
            scrollable,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.port_progress_label.pack(pady=(0, 5))
        
        self.port_progress_bar = ctk.CTkProgressBar(scrollable, width=400, height=20)
        self.port_progress_bar.pack(pady=(0, 15))
        self.port_progress_bar.set(0)
        
        # Results section
        results_title = ctk.CTkLabel(
            scrollable,
            text="Scan Results",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        results_title.pack(pady=(10, 10), anchor="w")
        
        # Results frame
        self.port_results_frame = ctk.CTkFrame(scrollable, corner_radius=8)
        self.port_results_frame.pack(fill="both", expand=True)
        
        # Initial message
        no_results_label = ctk.CTkLabel(
            self.port_results_frame,
            text="No scan results yet. Enter a target and start scanning.",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        no_results_label.pack(pady=50)
        
        # Port scan state
        self.port_scan_running = False
        self.port_scan_cancelled = False
        self.port_scan_results = []  # Store port scan results for export
        self.port_scan_target = ""   # Store target for export
    
    def update_port_mode(self):
        """Update port input based on selected mode"""
        mode = self.port_mode_var.get()
        
        if mode == "common":
            self.port_input_entry.configure(state="disabled", placeholder_text="Will scan common ports")
            self.port_input_entry.delete(0, 'end')
        elif mode == "range":
            self.port_input_entry.configure(state="normal", placeholder_text="e.g., 1-1000 or 80-443")
            self.port_input_entry.delete(0, 'end')
        elif mode == "custom":
            self.port_input_entry.configure(state="normal", placeholder_text="e.g., 21,22,23,80,443,3389")
            self.port_input_entry.delete(0, 'end')
    
    def get_ports_to_scan(self):
        """Get list of ports based on selection"""
        mode = self.port_mode_var.get()
        
        if mode == "common":
            # Common ports with services
            return [
                21,    # FTP
                22,    # SSH
                23,    # Telnet
                25,    # SMTP
                53,    # DNS
                80,    # HTTP
                110,   # POP3
                143,   # IMAP
                443,   # HTTPS
                445,   # SMB
                3306,  # MySQL
                3389,  # RDP
                5432,  # PostgreSQL
                5900,  # VNC
                8080,  # HTTP Alt
                8443,  # HTTPS Alt
            ]
        elif mode == "range":
            port_range = self.port_input_entry.get().strip()
            if not port_range:
                return []
            
            try:
                if '-' in port_range:
                    start, end = port_range.split('-')
                    start = int(start.strip())
                    end = int(end.strip())
                    if 1 <= start <= end <= 65535:
                        return list(range(start, end + 1))
                else:
                    port = int(port_range)
                    if 1 <= port <= 65535:
                        return [port]
            except:
                pass
            return []
        elif mode == "custom":
            ports_str = self.port_input_entry.get().strip()
            if not ports_str:
                return []
            
            try:
                ports = []
                for p in ports_str.split(','):
                    port = int(p.strip())
                    if 1 <= port <= 65535:
                        ports.append(port)
                return ports
            except:
                return []
        
        return []
    
    def start_port_scan(self):
        """Start port scanning"""
        target = self.port_target_entry.get().strip()
        if not target:
            messagebox.showwarning("Invalid Input", "Please enter a target host (IP or hostname)")
            return
        
        ports = self.get_ports_to_scan()
        if not ports:
            messagebox.showwarning("Invalid Ports", "Please specify valid ports to scan")
            return
        
        method = self.scan_method_var.get()
        
        # Update UI
        self.port_scan_btn.configure(state="disabled")
        self.port_cancel_btn.configure(state="normal")
        self.port_scan_running = True
        self.port_scan_cancelled = False
        self.port_progress_bar.set(0)
        self.port_progress_label.configure(text=f"Scanning {target} - {len(ports)} port(s)...")
        
        # Clear previous results
        for widget in self.port_results_frame.winfo_children():
            widget.destroy()
        
        # Start scan in background thread
        scan_thread = threading.Thread(
            target=self.run_port_scan,
            args=(target, ports, method),
            daemon=True
        )
        scan_thread.start()
    
    def cancel_port_scan(self):
        """Cancel ongoing port scan"""
        self.port_scan_cancelled = True
        self.port_progress_label.configure(text="Cancelling scan...")
    
    def run_port_scan(self, target, ports, method):
        """Run port scan in background"""
        results = []
        total_ports = len(ports)
        
        for i, port in enumerate(ports):
            if self.port_scan_cancelled:
                break
            
            # Update progress
            progress = (i + 1) / total_ports
            self.after(0, self.port_progress_bar.set, progress)
            self.after(0, self.port_progress_label.configure, 
                      {"text": f"Scanning {target}:{port} ({i+1}/{total_ports})..."})
            
            # Scan port
            is_open, service = self.scan_single_port(target, port, method)
            
            if is_open:
                results.append({
                    "port": port,
                    "state": "OPEN",
                    "service": service
                })
        
        # Update UI with results
        self.after(0, self.display_port_results, target, results, self.port_scan_cancelled)
    
    def scan_single_port(self, target, port, method):
        """Scan a single port using specified method"""
        if method == "socket":
            return self.scan_port_socket(target, port)
        elif method == "telnet":
            return self.scan_port_telnet(target, port)
        elif method == "powershell":
            return self.scan_port_powershell(target, port)
        return False, "Unknown"
    
    def scan_port_socket(self, target, port):
        """Scan port using socket"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target, port))
            sock.close()
            
            if result == 0:
                service = self.get_service_name(port)
                return True, service
            return False, ""
        except:
            return False, ""
    
    def scan_port_telnet(self, target, port):
        """Scan port using telnet"""
        if not TELNETLIB_AVAILABLE:
            return False, ""
        
        try:
            tn = telnetlib.Telnet()
            tn.open(target, port, timeout=2)
            tn.close()
            service = self.get_service_name(port)
            return True, service
        except:
            return False, ""
    
    def scan_port_powershell(self, target, port):
        """Scan port using PowerShell Test-NetConnection"""
        try:
            cmd = f'powershell -Command "Test-NetConnection -ComputerName {target} -Port {port} -InformationLevel Quiet"'
            result = self.run_subprocess(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )
            
            if result.stdout.strip().lower() == "true":
                service = self.get_service_name(port)
                return True, service
            return False, ""
        except:
            return False, ""
    
    def get_service_name(self, port):
        """Get common service name for port"""
        services = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            445: "SMB",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            5900: "VNC",
            8080: "HTTP-Alt",
            8443: "HTTPS-Alt",
        }
        return services.get(port, "Unknown")
    
    def display_port_results(self, target, results, was_cancelled):
        """Display port scan results"""
        # Store results for export
        self.port_scan_results = results
        self.port_scan_target = target
        
        # Clear frame
        for widget in self.port_results_frame.winfo_children():
            widget.destroy()
        
        # Reset UI state
        self.port_scan_btn.configure(state="normal")
        self.port_cancel_btn.configure(state="disabled")
        self.port_scan_running = False
        
        # Enable/disable export button
        if results and not was_cancelled:
            self.port_export_btn.configure(state="normal")
        else:
            self.port_export_btn.configure(state="disabled")
        
        if was_cancelled:
            self.port_progress_label.configure(text="Scan cancelled")
        else:
            self.port_progress_label.configure(text="Scan complete")
        
        if not results:
            no_results_label = ctk.CTkLabel(
                self.port_results_frame,
                text=f"No open ports found on {target}" if not was_cancelled else "Scan was cancelled",
                font=ctk.CTkFont(size=12),
                text_color=("gray60", "gray40")
            )
            no_results_label.pack(pady=50)
            return
        
        # Summary
        summary_frame = ctk.CTkFrame(self.port_results_frame, fg_color="transparent")
        summary_frame.pack(fill="x", padx=15, pady=15)
        
        summary_text = f"Found {len(results)} open port(s) on {target}"
        summary_label = ctk.CTkLabel(
            summary_frame,
            text=summary_text,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        summary_label.pack(anchor="w")
        
        # Results table header
        header_frame = ctk.CTkFrame(self.port_results_frame, corner_radius=0)
        header_frame.pack(fill="x", padx=15, pady=(0, 5))
        
        port_header = ctk.CTkLabel(
            header_frame,
            text="Port",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=100,
            anchor="w"
        )
        port_header.pack(side="left", padx=10, pady=10)
        
        state_header = ctk.CTkLabel(
            header_frame,
            text="State",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=100,
            anchor="w"
        )
        state_header.pack(side="left", padx=10, pady=10)
        
        service_header = ctk.CTkLabel(
            header_frame,
            text="Service",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=150,
            anchor="w"
        )
        service_header.pack(side="left", padx=10, pady=10)
        
        # Results rows
        for result in results:
            row_frame = ctk.CTkFrame(self.port_results_frame, corner_radius=4)
            row_frame.pack(fill="x", padx=15, pady=2)
            
            port_label = ctk.CTkLabel(
                row_frame,
                text=str(result["port"]),
                font=ctk.CTkFont(size=12),
                width=100,
                anchor="w"
            )
            port_label.pack(side="left", padx=10, pady=8)
            
            state_label = ctk.CTkLabel(
                row_frame,
                text=result["state"],
                font=ctk.CTkFont(size=12, weight="bold"),
                width=100,
                anchor="w",
                text_color=("#4CAF50", "#4CAF50")
            )
            state_label.pack(side="left", padx=10, pady=8)
            
            service_label = ctk.CTkLabel(
                row_frame,
                text=result["service"],
                font=ctk.CTkFont(size=12),
                width=150,
                anchor="w"
            )
            service_label.pack(side="left", padx=10, pady=8)
    
    def create_dns_content(self, parent):
        """Create DNS Lookup page content"""
        # Scrollable content area
        scrollable = ctk.CTkScrollableFrame(parent)
        scrollable.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            scrollable,
            text="DNS Lookup",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 5))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            scrollable,
            text="Resolve hostnames to IP addresses and vice versa",
            font=ctk.CTkFont(size=12)
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Input section
        input_frame = ctk.CTkFrame(scrollable, corner_radius=8)
        input_frame.pack(fill="x", pady=(0, 15))
        
        # Query input
        query_label = ctk.CTkLabel(
            input_frame,
            text="Enter Hostname or IP Address:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        query_label.pack(pady=(15, 5), padx=15, anchor="w")
        
        query_info = ctk.CTkLabel(
            input_frame,
            text="Examples: google.com, 8.8.8.8, github.com, 192.168.1.1",
            font=ctk.CTkFont(size=10),
            text_color=("gray60", "gray40")
        )
        query_info.pack(pady=(0, 5), padx=15, anchor="w")
        
        self.dns_query_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="google.com or 8.8.8.8",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.dns_query_entry.pack(fill="x", padx=15, pady=(0, 15))
        self.dns_query_entry.bind('<Return>', lambda e: self.perform_dns_lookup())
        
        # DNS server selection
        dns_server_label = ctk.CTkLabel(
            input_frame,
            text="DNS Server (Optional):",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        dns_server_label.pack(pady=(0, 5), padx=15, anchor="w")
        
        dns_server_info = ctk.CTkLabel(
            input_frame,
            text="Leave empty to use system default, or specify custom DNS server",
            font=ctk.CTkFont(size=10),
            text_color=("gray60", "gray40")
        )
        dns_server_info.pack(pady=(0, 5), padx=15, anchor="w")
        
        dns_server_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        dns_server_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.dns_server_var = ctk.StringVar(value="system")
        
        system_dns = ctk.CTkRadioButton(
            dns_server_frame,
            text="System Default",
            variable=self.dns_server_var,
            value="system",
            font=ctk.CTkFont(size=11)
        )
        system_dns.pack(anchor="w", pady=2)
        
        google_dns = ctk.CTkRadioButton(
            dns_server_frame,
            text="Google DNS (8.8.8.8)",
            variable=self.dns_server_var,
            value="8.8.8.8",
            font=ctk.CTkFont(size=11)
        )
        google_dns.pack(anchor="w", pady=2)
        
        cloudflare_dns = ctk.CTkRadioButton(
            dns_server_frame,
            text="Cloudflare DNS (1.1.1.1)",
            variable=self.dns_server_var,
            value="1.1.1.1",
            font=ctk.CTkFont(size=11)
        )
        cloudflare_dns.pack(anchor="w", pady=2)
        
        # Lookup button
        lookup_btn = ctk.CTkButton(
            scrollable,
            text="Lookup",
            command=self.perform_dns_lookup,
            width=180,
            height=48,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#4CAF50", "#388E3C")
        )
        lookup_btn.pack(pady=(0, 15))
        
        # Results section
        results_title = ctk.CTkLabel(
            scrollable,
            text="Results",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        results_title.pack(pady=(10, 10), anchor="w")
        
        # Results frame
        self.dns_results_frame = ctk.CTkFrame(scrollable, corner_radius=8)
        self.dns_results_frame.pack(fill="both", expand=True)
        
        # Initial message
        no_results_label = ctk.CTkLabel(
            self.dns_results_frame,
            text="No lookup performed yet. Enter a hostname or IP address and click Lookup.",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        no_results_label.pack(pady=50)
    
    def perform_dns_lookup(self):
        """Perform DNS lookup"""
        query = self.dns_query_entry.get().strip()
        if not query:
            messagebox.showwarning("Invalid Input", "Please enter a hostname or IP address")
            return
        
        dns_server = self.dns_server_var.get()
        
        # Clear previous results
        for widget in self.dns_results_frame.winfo_children():
            widget.destroy()
        
        # Show loading
        loading_label = ctk.CTkLabel(
            self.dns_results_frame,
            text=f"Looking up {query}...",
            font=ctk.CTkFont(size=12)
        )
        loading_label.pack(pady=50)
        
        # Perform lookup in background
        lookup_thread = threading.Thread(
            target=self.run_dns_lookup,
            args=(query, dns_server),
            daemon=True
        )
        lookup_thread.start()
    
    def run_dns_lookup(self, query, dns_server):
        """Run DNS lookup in background"""
        results = {}
        
        # Determine if query is IP or hostname
        try:
            ipaddress.ip_address(query)
            is_ip = True
        except:
            is_ip = False
        
        if is_ip:
            # Reverse lookup (IP to hostname)
            try:
                hostname = socket.gethostbyaddr(query)[0]
                results["type"] = "Reverse Lookup"
                results["query"] = query
                results["result"] = hostname
                results["success"] = True
            except socket.herror:
                results["type"] = "Reverse Lookup"
                results["query"] = query
                results["result"] = "No hostname found"
                results["success"] = False
            except Exception as e:
                results["type"] = "Reverse Lookup"
                results["query"] = query
                results["result"] = f"Error: {str(e)}"
                results["success"] = False
        else:
            # Forward lookup (hostname to IP)
            try:
                if dns_server != "system":
                    # Use custom DNS server via nslookup
                    if platform.system() == "Windows":
                        cmd = f'nslookup {query} {dns_server}'
                    else:
                        cmd = f'dig @{dns_server} {query} +short'
                    
                    result = self.run_subprocess(
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
                            if 'Address:' in line and not dns_server in line:
                                ip = line.split('Address:')[1].strip()
                                if ip:
                                    ips.append(ip)
                        
                        if ips:
                            results["type"] = "Forward Lookup"
                            results["query"] = query
                            results["result"] = ips
                            results["dns_server"] = dns_server
                            results["success"] = True
                        else:
                            results["type"] = "Forward Lookup"
                            results["query"] = query
                            results["result"] = "No IP addresses found"
                            results["success"] = False
                    else:
                        # Parse dig output
                        ips = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                        if ips:
                            results["type"] = "Forward Lookup"
                            results["query"] = query
                            results["result"] = ips
                            results["dns_server"] = dns_server
                            results["success"] = True
                        else:
                            results["type"] = "Forward Lookup"
                            results["query"] = query
                            results["result"] = "No IP addresses found"
                            results["success"] = False
                else:
                    # Use system DNS
                    ip_addresses = socket.gethostbyname_ex(query)[2]
                    results["type"] = "Forward Lookup"
                    results["query"] = query
                    results["result"] = ip_addresses
                    results["dns_server"] = "System Default"
                    results["success"] = True
            except socket.gaierror:
                results["type"] = "Forward Lookup"
                results["query"] = query
                results["result"] = "Hostname not found"
                results["success"] = False
            except Exception as e:
                results["type"] = "Forward Lookup"
                results["query"] = query
                results["result"] = f"Error: {str(e)}"
                results["success"] = False
        
        # Display results in UI
        self.after(0, self.display_dns_results, results)
    
    def display_dns_results(self, results):
        """Display DNS lookup results"""
        # Clear frame
        for widget in self.dns_results_frame.winfo_children():
            widget.destroy()
        
        # Result type
        type_label = ctk.CTkLabel(
            self.dns_results_frame,
            text=results["type"],
            font=ctk.CTkFont(size=16, weight="bold")
        )
        type_label.pack(pady=(20, 10), padx=20, anchor="w")
        
        # Query
        query_frame = ctk.CTkFrame(self.dns_results_frame, fg_color="transparent")
        query_frame.pack(fill="x", padx=20, pady=5)
        
        query_title = ctk.CTkLabel(
            query_frame,
            text="Query:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            anchor="w"
        )
        query_title.pack(side="left")
        
        query_value = ctk.CTkLabel(
            query_frame,
            text=results["query"],
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        query_value.pack(side="left", fill="x", expand=True)
        
        # DNS Server (if applicable)
        if "dns_server" in results:
            dns_frame = ctk.CTkFrame(self.dns_results_frame, fg_color="transparent")
            dns_frame.pack(fill="x", padx=20, pady=5)
            
            dns_title = ctk.CTkLabel(
                dns_frame,
                text="DNS Server:",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=120,
                anchor="w"
            )
            dns_title.pack(side="left")
            
            dns_value = ctk.CTkLabel(
                dns_frame,
                text=results["dns_server"],
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            dns_value.pack(side="left", fill="x", expand=True)
        
        # Result
        result_frame = ctk.CTkFrame(self.dns_results_frame, fg_color="transparent")
        result_frame.pack(fill="x", padx=20, pady=5)
        
        result_title = ctk.CTkLabel(
            result_frame,
            text="Result:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            anchor="w"
        )
        result_title.pack(side="left")
        
        result_color = ("#4CAF50", "#4CAF50") if results["success"] else ("#F44336", "#F44336")
        
        if isinstance(results["result"], list):
            # Multiple IPs
            result_text = ", ".join(results["result"])
        else:
            result_text = results["result"]
        
        result_value = ctk.CTkLabel(
            result_frame,
            text=result_text,
            font=ctk.CTkFont(size=12, weight="bold" if results["success"] else "normal"),
            anchor="w",
            text_color=result_color
        )
        result_value.pack(side="left", fill="x", expand=True)
        
        # Status icon
        status_text = "✅ Success" if results["success"] else "❌ Failed"
        status_label = ctk.CTkLabel(
            self.dns_results_frame,
            text=status_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=result_color
        )
        status_label.pack(pady=(20, 20), padx=20, anchor="w")
    
    def create_subnet_content(self, parent):
        """Create Subnet Calculator page content"""
        # Scrollable content area
        scrollable = ctk.CTkScrollableFrame(parent)
        scrollable.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            scrollable,
            text="Subnet Calculator",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 5))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            scrollable,
            text="Calculate subnet information from CIDR notation",
            font=ctk.CTkFont(size=12)
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Input section
        input_frame = ctk.CTkFrame(scrollable, corner_radius=8)
        input_frame.pack(fill="x", pady=(0, 15))
        
        # CIDR input
        cidr_label = ctk.CTkLabel(
            input_frame,
            text="Enter Network in CIDR Notation:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        cidr_label.pack(pady=(15, 5), padx=15, anchor="w")
        
        cidr_info = ctk.CTkLabel(
            input_frame,
            text="Examples: 192.168.1.0/24, 10.0.0.0/8, 172.16.0.0/16",
            font=ctk.CTkFont(size=10),
            text_color=("gray60", "gray40")
        )
        cidr_info.pack(pady=(0, 5), padx=15, anchor="w")
        
        self.subnet_cidr_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="192.168.1.0/24",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.subnet_cidr_entry.pack(fill="x", padx=15, pady=(0, 15))
        self.subnet_cidr_entry.bind('<Return>', lambda e: self.calculate_subnet())
        
        # Calculate button
        calc_btn = ctk.CTkButton(
            scrollable,
            text="Calculate",
            command=self.calculate_subnet,
            width=180,
            height=48,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#FF9800", "#F57C00")
        )
        calc_btn.pack(pady=(0, 15))
        
        # Results section
        results_title = ctk.CTkLabel(
            scrollable,
            text="Subnet Information",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        results_title.pack(pady=(10, 10), anchor="w")
        
        # Results frame
        self.subnet_results_frame = ctk.CTkFrame(scrollable, corner_radius=8)
        self.subnet_results_frame.pack(fill="both", expand=True)
        
        # Initial message
        no_results_label = ctk.CTkLabel(
            self.subnet_results_frame,
            text="No calculation performed yet. Enter a network in CIDR notation and click Calculate.",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        no_results_label.pack(pady=50)
    
    def calculate_subnet(self):
        """Calculate subnet information"""
        cidr = self.subnet_cidr_entry.get().strip()
        if not cidr:
            messagebox.showwarning("Invalid Input", "Please enter a network in CIDR notation (e.g., 192.168.1.0/24)")
            return
        
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            
            # Calculate subnet information
            info = {
                "network": str(network.network_address),
                "netmask": str(network.netmask),
                "cidr": f"/{network.prefixlen}",
                "wildcard": str(network.hostmask),
                "broadcast": str(network.broadcast_address),
                "first_host": str(network.network_address + 1) if network.num_addresses > 2 else "N/A",
                "last_host": str(network.broadcast_address - 1) if network.num_addresses > 2 else "N/A",
                "total_hosts": network.num_addresses,
                "usable_hosts": max(0, network.num_addresses - 2),
                "network_class": self.get_network_class(network.network_address),
                "type": "Private" if network.is_private else "Public"
            }
            
            self.display_subnet_results(info)
            
        except ValueError as e:
            messagebox.showerror("Invalid CIDR", f"Invalid CIDR notation:\n{str(e)}")
    
    def get_network_class(self, ip):
        """Get network class from IP address"""
        first_octet = int(str(ip).split('.')[0])
        
        if 1 <= first_octet <= 126:
            return "A"
        elif 128 <= first_octet <= 191:
            return "B"
        elif 192 <= first_octet <= 223:
            return "C"
        elif 224 <= first_octet <= 239:
            return "D (Multicast)"
        elif 240 <= first_octet <= 255:
            return "E (Reserved)"
        else:
            return "Unknown"
    
    def display_subnet_results(self, info):
        """Display subnet calculation results"""
        # Clear frame
        for widget in self.subnet_results_frame.winfo_children():
            widget.destroy()
        
        # Create result rows
        results = [
            ("Network Address", info["network"]),
            ("Subnet Mask", info["netmask"]),
            ("CIDR Notation", info["cidr"]),
            ("Wildcard Mask", info["wildcard"]),
            ("Broadcast Address", info["broadcast"]),
            ("First Usable Host", info["first_host"]),
            ("Last Usable Host", info["last_host"]),
            ("Total Addresses", f"{info['total_hosts']:,}"),
            ("Usable Hosts", f"{info['usable_hosts']:,}"),
            ("Network Class", info["network_class"]),
            ("IP Type", info["type"]),
        ]
        
        for label, value in results:
            row_frame = ctk.CTkFrame(self.subnet_results_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=20, pady=5)
            
            label_widget = ctk.CTkLabel(
                row_frame,
                text=f"{label}:",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=180,
                anchor="w"
            )
            label_widget.pack(side="left")
            
            value_widget = ctk.CTkLabel(
                row_frame,
                text=value,
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            value_widget.pack(side="left", fill="x", expand=True)
    
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
    
    def is_admin(self):
        """Check if running with administrator privileges"""
        try:
            if platform.system() == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            return os.geteuid() == 0
        except:
            return False
    
    def run_subprocess(self, cmd, **kwargs):
        """Run subprocess without showing console window (fixes ghost CMD windows)"""
        if platform.system() == "Windows":
            # Add flag to hide console window on Windows
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        return subprocess.run(cmd, **kwargs)
    
    def restart_as_admin(self):
        """Restart application with administrator privileges (Windows UAC)"""
        try:
            if platform.system() == "Windows":
                import ctypes
                
                # Get the path to the executable or script
                if getattr(sys, 'frozen', False):
                    # Running as exe
                    script = sys.executable
                else:
                    # Running as script
                    script = os.path.abspath(sys.argv[0])
                
                # Trigger UAC elevation
                ctypes.windll.shell32.ShellExecuteW(
                    None,
                    "runas",
                    sys.executable if getattr(sys, 'frozen', False) else "python",
                    script if not getattr(sys, 'frozen', False) else "",
                    None,
                    1  # SW_SHOWNORMAL
                )
                
                # Close current instance
                self.quit()
        except Exception as e:
            messagebox.showerror("Error", f"Could not restart with admin privileges:\n{str(e)}")
    
    def get_network_interfaces(self):
        """Get list of network interfaces (Windows)"""
        try:
            result = self.run_subprocess(
                ["netsh", "interface", "ipv4", "show", "interfaces"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            interfaces = []
            lines = result.stdout.split('\n')[3:]  # Skip header lines
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        idx = parts[0]
                        status = parts[2]
                        name = ' '.join(parts[3:])
                        interfaces.append({
                            "index": idx,
                            "name": name,
                            "status": status
                        })
            
            return interfaces
        except Exception as e:
            print(f"Error getting interfaces: {e}")
            return []
    
    def get_interface_config(self, interface_name):
        """Get current IP configuration for an interface"""
        try:
            result = self.run_subprocess(
                ["netsh", "interface", "ipv4", "show", "config", interface_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            config = {
                "dhcp": False,
                "ip": None,
                "subnet": None,
                "gateway": None,
                "dns": []
            }
            
            lines = result.stdout.split('\n')
            for i, line in enumerate(lines):
                if "DHCP enabled" in line and "Yes" in line:
                    config["dhcp"] = True
                elif "IP Address:" in line and i + 1 < len(lines):
                    config["ip"] = lines[i + 1].strip()
                elif "Subnet Prefix:" in line and i + 1 < len(lines):
                    subnet_line = lines[i + 1].strip()
                    config["subnet"] = subnet_line.split('/')[0] if '/' in subnet_line else subnet_line
                elif "Default Gateway:" in line and i + 1 < len(lines):
                    config["gateway"] = lines[i + 1].strip()
                elif "DNS servers configured through DHCP:" in line:
                    j = i + 1
                    while j < len(lines) and lines[j].strip() and not lines[j].startswith('Configuration'):
                        dns = lines[j].strip()
                        if dns:
                            config["dns"].append(dns)
                        j += 1
                elif "Statically Configured DNS Servers:" in line:
                    j = i + 1
                    while j < len(lines) and lines[j].strip() and not lines[j].startswith('Configuration'):
                        dns = lines[j].strip()
                        if dns:
                            config["dns"].append(dns)
                        j += 1
            
            return config
        except Exception as e:
            print(f"Error getting interface config: {e}")
            return None
    
    def refresh_interfaces(self):
        """Refresh the interface list display"""
        # Clear existing
        for widget in self.interfaces_frame.winfo_children():
            widget.destroy()
        
        interfaces = self.get_network_interfaces()
        
        if not interfaces:
            no_interfaces_label = ctk.CTkLabel(
                self.interfaces_frame,
                text="No network interfaces found",
                font=ctk.CTkFont(size=12)
            )
            no_interfaces_label.pack(pady=20)
            return
        
        for interface in interfaces:
            self.create_interface_card(interface)
    
    def create_interface_card(self, interface):
        """Create a card for an interface"""
        card = ctk.CTkFrame(self.interfaces_frame, corner_radius=8)
        card.pack(fill="x", pady=5)
        
        # Header with name and status
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        name_label = ctk.CTkLabel(
            header_frame,
            text=interface["name"],
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_label.pack(side="left")
        
        status_color = "#4CAF50" if interface["status"] == "connected" else "#757575"
        status_label = ctk.CTkLabel(
            header_frame,
            text=interface["status"].upper(),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=status_color
        )
        status_label.pack(side="right")
        
        # Get current config
        config = self.get_interface_config(interface["name"])
        
        if config:
            # IP info
            if config["dhcp"]:
                ip_text = "DHCP Enabled"
                if config["ip"]:
                    ip_text += f" (Current IP: {config['ip']})"
            else:
                ip_text = f"Static IP: {config['ip'] or 'Not configured'}"
            
            ip_label = ctk.CTkLabel(
                card,
                text=ip_text,
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            ip_label.pack(fill="x", padx=15, pady=(0, 10))
            
            # Action buttons
            button_frame = ctk.CTkFrame(card, fg_color="transparent")
            button_frame.pack(fill="x", padx=15, pady=(0, 10))
            
            if config["dhcp"]:
                static_btn = ctk.CTkButton(
                    button_frame,
                    text="Set Static IP",
                    command=lambda i=interface["name"]: self.show_static_ip_dialog(i),
                    width=140,
                    height=36
                )
                static_btn.pack(side="left", padx=(0, 5))
            else:
                dhcp_btn = ctk.CTkButton(
                    button_frame,
                    text="Switch to DHCP",
                    command=lambda i=interface["name"]: self.set_dhcp(i),
                    width=140,
                    height=36,
                    fg_color=("#4CAF50", "#388E3C")
                )
                dhcp_btn.pack(side="left", padx=(0, 5))
                
                edit_btn = ctk.CTkButton(
                    button_frame,
                    text="Edit Static IP",
                    command=lambda i=interface["name"]: self.show_static_ip_dialog(i),
                    width=140,
                    height=36
                )
                edit_btn.pack(side="left", padx=(0, 5))
    
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
        """Add a result row to the display with alternating colors"""
        # Determine if this should be an alternate row
        is_alternate = len(self.result_rows) % 2 == 1
        
        # Use ResultRow component with alternating colors
        row_color = ("gray92", "gray15") if is_alternate else COLORS['bg_card']
        row_frame = ResultRow(self.results_scrollable, fg_color=row_color)
        row_frame.pack(fill="x", padx=SPACING['xs'], pady=SPACING['xs'])
        row_frame._original_color = row_color
        
        # Status dot with better colors
        status_color = COLORS["online"] if result['status'] == 'Online' else COLORS["offline"]
        dot_label = ctk.CTkLabel(
            row_frame,
            text="●",
            font=ctk.CTkFont(size=16),
            text_color=status_color,
            width=50
        )
        dot_label.pack(side="left", padx=SPACING['sm'])
        
        # IP Address with better font
        ip_label = ctk.CTkLabel(
            row_frame,
            text=result['ip'],
            width=250,
            anchor="w",
            font=ctk.CTkFont(size=FONTS['body'])
        )
        ip_label.pack(side="left", padx=SPACING['sm'])
        
        # Status with color and bold font
        status_label = ctk.CTkLabel(
            row_frame,
            text=result['status'],
            width=200,
            anchor="w",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold"),
            text_color=status_color
        )
        status_label.pack(side="left", padx=SPACING['sm'])
        
        # RTT with subtle color
        rtt_label = ctk.CTkLabel(
            row_frame,
            text=result['rtt'],
            width=150,
            anchor="w",
            font=ctk.CTkFont(size=FONTS['small']),
            text_color=COLORS["text_secondary"]
        )
        rtt_label.pack(side="left", padx=SPACING['sm'])
        
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
        """Export scanner results in multiple formats"""
        if not self.scanner.results:
            messagebox.showinfo("Information", "No data to export.")
            return
        
        # Get desktop path
        desktop = Path.home() / "Desktop"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"NetToolsScan_{timestamp}"
        
        # Ask for save location with format selection
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("XML files", "*.xml"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ],
            initialdir=desktop,
            initialfile=default_filename
        )
        
        if not filepath:
            return
        
        try:
            file_ext = Path(filepath).suffix.lower()
            
            if file_ext == ".csv":
                self._export_scan_csv(filepath)
            elif file_ext == ".json":
                self._export_scan_json(filepath)
            elif file_ext == ".xml":
                self._export_scan_xml(filepath)
            elif file_ext == ".txt":
                self._export_scan_txt(filepath)
            else:
                # Default to CSV for unknown extensions
                self._export_scan_csv(filepath)
            
            messagebox.showinfo(
                "Export Successful",
                f"Scan results successfully exported to:\n{filepath}"
            )
        except Exception as e:
            messagebox.showerror(
                "Export Error",
                f"Error exporting scan results: {str(e)}"
            )
    
    def _export_scan_csv(self, filepath):
        """Export IP scan to CSV format"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['ip', 'status', 'rtt'])
            writer.writeheader()
            writer.writerows(self.scanner.results)
    
    def _export_scan_json(self, filepath):
        """Export IP scan to JSON format"""
        export_data = {
            'scan_info': {
                'cidr': self.cidr_entry.get(),
                'timestamp': datetime.now().isoformat(),
                'total_hosts': len(self.scanner.results),
                'online': sum(1 for r in self.scanner.results if r['status'] == 'Online'),
                'offline': sum(1 for r in self.scanner.results if r['status'] == 'Offline')
            },
            'results': self.scanner.results
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
    
    def _export_scan_xml(self, filepath):
        """Export IP scan to XML format"""
        root = ET.Element('ipscan')
        
        # Add scan info
        info = ET.SubElement(root, 'scan_info')
        ET.SubElement(info, 'cidr').text = self.cidr_entry.get()
        ET.SubElement(info, 'timestamp').text = datetime.now().isoformat()
        ET.SubElement(info, 'total_hosts').text = str(len(self.scanner.results))
        ET.SubElement(info, 'online').text = str(sum(1 for r in self.scanner.results if r['status'] == 'Online'))
        ET.SubElement(info, 'offline').text = str(sum(1 for r in self.scanner.results if r['status'] == 'Offline'))
        
        # Add results
        results = ET.SubElement(root, 'results')
        for result in self.scanner.results:
            host = ET.SubElement(results, 'host')
            ET.SubElement(host, 'ip').text = result['ip']
            ET.SubElement(host, 'status').text = result['status']
            ET.SubElement(host, 'rtt').text = str(result.get('rtt', ''))
        
        # Write to file
        tree = ET.ElementTree(root)
        ET.indent(tree, space='  ')
        tree.write(filepath, encoding='utf-8', xml_declaration=True)
    
    def _export_scan_txt(self, filepath):
        """Export IP scan to plain text format"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"IP Network Scan Results\n")
            f.write(f"=" * 60 + "\n")
            f.write(f"CIDR: {self.cidr_entry.get()}\n")
            f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Hosts: {len(self.scanner.results)}\n")
            f.write(f"Online: {sum(1 for r in self.scanner.results if r['status'] == 'Online')}\n")
            f.write(f"Offline: {sum(1 for r in self.scanner.results if r['status'] == 'Offline')}\n")
            f.write(f"=" * 60 + "\n\n")
            
            f.write(f"{'IP Address':<18} {'Status':<10} {'RTT (ms)':<15}\n")
            f.write(f"{'-' * 18} {'-' * 10} {'-' * 15}\n")
            
            for result in self.scanner.results:
                rtt_str = str(result.get('rtt', 'N/A'))
                f.write(f"{result['ip']:<18} {result['status']:<10} {rtt_str:<15}\n")
    
    def export_port_scan(self):
        """Export port scan results in multiple formats"""
        if not self.port_scan_results:
            messagebox.showinfo("Information", "No port scan data to export.")
            return
        
        # Get desktop path
        desktop = Path.home() / "Desktop"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"PortScan_{self.port_scan_target.replace('.', '_')}_{timestamp}"
        
        # Ask for save location with format selection
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("XML files", "*.xml"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ],
            initialdir=desktop,
            initialfile=default_filename
        )
        
        if not filepath:
            return
        
        try:
            file_ext = Path(filepath).suffix.lower()
            
            if file_ext == ".csv":
                self._export_port_scan_csv(filepath)
            elif file_ext == ".json":
                self._export_port_scan_json(filepath)
            elif file_ext == ".xml":
                self._export_port_scan_xml(filepath)
            elif file_ext == ".txt":
                self._export_port_scan_txt(filepath)
            else:
                # Default to CSV for unknown extensions
                self._export_port_scan_csv(filepath)
            
            messagebox.showinfo(
                "Export Successful",
                f"Port scan results successfully exported to:\n{filepath}"
            )
        except Exception as e:
            messagebox.showerror(
                "Export Error",
                f"Error exporting port scan results: {str(e)}"
            )
    
    def _export_port_scan_csv(self, filepath):
        """Export port scan to CSV format"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['target', 'port', 'state', 'service'])
            writer.writeheader()
            for result in self.port_scan_results:
                writer.writerow({
                    'target': self.port_scan_target,
                    'port': result['port'],
                    'state': result['state'],
                    'service': result['service']
                })
    
    def _export_port_scan_json(self, filepath):
        """Export port scan to JSON format"""
        export_data = {
            'scan_info': {
                'target': self.port_scan_target,
                'timestamp': datetime.now().isoformat(),
                'total_open_ports': len(self.port_scan_results)
            },
            'results': self.port_scan_results
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
    
    def _export_port_scan_xml(self, filepath):
        """Export port scan to XML format"""
        root = ET.Element('portscan')
        
        # Add scan info
        info = ET.SubElement(root, 'scan_info')
        ET.SubElement(info, 'target').text = self.port_scan_target
        ET.SubElement(info, 'timestamp').text = datetime.now().isoformat()
        ET.SubElement(info, 'total_open_ports').text = str(len(self.port_scan_results))
        
        # Add results
        results = ET.SubElement(root, 'results')
        for result in self.port_scan_results:
            port_elem = ET.SubElement(results, 'port')
            ET.SubElement(port_elem, 'number').text = str(result['port'])
            ET.SubElement(port_elem, 'state').text = result['state']
            ET.SubElement(port_elem, 'service').text = result['service']
        
        # Write to file
        tree = ET.ElementTree(root)
        ET.indent(tree, space='  ')
        tree.write(filepath, encoding='utf-8', xml_declaration=True)
    
    def _export_port_scan_txt(self, filepath):
        """Export port scan to plain text format"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Port Scan Results\n")
            f.write(f"=" * 60 + "\n")
            f.write(f"Target: {self.port_scan_target}\n")
            f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Open Ports: {len(self.port_scan_results)}\n")
            f.write(f"=" * 60 + "\n\n")
            
            f.write(f"{'Port':<10} {'State':<10} {'Service':<20}\n")
            f.write(f"{'-' * 10} {'-' * 10} {'-' * 20}\n")
            
            for result in self.port_scan_results:
                f.write(f"{str(result['port']):<10} {result['state']:<10} {result['service']:<20}\n")
    
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
        
        # Ensure dialog is on top and focused
        history_window.lift()
        history_window.focus_force()
        
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
        
        # Ensure dialog is on top and focused
        history_window.lift()
        history_window.focus_force()
        
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
    
    def refresh_profiles(self):
        """Refresh the profiles list display"""
        # Clear existing
        for widget in self.profiles_frame.winfo_children():
            widget.destroy()
        
        profiles = self.profile_manager.profiles
        
        if not profiles:
            no_profiles_label = ctk.CTkLabel(
                self.profiles_frame,
                text="No saved profiles. Create one to get started!",
                font=ctk.CTkFont(size=12)
            )
            no_profiles_label.pack(pady=20)
            return
        
        # Display profiles in reverse order (newest first)
        for profile in reversed(profiles):
            self.create_profile_card(profile)
    
    def create_profile_card(self, profile):
        """Create a card for a saved profile"""
        card = ctk.CTkFrame(self.profiles_frame, corner_radius=8)
        card.pack(fill="x", pady=5)
        
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=10)
        
        # Profile name
        name_label = ctk.CTkLabel(
            content_frame,
            text=profile["name"],
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True)
        
        # Apply button
        apply_btn = ctk.CTkButton(
            content_frame,
            text="Apply Profile",
            command=lambda p=profile: self.apply_profile(p),
            width=120,
            height=36,
            fg_color=("#2196F3", "#1976D2")
        )
        apply_btn.pack(side="right", padx=(5, 0))
        
        # Delete button
        delete_btn = ctk.CTkButton(
            content_frame,
            text="Delete",
            command=lambda p=profile: self.delete_profile_confirm(p),
            width=80,
            height=36,
            fg_color=("#F44336", "#D32F2F")
        )
        delete_btn.pack(side="right", padx=(5, 0))
        
        # Show interface count
        interface_count = len(profile.get("interfaces", []))
        count_label = ctk.CTkLabel(
            card,
            text=f"{interface_count} interface(s) configured",
            font=ctk.CTkFont(size=11),
            text_color=("gray60", "gray40")
        )
        count_label.pack(padx=15, pady=(0, 10), anchor="w")
    
    def set_dhcp(self, interface_name):
        """Set interface to DHCP"""
        if not self.is_admin():
            # Try to elevate privileges via UAC
            result = messagebox.askyesno(
                "Administrator Required",
                "Administrator privileges are required to change network settings.\n\n"
                "Do you want to restart the application with administrator privileges?"
            )
            if result:
                self.restart_as_admin()
            return
        
        try:
            # Set DHCP for IP
            result = self.run_subprocess(
                ["netsh", "interface", "ipv4", "set", "address", interface_name, "dhcp"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                if "disconnected" in error_msg.lower():
                    messagebox.showwarning(
                        "Interface Disconnected",
                        f"Cannot configure '{interface_name}' because it is currently disconnected.\n\n"
                        "Please connect the network cable or enable Wi-Fi, then try again."
                    )
                else:
                    messagebox.showerror("Error", f"Failed to set DHCP:\n{error_msg}")
                return
            
            # Set DHCP for DNS
            self.run_subprocess(
                ["netsh", "interface", "ipv4", "set", "dnsservers", interface_name, "dhcp"],
                timeout=10
            )
            
            messagebox.showinfo("Success", f"Interface '{interface_name}' set to DHCP successfully!")
            self.refresh_interfaces()
            
        except subprocess.TimeoutExpired:
            messagebox.showerror("Timeout", "The command took too long to execute. Please try again.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
    
    def show_static_ip_dialog(self, interface_name):
        """Show dialog to configure static IP"""
        # Get current config
        current_config = self.get_interface_config(interface_name)
        
        # Create dialog window
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Configure Static IP - {interface_name}")
        dialog.geometry("550x600")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center window
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Ensure dialog is on top and focused
        dialog.lift()
        dialog.focus_force()
        
        # Title section (fixed at top)
        title_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 0))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text=f"Static IP Configuration",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 5))
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text=interface_name,
            font=ctk.CTkFont(size=12)
        )
        subtitle_label.pack(pady=(0, 15))
        
        # Scrollable form frame
        form_scroll = ctk.CTkScrollableFrame(dialog, height=380)
        form_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Inner form frame for consistent padding
        form_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        form_frame.pack(fill="both", expand=True)
        
        # IP Address
        ip_label = ctk.CTkLabel(form_frame, text="IP Address:", font=ctk.CTkFont(size=12, weight="bold"))
        ip_label.pack(pady=(15, 5), anchor="w", padx=15)
        
        ip_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., 192.168.1.100", height=40)
        ip_entry.pack(fill="x", padx=15)
        if current_config and current_config["ip"]:
            ip_entry.insert(0, current_config["ip"])
        
        # Subnet Mask
        subnet_label = ctk.CTkLabel(form_frame, text="Subnet Mask:", font=ctk.CTkFont(size=12, weight="bold"))
        subnet_label.pack(pady=(15, 5), anchor="w", padx=15)
        
        subnet_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., 255.255.255.0", height=40)
        subnet_entry.pack(fill="x", padx=15)
        if current_config and current_config["subnet"]:
            subnet_entry.insert(0, current_config["subnet"])
        else:
            subnet_entry.insert(0, "255.255.255.0")
        
        # Default Gateway
        gateway_label = ctk.CTkLabel(form_frame, text="Default Gateway:", font=ctk.CTkFont(size=12, weight="bold"))
        gateway_label.pack(pady=(15, 5), anchor="w", padx=15)
        
        gateway_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., 192.168.1.1", height=40)
        gateway_entry.pack(fill="x", padx=15)
        if current_config and current_config["gateway"]:
            gateway_entry.insert(0, current_config["gateway"])
        
        # DNS Server (Primary)
        dns_label = ctk.CTkLabel(form_frame, text="Primary DNS:", font=ctk.CTkFont(size=12, weight="bold"))
        dns_label.pack(pady=(15, 5), anchor="w", padx=15)
        
        dns_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., 8.8.8.8 (optional)", height=40)
        dns_entry.pack(fill="x", padx=15, pady=(0, 15))
        if current_config and current_config["dns"] and len(current_config["dns"]) > 0:
            dns_entry.insert(0, current_config["dns"][0])
        
        # Button frame (fixed at bottom)
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", side="bottom", padx=20, pady=20)
        
        def apply_static():
            ip = ip_entry.get().strip()
            subnet = subnet_entry.get().strip()
            gateway = gateway_entry.get().strip()
            dns = dns_entry.get().strip()
            
            if not ip:
                messagebox.showwarning("Invalid Input", "IP Address is required")
                return
            
            if not subnet:
                messagebox.showwarning("Invalid Input", "Subnet Mask is required")
                return
            
            self.set_static_ip(interface_name, ip, subnet, gateway, dns)
            dialog.destroy()
        
        apply_btn = ctk.CTkButton(
            button_frame,
            text="Apply",
            command=apply_static,
            width=120,
            height=40,
            fg_color=("#4CAF50", "#388E3C")
        )
        apply_btn.pack(side="left", padx=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            width=120,
            height=40
        )
        cancel_btn.pack(side="left")
    
    def set_static_ip(self, interface_name, ip, subnet, gateway, dns):
        """Set static IP configuration"""
        if not self.is_admin():
            result = messagebox.askyesno(
                "Administrator Required",
                "Administrator privileges are required to change network settings.\n\n"
                "Do you want to restart the application with administrator privileges?"
            )
            if result:
                self.restart_as_admin()
            return
        
        try:
            # Build command
            if gateway:
                cmd = ["netsh", "interface", "ipv4", "set", "address", interface_name, "static", ip, subnet, gateway]
            else:
                cmd = ["netsh", "interface", "ipv4", "set", "address", interface_name, "static", ip, subnet]
            
            result = self.run_subprocess(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                if "disconnected" in error_msg.lower():
                    messagebox.showwarning(
                        "Interface Disconnected",
                        f"Cannot configure '{interface_name}' because it is currently disconnected.\n\n"
                        "Please connect the network cable or enable Wi-Fi, then try again."
                    )
                elif "not valid" in error_msg.lower() or "incorrect" in error_msg.lower():
                    messagebox.showerror(
                        "Invalid Configuration",
                        f"The IP configuration is invalid:\n\n{error_msg}\n\n"
                        "Please check:\n"
                        "• IP address format (e.g., 192.168.1.100)\n"
                        "• Subnet mask format (e.g., 255.255.255.0)\n"
                        "• Gateway is in the same subnet"
                    )
                else:
                    messagebox.showerror("Error", f"Failed to set static IP:\n{error_msg}")
                return
            
            # Set DNS if provided
            if dns:
                self.run_subprocess(
                    ["netsh", "interface", "ipv4", "set", "dnsservers", interface_name, "static", dns, "primary"],
                    timeout=10
                )
            
            messagebox.showinfo("Success", f"Static IP configured successfully!\n\nIP: {ip}\nSubnet: {subnet}")
            self.refresh_interfaces()
            
        except subprocess.TimeoutExpired:
            messagebox.showerror("Timeout", "The command took too long to execute. Please try again.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
    
    def create_new_profile(self):
        """Show dialog to create and configure a new profile"""
        # Get current interfaces
        interfaces = self.get_network_interfaces()
        
        if not interfaces:
            messagebox.showerror("Error", "No network interfaces found.")
            return
        
        # Create dialog window
        dialog = ctk.CTkToplevel(self)
        dialog.title("Create Network Profile")
        dialog.geometry("800x700")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center window
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Ensure dialog is on top and focused
        dialog.lift()
        dialog.focus_force()
        
        # Title
        title_label = ctk.CTkLabel(
            dialog,
            text="Create Network Profile",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(padx=20, pady=(20, 10))
        
        # Profile name
        name_frame = ctk.CTkFrame(dialog)
        name_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        name_label = ctk.CTkLabel(
            name_frame,
            text="Profile Name:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        name_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        name_entry = ctk.CTkEntry(
            name_frame,
            placeholder_text="e.g., Home Network, Office WiFi",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        name_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Instructions
        info_label = ctk.CTkLabel(
            dialog,
            text="Select interfaces to configure and set their network settings:",
            font=ctk.CTkFont(size=11),
            text_color=("gray60", "gray40")
        )
        info_label.pack(padx=20, pady=(0, 10))
        
        # Scrollable frame for interfaces
        scroll_frame = ctk.CTkScrollableFrame(dialog, height=400)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Store interface configurations
        interface_configs = {}
        
        # Display configurable interfaces
        for interface in interfaces:
            interface_frame = ctk.CTkFrame(scroll_frame, corner_radius=8)
            interface_frame.pack(fill="x", pady=5)
            
            # Checkbox to include this interface
            include_var = ctk.BooleanVar(value=True)
            include_check = ctk.CTkCheckBox(
                interface_frame,
                text=f"📶 {interface['name']}",
                variable=include_var,
                font=ctk.CTkFont(size=12, weight="bold")
            )
            include_check.pack(anchor="w", padx=10, pady=(10, 5))
            
            # Configuration section
            config_frame = ctk.CTkFrame(interface_frame, fg_color="transparent")
            config_frame.pack(fill="x", padx=20, pady=(0, 10))
            
            # DHCP or Static
            dhcp_var = ctk.StringVar(value="dhcp")
            
            # Function to toggle static fields (defined before widgets)
            def toggle_static_fields(*args):
                if dhcp_var.get() == "static":
                    ip_entry.configure(state="normal")
                    mask_entry.configure(state="normal")
                    gateway_entry.configure(state="normal")
                    dns_entry.configure(state="normal")
                else:
                    ip_entry.configure(state="disabled")
                    mask_entry.configure(state="disabled")
                    gateway_entry.configure(state="disabled")
                    dns_entry.configure(state="disabled")
            
            # Radio buttons at the top
            dhcp_radio = ctk.CTkRadioButton(
                config_frame,
                text="DHCP (Automatic)",
                variable=dhcp_var,
                value="dhcp",
                command=toggle_static_fields
            )
            dhcp_radio.pack(anchor="w", pady=2)
            
            static_radio = ctk.CTkRadioButton(
                config_frame,
                text="Static (Manual)",
                variable=dhcp_var,
                value="static",
                command=toggle_static_fields
            )
            static_radio.pack(anchor="w", pady=2)
            
            # Static IP fields frame
            static_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
            static_frame.pack(fill="x", pady=(10, 0))
            
            # IP Address (Required)
            ip_label = ctk.CTkLabel(static_frame, text="IP Address: *", font=ctk.CTkFont(size=11))
            ip_label.grid(row=0, column=0, sticky="w", pady=2)
            ip_entry = ctk.CTkEntry(static_frame, placeholder_text="192.168.1.100", width=150, state="disabled")
            ip_entry.grid(row=0, column=1, padx=(10, 0), pady=2)
            
            # Subnet Mask (Required)
            mask_label = ctk.CTkLabel(static_frame, text="Subnet Mask: *", font=ctk.CTkFont(size=11))
            mask_label.grid(row=1, column=0, sticky="w", pady=2)
            mask_entry = ctk.CTkEntry(static_frame, placeholder_text="255.255.255.0", width=150, state="disabled")
            mask_entry.grid(row=1, column=1, padx=(10, 0), pady=2)
            
            # Gateway (Optional)
            gateway_label = ctk.CTkLabel(static_frame, text="Gateway (Optional):", font=ctk.CTkFont(size=11))
            gateway_label.grid(row=2, column=0, sticky="w", pady=2)
            gateway_entry = ctk.CTkEntry(static_frame, placeholder_text="192.168.1.1", width=150, state="disabled")
            gateway_entry.grid(row=2, column=1, padx=(10, 0), pady=2)
            
            # DNS (Optional)
            dns_label = ctk.CTkLabel(static_frame, text="DNS Server (Optional):", font=ctk.CTkFont(size=11))
            dns_label.grid(row=3, column=0, sticky="w", pady=2)
            dns_entry = ctk.CTkEntry(static_frame, placeholder_text="8.8.8.8, 8.8.4.4", width=150, state="disabled")
            dns_entry.grid(row=3, column=1, padx=(10, 0), pady=2)
            
            # Help text
            help_label = ctk.CTkLabel(
                static_frame,
                text="* Required fields. DNS supports multiple servers (comma-separated).",
                font=ctk.CTkFont(size=10),
                text_color=("gray60", "gray40")
            )
            help_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=(8, 0))
            
            # Store references
            interface_configs[interface['name']] = {
                'include': include_var,
                'dhcp_var': dhcp_var,
                'ip_entry': ip_entry,
                'mask_entry': mask_entry,
                'gateway_entry': gateway_entry,
                'dns_entry': dns_entry
            }
        
        # Button frame
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        def save_profile():
            """Save the configured profile"""
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter a profile name.")
                return
            
            # Collect selected interface configurations
            saved_interfaces = []
            for interface_name, config_refs in interface_configs.items():
                if not config_refs['include'].get():
                    continue  # Skip unchecked interfaces
                
                # Build configuration
                if config_refs['dhcp_var'].get() == "dhcp":
                    config = {
                        "dhcp": True,
                        "ip": None,
                        "subnet": None,
                        "gateway": None,
                        "dns": []
                    }
                else:
                    ip = config_refs['ip_entry'].get().strip()
                    mask = config_refs['mask_entry'].get().strip()
                    gateway = config_refs['gateway_entry'].get().strip()
                    dns_input = config_refs['dns_entry'].get().strip()
                    
                    if not ip or not mask:
                        messagebox.showwarning("Warning", f"Static IP requires IP address and subnet mask for {interface_name}")
                        return
                    
                    # Parse DNS servers (support comma-separated list)
                    dns_servers = []
                    if dns_input:
                        dns_servers = [d.strip() for d in dns_input.split(',') if d.strip()]
                    
                    config = {
                        "dhcp": False,
                        "ip": ip,
                        "subnet": mask,
                        "subnet_mask": mask,
                        "gateway": gateway if gateway else None,
                        "dns": dns_servers
                    }
                
                saved_interfaces.append({
                    "name": interface_name,
                    "config": config
                })
            
            if not saved_interfaces:
                messagebox.showwarning("Warning", "Please select at least one interface to configure.")
                return
            
            # Save profile
            self.profile_manager.add_profile(name, saved_interfaces)
            self.refresh_profiles()
            
            dialog.destroy()
            messagebox.showinfo("Success", f"Profile '{name}' created with {len(saved_interfaces)} interface(s)!")
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Create Profile",
            command=save_profile,
            width=160,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"]
        )
        save_btn.pack(side="right", padx=(10, 0))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        cancel_btn.pack(side="right")
    
    def apply_profile(self, profile):
        """Apply a saved profile"""
        if not self.is_admin():
            # Offer to restart as admin
            result = messagebox.askyesno(
                "Admin Required",
                "Administrator privileges are required to apply profiles.\n\nWould you like to restart the application as administrator?"
            )
            if result:
                self.restart_as_admin()
            return
        
        # Confirmation dialog
        result = messagebox.askyesno(
            "Apply Profile",
            f"Are you sure you want to apply the profile '{profile['name']}'?\n\nThis will change network settings for all configured interfaces."
        )
        
        if not result:
            return
        
        # Show progress message
        progress_label = ctk.CTkLabel(
            self.profiles_frame.master,
            text=f"Applying profile '{profile['name']}'...",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["primary"]
        )
        progress_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Apply profile in background thread
        def apply_in_background():
            try:
                success_count = 0
                error_count = 0
                errors = []
                
                for interface_data in profile["interfaces"]:
                    interface_name = interface_data["name"]
                    config = interface_data["config"]
                    
                    try:
                        # Check if interface still exists
                        current_interfaces = self.get_network_interfaces()
                        if not any(i["name"] == interface_name for i in current_interfaces):
                            errors.append(f"{interface_name}: Interface not found")
                            error_count += 1
                            continue
                        
                        # Apply configuration
                        if config["dhcp"]:
                            # Set to DHCP
                            result = self.run_subprocess(
                                ["netsh", "interface", "ipv4", "set", "address", 
                                 interface_name, "dhcp"],
                                capture_output=True,
                                text=True,
                                timeout=10
                            )
                            
                            if result.returncode == 0:
                                # Set DNS to DHCP
                                self.run_subprocess(
                                    ["netsh", "interface", "ipv4", "set", "dnsservers",
                                     interface_name, "dhcp"],
                                    capture_output=True,
                                    text=True,
                                    timeout=10
                                )
                                success_count += 1
                            else:
                                errors.append(f"{interface_name}: Failed to set DHCP")
                                error_count += 1
                        else:
                            # Set static IP
                            if config["ip"] and config["subnet"]:
                                # Determine subnet mask from prefix or use default
                                subnet_mask = config.get("subnet_mask", config.get("subnet", "255.255.255.0"))
                                gateway = config.get("gateway", "none")
                                
                                # Build netsh command for static IP
                                cmd = [
                                    "netsh", "interface", "ipv4", "set", "address",
                                    "name=" + interface_name,
                                    "source=static",
                                    "address=" + config["ip"],
                                    "mask=" + subnet_mask,
                                    "gateway=" + gateway
                                ]
                                
                                result = self.run_subprocess(
                                    cmd,
                                    capture_output=True,
                                    text=True,
                                    encoding='cp850',
                                    timeout=15
                                )
                                
                                if result.returncode == 0:
                                    # Set DNS if configured
                                    if config.get("dns") and len(config["dns"]) > 0:
                                        for i, dns in enumerate(config["dns"]):
                                            if dns.strip():  # Only add non-empty DNS
                                                if i == 0:
                                                    # Primary DNS
                                                    dns_cmd = [
                                                        "netsh", "interface", "ipv4", "set", "dns",
                                                        "name=" + interface_name,
                                                        "source=static",
                                                        "address=" + dns,
                                                        "register=primary"
                                                    ]
                                                else:
                                                    # Additional DNS servers
                                                    dns_cmd = [
                                                        "netsh", "interface", "ipv4", "add", "dns",
                                                        "name=" + interface_name,
                                                        "address=" + dns,
                                                        "index=" + str(i + 1)
                                                    ]
                                                self.run_subprocess(dns_cmd, capture_output=True, timeout=10)
                                    
                                    success_count += 1
                                else:
                                    error_msg = result.stderr if result.stderr else "Unknown error"
                                    errors.append(f"{interface_name}: {error_msg[:100]}")
                                    error_count += 1
                            else:
                                errors.append(f"{interface_name}: Missing IP or subnet mask")
                                error_count += 1
                    
                    except Exception as e:
                        errors.append(f"{interface_name}: {str(e)}")
                        error_count += 1
                
                # Hide progress and show results
                self.after(0, lambda: progress_label.destroy())
                self.after(0, self.refresh_interfaces)
                
                if error_count == 0:
                    self.after(0, lambda: messagebox.showinfo(
                        "Success",
                        f"Profile '{profile['name']}' applied successfully!\n\n{success_count} interface(s) configured."
                    ))
                else:
                    error_msg = f"Profile partially applied.\n\nSuccessful: {success_count}\nFailed: {error_count}"
                    if errors:
                        error_msg += f"\n\nErrors:\n" + "\n".join(errors[:5])
                    self.after(0, lambda: messagebox.showwarning(
                        "Partial Success",
                        error_msg
                    ))
            
            except Exception as e:
                self.after(0, lambda: progress_label.destroy())
                self.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Error applying profile: {str(e)}"
                ))
        
        # Run in thread
        thread = threading.Thread(target=apply_in_background, daemon=True)
        thread.start()
    
    def delete_profile_confirm(self, profile):
        """Confirm and delete a profile"""
        result = messagebox.askyesno(
            "Delete Profile",
            f"Are you sure you want to delete the profile '{profile['name']}'?\n\nThis cannot be undone."
        )
        
        if result:
            self.profile_manager.delete_profile(profile["id"])
            self.refresh_profiles()
            messagebox.showinfo("Success", f"Profile '{profile['name']}' deleted successfully.")
    
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
        
        # Ensure dialog is on top and focused
        comp_window.lift()
        comp_window.focus_force()
        
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
    
    def create_traceroute_content(self, parent):
        """Create Traceroute and Pathping page content"""
        # Scrollable content area
        scrollable = ctk.CTkScrollableFrame(parent)
        scrollable.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            scrollable,
            text="Traceroute & Pathping",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 5))
        
        subtitle_label = ctk.CTkLabel(
            scrollable,
            text="Trace network path and analyze packet loss and latency",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        subtitle_label.pack(pady=(0, 5))
        
        # System info
        system_info = ctk.CTkLabel(
            scrollable,
            text=f"Platform: {platform.system()} | Note: Requires Windows for tracert/pathping commands",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        )
        system_info.pack(pady=(0, 15))
        
        # Input Section
        input_frame = ctk.CTkFrame(scrollable, corner_radius=8)
        input_frame.pack(fill="x", pady=(0, 15))
        
        # Target input
        target_label = ctk.CTkLabel(
            input_frame,
            text="Target Host or IP:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        target_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        target_entry_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        target_entry_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.traceroute_target_entry = ctk.CTkEntry(
            target_entry_frame,
            placeholder_text="e.g., google.com or 8.8.8.8",
            height=38,
            font=ctk.CTkFont(size=13)
        )
        self.traceroute_target_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Tool Selection
        tool_frame = ctk.CTkFrame(scrollable, corner_radius=8)
        tool_frame.pack(fill="x", pady=(0, 15))
        
        tool_label = ctk.CTkLabel(
            tool_frame,
            text="Select Tool:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        tool_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Tool radio buttons
        self.trace_tool_var = ctk.StringVar(value="tracert")
        
        tracert_frame = ctk.CTkFrame(tool_frame, fg_color="transparent")
        tracert_frame.pack(fill="x", padx=15, pady=(0, 5))
        
        tracert_radio = ctk.CTkRadioButton(
            tracert_frame,
            text="Traceroute (tracert)",
            variable=self.trace_tool_var,
            value="tracert",
            font=ctk.CTkFont(size=12)
        )
        tracert_radio.pack(side="left")
        
        tracert_info = ctk.CTkLabel(
            tracert_frame,
            text="Fast - Shows route path with latency per hop",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        )
        tracert_info.pack(side="left", padx=(10, 0))
        
        pathping_frame = ctk.CTkFrame(tool_frame, fg_color="transparent")
        pathping_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        pathping_radio = ctk.CTkRadioButton(
            pathping_frame,
            text="Pathping",
            variable=self.trace_tool_var,
            value="pathping",
            font=ctk.CTkFont(size=12)
        )
        pathping_radio.pack(side="left")
        
        pathping_info = ctk.CTkLabel(
            pathping_frame,
            text="Detailed - Includes packet loss statistics (takes ~5 minutes)",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        )
        pathping_info.pack(side="left", padx=(10, 0))
        
        # Options
        options_frame = ctk.CTkFrame(scrollable, corner_radius=8)
        options_frame.pack(fill="x", pady=(0, 15))
        
        options_label = ctk.CTkLabel(
            options_frame,
            text="Options:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        options_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Max hops option
        hops_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        hops_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        hops_label = ctk.CTkLabel(
            hops_frame,
            text="Max Hops:",
            font=ctk.CTkFont(size=11)
        )
        hops_label.pack(side="left")
        
        self.traceroute_maxhops_entry = ctk.CTkEntry(
            hops_frame,
            width=80,
            height=32,
            placeholder_text="30"
        )
        self.traceroute_maxhops_entry.insert(0, "30")
        self.traceroute_maxhops_entry.pack(side="left", padx=(10, 0))
        
        hops_info = ctk.CTkLabel(
            hops_frame,
            text="(Default: 30, Range: 1-255)",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        )
        hops_info.pack(side="left", padx=(10, 0))
        
        # Action Buttons
        button_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 15))
        
        self.trace_start_btn = ctk.CTkButton(
            button_frame,
            text="▶ Start Trace",
            command=self.start_traceroute,
            width=160,
            height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"]
        )
        self.trace_start_btn.pack(side="left", padx=(0, 10))
        
        self.trace_cancel_btn = ctk.CTkButton(
            button_frame,
            text="⏹ Cancel",
            command=self.cancel_traceroute,
            width=120,
            height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled",
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"]
        )
        self.trace_cancel_btn.pack(side="left", padx=(0, 10))
        
        self.trace_export_btn = ctk.CTkButton(
            button_frame,
            text="📤 Export Results",
            command=self.export_traceroute,
            width=160,
            height=42,
            font=ctk.CTkFont(size=14),
            state="disabled",
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"]
        )
        self.trace_export_btn.pack(side="left")
        
        # Progress label
        self.trace_progress_label = ctk.CTkLabel(
            scrollable,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        self.trace_progress_label.pack(pady=(0, 10))
        
        # Results Section
        results_title = ctk.CTkLabel(
            scrollable,
            text="Results",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        results_title.pack(pady=(10, 10), anchor="w")
        
        self.traceroute_results_frame = ctk.CTkFrame(scrollable, corner_radius=8)
        self.traceroute_results_frame.pack(fill="both", expand=True)
        
        # Initial message
        no_results_label = ctk.CTkLabel(
            self.traceroute_results_frame,
            text="No results yet. Enter a target and start trace.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        no_results_label.pack(pady=50)
        
        # State tracking
        self.trace_running = False
        self.trace_process = None
        self.trace_results_text = ""
    
    def start_traceroute(self):
        """Start traceroute or pathping"""
        target = self.traceroute_target_entry.get().strip()
        if not target:
            messagebox.showwarning("Input Required", "Please enter a target host or IP address")
            return
        
        # Validate max hops
        try:
            max_hops = int(self.traceroute_maxhops_entry.get())
            if not 1 <= max_hops <= 255:
                raise ValueError()
        except:
            messagebox.showwarning("Invalid Input", "Max hops must be between 1 and 255")
            return
        
        # Update UI
        self.trace_start_btn.configure(state="disabled")
        self.trace_cancel_btn.configure(state="normal")
        self.trace_export_btn.configure(state="disabled")
        self.trace_running = True
        
        # Clear previous results
        for widget in self.traceroute_results_frame.winfo_children():
            widget.destroy()
        
        # Show progress
        tool_name = "Traceroute" if self.trace_tool_var.get() == "tracert" else "Pathping"
        time_estimate = "~30 seconds" if self.trace_tool_var.get() == "tracert" else "~5 minutes"
        self.trace_progress_label.configure(
            text=f"⏳ Running {tool_name} to {target}... (estimated time: {time_estimate})"
        )
        
        # Run in background thread
        def trace_thread():
            try:
                tool = self.trace_tool_var.get()
                
                if tool == "tracert":
                    cmd = ["tracert", "-h", str(max_hops), target]
                else:
                    cmd = ["pathping", "-h", str(max_hops), target]
                
                # Run command with explicit settings
                if platform.system() == "Windows":
                    # Windows - use CREATE_NO_WINDOW flag
                    import subprocess
                    
                    # For pathping, use same approach as tracert with longer timeout
                    if tool == "pathping":
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=600,
                            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
                            shell=False,
                            encoding='cp850',  # Windows console encoding
                            errors='replace'    # Replace invalid characters
                        )
                    else:
                        # For tracert, regular run is fine
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=600,
                            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
                            shell=False,
                            encoding='cp850'  # Use Windows console encoding
                        )
                else:
                    # Non-Windows (shouldn't happen, but fallback)
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=600,
                        shell=False
                    )
                
                # Capture both stdout and stderr - pathping might use either
                output = ""
                stdout_data = result.stdout if result.stdout else ""
                stderr_data = result.stderr if result.stderr else ""
                
                # Debug info
                debug_info = f"Debug Info:\n"
                debug_info += f"Command: {' '.join(cmd)}\n"
                debug_info += f"Return code: {result.returncode}\n"
                debug_info += f"Stdout length: {len(stdout_data)} chars\n"
                debug_info += f"Stderr length: {len(stderr_data)} chars\n"
                debug_info += f"Stdout first 200 chars: {repr(stdout_data[:200])}\n"
                debug_info += f"Stderr first 200 chars: {repr(stderr_data[:200])}\n"
                
                # Try stdout first
                if stdout_data and len(stdout_data.strip()) > 0:
                    output = stdout_data
                    if stderr_data and len(stderr_data.strip()) > 0:
                        output += f"\n\n--- Stderr Output ---\n{stderr_data}"
                # Try stderr if no stdout
                elif stderr_data and len(stderr_data.strip()) > 0:
                    output = stderr_data
                # No output at all
                else:
                    output = f"Command completed but produced no output.\n\n{debug_info}"
                
                # Store results
                self.trace_results_text = output
                
                # Update UI in main thread
                success = bool(output and result.returncode in [0, 1])  # tracert returns 1 on some errors but still has output
                self.after(0, self.display_traceroute_results, output, success)
                
            except subprocess.TimeoutExpired:
                error_msg = f"Command timeout (10 minutes exceeded)\nCommand: {' '.join(cmd)}"
                self.after(0, self.display_traceroute_results, error_msg, False)
            except FileNotFoundError:
                error_msg = f"Command not found: {cmd[0]}\nThis command may not be available on your system."
                self.after(0, self.display_traceroute_results, error_msg, False)
            except Exception as e:
                error_msg = f"Error executing command:\n{str(e)}\n\nCommand: {' '.join(cmd)}"
                self.after(0, self.display_traceroute_results, error_msg, False)
        
        thread = threading.Thread(target=trace_thread, daemon=True)
        thread.start()
    
    def cancel_traceroute(self):
        """Cancel running trace"""
        self.trace_running = False
        if self.trace_process:
            try:
                self.trace_process.terminate()
            except:
                pass
        
        self.trace_start_btn.configure(state="normal")
        self.trace_cancel_btn.configure(state="disabled")
        self.trace_progress_label.configure(text="Trace cancelled")
    
    def display_traceroute_results(self, output, success):
        """Display traceroute/pathping results"""
        # Clear results frame
        for widget in self.traceroute_results_frame.winfo_children():
            widget.destroy()
        
        # Update UI state
        self.trace_start_btn.configure(state="normal")
        self.trace_cancel_btn.configure(state="disabled")
        self.trace_running = False
        
        if success:
            self.trace_progress_label.configure(text="✅ Trace complete")
            self.trace_export_btn.configure(state="normal")
        else:
            self.trace_progress_label.configure(text="❌ Trace failed or encountered errors")
            # Still allow export even if there are errors - might have partial results
            if output and len(output) > 50:
                self.trace_export_btn.configure(state="normal")
            else:
                self.trace_export_btn.configure(state="disabled")
        
        # Create info header
        info_frame = ctk.CTkFrame(self.traceroute_results_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=f"Output length: {len(output)} characters",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        info_label.pack(side="left")
        
        # Create scrollable text widget for results
        results_scroll = ctk.CTkScrollableFrame(self.traceroute_results_frame)
        results_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # If output is empty or very short, show helpful message
        if not output or len(output) < 10:
            error_label = ctk.CTkLabel(
                results_scroll,
                text="No output received from command.\n\nPossible causes:\n• Command not found on system\n• Insufficient permissions\n• Network adapter issue\n\nTry running NetTools as Administrator.",
                font=ctk.CTkFont(size=13),
                text_color=COLORS["danger"],
                justify="left"
            )
            error_label.pack(pady=20)
            return
        
        # Parse and display results with formatting
        lines = output.split('\n')
        
        # Show total line count
        line_count_label = ctk.CTkLabel(
            results_scroll,
            text=f"Total lines: {len(lines)}",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        line_count_label.pack(pady=(0, 10))
        
        for idx, line in enumerate(lines):
            # Keep empty lines for spacing but limit consecutive empties
            if not line.strip():
                ctk.CTkLabel(results_scroll, text=" ", height=5).pack()
                continue
            
            # Color code different types of lines
            text_color = COLORS["text_primary"]
            font_weight = "normal"
            
            # Headers
            if "Tracing" in line or "Computing" in line or "over a maximum" in line:
                text_color = COLORS["primary"]
                font_weight = "bold"
            # Hop numbers (lines starting with numbers)
            elif line.strip() and line.strip()[0].isdigit():
                text_color = COLORS["text_primary"]
            # Timeouts
            elif "*" in line or "Request timed out" in line or "timed out" in line.lower():
                text_color = COLORS["warning"]
            # Errors
            elif "error" in line.lower() or "failed" in line.lower() or "unable" in line.lower():
                text_color = COLORS["danger"]
                font_weight = "bold"
            # Summary lines (pathping)
            elif "%" in line or "Loss" in line or "Sent" in line:
                text_color = COLORS["success"]
            # Complete messages
            elif "complete" in line.lower():
                text_color = COLORS["success"]
                font_weight = "bold"
            
            line_label = ctk.CTkLabel(
                results_scroll,
                text=line,
                font=ctk.CTkFont(size=12, weight=font_weight, family="Courier New"),
                anchor="w",
                justify="left",
                text_color=text_color
            )
            line_label.pack(fill="x", pady=2)
    
    def export_traceroute(self):
        """Export traceroute results"""
        if not self.trace_results_text:
            messagebox.showinfo("No Data", "No traceroute data to export")
            return
        
        # Get desktop path
        desktop = Path.home() / "Desktop"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = self.traceroute_target_entry.get().strip().replace(".", "_")
        tool = "tracert" if self.trace_tool_var.get() == "tracert" else "pathping"
        default_filename = f"{tool}_{target}_{timestamp}.txt"
        
        # Ask for save location
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=desktop,
            initialfile=default_filename
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Traceroute/Pathping Results\n")
                f.write(f"=" * 60 + "\n")
                f.write(f"Target: {self.traceroute_target_entry.get()}\n")
                f.write(f"Tool: {self.trace_tool_var.get()}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"=" * 60 + "\n\n")
                f.write(self.trace_results_text)
            
            messagebox.showinfo(
                "Export Successful",
                f"Results exported to:\n{filepath}"
            )
        except Exception as e:
            messagebox.showerror(
                "Export Error",
                f"Error exporting results: {str(e)}"
            )
    
    def create_phpipam_content(self, parent):
        """Create phpIPAM integration page content"""
        if not PHPIPAM_AVAILABLE:
            # Show error if modules not available
            error_frame = ctk.CTkFrame(parent)
            error_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            error_label = ctk.CTkLabel(
                error_frame,
                text="⚠️ phpIPAM Integration Unavailable",
                font=ctk.CTkFont(size=24, weight="bold")
            )
            error_label.pack(pady=(50, 10))
            
            msg_label = ctk.CTkLabel(
                error_frame,
                text="Required modules are missing. Please install:\n\npip install cryptography requests",
                font=ctk.CTkFont(size=14)
            )
            msg_label.pack(pady=20)
            return
        
        # Initialize phpIPAM config
        self.phpipam_config = PHPIPAMConfig()
        self.phpipam_client = None
        
        # Scrollable content area
        scrollable = ctk.CTkScrollableFrame(parent)
        scrollable.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            scrollable,
            text="phpIPAM Integration",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 5))
        
        subtitle_label = ctk.CTkLabel(
            scrollable,
            text="Manage IP addresses with phpIPAM API",
            font=ctk.CTkFont(size=12)
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Status Section
        status_frame = ctk.CTkFrame(scrollable, corner_radius=8)
        status_frame.pack(fill="x", pady=(0, 15))
        
        status_title = ctk.CTkLabel(
            status_frame,
            text="Connection Status",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        status_title.pack(pady=(15, 5), padx=15, anchor="w")
        
        self.phpipam_status_label = ctk.CTkLabel(
            status_frame,
            text="⚪ Not configured" if not self.phpipam_config.is_enabled() else "🟢 Enabled",
            font=ctk.CTkFont(size=12)
        )
        self.phpipam_status_label.pack(pady=(0, 15), padx=15, anchor="w")
        
        # Action buttons
        button_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 15))
        
        settings_btn = ctk.CTkButton(
            button_frame,
            text="⚙️ Settings",
            command=self.show_phpipam_settings,
            width=140,
            height=42,
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"]
        )
        settings_btn.pack(side="left", padx=(0, 10))
        
        test_btn = ctk.CTkButton(
            button_frame,
            text="🔌 Test Connection",
            command=self.test_phpipam_connection,
            width=180,
            height=42,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"]
        )
        test_btn.pack(side="left", padx=(0, 10))
        
        auth_btn = ctk.CTkButton(
            button_frame,
            text="🔑 Authenticate",
            command=self.authenticate_phpipam,
            width=160,
            height=42,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"]
        )
        auth_btn.pack(side="left")
        
        # Operations Section
        ops_frame = ctk.CTkFrame(scrollable, corner_radius=8)
        ops_frame.pack(fill="x", pady=(0, 15))
        
        ops_title = ctk.CTkLabel(
            ops_frame,
            text="Operations",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        ops_title.pack(pady=(15, 10), padx=15, anchor="w")
        
        # IP Search
        search_frame = ctk.CTkFrame(ops_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="Search IP Address:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        search_label.pack(anchor="w", pady=(0, 5))
        
        search_entry_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_entry_frame.pack(fill="x")
        
        self.phpipam_search_entry = ctk.CTkEntry(
            search_entry_frame,
            placeholder_text="e.g., 192.168.1.10",
            height=38,
            font=ctk.CTkFont(size=13)
        )
        self.phpipam_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        search_btn = ctk.CTkButton(
            search_entry_frame,
            text="🔍 Search",
            command=self.search_phpipam_ip,
            width=120,
            height=38,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"]
        )
        search_btn.pack(side="left")
        
        # View Subnets
        subnet_btn_frame = ctk.CTkFrame(ops_frame, fg_color="transparent")
        subnet_btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        view_subnets_btn = ctk.CTkButton(
            subnet_btn_frame,
            text="📋 View All Subnets",
            command=self.view_phpipam_subnets,
            width=200,
            height=38,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"]
        )
        view_subnets_btn.pack(side="left")
        
        # Results Section
        results_header_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        results_header_frame.pack(fill="x", pady=(10, 10))
        
        results_title = ctk.CTkLabel(
            results_header_frame,
            text="Results",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        results_title.pack(side="left", anchor="w")
        
        # Filter box for results
        filter_frame = ctk.CTkFrame(scrollable, corner_radius=6)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        filter_label = ctk.CTkLabel(
            filter_frame,
            text="Filter results:",
            font=ctk.CTkFont(size=11)
        )
        filter_label.pack(side="left", padx=(10, 5))
        
        self.phpipam_filter_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Type to filter displayed results...",
            height=32,
            width=300
        )
        self.phpipam_filter_entry.pack(side="left", padx=5)
        self.phpipam_filter_entry.bind('<KeyRelease>', self._filter_phpipam_results)
        
        clear_filter_btn = ctk.CTkButton(
            filter_frame,
            text="✕",
            command=lambda: (self.phpipam_filter_entry.delete(0, 'end'), self._filter_phpipam_results()),
            width=30,
            height=32,
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"]
        )
        clear_filter_btn.pack(side="left", padx=(0, 10))
        
        self.phpipam_results_frame = ctk.CTkFrame(scrollable, corner_radius=8)
        self.phpipam_results_frame.pack(fill="both", expand=True)
        
        # Initial message
        no_results_label = ctk.CTkLabel(
            self.phpipam_results_frame,
            text="No results yet. Configure settings and perform an operation.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        no_results_label.pack(pady=50)
    
    def show_phpipam_settings(self):
        """Show phpIPAM settings dialog"""
        if not PHPIPAM_AVAILABLE:
            messagebox.showerror("Error", "phpIPAM modules not available")
            return
        
        # Create settings dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("phpIPAM Settings")
        dialog.geometry("600x700")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center window
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Ensure dialog is on top and focused
        dialog.lift()
        dialog.focus_force()
        
        # Content
        content = ctk.CTkScrollableFrame(dialog)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            content,
            text="phpIPAM Configuration",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Enable/Disable
        enabled_var = ctk.BooleanVar(value=self.phpipam_config.is_enabled())
        enabled_check = ctk.CTkCheckBox(
            content,
            text="Enable phpIPAM Integration",
            variable=enabled_var,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        enabled_check.pack(anchor="w", pady=(0, 20))
        
        # phpIPAM URL
        url_label = ctk.CTkLabel(
            content,
            text="phpIPAM URL:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        url_label.pack(anchor="w", pady=(0, 5))
        
        url_entry = ctk.CTkEntry(
            content,
            placeholder_text="https://ipam.example.com",
            height=38
        )
        url_entry.insert(0, self.phpipam_config.get_phpipam_url())
        url_entry.pack(fill="x", pady=(0, 15))
        
        # App ID
        appid_label = ctk.CTkLabel(
            content,
            text="App ID:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        appid_label.pack(anchor="w", pady=(0, 5))
        
        appid_info = ctk.CTkLabel(
            content,
            text="Must match an API application created in phpIPAM (Administration → API)",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        )
        appid_info.pack(anchor="w", pady=(0, 5))
        
        appid_entry = ctk.CTkEntry(
            content,
            placeholder_text="MyApplication",
            height=38
        )
        appid_entry.insert(0, self.phpipam_config.get_app_id())
        appid_entry.pack(fill="x", pady=(0, 15))
        
        # Authentication Method
        auth_label = ctk.CTkLabel(
            content,
            text="Authentication Method:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        auth_label.pack(anchor="w", pady=(0, 5))
        
        auth_var = ctk.StringVar(value=self.phpipam_config.get_auth_method())
        
        dynamic_radio = ctk.CTkRadioButton(
            content,
            text="Dynamic (Username + Password)",
            variable=auth_var,
            value="dynamic"
        )
        dynamic_radio.pack(anchor="w", pady=2)
        
        static_radio = ctk.CTkRadioButton(
            content,
            text="Static Token",
            variable=auth_var,
            value="static"
        )
        static_radio.pack(anchor="w", pady=(2, 15))
        
        # Username (for dynamic)
        username_label = ctk.CTkLabel(
            content,
            text="Username (Dynamic Auth):",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        username_label.pack(anchor="w", pady=(0, 5))
        
        username_entry = ctk.CTkEntry(
            content,
            placeholder_text="admin",
            height=38
        )
        username_entry.insert(0, self.phpipam_config.get_username())
        username_entry.pack(fill="x", pady=(0, 15))
        
        # Password (for dynamic)
        password_label = ctk.CTkLabel(
            content,
            text="Password (Dynamic Auth):",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        password_label.pack(anchor="w", pady=(0, 5))
        
        password_entry = ctk.CTkEntry(
            content,
            placeholder_text="Enter password",
            height=38,
            show="*"
        )
        password_entry.pack(fill="x", pady=(0, 15))
        
        # Static Token
        token_label = ctk.CTkLabel(
            content,
            text="Static Token (Static Auth):",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        token_label.pack(anchor="w", pady=(0, 5))
        
        token_entry = ctk.CTkEntry(
            content,
            placeholder_text="Enter static API token",
            height=38,
            show="*"
        )
        token_entry.pack(fill="x", pady=(0, 15))
        
        # SSL Verify
        ssl_var = ctk.BooleanVar(value=self.phpipam_config.get_ssl_verify())
        ssl_check = ctk.CTkCheckBox(
            content,
            text="Verify SSL Certificates",
            variable=ssl_var
        )
        ssl_check.pack(anchor="w", pady=(0, 20))
        
        # Save function
        def save_settings():
            password = password_entry.get()
            token = token_entry.get()
            
            # Don't overwrite if fields are empty (means user didn't change them)
            if not password:
                password = self.phpipam_config.get_password()
            if not token:
                token = self.phpipam_config.get_static_token()
            
            success = self.phpipam_config.update_config(
                enabled=enabled_var.get(),
                phpipam_url=url_entry.get(),
                app_id=appid_entry.get(),
                auth_method=auth_var.get(),
                username=username_entry.get(),
                password=password,
                static_token=token,
                ssl_verify=ssl_var.get()
            )
            
            if success:
                # Update status label
                if self.phpipam_config.is_enabled():
                    self.phpipam_status_label.configure(text="🟢 Enabled")
                else:
                    self.phpipam_status_label.configure(text="⚪ Disabled")
                
                # Reset client to force re-auth
                self.phpipam_client = None
                
                dialog.destroy()
                messagebox.showinfo("Success", "Settings saved successfully!")
            else:
                messagebox.showerror("Error", "Failed to save settings")
        
        # Buttons
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save",
            command=save_settings,
            width=120,
            height=40,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"]
        )
        save_btn.pack(side="right", padx=(10, 0))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            width=100,
            height=40
        )
        cancel_btn.pack(side="right")
    
    def test_phpipam_connection(self):
        """Test connection to phpIPAM"""
        if not PHPIPAM_AVAILABLE:
            messagebox.showerror("Error", "phpIPAM modules not available")
            return
        
        if not self.phpipam_config.is_enabled():
            messagebox.showwarning("Not Enabled", "phpIPAM integration is disabled. Enable it in Settings.")
            return
        
        # Reload config to get latest SSL settings
        self.phpipam_config.config = self.phpipam_config.load_config()
        
        # Create fresh client with updated config and test
        client = PHPIPAMClient(self.phpipam_config)
        success, message = client.test_connection()
        
        if success:
            messagebox.showinfo("Connection Test - Success", message)
        else:
            messagebox.showerror("Connection Test - Failed", message)
    
    def authenticate_phpipam(self):
        """Authenticate with phpIPAM"""
        if not PHPIPAM_AVAILABLE:
            messagebox.showerror("Error", "phpIPAM modules not available")
            return
        
        if not self.phpipam_config.is_enabled():
            messagebox.showwarning("Not Enabled", "phpIPAM integration is disabled. Enable it in Settings.")
            return
        
        # Create/get client
        if not self.phpipam_client:
            self.phpipam_client = PHPIPAMClient(self.phpipam_config)
        
        success, message = self.phpipam_client.authenticate()
        
        if success:
            messagebox.showinfo("Success", f"✅ {message}")
        else:
            messagebox.showerror("Authentication Failed", f"❌ {message}")
    
    def search_phpipam_ip(self):
        """Search for IP address in phpIPAM"""
        if not PHPIPAM_AVAILABLE:
            messagebox.showerror("Error", "phpIPAM modules not available")
            return
        
        if not self.phpipam_config.is_enabled():
            messagebox.showwarning("Not Enabled", "phpIPAM integration is disabled. Enable it in Settings.")
            return
        
        ip_address = self.phpipam_search_entry.get().strip()
        if not ip_address:
            messagebox.showwarning("Input Required", "Please enter an IP address to search")
            return
        
        # Show loading message
        self.display_phpipam_loading("Searching for IP address...")
        
        # Create/get client
        if not self.phpipam_client:
            self.phpipam_client = PHPIPAMClient(self.phpipam_config)
        
        # Run search in background thread
        def search_thread():
            success, results = self.phpipam_client.search_ip(ip_address)
            # Update UI in main thread
            self.after(0, self.display_phpipam_results, "IP Search Results", results, success)
        
        thread = threading.Thread(target=search_thread, daemon=True)
        thread.start()
    
    def view_phpipam_subnets(self):
        """View all subnets from phpIPAM"""
        if not PHPIPAM_AVAILABLE:
            messagebox.showerror("Error", "phpIPAM modules not available")
            return
        
        if not self.phpipam_config.is_enabled():
            messagebox.showwarning("Not Enabled", "phpIPAM integration is disabled. Enable it in Settings.")
            return
        
        # Show loading message
        self.display_phpipam_loading("Loading subnets from phpIPAM...")
        
        # Create/get client
        if not self.phpipam_client:
            self.phpipam_client = PHPIPAMClient(self.phpipam_config)
        
        # Get subnets in background thread
        def subnets_thread():
            success, results = self.phpipam_client.get_all_subnets()
            # Update UI in main thread
            self.after(0, self.display_phpipam_results, "All Subnets", results, success)
        
        thread = threading.Thread(target=subnets_thread, daemon=True)
        thread.start()
    
    def display_phpipam_loading(self, message):
        """Display loading message"""
        # Clear existing results
        for widget in self.phpipam_results_frame.winfo_children():
            widget.destroy()
        
        loading_label = ctk.CTkLabel(
            self.phpipam_results_frame,
            text=f"⏳ {message}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["primary"]
        )
        loading_label.pack(pady=50)
    
    def display_phpipam_results(self, title, data, success):
        """Display phpIPAM operation results with pagination for large datasets"""
        # Clear existing results
        for widget in self.phpipam_results_frame.winfo_children():
            widget.destroy()
        
        # Title
        result_title = ctk.CTkLabel(
            self.phpipam_results_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        result_title.pack(pady=(15, 10), padx=15, anchor="w")
        
        if not success:
            error_label = ctk.CTkLabel(
                self.phpipam_results_frame,
                text=f"❌ Error: {data}",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["danger"]
            )
            error_label.pack(pady=20, padx=15)
            return
        
        if not data:
            no_data_label = ctk.CTkLabel(
                self.phpipam_results_frame,
                text="No results found",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"]
            )
            no_data_label.pack(pady=20, padx=15)
            return
        
        # Store data for pagination and filtering
        self.phpipam_all_results = data  # Keep original for filtering
        self.phpipam_current_results = data
        self.phpipam_current_page = 0
        self.phpipam_items_per_page = 50  # Show 50 items at a time
        
        # Info bar with count and warning for large datasets
        info_frame = ctk.CTkFrame(self.phpipam_results_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        count_text = f"Found {len(data)} result(s)"
        if len(data) > 100:
            count_text += f" • Showing {self.phpipam_items_per_page} per page for performance"
        
        count_label = ctk.CTkLabel(
            info_frame,
            text=count_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_secondary"]
        )
        count_label.pack(side="left")
        
        # Scrollable results container
        self.phpipam_results_scroll = ctk.CTkScrollableFrame(
            self.phpipam_results_frame, 
            height=300
        )
        self.phpipam_results_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        # Display first page
        self._display_phpipam_page()
        
        # Pagination controls if needed
        if len(data) > self.phpipam_items_per_page:
            self._create_pagination_controls()
    
    def _create_subnet_card(self, parent, subnet_data):
        """Create formatted card for subnet display"""
        # Main subnet info
        subnet_str = subnet_data.get("subnet", "N/A")
        mask = subnet_data.get("mask", "")
        cidr = f"{subnet_str}/{mask}" if mask else subnet_str
        
        # Header with CIDR
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(12, 5))
        
        cidr_label = ctk.CTkLabel(
            header_frame,
            text=f"🌐 {cidr}",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        cidr_label.pack(side="left")
        
        # ID badge
        subnet_id = subnet_data.get("id", "")
        if subnet_id:
            id_label = ctk.CTkLabel(
                header_frame,
                text=f"ID: {subnet_id}",
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text_secondary"]
            )
            id_label.pack(side="right")
        
        # Description
        description = subnet_data.get("description", "")
        if description:
            desc_label = ctk.CTkLabel(
                parent,
                text=description,
                font=ctk.CTkFont(size=11),
                anchor="w",
                text_color=COLORS["text_secondary"]
            )
            desc_label.pack(fill="x", padx=12, pady=(0, 5))
        
        # Additional info in compact format
        info_items = []
        
        if "vlanId" in subnet_data and subnet_data["vlanId"]:
            info_items.append(f"VLAN: {subnet_data['vlanId']}")
        
        if "location" in subnet_data and subnet_data["location"]:
            info_items.append(f"Location: {subnet_data['location']}")
        
        if "isFolder" in subnet_data and subnet_data["isFolder"] == "1":
            info_items.append("📁 Folder")
        
        if info_items:
            info_text = " • ".join(info_items)
            info_label = ctk.CTkLabel(
                parent,
                text=info_text,
                font=ctk.CTkFont(size=10),
                anchor="w",
                text_color=COLORS["text_secondary"]
            )
            info_label.pack(fill="x", padx=12, pady=(0, 12))
        else:
            # Add bottom padding
            ctk.CTkFrame(parent, height=5, fg_color="transparent").pack()
    
    def _display_phpipam_page(self):
        """Display current page of phpIPAM results"""
        # Clear scroll frame
        for widget in self.phpipam_results_scroll.winfo_children():
            widget.destroy()
        
        # Calculate page boundaries
        start_idx = self.phpipam_current_page * self.phpipam_items_per_page
        end_idx = min(start_idx + self.phpipam_items_per_page, len(self.phpipam_current_results))
        
        # Get items for current page
        page_items = self.phpipam_current_results[start_idx:end_idx]
        
        # Display items
        for item in page_items:
            # Create card for each item
            item_card = ctk.CTkFrame(
                self.phpipam_results_scroll, 
                corner_radius=6, 
                fg_color=COLORS["bg_card"]
            )
            item_card.pack(fill="x", pady=3, padx=2)
            
            # Determine if this is a subnet or IP address
            is_subnet = "subnet" in item or "mask" in item
            
            if is_subnet:
                # Subnet card layout
                self._create_subnet_card(item_card, item)
            else:
                # IP address card layout
                self._create_ip_card(item_card, item)
    
    def _create_pagination_controls(self):
        """Create pagination controls for phpIPAM results"""
        total_items = len(self.phpipam_current_results)
        total_pages = (total_items + self.phpipam_items_per_page - 1) // self.phpipam_items_per_page
        
        pagination_frame = ctk.CTkFrame(self.phpipam_results_frame, fg_color="transparent")
        pagination_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        # Previous button
        prev_btn = ctk.CTkButton(
            pagination_frame,
            text="← Previous",
            command=self._prev_page,
            width=100,
            height=32,
            state="normal" if self.phpipam_current_page > 0 else "disabled",
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"]
        )
        prev_btn.pack(side="left", padx=(0, 10))
        
        # Page indicator
        start_idx = self.phpipam_current_page * self.phpipam_items_per_page + 1
        end_idx = min(start_idx + self.phpipam_items_per_page - 1, total_items)
        
        self.phpipam_page_label = ctk.CTkLabel(
            pagination_frame,
            text=f"Showing {start_idx}-{end_idx} of {total_items} • Page {self.phpipam_current_page + 1}/{total_pages}",
            font=ctk.CTkFont(size=11)
        )
        self.phpipam_page_label.pack(side="left", padx=10)
        
        # Next button
        next_btn = ctk.CTkButton(
            pagination_frame,
            text="Next →",
            command=self._next_page,
            width=100,
            height=32,
            state="normal" if self.phpipam_current_page < total_pages - 1 else "disabled",
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"]
        )
        next_btn.pack(side="left")
        
        # Jump to page
        jump_label = ctk.CTkLabel(
            pagination_frame,
            text="Jump to:",
            font=ctk.CTkFont(size=11)
        )
        jump_label.pack(side="right", padx=(10, 5))
        
        self.phpipam_page_entry = ctk.CTkEntry(
            pagination_frame,
            width=60,
            height=32,
            placeholder_text="Page"
        )
        self.phpipam_page_entry.pack(side="right", padx=(0, 5))
        
        jump_btn = ctk.CTkButton(
            pagination_frame,
            text="Go",
            command=self._jump_to_page,
            width=50,
            height=32,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"]
        )
        jump_btn.pack(side="right")
    
    def _prev_page(self):
        """Go to previous page"""
        if self.phpipam_current_page > 0:
            self.phpipam_current_page -= 1
            # Clear and recreate
            for widget in self.phpipam_results_frame.winfo_children():
                if widget != self.phpipam_results_frame.winfo_children()[0]:  # Keep title
                    widget.destroy()
            
            # Recreate display
            self._display_phpipam_page()
            self._create_pagination_controls()
    
    def _next_page(self):
        """Go to next page"""
        total_pages = (len(self.phpipam_current_results) + self.phpipam_items_per_page - 1) // self.phpipam_items_per_page
        if self.phpipam_current_page < total_pages - 1:
            self.phpipam_current_page += 1
            # Clear and recreate
            for widget in self.phpipam_results_frame.winfo_children():
                if widget != self.phpipam_results_frame.winfo_children()[0]:  # Keep title
                    widget.destroy()
            
            # Recreate display
            self._display_phpipam_page()
            self._create_pagination_controls()
    
    def _jump_to_page(self):
        """Jump to specific page"""
        try:
            page_num = int(self.phpipam_page_entry.get())
            total_pages = (len(self.phpipam_current_results) + self.phpipam_items_per_page - 1) // self.phpipam_items_per_page
            
            if 1 <= page_num <= total_pages:
                self.phpipam_current_page = page_num - 1
                # Clear and recreate
                for widget in self.phpipam_results_frame.winfo_children():
                    if widget != self.phpipam_results_frame.winfo_children()[0]:  # Keep title
                        widget.destroy()
                
                # Recreate display
                self._display_phpipam_page()
                self._create_pagination_controls()
            else:
                messagebox.showwarning("Invalid Page", f"Please enter a page number between 1 and {total_pages}")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid page number")
    
    def _filter_phpipam_results(self, event=None):
        """Filter displayed phpIPAM results based on search text"""
        if not hasattr(self, 'phpipam_all_results'):
            return
        
        filter_text = self.phpipam_filter_entry.get().lower().strip()
        
        if not filter_text:
            # Show all results
            self.phpipam_current_results = self.phpipam_all_results
        else:
            # Filter results
            filtered = []
            for item in self.phpipam_all_results:
                # Search in all string values
                item_text = " ".join(str(v).lower() for v in item.values() if v)
                if filter_text in item_text:
                    filtered.append(item)
            
            self.phpipam_current_results = filtered
        
        # Reset to first page and redisplay
        self.phpipam_current_page = 0
        
        # Clear and recreate (keeping title)
        for widget in self.phpipam_results_frame.winfo_children():
            if widget != self.phpipam_results_frame.winfo_children()[0]:
                widget.destroy()
        
        # Update count label
        info_frame = ctk.CTkFrame(self.phpipam_results_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        count_text = f"Showing {len(self.phpipam_current_results)} of {len(self.phpipam_all_results)} result(s)"
        if len(self.phpipam_current_results) > self.phpipam_items_per_page:
            count_text += f" • {self.phpipam_items_per_page} per page"
        
        count_label = ctk.CTkLabel(
            info_frame,
            text=count_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_secondary"]
        )
        count_label.pack(side="left")
        
        # Recreate scroll frame
        self.phpipam_results_scroll = ctk.CTkScrollableFrame(
            self.phpipam_results_frame,
            height=300
        )
        self.phpipam_results_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        # Display page
        self._display_phpipam_page()
        
        # Add pagination if needed
        if len(self.phpipam_current_results) > self.phpipam_items_per_page:
            self._create_pagination_controls()
    
    def _create_ip_card(self, parent, ip_data):
        """Create formatted card for IP address display"""
        # IP address
        ip = ip_data.get("ip", "N/A")
        
        # Header with IP
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(12, 5))
        
        ip_label = ctk.CTkLabel(
            header_frame,
            text=f"💻 {ip}",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        ip_label.pack(side="left")
        
        # Status badge if available
        if "state" in ip_data:
            state = ip_data["state"]
            state_color = COLORS["online"] if state == "1" else COLORS["offline"]
            state_text = "Active" if state == "1" else "Inactive"
            
            state_label = ctk.CTkLabel(
                header_frame,
                text=state_text,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=state_color
            )
            state_label.pack(side="right")
        
        # Hostname
        hostname = ip_data.get("hostname", "")
        if hostname:
            host_label = ctk.CTkLabel(
                parent,
                text=f"🏷️ {hostname}",
                font=ctk.CTkFont(size=11, weight="bold"),
                anchor="w"
            )
            host_label.pack(fill="x", padx=12, pady=(0, 5))
        
        # Description
        description = ip_data.get("description", "")
        if description:
            desc_label = ctk.CTkLabel(
                parent,
                text=description,
                font=ctk.CTkFont(size=10),
                anchor="w",
                text_color=COLORS["text_secondary"]
            )
            desc_label.pack(fill="x", padx=12, pady=(0, 5))
        
        # Additional details
        details = []
        
        if "mac" in ip_data and ip_data["mac"]:
            details.append(f"MAC: {ip_data['mac']}")
        
        if "owner" in ip_data and ip_data["owner"]:
            details.append(f"Owner: {ip_data['owner']}")
        
        if "port" in ip_data and ip_data["port"]:
            details.append(f"Port: {ip_data['port']}")
        
        if details:
            details_text = " • ".join(details)
            details_label = ctk.CTkLabel(
                parent,
                text=details_text,
                font=ctk.CTkFont(size=10),
                anchor="w",
                text_color=COLORS["text_secondary"]
            )
            details_label.pack(fill="x", padx=12, pady=(0, 12))
        else:
            # Add bottom padding
            ctk.CTkFrame(parent, height=5, fg_color="transparent").pack()
    
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
