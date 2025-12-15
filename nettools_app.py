#!/usr/bin/env python3
"""
NetTools Suite - IPv4 Scanner & MAC Formatter
Author: freakms
Company: ich schwöre feierlich ich bin ein tunichtgut
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

# Import UI modules
from ui.dashboard_ui import DashboardUI
from ui.scanner_ui import ScannerUI
from ui.portscan_ui import PortScannerUI
from ui.dns_ui import DNSLookupUI
from ui.subnet_ui import SubnetCalculatorUI
from ui.mac_ui import MACFormatterUI
from ui.traceroute_ui import TracerouteUI
from ui.panos_ui import PANOSUI
from ui.bandwidth_ui import BandwidthUI
from ui.phpipam_ui import PhpipamUI
# Remote Tools temporarily disabled
# from ui.remote_tools_ui import RemoteToolsUI
from ui.speedtest_ui import SpeedtestUI
from ui.password_generator_ui import PasswordGeneratorUI
from ui.whois_ui import WhoisUI
from ui.ssl_checker_ui import SSLCheckerUI
from ui.hash_generator_ui import HashGeneratorUI
from ui.api_tester_ui import APITesterUI
from ui.arp_viewer_ui import ARPViewerUI
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

# Try to import matplotlib (optional, used for Live Ping Monitor graphing)
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    Figure = None
    FigureCanvasTkAgg = None

# Design system and UI components
from design_constants import COLORS, SPACING, RADIUS, FONTS, BUTTON_SIZES
from ui_components import (
    StyledCard, StyledButton, StyledEntry, SectionTitle, SubTitle,
    ResultRow, StatusBadge, SectionSeparator, LoadingSpinner, InfoBox, DataGrid,
    Tooltip, ToastNotification, NAV_ICONS, HistoryPanel, SmartCommandPalette, ContextMenu
)

# Tool modules
from tools.scanner import IPv4Scanner
from tools.mac_formatter import OUILookup, MACFormatter
from tools.scan_manager import ScanManager
from tools.network_profile_manager import NetworkProfileManager
from tools.history_manager import HistoryManager
from tools.network_icon import NetworkIcon
from tools.live_ping_monitor import LivePingMonitor
from tools.bandwidth_tester import BandwidthTester
from tools.port_scanner import PortScanner
from tools.dns_lookup import DNSLookup
from tools.subnet_calculator import SubnetCalculator
from tools.traceroute import Traceroute
from tools.traceroute_manager import TracerouteManager
from tools.comparison_history import ComparisonHistory
from tools.phpipam_tool import PHPIPAMTool

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
APP_COMPANY = "freakms - ich schwöre feierlich ich bin ein tunichtgut"

# Configure CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


# Classes moved to tools/ module for better organization
# - ScanManager -> tools/scan_manager.py
# - NetworkProfileManager -> tools/network_profile_manager.py
# - HistoryManager -> tools/history_manager.py
# - NetworkIcon -> tools/network_icon.py
# - IPv4Scanner -> tools/scanner.py
# - OUILookup, MACFormatter -> tools/mac_formatter.py


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
        self.scanner = IPv4Scanner()
        self.scan_thread = None
        
        # Performance: Debounced updates
        self.update_buffer = []
        self.update_timer = None
        self.UPDATE_BATCH_SIZE = 10  # Update UI every 10 results
        self.UPDATE_INTERVAL_MS = 100  # Or every 100ms
        
        # Pagination for results
        self.all_results = []  # Store all results
        self.scan_current_page = 1
        self.results_per_page = 100
        self.scan_total_pages = 1
        
        # Window persistence - MUST be set before loading favorites
        self.config_file = Path.home() / '.nettools_config.json'
        
        # Favorites only (recent removed as not useful)
        self.favorite_tools = self.load_favorites()
        
        # Scan profiles
        self.scan_profiles = self.load_scan_profiles()
        
        # Initialize history manager
        self.history = HistoryManager()
        
        # Initialize scan manager
        self.scan_manager = ScanManager()
        
        # Initialize traceroute manager
        self.traceroute_manager = TracerouteManager()
        
        # Initialize comparison history for port scans and DNS
        self.comparison_history = ComparisonHistory()
        
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
        
        # Load window state
        self.load_window_state()
        
        # Load theme preferences
        self.load_theme_preferences()
        
        # Create UI (order matters: status bar must be packed before main content)
        self.create_sidebar()
        self.create_status_bar()
        self.create_main_content()
        
        # Bind keyboard shortcuts
        self.bind('<Return>', self.on_enter_key)
        # Quick access shortcuts (existing)
        self.bind('<Control-k>', self.open_quick_switcher)  # Quick switcher
        self.bind('<Control-h>', lambda e: self.toggle_history_panel())  # History panel
        
        # Global keyboard shortcuts (Phase 5)
        self.bind('<Control-Key-1>', lambda e: self.switch_tool('dashboard'))
        self.bind('<Control-Key-2>', lambda e: self.switch_tool('scanner'))
        self.bind('<Control-Key-3>', lambda e: self.switch_tool('portscan'))
        self.bind('<Control-Key-4>', lambda e: self.switch_tool('dns'))
        self.bind('<Control-Key-5>', lambda e: self.switch_tool('subnet'))
        self.bind('<Control-Key-6>', lambda e: self.switch_tool('traceroute'))
        self.bind('<Control-Key-7>', lambda e: self.switch_tool('mac'))
        self.bind('<Control-Key-8>', lambda e: self.switch_tool('compare'))
        self.bind('<Control-Key-9>', lambda e: self.switch_tool('profiles'))
        
        # Action shortcuts
        self.bind('<Control-e>', lambda e: self.quick_export())  # Quick export
        self.bind('<Control-r>', lambda e: self.quick_refresh())  # Refresh/Rescan
        self.bind('<Control-q>', lambda e: self.on_closing())  # Quit application
        self.bind('<Control-comma>', lambda e: self.open_settings())  # Settings (Ctrl+,)
        
        # Bind window resize for auto-scaling
        self.bind('<Configure>', self.on_window_resize)
        
        # Save window state on close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_window_state(self):
        """Load and apply saved window geometry"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    geometry = config.get('window_geometry')
                    if geometry:
                        self.geometry(geometry)
                        return
        except Exception as e:
            print(f"Could not load window state: {e}")
        
        # Default window size and position
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Set minimum size
        self.minsize(1200, 800)
        
        # Center window on screen
        x = (screen_width - self.base_width) // 2
        y = (screen_height - self.base_height) // 2
        self.geometry(f"{self.base_width}x{self.base_height}+{x}+{y}")
    
    def save_window_state(self):
        """Save current window geometry and preferences"""
        try:
            config = {}
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            
            # Save geometry
            config['window_geometry'] = self.geometry()
            
            # Save favorites
            config['favorite_tools'] = list(self.favorite_tools)
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Could not save window state: {e}")
    
    def save_theme_preference(self, theme):
        """Save theme preference to config"""
        try:
            config = {}
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            
            config['theme'] = theme
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Could not save theme preference: {e}")
    
    def save_accent_color(self, color_name, color_hex):
        """Save accent color preference to config"""
        try:
            config = {}
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            
            config['accent_color'] = {
                'name': color_name,
                'hex': color_hex
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Could not save accent color: {e}")
    
    def load_theme_preferences(self):
        """Load and apply saved theme preferences"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                    # Apply theme
                    theme = config.get('theme', 'Dark')
                    ctk.set_appearance_mode(theme)
                    
                    # Apply accent color
                    accent = config.get('accent_color')
                    if accent and 'hex' in accent:
                        COLORS['electric_violet'] = accent['hex']
                        COLORS['neon_cyan'] = accent['hex']
        except Exception as e:
            print(f"Could not load theme preferences: {e}")
    
    def load_favorites(self):
        """Load favorite tools from config"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return set(config.get('favorite_tools', []))
        except Exception as e:
            print(f"Could not load favorites: {e}")
        return set()
    
    def load_scan_profiles(self):
        """Load saved scan profiles"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('scan_profiles', {})
        except Exception as e:
            print(f"Could not load scan profiles: {e}")
        return {}
    
    def save_scan_profiles(self):
        """Save scan profiles to config"""
        try:
            config = {}
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            
            config['scan_profiles'] = self.scan_profiles
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Could not save scan profiles: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        self.save_window_state()
        self.destroy()
    
    def open_quick_switcher(self, event=None):
        """Focus the command palette in sidebar (Ctrl+K)"""
        # Focus the command palette in sidebar
        if hasattr(self, 'command_palette'):
            # Expand sidebar if collapsed
            if self.sidebar_collapsed:
                self._expand_sidebar()
            self.command_palette.focus()
        return "break"  # Prevent default behavior
    
    def _handle_content_search(self, search_text):
        """Handle content search from command palette"""
        if not search_text:
            return
        
        # Perform search based on current page
        if self.current_page == "scanner" and hasattr(self, 'all_results'):
            self.global_search_var.set(search_text)
            self.filter_scanner_results(search_text)
            self.show_toast(f"Searching for \"{search_text}\" in scanner results", "info")
        elif self.current_page == "portscan":
            self.show_toast(f"Searching for \"{search_text}\" in port scan results", "info")
            # TODO: Implement port scan content search
        elif self.current_page == "dns":
            self.show_toast(f"Searching for \"{search_text}\" in DNS results", "info")
            # TODO: Implement DNS content search
        else:
            # Fall back to global search bar
            self.global_search_var.set(search_text)
            self.show_toast(f"Searching for \"{search_text}\"", "info")
    
    def quick_export(self, event=None):
        """Context-aware quick export (Ctrl+E)"""
        # Export based on current page
        if self.current_page == "scanner":
            if hasattr(self, 'scanner_ui') and hasattr(self.scanner_ui, 'export_results'):
                self.scanner_ui.export_results()
                self.show_toast("Export initiated", "info")
        elif self.current_page == "portscan":
            # Could trigger port scanner export
            self.show_toast("Port scanner export - feature coming soon", "info")
        elif self.current_page == "dns":
            self.show_toast("DNS lookup export - feature coming soon", "info")
        else:
            self.show_toast("No exportable data on this page", "warning")
        return "break"
    
    def quick_refresh(self, event=None):
        """Context-aware quick refresh/rescan (Ctrl+R)"""
        # Refresh based on current page
        if self.current_page == "scanner":
            if hasattr(self, 'scanner_ui') and hasattr(self.scanner_ui, 'start_scan'):
                self.show_toast("Re-running last scan...", "info")
                # Re-trigger the last scan
                self.scanner_ui.start_scan()
        elif self.current_page == "dashboard":
            # Refresh dashboard stats
            self.show_toast("Refreshing dashboard...", "info")
            if hasattr(self, 'dashboard_ui'):
                # Could refresh network info
                pass
        elif self.current_page == "profiles":
            # Refresh network profiles
            self.show_toast("Refreshing profiles...", "info")
            if hasattr(self, 'refresh_profiles'):
                self.refresh_profiles()
        else:
            self.show_toast(f"Refresh not available on {self.current_page}", "info")
        return "break"
    
    def open_settings(self, event=None):
        """Open settings dialog (Ctrl+,)"""
        self.show_settings_dialog()
        return "break"
    
    def show_settings_dialog(self):
        """Show comprehensive settings dialog with theme and preferences"""
        # Create settings window
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("600x500")
        settings_window.transient(self)
        settings_window.grab_set()
        
        # Center window
        settings_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - settings_window.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - settings_window.winfo_height()) // 2
        settings_window.geometry(f"+{x}+{y}")
        
        # Make sure dialog is on top
        settings_window.lift()
        settings_window.focus_force()
        
        # Scrollable content
        scroll_frame = ctk.CTkScrollableFrame(settings_window, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            scroll_frame,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['electric_violet']
        )
        title_label.pack(pady=(0, 20))
        
        # Theme Settings Section
        theme_section = StyledCard(scroll_frame)
        theme_section.pack(fill="x", pady=(0, 15))
        
        theme_title = ctk.CTkLabel(
            theme_section,
            text="🎨 Appearance",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        theme_title.pack(padx=20, pady=(15, 10), anchor="w")
        
        # Theme mode selector
        theme_frame = ctk.CTkFrame(theme_section, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Theme Mode:",
            font=ctk.CTkFont(size=13)
        )
        theme_label.pack(side="left", padx=(0, 15))
        
        # Get current theme
        current_theme = ctk.get_appearance_mode()
        
        def change_theme(choice):
            ctk.set_appearance_mode(choice)
            self.save_theme_preference(choice)
            self.show_toast(f"Theme changed to {choice}", "success")
        
        theme_selector = ctk.CTkSegmentedButton(
            theme_frame,
            values=["Light", "Dark", "System"],
            command=change_theme
        )
        theme_selector.set(current_theme)
        theme_selector.pack(side="left", fill="x", expand=True)
        
        # Accent Color Picker
        accent_frame = ctk.CTkFrame(theme_section, fg_color="transparent")
        accent_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        accent_label = ctk.CTkLabel(
            accent_frame,
            text="Accent Color:",
            font=ctk.CTkFont(size=13)
        )
        accent_label.pack(side="left", padx=(0, 15))
        
        # Predefined accent colors
        accent_colors = {
            "Electric Violet": "#a78bfa",
            "Neon Cyan": "#06b6d4",
            "Pink": "#ec4899",
            "Orange": "#f97316",
            "Green": "#10b981",
            "Blue": "#3b82f6",
            "Red": "#ef4444",
            "Yellow": "#eab308"
        }
        
        accent_colors_frame = ctk.CTkFrame(accent_frame, fg_color="transparent")
        accent_colors_frame.pack(side="left", fill="x")
        
        def change_accent_color(color_name, color_hex):
            # Update COLORS dictionary
            COLORS['electric_violet'] = color_hex
            COLORS['neon_cyan'] = color_hex
            self.save_accent_color(color_name, color_hex)
            self.show_toast(f"Accent color changed to {color_name}. Restart to see full effect.", "info")
        
        # Create color buttons
        for idx, (color_name, color_hex) in enumerate(accent_colors.items()):
            color_btn = ctk.CTkButton(
                accent_colors_frame,
                text="",
                width=40,
                height=30,
                fg_color=color_hex,
                hover_color=color_hex,
                corner_radius=6,
                command=lambda cn=color_name, ch=color_hex: change_accent_color(cn, ch)
            )
            color_btn.grid(row=idx // 4, column=idx % 4, padx=3, pady=3)
            Tooltip(color_btn, color_name)
        
        # Keyboard Shortcuts Section
        shortcuts_section = StyledCard(scroll_frame)
        shortcuts_section.pack(fill="x", pady=(0, 15))
        
        shortcuts_title = ctk.CTkLabel(
            shortcuts_section,
            text="⌨️ Keyboard Shortcuts",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        shortcuts_title.pack(padx=20, pady=(15, 10), anchor="w")
        
        shortcuts_text = """
Navigation:
  • Ctrl+1 to Ctrl+9 - Quick switch between tools
  • Ctrl+K - Global search / Quick switcher
  • Ctrl+H - Toggle history panel

Actions:
  • Ctrl+E - Quick export (context-aware)
  • Ctrl+R - Refresh/Rescan (context-aware)
  • Ctrl+Q - Quit application
  • Ctrl+, - Open settings (this dialog)
  • Enter - Submit/Execute (context-aware)
        """
        
        shortcuts_label = ctk.CTkLabel(
            shortcuts_section,
            text=shortcuts_text.strip(),
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w"
        )
        shortcuts_label.pack(padx=20, pady=(0, 15), anchor="w")
        
        # Close button
        close_btn = StyledButton(
            scroll_frame,
            text="Close",
            command=settings_window.destroy,
            variant="primary"
        )
        close_btn.pack(pady=(10, 0))
    
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
        """Create modern professional sidebar navigation"""
        # Sidebar frame with subtle gradient background
        self.sidebar = ctk.CTkFrame(
            self, 
            width=260, 
            corner_radius=0,
            fg_color=COLORS['dashboard_card'],
            border_width=0
        )
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)
        
        self.sidebar_collapsed = False
        self.sidebar_expanded_width = 260
        self.sidebar_collapsed_width = 68
        
        # Right border accent
        border_accent = ctk.CTkFrame(
            self.sidebar,
            width=2,
            corner_radius=0,
            fg_color=COLORS['electric_violet']
        )
        border_accent.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")
        
        # Header with logo and collapse button
        header_frame = ctk.CTkFrame(self.sidebar, height=80, corner_radius=0, fg_color="transparent")
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Logo row
        logo_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_row.pack(fill="x", padx=16, pady=(20, 8))
        
        self.logo_icon = ctk.CTkLabel(
            logo_row,
            text="⚡",
            font=ctk.CTkFont(size=26)
        )
        self.logo_icon.pack(side="left")
        
        self.logo_text = ctk.CTkLabel(
            logo_row,
            text="NetTools",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['electric_violet']
        )
        self.logo_text.pack(side="left", padx=(4, 0))
        
        # Collapse button with rounded style
        self.collapse_btn = ctk.CTkButton(
            logo_row,
            text="◀",
            width=32,
            height=32,
            corner_radius=8,
            fg_color=COLORS.get('bg_card', ("gray90", "gray25")),
            hover_color=COLORS['dashboard_card_hover'],
            text_color=COLORS['text_secondary'],
            command=self.toggle_sidebar,
            font=ctk.CTkFont(size=11)
        )
        self.collapse_btn.pack(side="right")
        Tooltip(self.collapse_btn, "Collapse/Expand (Ctrl+B)")
        
        self.subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Professional Network Suite",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_secondary']
        )
        self.subtitle_label.pack(padx=20, pady=(0, 8), anchor="w")
        
        # Separator with subtle style
        separator = ctk.CTkFrame(
            self.sidebar, 
            height=1, 
            corner_radius=0,
            fg_color=COLORS.get('border', ("#E5E7EB", "#374151"))
        )
        separator.pack(fill="x", padx=16, pady=8)
        
        # Smart Command Palette - Search bar in sidebar
        # Define tools for the command palette with keywords (organized by category)
        self.command_palette_tools = [
            # Dashboard
            ("dashboard", "🏠", "Dashboard", ["home", "overview", "start", "main"]),
            # Scanning
            ("scanner", "📡", "IPv4 Scanner", ["scan", "network", "ip", "ping", "hosts", "discover"]),
            ("portscan", "🔌", "Port Scanner", ["port", "service", "open", "tcp", "udp"]),
            ("traceroute", "🛤️", "Traceroute", ["trace", "route", "path", "hop", "latency"]),
            ("arp", "📊", "ARP Table", ["arp", "cache", "mac", "address", "neighbor"]),
            # Tools
            ("dns", "🌐", "DNS Lookup", ["dns", "resolve", "domain", "hostname", "mx", "ns"]),
            ("whois", "🔍", "WHOIS Lookup", ["whois", "domain", "owner", "registrar", "ip"]),
            ("ssl", "🔒", "SSL Checker", ["ssl", "certificate", "https", "tls", "expiry"]),
            ("subnet", "🔢", "Subnet Calculator", ["subnet", "cidr", "mask", "calculate", "ip"]),
            ("mac", "🔗", "MAC Formatter", ["mac", "address", "oui", "vendor", "format"]),
            ("hash", "#️⃣", "Hash Generator", ["hash", "md5", "sha", "sha256", "checksum"]),
            ("password", "🔐", "Password Generator", ["password", "passphrase", "generate", "secure", "random"]),
            # Testing
            ("api", "📡", "API Tester", ["api", "http", "rest", "postman", "request", "curl"]),
            ("bandwidth", "📶", "Bandwidth Test", ["speed", "iperf", "throughput", "test"]),
            ("speedtest", "🚀", "Speedtest", ["speed", "internet", "download", "upload"]),
            ("compare", "⚖️", "Scan Comparison", ["compare", "diff", "history", "changes"]),
            # Advanced
            ("profiles", "📁", "Network Profiles", ["profile", "config", "interface", "static", "dhcp"]),
            # ("remote", "🖥️", "Remote Tools", ["psexec", "iperf", "remote", "command", "execute"]),  # Temporarily disabled
            ("panos", "🛡️", "PAN-OS Generator", ["palo", "alto", "firewall", "cli", "config"]),
            ("phpipam", "📦", "phpIPAM", ["ipam", "ip", "management", "inventory"]),
        ]
        
        self.command_palette = SmartCommandPalette(
            self.sidebar,
            tools=self.command_palette_tools,
            on_tool_select=self.switch_tool,
            on_content_search=self._handle_content_search
        )
        self.command_palette.pack(fill="x", padx=5, pady=(5, 10))
        
        # Scrollable navigation container
        self.nav_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.nav_scroll.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Quick Access - Live Monitor (prominent button)
        self.live_monitor_btn = StyledButton(
            self.nav_scroll,
            text="📊 Live Monitor",
            command=self.open_live_ping_monitor,
            size="large",
            variant="success",
            width=220
        )
        self.live_monitor_btn.configure(anchor="w")
        self.live_monitor_btn.pack(fill="x", padx=10, pady=(5, 15))
        Tooltip(self.live_monitor_btn, "Open Live Ping Monitor")
        
        # Favorites section - create but don't pack yet (will pack when populated)
        self.favorites_frame = ctk.CTkFrame(self.nav_scroll, fg_color="transparent")
        self.favorites_label = ctk.CTkLabel(
            self.favorites_frame,
            text="⭐ FAVORITES",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS['neon_cyan'],
            anchor="w"
        )
        self.favorites_buttons_frame = ctk.CTkFrame(self.favorites_frame, fg_color="transparent")
        
        # Navigation organized by categories with icons
        self.nav_buttons = {}
        self.category_labels = []
        self.nav_categories_data = []  # Store category data for rebuilding
        
        # Category structure - Clean 4-category layout
        # (category_name, icon, [(page_id, icon, label, tooltip), ...])
        nav_categories = [
            ("DASHBOARD", "📊", [
                ("dashboard", "🏠", "Dashboard", "Overview and system info"),
            ]),
            ("SCANNING", "🔍", [
                ("scanner", "📡", "IPv4 Scanner", "Scan network for active hosts"),
                ("portscan", "🔌", "Port Scanner", "Scan for open ports"),
                ("traceroute", "🛤️", "Traceroute", "Trace network path"),
                ("arp", "📊", "ARP Table", "View ARP cache entries"),
            ]),
            ("TOOLS", "🛠️", [
                ("dns", "🌐", "DNS Lookup", "Resolve hostnames and IPs"),
                ("whois", "🔍", "WHOIS Lookup", "Domain/IP ownership info"),
                ("ssl", "🔒", "SSL Checker", "Check SSL certificates"),
                ("subnet", "🔢", "Subnet Calculator", "Calculate subnet info"),
                ("mac", "🔗", "MAC Formatter", "Format MAC addresses"),
                ("hash", "#️⃣", "Hash Generator", "Generate MD5/SHA hashes"),
                ("password", "🔐", "Password Generator", "Generate secure passwords"),
            ]),
            ("TESTING", "🧪", [
                ("api", "📡", "API Tester", "Test REST APIs"),
                ("bandwidth", "📶", "Bandwidth Test", "Test with iPerf3"),
                ("speedtest", "🚀", "Speedtest", "Internet speed test"),
                ("compare", "⚖️", "Scan Comparison", "Compare scan results"),
            ]),
            ("ADVANCED", "⚙️", [
                ("profiles", "📁", "Network Profiles", "Manage network configs"),
                # ("remote", "🖥️", "Remote Tools", "PSExec & iPerf"),  # Temporarily disabled
                ("panos", "🛡️", "PAN-OS Generator", "Generate PAN-OS CLI"),
                ("phpipam", "📦", "phpIPAM", "IP address management"),
            ]),
        ]
        
        self.current_page = "dashboard"
        
        # Store first category for positioning
        self.first_category_label = None
        
        # Render navigation with categories
        for idx, (category_name, cat_icon, items) in enumerate(nav_categories):
            # Store category data for rebuilding later
            self.nav_categories_data.append((category_name, cat_icon, items))
            
            # Category header
            category_label = ctk.CTkLabel(
                self.nav_scroll,
                text=f"{cat_icon} {category_name}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS['neon_cyan'],
                anchor="w"
            )
            category_label.pack(fill="x", padx=15, pady=(12, 5))
            
            # Store category info: (label widget, cat_icon, category_name, list of button page_ids in this category)
            category_buttons = []
            
            # Store reference to first category
            if idx == 0:
                self.first_category_label = category_label
            
            # Category items with icons - professional styling
            for page_id, icon, label, tooltip in items:
                btn = ctk.CTkButton(
                    self.nav_scroll,
                    text=f" {icon}  {label}",
                    command=lambda p=page_id: self.switch_tool(p),
                    width=220,
                    height=40,
                    corner_radius=8,
                    anchor="w",
                    font=ctk.CTkFont(size=13),
                    fg_color="transparent",
                    text_color=COLORS['text_primary'],
                    hover_color=COLORS['dashboard_card_hover'],
                    border_width=0
                )
                btn.pack(fill="x", padx=10, pady=2)
                
                # Store icon and label for collapse/expand
                btn._nav_icon = icon
                btn._nav_label = label
                
                # Add tooltip
                Tooltip(btn, tooltip)
                
                # Add right-click context menu for favorites
                btn.bind("<Button-3>", lambda e, tid=page_id: self.show_tool_context_menu(e, tid))
                
                self.nav_buttons[page_id] = btn
                category_buttons.append(page_id)
            
            # Append category with its associated buttons
            self.category_labels.append((category_label, cat_icon, category_name, category_buttons))
        
        # Update initial button state - highlight dashboard
        self.nav_buttons["dashboard"].configure(
            fg_color=COLORS['electric_violet'],
            text_color="white"
        )
        
        # Add some bottom padding to scroll area
        bottom_padding = ctk.CTkFrame(self.nav_scroll, fg_color="transparent", height=30)
        bottom_padding.pack(fill="x")
        
        # Theme selector at bottom (fixed position outside scroll) - compact professional style
        theme_frame = ctk.CTkFrame(self.sidebar, corner_radius=0, fg_color="transparent")
        theme_frame.pack(side="bottom", fill="x", padx=16, pady=16)
        
        self.theme_label = ctk.CTkLabel(
            theme_frame, 
            text="Appearance", 
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS['text_secondary']
        )
        self.theme_label.pack(pady=(0, 8), anchor="w")
        
        self.theme_selector = ctk.CTkSegmentedButton(
            theme_frame,
            values=["☀️ Light", "🌙 Dark"],
            command=lambda v: self.change_theme("Light" if "Light" in v else "Dark"),
            font=ctk.CTkFont(size=11),
            corner_radius=8
        )
        self.theme_selector.set("🌙 Dark")
        self.theme_selector.pack(fill="x")
        
        # Initialize favorites UI
        self.update_favorites_ui()
        self.update_nav_button_stars()
    
    def toggle_sidebar(self):
        """Toggle sidebar between collapsed and expanded state"""
        if self.sidebar_collapsed:
            self._expand_sidebar()
        else:
            self._collapse_sidebar()
    
    def _collapse_sidebar(self):
        """Collapse sidebar to show only icons"""
        self.sidebar_collapsed = True
        self.sidebar.configure(width=self.sidebar_collapsed_width)
        
        # Hide text elements
        self.logo_text.pack_forget()
        self.subtitle_label.pack_forget()
        self.theme_label.pack_forget()
        self.theme_selector.pack_forget()
        self.collapse_btn.configure(
            text="▶",
            fg_color=COLORS['electric_violet'],
            width=36,
            height=36
        )
        
        # Hide command palette (too small when collapsed)
        if hasattr(self, 'command_palette'):
            self.command_palette.pack_forget()
        
        # Update live monitor button - icon only, centered, brighter
        self.live_monitor_btn.configure(
            text="📊", 
            width=48, 
            anchor="center",
            fg_color=COLORS['success'],
            text_color="white"
        )
        
        # Update nav buttons to show only icons (centered, brighter text)
        for page_id, btn in self.nav_buttons.items():
            icon = getattr(btn, '_nav_icon', '•')
            # Check if this is the active page
            if page_id == self.current_page:
                btn.configure(
                    text=icon, 
                    anchor="center", 
                    width=48,
                    fg_color=COLORS['electric_violet'],
                    text_color="white"
                )
            else:
                btn.configure(
                    text=icon, 
                    anchor="center", 
                    width=48,
                    fg_color="transparent",
                    text_color=COLORS['neon_cyan']  # Brighter cyan color for icons
                )
        
        # Update favorite buttons if any - brighter icons
        if hasattr(self, 'favorites_buttons_frame'):
            for btn in self.favorites_buttons_frame.winfo_children():
                icon = getattr(btn, '_nav_icon', '•')
                btn.configure(
                    text=icon, 
                    anchor="center", 
                    width=48,
                    text_color=COLORS['neon_cyan']
                )
        
        # Hide category labels completely
        for label, icon, name, buttons in self.category_labels:
            label.pack_forget()
        
        # Hide favorites label if exists
        if hasattr(self, 'favorites_label'):
            self.favorites_label.pack_forget()
    
    def _expand_sidebar(self):
        """Expand sidebar to full width"""
        self.sidebar_collapsed = False
        self.sidebar.configure(width=self.sidebar_expanded_width)
        
        # Show text elements in correct order
        self.logo_text.pack(side="left", padx=(4, 0))
        self.subtitle_label.pack(padx=20, pady=(0, 8), anchor="w")
        self.theme_label.pack(pady=(0, 8), anchor="w")
        self.theme_selector.pack(fill="x")
        self.collapse_btn.configure(
            text="◀",
            fg_color=COLORS.get('bg_card', ("gray90", "gray25")),
            width=32,
            height=32
        )
        
        # Show command palette (pack it in sidebar, not nav_scroll)
        if hasattr(self, 'command_palette'):
            # Re-pack command palette between separator and nav_scroll
            self.command_palette.pack(fill="x", padx=5, pady=(5, 10))
            # Move nav_scroll below it
            self.nav_scroll.pack_forget()
            self.nav_scroll.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Update live monitor button - full text
        self.live_monitor_btn.configure(text="📊 Live Monitor", width=220, anchor="w")
        
        # Update nav buttons to show icons + text
        for page_id, btn in self.nav_buttons.items():
            icon = getattr(btn, '_nav_icon', '•')
            label = getattr(btn, '_nav_label', page_id)
            btn.configure(text=f" {icon}  {label}", anchor="w", width=220)
        
        # Update favorite buttons if any
        if hasattr(self, 'favorites_buttons_frame'):
            for btn in self.favorites_buttons_frame.winfo_children():
                icon = getattr(btn, '_nav_icon', '•')
                label = getattr(btn, '_nav_label', '')
                btn.configure(text=f" {icon}  {label}", anchor="w", width=220)
        
        # Show favorites label if exists and favorites are present
        if hasattr(self, 'favorites_label') and self.favorite_tools:
            self.favorites_label.pack(anchor="w", pady=(5, 5))
        
        # Restore category labels in the correct order by re-packing them before their buttons
        for label_widget, icon, name, button_ids in self.category_labels:
            # Restore full text
            label_widget.configure(text=f"{icon} {name}", font=ctk.CTkFont(size=11, weight="bold"))
            
            # Re-pack the category label before its first button
            if button_ids and button_ids[0] in self.nav_buttons:
                first_button = self.nav_buttons[button_ids[0]]
                label_widget.pack(fill="x", padx=15, pady=(12, 5), before=first_button)
            else:
                # Fallback: just pack it normally
                label_widget.pack(fill="x", padx=15, pady=(12, 5))
    
    def _fade_out_page(self, page_widget, steps=5, current_step=0):
        """Animate fade-out effect for page transitions"""
        if current_step < steps:
            # Calculate opacity (from 1.0 to 0.3)
            opacity = 1.0 - (current_step / steps * 0.7)
            try:
                # CustomTkinter doesn't support direct opacity, so we use a workaround
                # by adjusting the widget's position slightly for a "slide out" effect
                current_step += 1
                self.after(30, lambda: self._fade_out_page(page_widget, steps, current_step))
            except:
                pass  # Widget might be destroyed
    
    def _fade_in_page(self, page_widget, steps=5, current_step=0):
        """Animate fade-in effect for page transitions"""
        if current_step < steps:
            # Calculate opacity (from 0.3 to 1.0)
            opacity = 0.3 + (current_step / steps * 0.7)
            try:
                # Simulated fade-in by triggering updates
                current_step += 1
                page_widget.update_idletasks()
                self.after(30, lambda: self._fade_in_page(page_widget, steps, current_step))
            except:
                pass  # Widget might be destroyed
    
    def show_toast(self, message, toast_type="info"):
        """Show a toast notification"""
        ToastNotification(self, message, toast_type)
    
    def switch_page(self, page_id):
        """Switch between pages with lazy loading and smooth transitions"""
        if page_id == self.current_page:
            return
        
        # Update button states - professional active state
        for btn_id, btn in self.nav_buttons.items():
            if btn_id == page_id:
                # Active state - filled with accent color
                btn.configure(
                    fg_color=COLORS['electric_violet'],
                    text_color="white",
                    border_width=0
                )
            else:
                # Inactive state - transparent
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS['text_primary'],
                    border_width=0
                )
        
        # Animate fade-out of current page
        old_page = self.pages.get(self.current_page)
        if old_page:
            self._fade_out_page(old_page)
        
        # Hide all pages after fade out
        def _complete_transition():
            for page in self.pages.values():
                page.pack_forget()
            
            # Lazy load page content if not already loaded
            if page_id not in self.pages_loaded:
                if page_id not in self.pages:
                    self.pages[page_id] = ctk.CTkFrame(self.main_content, corner_radius=0)
                
                # Load page content based on page_id
                if page_id == "dashboard":
                    self.create_dashboard_content(self.pages[page_id])
                elif page_id == "scanner":
                    self.create_scanner_content(self.pages[page_id])
                elif page_id == "mac":
                    self.create_mac_content(self.pages[page_id])
                elif page_id == "compare":
                    self.create_comparison_content(self.pages[page_id])
                elif page_id == "profiles":
                    self.create_profiles_content(self.pages[page_id])
                elif page_id == "portscan":
                    self.create_portscan_content(self.pages[page_id])
                elif page_id == "traceroute":
                    TracerouteUI(self, self.pages[page_id])
                elif page_id == "dns":
                    self.create_dns_content(self.pages[page_id])
                elif page_id == "panos":
                    PANOSUI(self, self.pages[page_id])
                elif page_id == "subnet":
                    self.create_subnet_content(self.pages[page_id])
                elif page_id == "phpipam":
                    PhpipamUI(self, self.pages[page_id])
                elif page_id == "bandwidth":
                    BandwidthUI(self, self.pages[page_id])
                # Remote Tools temporarily disabled
                # elif page_id == "remote":
                #     remote_ui = RemoteToolsUI(self)
                #     remote_ui.create_content(self.pages[page_id])
                elif page_id == "speedtest":
                    SpeedtestUI(self, self.pages[page_id])
                elif page_id == "password":
                    PasswordGeneratorUI(self, self.pages[page_id])
                elif page_id == "whois":
                    WhoisUI(self, self.pages[page_id])
                elif page_id == "ssl":
                    SSLCheckerUI(self, self.pages[page_id])
                elif page_id == "hash":
                    HashGeneratorUI(self, self.pages[page_id])
                elif page_id == "api":
                    APITesterUI(self, self.pages[page_id])
                elif page_id == "arp":
                    ARPViewerUI(self, self.pages[page_id])
                
                self.pages_loaded[page_id] = True
            
            # Show selected page with fade-in animation
            self.pages[page_id].pack(fill="both", expand=True, padx=0, pady=0)
            self._fade_in_page(self.pages[page_id])
            self.current_page = page_id
        
        # Complete transition after fade-out animation
        self.after(150, _complete_transition)
        
        # Update status bar based on page
        if page_id == "dashboard":
            self.status_label.configure(text="Network Command Center - Ready")
        elif page_id == "scanner":
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
        elif page_id == "panos":
            self.status_label.configure(text="Generate PAN-OS address object CLI commands")
        elif page_id == "subnet":
            self.status_label.configure(text="Calculate subnet information from CIDR")
        elif page_id == "phpipam":
            self.status_label.configure(text="Manage IP addresses with phpIPAM")
        elif page_id == "remote":
            self.status_label.configure(text="Execute remote commands and bandwidth tests")
        elif page_id == "speedtest":
            self.status_label.configure(text="Test internet speed with Ookla servers")
        elif page_id == "password":
            self.status_label.configure(text="Generate secure passwords and passphrases")
        elif page_id == "whois":
            self.status_label.configure(text="Query domain and IP ownership information")
        elif page_id == "ssl":
            self.status_label.configure(text="Check SSL/TLS certificate validity and details")
        elif page_id == "hash":
            self.status_label.configure(text="Generate cryptographic hashes for text and files")
        elif page_id == "api":
            self.status_label.configure(text="Test REST APIs and HTTP endpoints")
        elif page_id == "arp":
            self.status_label.configure(text="View local ARP cache entries")
    
    
    def show_page(self, page_id):
        """Alias for switch_page() - used by dashboard"""
        self.switch_page(page_id)

    def create_main_content(self):
        """Create main content area with global search and pages"""
        # Main container (holds content)
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.pack(side="right", fill="both", expand=True, padx=0, pady=0)
        
        # Initialize global_search_var for backward compatibility (used by some methods)
        self.global_search_var = ctk.StringVar()
        
        # Main content frame (full area now, no search bar)
        self.main_content = ctk.CTkFrame(self.main_container, corner_radius=0)
        self.main_content.pack(fill="both", expand=True, padx=0, pady=0)
        
        # History panel (initially hidden, on the right)
        self.history_panel = HistoryPanel(self.main_content)
        
        # Create pages dictionary (empty frames, content loaded on demand)
        self.pages = {}
        self.pages_loaded = {}  # Track which pages have been loaded
        
        # Pre-create the dashboard page for fast initial display
        self.pages["dashboard"] = ctk.CTkFrame(self.main_content, corner_radius=0)
        self.create_dashboard_content(self.pages["dashboard"])
        self.pages_loaded["dashboard"] = True
        
        # Show the initial page (dashboard)
        self.pages["dashboard"].pack(fill="both", expand=True, padx=0, pady=0)
    
    def on_global_search_typing(self, event=None):
        """Handle typing in global search - debounced filter"""
        # Cancel previous scheduled filter
        if hasattr(self, '_search_debounce_id') and self._search_debounce_id:
            self.after_cancel(self._search_debounce_id)
        
        # Schedule filter after 300ms of no typing
        self._search_debounce_id = self.after(300, self._do_search_filter)
    
    def _do_search_filter(self):
        """Actually perform the search filter (called after debounce)"""
        search_text = self.global_search_var.get().strip().lower()
        
        # If on scanner page, filter results
        if self.current_page == "scanner" and hasattr(self, 'all_results') and self.all_results:
            self.filter_scanner_results(search_text)
    
    def perform_global_search(self, event=None):
        """Handle global search on Enter key"""
        search_text = self.global_search_var.get().strip().lower()
        
        if not search_text:
            return
        
        # Check for tool navigation commands
        tool_shortcuts = {
            "scan": "scanner",
            "scanner": "scanner",
            "ipv4": "scanner",
            "port": "portscan",
            "dns": "dns",
            "subnet": "subnet",
            "mac": "mac",
            "trace": "traceroute",
            "traceroute": "traceroute",
            "bandwidth": "bandwidth",
            "speed": "bandwidth",
            "dashboard": "dashboard",
            "home": "dashboard",
            "compare": "compare",
            "panos": "panos",
            "phpipam": "phpipam",
        }
        
        for keyword, page_id in tool_shortcuts.items():
            if keyword in search_text:
                self.switch_tool(page_id)
                self.global_search_var.set("")
                self.show_toast(f"Switched to {page_id.replace('_', ' ').title()}", "info")
                return
        
        # Otherwise filter current page
        if self.current_page == "scanner" and hasattr(self, 'all_results'):
            self.filter_scanner_results(search_text)
    
    def filter_scanner_results(self, search_text):
        """Filter scanner results by search text"""
        if not hasattr(self, 'all_results') or not self.all_results:
            return
        
        if not search_text:
            self.filtered_results = self.all_results
        else:
            self.filtered_results = [
                r for r in self.all_results
                if search_text in r.get('ip', '').lower() or
                   search_text in r.get('hostname', '').lower() or
                   search_text in r.get('status', '').lower()
            ]
        
        # Re-render with filtered data
        self.scan_current_page = 1
        
        # Find scanner UI and render
        if hasattr(self, 'scanner_ui_instance'):
            self.scanner_ui_instance.render_current_page(use_filtered=True)
            
            # Update pagination label
            total = len(self.all_results)
            filtered = len(self.filtered_results)
            if search_text:
                self.pagination_label.configure(text=f"Showing {filtered} of {total} results")
    
    def quick_filter(self, filter_type):
        """Quick filter buttons for Online/Offline"""
        if filter_type == "online":
            self.global_search_var.set("Online")
        elif filter_type == "offline":
            self.global_search_var.set("No Response")
        
        self.perform_global_search()
    
    def clear_global_search(self):
        """Clear global search and reset filters"""
        self.global_search_var.set("")
        
        if self.current_page == "scanner" and hasattr(self, 'all_results'):
            self.filtered_results = self.all_results
            if hasattr(self, 'scanner_ui_instance'):
                self.scan_current_page = 1
                self.scanner_ui_instance.render_current_page(use_filtered=False)
    
    def toggle_history_panel(self):
        """Toggle the history panel visibility"""
        if hasattr(self, 'history_panel'):
            self.history_panel.toggle()
            # Update button appearance
            if self.history_panel.is_visible:
                self.history_btn.configure(fg_color=COLORS['neon_cyan'])
            else:
                self.history_btn.configure(fg_color="transparent")
    
    def add_to_history(self, action_type, title, subtitle="", data=None, on_click=None):
        """Add an item to the history panel"""
        if hasattr(self, 'history_panel'):
            self.history_panel.add_item(action_type, title, subtitle, data, on_click)
    

    def create_dashboard_content(self, parent):
        """Create Dashboard home page with electric violet theme"""
        dashboard_ui = DashboardUI(self)
        dashboard_ui.create_content(parent)
    def create_scanner_content(self, parent):
        """Create IPv4 Scanner page content"""
        try:
            scanner_ui = ScannerUI(self)
            scanner_ui.create_content(parent)
            self.scanner_ui_instance = scanner_ui  # Store reference for global search
        except Exception as e:
            # Show error if scanner fails to load
            error_label = ctk.CTkLabel(
                parent,
                text=f"Error loading scanner:\n{str(e)}",
                font=ctk.CTkFont(size=14),
                text_color="red"
            )
            error_label.pack(padx=20, pady=20)
            print(f"Scanner error: {e}")
            import traceback
            traceback.print_exc()
    def create_mac_content(self, parent):
        """Create MAC Formatter page content"""
        mac_ui = MACFormatterUI(self)
        mac_ui.create_content(parent)
    
    
    def create_comparison_content(self, parent):
        """Create unified Scan Comparison page content for all tools"""
        # Scrollable content area
        scrollable = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scrollable.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Title
        title_label = ctk.CTkLabel(
            scrollable,
            text="⚖️ Scan Comparison Tool",
            font=ctk.CTkFont(size=FONTS['title'], weight="bold"),
            text_color=COLORS['electric_violet']
        )
        title_label.pack(pady=(0, SPACING['xs']))
        
        # Description
        desc_label = SubTitle(
            scrollable,
            text="Compare results from different scans to identify changes, additions, and removals"
        )
        desc_label.pack(pady=(0, SPACING['lg']))
        
        # Tool selector cards
        tools_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        tools_frame.pack(fill="x", pady=SPACING['md'])
        
        # Define comparison tools with their properties
        comparison_tools = [
            {
                "name": "IPv4 Scanner",
                "icon": "📡",
                "description": "Compare network scans to see devices that appeared, disappeared, or changed status",
                "command": self.show_scan_comparison
            },
            {
                "name": "Port Scanner",
                "icon": "🔌",
                "description": "Compare port scan results to detect newly opened or closed ports",
                "command": self.show_portscan_comparison
            },
            {
                "name": "DNS Lookup",
                "icon": "🌐",
                "description": "Compare DNS resolution results to track changes in domain records",
                "command": self.show_dns_comparison
            },
            {
                "name": "Traceroute",
                "icon": "🛤️",
                "description": "Compare network paths to identify routing changes and latency differences",
                "command": self.show_traceroute_comparison
            }
        ]
        
        # Create cards for each tool
        for idx, tool in enumerate(comparison_tools):
            card = StyledCard(tools_frame)
            card.pack(fill="x", pady=SPACING['sm'])
            
            # Card header with icon and name
            header_frame = ctk.CTkFrame(card, fg_color="transparent")
            header_frame.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['xs']))
            
            icon_label = ctk.CTkLabel(
                header_frame,
                text=tool["icon"],
                font=ctk.CTkFont(size=24)
            )
            icon_label.pack(side="left", padx=(0, SPACING['sm']))
            
            name_label = ctk.CTkLabel(
                header_frame,
                text=tool["name"],
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS['text_primary']
            )
            name_label.pack(side="left")
            
            # Description
            desc = ctk.CTkLabel(
                card,
                text=tool["description"],
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_secondary'],
                wraplength=650,
                justify="left"
            )
            desc.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))
            
            # Compare button
            compare_btn = StyledButton(
                card,
                text="Compare Results",
                command=tool["command"],
                size="small",
                variant="primary"
            )
            compare_btn.pack(padx=SPACING['md'], pady=(0, SPACING['md']), anchor="w")
        
        # Info box about comparison
        info_box = InfoBox(
            scrollable,
            message="💡 Tip: Run multiple scans using each tool to build comparison history. Comparisons help you monitor changes over time.",
            box_type="info"
        )
        info_box.pack(fill="x", pady=(SPACING['lg'], 0))
    
    def create_profiles_content(self, parent):
        """Create Network Profiles page content"""
        # Scrollable content area
        scrollable = ctk.CTkScrollableFrame(parent)
        scrollable.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Title
        title_label = ctk.CTkLabel(
            scrollable,
            text="Network Profile Manager",
            font=ctk.CTkFont(size=FONTS['title'], weight="bold")
        )
        title_label.pack(pady=(0, SPACING['xs']))
        
        # Subtitle
        subtitle_label = SubTitle(
            scrollable,
            text="Manage network interface configurations and quick-switch profiles"
        )
        subtitle_label.pack(pady=(0, SPACING['lg']))
        
        # Admin warning if not admin
        if not self.is_admin():
            warning_frame = InfoBox(
                scrollable,
                message="⚠️ Administrator privileges required to change network settings",
                box_type="warning"
            )
            warning_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        # Refresh button
        refresh_btn = StyledButton(
            scrollable,
            text="🔄 Refresh Interfaces",
            command=self.refresh_interfaces,
            size="large",
            variant="neutral"
        )
        refresh_btn.pack(pady=(0, SPACING['lg']))
        
        # Current Interfaces Section
        interfaces_title = SectionTitle(
            scrollable,
            text="Network Interfaces (Current Status)"
        )
        interfaces_title.pack(pady=(SPACING['md'], SPACING['md']), anchor="w")
        
        # Frame to hold interface cards
        self.interfaces_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        self.interfaces_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        # Separator
        separator = SectionSeparator(scrollable)
        separator.pack(fill="x", pady=SPACING['lg'])
        
        # Saved Profiles Section
        profiles_title = SectionTitle(
            scrollable,
            text="Saved Profiles"
        )
        profiles_title.pack(pady=(0, SPACING['md']), anchor="w")
        
        # New profile button
        new_profile_btn = StyledButton(
            scrollable,
            text="➕ Create New Profile",
            command=self.create_new_profile,
            size="large",
            variant="success"
        )
        new_profile_btn.pack(pady=(0, SPACING['lg']))
        
        # Frame to hold profile cards
        self.profiles_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        self.profiles_frame.pack(fill="x")
        
        # Load initial data
        self.refresh_interfaces()
        self.refresh_profiles()
    def create_portscan_content(self, parent):
        """Create Port Scanner page content"""
        try:
            portscan_ui = PortScannerUI(self)
            portscan_ui.create_content(parent)
        except Exception as e:
            error_label = ctk.CTkLabel(
                parent,
                text=f"Error loading port scanner:\n{str(e)}",
                font=ctk.CTkFont(size=14),
                text_color="red"
            )
            error_label.pack(padx=20, pady=20)
            print(f"Port Scanner error: {e}")
            import traceback
            traceback.print_exc()
    
    def create_dns_content(self, parent):
        """Create DNS Lookup page content"""
        dns_ui = DNSLookupUI(self)
        dns_ui.create_content(parent)
    
    def create_subnet_content(self, parent):
        """Create Subnet Calculator page content"""
        subnet_ui = SubnetCalculatorUI(self)
        subnet_ui.create_content(parent)
    
    
    def create_status_bar(self):
        """Create status bar with electric violet theme"""
        # Professional status bar with subtle top border
        status_frame = ctk.CTkFrame(
            self, 
            height=32, 
            corner_radius=0,
            fg_color=COLORS['dashboard_card'],
            border_width=0
        )
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)
        
        # Top border accent
        status_border = ctk.CTkFrame(status_frame, height=1, fg_color=COLORS.get('border', ("#E5E7EB", "#374151")))
        status_border.pack(fill="x", side="top")
        
        # Status indicator dot
        self.status_dot = ctk.CTkLabel(
            status_frame,
            text="●",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['success']
        )
        self.status_dot.pack(side="left", padx=(16, 4), pady=5)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary']
        )
        self.status_label.pack(side="left", pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(
            status_frame, 
            width=150,
            height=4,
            progress_color=COLORS['electric_violet'],
            corner_radius=2
        )
        self.progress_bar.pack(side="left", padx=16, pady=5)
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()  # Hide initially
        
        # Keyboard shortcuts hint - minimal style
        shortcuts_hint = ctk.CTkLabel(
            status_frame,
            text="⌨ Ctrl+K Search  •  Ctrl+H History  •  Ctrl+, Settings",
            font=ctk.CTkFont(size=9),
            text_color=COLORS['text_secondary']
        )
        shortcuts_hint.pack(side="right", padx=16, pady=5)
    
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
                    # Running as compiled exe
                    executable = sys.executable
                    params = ""
                else:
                    # Running as Python script
                    executable = sys.executable  # python.exe
                    script = os.path.abspath(sys.argv[0])
                    # Quote the script path in case it has spaces
                    params = f'"{script}"'
                
                # Get current working directory
                cwd = os.getcwd()
                
                # Debug output
                print(f"DEBUG: Restarting as admin")
                print(f"DEBUG: executable={executable}")
                print(f"DEBUG: params={params}")
                print(f"DEBUG: cwd={cwd}")
                
                # Trigger UAC elevation
                result = ctypes.windll.shell32.ShellExecuteW(
                    None,           # hwnd
                    "runas",        # operation
                    executable,     # file (python.exe or app.exe)
                    params,         # parameters (script path for python)
                    cwd,            # directory
                    1               # SW_SHOWNORMAL
                )
                
                # ShellExecuteW returns > 32 on success
                if result > 32:
                    # Close current instance after a short delay
                    self.after(500, self.quit)
                else:
                    messagebox.showwarning(
                        "Restart Cancelled",
                        "Administrator elevation was cancelled or failed.\n\n"
                        "Please manually run the application as administrator."
                    )
        except Exception as e:
            print(f"DEBUG: Exception in restart_as_admin: {e}")
            messagebox.showerror("Error", f"Could not restart with admin privileges:\n{str(e)}")
    
    def get_network_interfaces(self):
        """Get list of network interfaces (Windows)"""
        try:
            result = self.run_subprocess(
                ["netsh", "interface", "ipv4", "show", "interfaces"],
                capture_output=True,
                text=True,
                encoding='cp1252',  # Windows-1252 for proper German characters
                errors='replace',
                timeout=5
            )
            
            interfaces = []
            lines = result.stdout.split('\n')[3:]  # Skip header lines
            
            # Debug: print raw output
            print(f"DEBUG: netsh output:\n{result.stdout}")
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        idx = parts[0]
                        # Met column is parts[1] (MTU)
                        # Status column is parts[2]
                        # But sometimes status is "disconnected" which shows as separate word
                        # Format: Idx  Met  MTU  State  Name
                        # Example: "5  25  1500  disconnected  WLAN"
                        # Or:      "5  25  1500  connected  Ethernet"
                        
                        status = parts[2]
                        
                        # If status is a number (MTU), adjust parsing
                        if parts[2].isdigit():
                            # Format: Idx Met MTU State Name
                            status = parts[3] if len(parts) > 3 else "unknown"
                            name = ' '.join(parts[4:]) if len(parts) > 4 else "Unknown"
                        else:
                            # Standard format
                            name = ' '.join(parts[3:])
                        
                        # Debug output
                        print(f"DEBUG: Parsed interface - idx={idx}, status={status}, name={name}")
                        
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
                ["netsh", "interface", "ipv4", "show", "config", f'name="{interface_name}"'],
                capture_output=True,
                text=True,
                encoding='cp1252',  # Windows-1252 for proper German characters
                errors='replace',  # Replace errors instead of failing
                timeout=5
            )
            
            # Debug: print the raw output
            print(f"\nDEBUG: get_interface_config for '{interface_name}'")
            print(f"DEBUG: Return code: {result.returncode}")
            print(f"DEBUG: Raw output:\n{result.stdout}")
            print(f"DEBUG: Stderr: {result.stderr}")
            
            config = {
                "dhcp": False,
                "ip": None,
                "subnet": None,
                "gateway": None,
                "dns": []
            }
            
            # Check if command failed
            if result.returncode != 0:
                print(f"DEBUG: Command failed for interface '{interface_name}'")
                return config
            
            lines = result.stdout.split('\n')
            
            # Parse German netsh output line by line
            # German format:
            # IP-Adresse:                           172.20.29.2
            # Subnetzpräfix:                        172.20.29.0/24 (Maske 255.255.255.0)
            # Standardgateway:                      172.20.1.1
            
            for line in lines:
                line = line.strip()
                if not line or ':' not in line:
                    continue
                
                # Split on first colon
                parts = line.split(':', 1)
                if len(parts) != 2:
                    continue
                
                key = parts[0].strip().lower()
                value = parts[1].strip()
                
                # DHCP detection
                if "dhcp aktiviert" in key or "dhcp enabled" in key:
                    if "ja" in value.lower() or "yes" in value.lower():
                        config["dhcp"] = True
                        print(f"DEBUG: Detected DHCP enabled")
                    elif "nein" in value.lower() or "no" in value.lower():
                        config["dhcp"] = False
                        print(f"DEBUG: Detected DHCP disabled (Static IP)")
                
                # IP Address
                elif "ip-adresse" in key or "ip address" in key:
                    if value and value != "None" and value != "Keine":
                        config["ip"] = value
                        print(f"DEBUG: Found IP: {config['ip']}")
                
                # Subnet - extract mask from format "172.20.29.0/24 (Maske 255.255.255.0)"
                elif "subnetzpr" in key or "subnet prefix" in key:
                    if "Maske" in value or "mask" in value.lower():
                        # Extract mask: "172.20.29.0/24 (Maske 255.255.255.0)" -> "255.255.255.0"
                        if '(' in value:
                            mask_part = value.split('(')[1].split(')')[0]
                            if 'Maske' in mask_part or 'mask' in mask_part.lower():
                                mask_parts = mask_part.split()
                                config["subnet"] = mask_parts[-1]  # Last part is the mask
                                print(f"DEBUG: Found Subnet: {config['subnet']}")
                
                # Gateway
                elif "standardgateway" in key or "default gateway" in key:
                    if value and value != "None" and value != "Keine" and value !="0":
                        config["gateway"] = value
                        print(f"DEBUG: Found Gateway: {config['gateway']}")
                
                # DNS Servers
                elif ("dns-server" in key or "dns server" in key) and "konfiguriert" in key:
                    # DNS value might be on same line or next lines
                    if value and value != "Keine" and value != "None":
                        # Could be IP address directly
                        if '.' in value and not any(x in value for x in ['Über', 'Mit', 'Statisch']):
                            config["dns"].append(value)
                            print(f"DEBUG: Found DNS: {value}")
            
            print(f"DEBUG: Final config: {config}")
            return config
        except Exception as e:
            print(f"Error getting interface config for '{interface_name}': {e}")
            import traceback
            traceback.print_exc()
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
            # Debug: print interface name to check encoding
            print(f"DEBUG: Creating card for interface: {interface['name']} (repr: {repr(interface['name'])})")
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
        
        if config and (config.get("ip") or config.get("dhcp")):
            # Configuration mode badge (DHCP or Static)
            mode_frame = ctk.CTkFrame(card, fg_color="transparent")
            mode_frame.pack(fill="x", padx=15, pady=(5, 0))
            
            mode_badge_color = COLORS['electric_violet'] if config["dhcp"] else COLORS['neon_cyan']
            mode_badge = ctk.CTkLabel(
                mode_frame,
                text="📡 DHCP" if config["dhcp"] else "📌 Static IP",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=mode_badge_color,
                corner_radius=6,
                padx=10,
                pady=5
            )
            mode_badge.pack(side="left")
            
            # IP info
            if config["dhcp"]:
                if config["ip"]:
                    ip_text = f"Current IP: {config['ip']}"
                else:
                    ip_text = "Waiting for DHCP assignment..."
            else:
                ip_text = f"IP: {config['ip'] or 'Not configured'}"
                if config['subnet']:
                    ip_text += f" / {config['subnet']}"
                if config['gateway']:
                    ip_text += f" (GW: {config['gateway']})"
            
            # IP info frame with copy button
            ip_info_frame = ctk.CTkFrame(card, fg_color="transparent")
            ip_info_frame.pack(fill="x", padx=15, pady=(5, 10))
            
            ip_label = ctk.CTkLabel(
                ip_info_frame,
                text=ip_text,
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            ip_label.pack(side="left", fill="x", expand=True)
            
            # Copy IP button
            if config.get("ip"):
                def copy_ip_info(ip=config["ip"], subnet=config.get("subnet"), gw=config.get("gateway")):
                    copy_text = f"IP: {ip}"
                    if subnet:
                        copy_text += f"\nSubnet: {subnet}"
                    if gw:
                        copy_text += f"\nGateway: {gw}"
                    self.clipboard_clear()
                    self.clipboard_append(copy_text)
                    self.update()
                    self.show_toast("IP configuration copied", "success")
                
                copy_ip_btn = ctk.CTkButton(
                    ip_info_frame,
                    text="📋",
                    command=copy_ip_info,
                    width=35,
                    height=28,
                    font=ctk.CTkFont(size=14)
                )
                copy_ip_btn.pack(side="left", padx=(10, 0))
            
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
        else:
            # Config could not be retrieved
            error_label = ctk.CTkLabel(
                card,
                text="⚠️ Could not retrieve configuration. Check console for details.",
                font=ctk.CTkFont(size=11),
                text_color=("orange", "orange"),
                anchor="w"
            )
            error_label.pack(fill="x", padx=15, pady=(5, 10))
            
            # Still show config buttons
            button_frame = ctk.CTkFrame(card, fg_color="transparent")
            button_frame.pack(fill="x", padx=15, pady=(0, 10))
            
            config_btn = ctk.CTkButton(
                button_frame,
                text="Configure",
                command=lambda i=interface["name"]: self.show_static_ip_dialog(i),
                width=140,
                height=36
            )
            config_btn.pack(side="left", padx=(0, 5))
    
    def change_theme(self, theme):
        """Change application theme"""
        ctk.set_appearance_mode(theme)
    
    def _flush_update_buffer(self):
        """Flush buffered updates to UI"""
        if self.update_timer:
            self.after_cancel(self.update_timer)
            self.update_timer = None
        
        if not self.update_buffer:
            return
        
        # Process all buffered updates
        for completed, total, result in self.update_buffer:
            self._update_scan_progress(completed, total, result)
        
        self.update_buffer.clear()
    
    def show_export_dialog(self):
        """Show export options dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Export Options")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 500) // 2
        y = self.winfo_y() + (self.winfo_height() - 400) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Content
        content = ctk.CTkFrame(dialog)
        content.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Title
        title = ctk.CTkLabel(
            content,
            text="📤 Export Scan Results",
            font=ctk.CTkFont(size=FONTS['heading'], weight="bold")
        )
        title.pack(pady=(0, SPACING['lg']))
        
        # Export scope
        scope_frame = ctk.CTkFrame(content, fg_color="transparent")
        scope_frame.pack(fill="x", pady=SPACING['md'])
        
        scope_label = ctk.CTkLabel(
            scope_frame,
            text="Export Scope:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        scope_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        scope_var = ctk.StringVar(value="all")
        
        all_radio = ctk.CTkRadioButton(
            scope_frame,
            text=f"All Results ({len(self.all_results)} total)",
            variable=scope_var,
            value="all"
        )
        all_radio.pack(anchor="w", pady=SPACING['xs'])
        
        current_page_radio = ctk.CTkRadioButton(
            scope_frame,
            text=f"Current Page Only ({len(self.result_rows)} results)",
            variable=scope_var,
            value="page"
        )
        current_page_radio.pack(anchor="w", pady=SPACING['xs'])
        
        online_radio = ctk.CTkRadioButton(
            scope_frame,
            text=f"Online Hosts Only ({sum(1 for r in self.all_results if r.get('status') == 'Online')} results)",
            variable=scope_var,
            value="online"
        )
        online_radio.pack(anchor="w", pady=SPACING['xs'])
        
        # Format selection
        format_frame = ctk.CTkFrame(content, fg_color="transparent")
        format_frame.pack(fill="x", pady=SPACING['md'])
        
        format_label = ctk.CTkLabel(
            format_frame,
            text="Export Format:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        format_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        format_var = ctk.StringVar(value="csv")
        
        formats = [
            ("csv", "CSV - Comma Separated Values"),
            ("json", "JSON - JavaScript Object Notation"),
            ("html", "HTML - Web Page Report"),
            ("txt", "TXT - Plain Text"),
            ("xml", "XML - Extensible Markup Language"),
        ]
        
        for value, label in formats:
            radio = ctk.CTkRadioButton(
                format_frame,
                text=label,
                variable=format_var,
                value=value
            )
            radio.pack(anchor="w", pady=SPACING['xs'])
        
        # Buttons
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x", pady=SPACING['lg'], side="bottom")
        
        cancel_btn = StyledButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            size="medium",
            variant="neutral"
        )
        cancel_btn.pack(side="right", padx=SPACING['xs'])
        
        def do_export():
            scope = scope_var.get()
            format_type = format_var.get()
            dialog.destroy()
            self.perform_export(scope, format_type)
        
        export_btn = StyledButton(
            button_frame,
            text="📤 Export",
            command=do_export,
            size="large",
            variant="primary"
        )
        export_btn.pack(side="right")
    
    def perform_export(self, scope, format_type):
        """Perform the actual export"""
        # Filter results based on scope
        if scope == "all":
            results_to_export = self.all_results
        elif scope == "page":
            results_to_export = [row.result_data for row in self.result_rows if hasattr(row, 'result_data')]
        elif scope == "online":
            results_to_export = [r for r in self.all_results if r.get('status') == 'Online']
        else:
            results_to_export = self.all_results
        
        if not results_to_export:
            messagebox.showinfo("Information", "No data to export with selected filter.")
            return
        
        # Get desktop path
        desktop = Path.home() / "Desktop"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"NetToolsScan_{timestamp}"
        
        # File extension mapping
        ext_map = {
            "csv": ".csv",
            "json": ".json",
            "html": ".html",
            "txt": ".txt",
            "xml": ".xml"
        }
        
        # Ask for save location
        filepath = filedialog.asksaveasfilename(
            defaultextension=ext_map.get(format_type, ".csv"),
            filetypes=[(f"{format_type.upper()} files", f"*{ext_map.get(format_type, '.csv')}")],
            initialdir=desktop,
            initialfile=default_filename
        )
        
        if not filepath:
            return
        
        try:
            if format_type == "csv":
                self._export_as_csv(filepath, results_to_export)
            elif format_type == "json":
                self._export_as_json(filepath, results_to_export)
            elif format_type == "html":
                self._export_as_html(filepath, results_to_export)
            elif format_type == "txt":
                self._export_as_txt(filepath, results_to_export)
            elif format_type == "xml":
                self._export_as_xml(filepath, results_to_export)
            
            self.show_toast(f"✓ Exported {len(results_to_export)} results", "success")
            self.status_label.configure(text=f"Exported to: {filepath}")
        except Exception as e:
            self.show_toast(f"Export failed: {str(e)}", "error")
    
    def _export_as_csv(self, filepath, results):
        """Export results as CSV"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['IP Address', 'Hostname', 'Status', 'Response Time'])
            for result in results:
                writer.writerow([
                    result.get('ip', ''),
                    result.get('hostname', ''),
                    result.get('status', ''),
                    result.get('rtt', '')
                ])
    
    def _export_as_json(self, filepath, results):
        """Export results as JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    def _export_as_html(self, filepath, results):
        """Export results as HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>NetTools Scan Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        .info {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        th {{ background: #4472C4; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f5f5f5; }}
        .online {{ color: green; font-weight: bold; }}
        .offline {{ color: red; }}
    </style>
</head>
<body>
    <h1>🔍 NetTools Scan Report</h1>
    <div class="info">
        <strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
        <strong>Total Results:</strong> {len(results)}<br>
        <strong>Online Hosts:</strong> {sum(1 for r in results if r.get('status') == 'Online')}<br>
        <strong>Offline Hosts:</strong> {sum(1 for r in results if r.get('status') == 'Offline')}
    </div>
    <table>
        <thead>
            <tr>
                <th>IP Address</th>
                <th>Hostname</th>
                <th>Status</th>
                <th>Response Time</th>
            </tr>
        </thead>
        <tbody>
"""
        for result in results:
            status_class = "online" if result.get('status') == 'Online' else "offline"
            html_content += f"""
            <tr>
                <td>{result.get('ip', '')}</td>
                <td>{result.get('hostname', '-')}</td>
                <td class="{status_class}">{result.get('status', '')}</td>
                <td>{result.get('rtt', '')}</td>
            </tr>
"""
        
        html_content += """
        </tbody>
    </table>
</body>
</html>
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _export_as_txt(self, filepath, results):
        """Export results as plain text"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("NetTools Scan Report\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Results: {len(results)}\n\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'IP Address':<20} {'Hostname':<30} {'Status':<10} {'RTT':<10}\n")
            f.write("-" * 80 + "\n")
            for result in results:
                f.write(f"{result.get('ip', ''):<20} {result.get('hostname', '-'):<30} {result.get('status', ''):<10} {result.get('rtt', ''):<10}\n")
    
    def _export_as_xml(self, filepath, results):
        """Export results as XML"""
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_content += '<scan_results>\n'
        xml_content += f'  <metadata>\n'
        xml_content += f'    <timestamp>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</timestamp>\n'
        xml_content += f'    <total_results>{len(results)}</total_results>\n'
        xml_content += f'  </metadata>\n'
        xml_content += '  <hosts>\n'
        for result in results:
            xml_content += '    <host>\n'
            xml_content += f'      <ip>{result.get("ip", "")}</ip>\n'
            xml_content += f'      <hostname>{result.get("hostname", "")}</hostname>\n'
            xml_content += f'      <status>{result.get("status", "")}</status>\n'
            xml_content += f'      <response_time>{result.get("rtt", "")}</response_time>\n'
            xml_content += '    </host>\n'
        xml_content += '  </hosts>\n'
        xml_content += '</scan_results>\n'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)
            self.after(2000, lambda: self.status_label.configure(text="Ready."))
    
    def copy_textbox_to_clipboard(self, textbox):
        """Copy textbox content to clipboard"""
        text = textbox.get("1.0", 'end-1c')
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.show_toast("Copied to clipboard!", "success")
            self.status_label.configure(text="Copied to clipboard!")
    
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
            # Set DHCP for IP - use 'name=' format with quotes for interface names with spaces
            result = self.run_subprocess(
                ["netsh", "interface", "ipv4", "set", "address", f'name="{interface_name}"', "dhcp"],
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
                ["netsh", "interface", "ipv4", "set", "dnsservers", f'name="{interface_name}"', "dhcp"],
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
        # Check admin privileges first
        if not self.is_admin():
            result = messagebox.askyesno(
                "Administrator Required",
                "Administrator privileges are required to change network settings.\n\n"
                "Do you want to restart the application with administrator privileges?"
            )
            if result:
                self.restart_as_admin()
            return
        
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
            # Build command - use 'name=' format with quotes for interface names with spaces
            if gateway:
                cmd = ["netsh", "interface", "ipv4", "set", "address", f'name="{interface_name}"', "static", ip, subnet, gateway]
            else:
                cmd = ["netsh", "interface", "ipv4", "set", "address", f'name="{interface_name}"', "static", ip, subnet]
            
            # Debug: print command
            print(f"DEBUG: Running command: {' '.join(cmd)}")
            
            result = self.run_subprocess(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                # Debug output
                print(f"DEBUG: Error occurred. Return code: {result.returncode}")
                print(f"DEBUG: stdout: {result.stdout}")
                print(f"DEBUG: stderr: {result.stderr}")
                
                if "disconnected" in error_msg.lower():
                    messagebox.showwarning(
                        "Interface Disconnected",
                        f"Cannot configure '{interface_name}' because it is currently disconnected.\n\n"
                        "Please connect the network cable or enable Wi-Fi, then try again."
                    )
                elif "not valid" in error_msg.lower() or "incorrect" in error_msg.lower() or "syntax" in error_msg.lower():
                    messagebox.showerror(
                        "Invalid Configuration",
                        f"The IP configuration is invalid:\n\n{error_msg}\n\n"
                        "Command run:\n{' '.join(cmd)}\n\n"
                        "Please check:\n"
                        "• IP address format (e.g., 192.168.1.100)\n"
                        "• Subnet mask format (e.g., 255.255.255.0)\n"
                        "• Gateway is in the same subnet"
                    )
                else:
                    messagebox.showerror("Error", f"Failed to set static IP:\n{error_msg}\n\nCommand: {' '.join(cmd)}")
                return
            
            # Set DNS if provided
            if dns:
                self.run_subprocess(
                    ["netsh", "interface", "ipv4", "set", "dnsservers", f'name="{interface_name}"', "static", dns, "primary"],
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
                            # Set to DHCP - use proper name format with quotes
                            result = self.run_subprocess(
                                ["netsh", "interface", "ipv4", "set", "address", 
                                 f'name="{interface_name}"', "dhcp"],
                                capture_output=True,
                                text=True,
                                timeout=10
                            )
                            
                            if result.returncode == 0:
                                # Set DNS to DHCP
                                self.run_subprocess(
                                    ["netsh", "interface", "ipv4", "set", "dnsservers",
                                     f'name="{interface_name}"', "dhcp"],
                                    capture_output=True,
                                    text=True,
                                    timeout=10
                                )
                                success_count += 1
                            else:
                                error_msg = result.stderr or result.stdout
                                if "disconnected" in error_msg.lower():
                                    errors.append(f"{interface_name}: Interface is disconnected")
                                else:
                                    errors.append(f"{interface_name}: Failed to set DHCP")
                                error_count += 1
                        else:
                            # Set static IP
                            if config["ip"] and config["subnet"]:
                                # Determine subnet mask from prefix or use default
                                subnet_mask = config.get("subnet_mask", config.get("subnet", "255.255.255.0"))
                                gateway = config.get("gateway", "none")
                                
                                # Build netsh command for static IP - use proper name format with quotes
                                cmd = [
                                    "netsh", "interface", "ipv4", "set", "address",
                                    f'name="{interface_name}"',
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
                                                        f'name="{interface_name}"',
                                                        "source=static",
                                                        "address=" + dns,
                                                        "register=primary"
                                                    ]
                                                else:
                                                    # Additional DNS servers
                                                    dns_cmd = [
                                                        "netsh", "interface", "ipv4", "add", "dns",
                                                        f'name="{interface_name}"',
                                                        "address=" + dns,
                                                        "index=" + str(i + 1)
                                                    ]
                                                self.run_subprocess(dns_cmd, capture_output=True, timeout=10)
                                    
                                    success_count += 1
                                else:
                                    error_msg = result.stderr or result.stdout or "Unknown error"
                                    if "disconnected" in error_msg.lower():
                                        errors.append(f"{interface_name}: Interface is disconnected")
                                    else:
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
            
            except Exception as ex:
                error_str = str(ex)
                self.after(0, lambda: progress_label.destroy())
                self.after(0, lambda msg=error_str: messagebox.showerror(
                    "Error",
                    f"Error applying profile: {msg}"
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
    
    def show_portscan_comparison(self):
        """Show port scan comparison window"""
        scans = self.comparison_history.get_port_scan_history()
        
        if len(scans) < 2:
            messagebox.showinfo(
                "Port Scan Comparison", 
                "You need at least 2 saved port scans to compare.\n\n"
                "Run multiple port scans using the Port Scanner tool first.\n"
                "Results are automatically saved to history."
            )
            return
        
        # Create comparison window
        comp_window = ctk.CTkToplevel(self)
        comp_window.title("Port Scan Comparison")
        comp_window.geometry("900x700")
        comp_window.transient(self)
        comp_window.grab_set()
        
        comp_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - comp_window.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - comp_window.winfo_height()) // 2
        comp_window.geometry(f"+{x}+{y}")
        
        comp_window.lift()
        comp_window.focus_force()
        
        # Title
        ctk.CTkLabel(
            comp_window,
            text="🔌 Port Scan Comparison",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['electric_violet']
        ).pack(padx=20, pady=(20, 10))
        
        # Selection frame
        select_frame = ctk.CTkFrame(comp_window)
        select_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Prepare scan options
        scan_options = [
            f"{i+1}. {s['target']} ({len(s['open_ports'])} open) - {s['timestamp'][:16]}" 
            for i, s in enumerate(scans)
        ]
        
        ctk.CTkLabel(select_frame, text="Scan 1 (Baseline):", 
                    font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        scan1_var = ctk.StringVar(value=scan_options[0])
        ctk.CTkOptionMenu(select_frame, variable=scan1_var, values=scan_options, width=400).grid(row=0, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(select_frame, text="Scan 2 (Compare):", 
                    font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        scan2_var = ctk.StringVar(value=scan_options[-1] if len(scan_options) > 1 else scan_options[0])
        ctk.CTkOptionMenu(select_frame, variable=scan2_var, values=scan_options, width=400).grid(row=1, column=1, padx=10, pady=10)
        
        compare_btn = StyledButton(select_frame, text="⚖️ Compare", variant="primary")
        compare_btn.grid(row=0, column=2, rowspan=2, padx=20, pady=10)
        
        # Results area
        results_frame = ctk.CTkFrame(comp_window)
        results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        results_scroll = ctk.CTkScrollableFrame(results_frame)
        results_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(results_scroll, text="Select two scans and click 'Compare'",
                    font=ctk.CTkFont(size=12), text_color=COLORS['text_secondary']).pack(pady=50)
        
        def do_comparison():
            idx1 = int(scan1_var.get().split(".")[0]) - 1
            idx2 = int(scan2_var.get().split(".")[0]) - 1
            
            if idx1 == idx2:
                messagebox.showwarning("Same Scan", "Please select two different scans.")
                return
            
            comparison = self.comparison_history.compare_port_scans(scans[idx1], scans[idx2])
            
            for widget in results_scroll.winfo_children():
                widget.destroy()
            
            # Summary
            summary_frame = StyledCard(results_scroll, variant="elevated")
            summary_frame.pack(fill="x", padx=5, pady=10)
            
            ctk.CTkLabel(summary_frame, text="📊 Comparison Summary",
                        font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
            
            ctk.CTkLabel(summary_frame,
                text=f"Target: {comparison['target']}  |  Changes: {comparison['total_changes']}",
                font=ctk.CTkFont(size=12)).pack(pady=5)
            
            summary_text = f"🆕 Newly Opened: {len(comparison['newly_opened'])}  |  "
            summary_text += f"❌ Newly Closed: {len(comparison['newly_closed'])}  |  "
            summary_text += f"➖ Unchanged: {len(comparison['unchanged'])}"
            
            ctk.CTkLabel(summary_frame, text=summary_text, font=ctk.CTkFont(size=11)).pack(pady=(0, 10))
            
            # Newly opened ports
            if comparison['newly_opened']:
                opened_frame = StyledCard(results_scroll, variant="elevated")
                opened_frame.pack(fill="x", padx=5, pady=5)
                
                ctk.CTkLabel(opened_frame, text="🆕 Newly Opened Ports",
                            font=ctk.CTkFont(size=13, weight="bold"),
                            text_color=COLORS['success']).pack(anchor="w", padx=15, pady=(10, 5))
                
                for port in sorted(comparison['newly_opened']):
                    details = comparison['newly_opened_details'].get(port, {})
                    service = details.get('service', 'unknown')
                    ctk.CTkLabel(opened_frame,
                        text=f"  Port {port} - {service}",
                        font=ctk.CTkFont(family="Consolas", size=11),
                        text_color=COLORS['success']).pack(anchor="w", padx=15)
                
                ctk.CTkFrame(opened_frame, height=10, fg_color="transparent").pack()
            
            # Newly closed ports
            if comparison['newly_closed']:
                closed_frame = StyledCard(results_scroll, variant="elevated")
                closed_frame.pack(fill="x", padx=5, pady=5)
                
                ctk.CTkLabel(closed_frame, text="❌ Newly Closed Ports",
                            font=ctk.CTkFont(size=13, weight="bold"),
                            text_color=COLORS['danger']).pack(anchor="w", padx=15, pady=(10, 5))
                
                for port in sorted(comparison['newly_closed']):
                    details = comparison['newly_closed_details'].get(port, {})
                    service = details.get('service', 'unknown')
                    ctk.CTkLabel(closed_frame,
                        text=f"  Port {port} - {service}",
                        font=ctk.CTkFont(family="Consolas", size=11),
                        text_color=COLORS['danger']).pack(anchor="w", padx=15)
                
                ctk.CTkFrame(closed_frame, height=10, fg_color="transparent").pack()
            
            # Unchanged ports
            if comparison['unchanged']:
                unchanged_frame = StyledCard(results_scroll, variant="elevated")
                unchanged_frame.pack(fill="x", padx=5, pady=5)
                
                ctk.CTkLabel(unchanged_frame, text=f"➖ Unchanged Ports ({len(comparison['unchanged'])})",
                            font=ctk.CTkFont(size=13, weight="bold"),
                            text_color=COLORS['text_secondary']).pack(anchor="w", padx=15, pady=(10, 5))
                
                ports_text = ", ".join(str(p) for p in sorted(comparison['unchanged'])[:20])
                if len(comparison['unchanged']) > 20:
                    ports_text += f"... (+{len(comparison['unchanged']) - 20} more)"
                
                ctk.CTkLabel(unchanged_frame, text=ports_text,
                            font=ctk.CTkFont(size=11),
                            text_color=COLORS['text_secondary']).pack(anchor="w", padx=15, pady=(0, 10))
            
            self.show_toast("Comparison complete", "success")
        
        compare_btn.configure(command=do_comparison)
        
        StyledButton(comp_window, text="Close", command=comp_window.destroy,
                    variant="secondary").pack(pady=(0, 15))
    
    def show_dns_comparison(self):
        """Show DNS lookup comparison window"""
        lookups = self.comparison_history.get_dns_lookup_history()
        
        if len(lookups) < 2:
            messagebox.showinfo(
                "DNS Lookup Comparison", 
                "You need at least 2 saved DNS lookups to compare.\n\n"
                "Perform multiple DNS lookups using the DNS tool first.\n"
                "Results are automatically saved to history."
            )
            return
        
        # Create comparison window
        comp_window = ctk.CTkToplevel(self)
        comp_window.title("DNS Lookup Comparison")
        comp_window.geometry("900x650")
        comp_window.transient(self)
        comp_window.grab_set()
        
        comp_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - comp_window.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - comp_window.winfo_height()) // 2
        comp_window.geometry(f"+{x}+{y}")
        
        comp_window.lift()
        comp_window.focus_force()
        
        # Title
        ctk.CTkLabel(
            comp_window,
            text="🌐 DNS Lookup Comparison",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['electric_violet']
        ).pack(padx=20, pady=(20, 10))
        
        # Selection frame
        select_frame = ctk.CTkFrame(comp_window)
        select_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Prepare lookup options
        lookup_options = [
            f"{i+1}. {l['query']} ({l['record_type']}) - {l['timestamp'][:16]}" 
            for i, l in enumerate(lookups)
        ]
        
        ctk.CTkLabel(select_frame, text="Lookup 1 (Baseline):", 
                    font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        lookup1_var = ctk.StringVar(value=lookup_options[0])
        ctk.CTkOptionMenu(select_frame, variable=lookup1_var, values=lookup_options, width=400).grid(row=0, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(select_frame, text="Lookup 2 (Compare):", 
                    font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        lookup2_var = ctk.StringVar(value=lookup_options[-1] if len(lookup_options) > 1 else lookup_options[0])
        ctk.CTkOptionMenu(select_frame, variable=lookup2_var, values=lookup_options, width=400).grid(row=1, column=1, padx=10, pady=10)
        
        compare_btn = StyledButton(select_frame, text="⚖️ Compare", variant="primary")
        compare_btn.grid(row=0, column=2, rowspan=2, padx=20, pady=10)
        
        # Results area
        results_frame = ctk.CTkFrame(comp_window)
        results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        results_scroll = ctk.CTkScrollableFrame(results_frame)
        results_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(results_scroll, text="Select two lookups and click 'Compare'",
                    font=ctk.CTkFont(size=12), text_color=COLORS['text_secondary']).pack(pady=50)
        
        def do_comparison():
            idx1 = int(lookup1_var.get().split(".")[0]) - 1
            idx2 = int(lookup2_var.get().split(".")[0]) - 1
            
            if idx1 == idx2:
                messagebox.showwarning("Same Lookup", "Please select two different lookups.")
                return
            
            comparison = self.comparison_history.compare_dns_lookups(lookups[idx1], lookups[idx2])
            
            for widget in results_scroll.winfo_children():
                widget.destroy()
            
            # Summary
            summary_frame = StyledCard(results_scroll, variant="elevated")
            summary_frame.pack(fill="x", padx=5, pady=10)
            
            ctk.CTkLabel(summary_frame, text="📊 DNS Comparison Summary",
                        font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
            
            status_text = "🔄 Changes detected" if comparison['has_changes'] else "✅ No changes"
            status_color = COLORS['warning'] if comparison['has_changes'] else COLORS['success']
            
            ctk.CTkLabel(summary_frame,
                text=f"Query: {comparison['query']}  |  Type: {comparison['record_type']}  |  {status_text}",
                font=ctk.CTkFont(size=12), text_color=status_color).pack(pady=5)
            
            ctk.CTkLabel(summary_frame,
                text=f"From: {comparison['lookup1_time'][:16]}  →  To: {comparison['lookup2_time'][:16]}",
                font=ctk.CTkFont(size=11), text_color=COLORS['text_secondary']).pack(pady=(0, 10))
            
            # Added records
            if comparison['added']:
                added_frame = StyledCard(results_scroll, variant="elevated")
                added_frame.pack(fill="x", padx=5, pady=5)
                
                ctk.CTkLabel(added_frame, text="🆕 Added Records",
                            font=ctk.CTkFont(size=13, weight="bold"),
                            text_color=COLORS['success']).pack(anchor="w", padx=15, pady=(10, 5))
                
                for record in comparison['added']:
                    ctk.CTkLabel(added_frame, text=f"  + {record}",
                        font=ctk.CTkFont(family="Consolas", size=11),
                        text_color=COLORS['success']).pack(anchor="w", padx=15)
                
                ctk.CTkFrame(added_frame, height=10, fg_color="transparent").pack()
            
            # Removed records
            if comparison['removed']:
                removed_frame = StyledCard(results_scroll, variant="elevated")
                removed_frame.pack(fill="x", padx=5, pady=5)
                
                ctk.CTkLabel(removed_frame, text="❌ Removed Records",
                            font=ctk.CTkFont(size=13, weight="bold"),
                            text_color=COLORS['danger']).pack(anchor="w", padx=15, pady=(10, 5))
                
                for record in comparison['removed']:
                    ctk.CTkLabel(removed_frame, text=f"  - {record}",
                        font=ctk.CTkFont(family="Consolas", size=11),
                        text_color=COLORS['danger']).pack(anchor="w", padx=15)
                
                ctk.CTkFrame(removed_frame, height=10, fg_color="transparent").pack()
            
            # Unchanged records
            if comparison['unchanged']:
                unchanged_frame = StyledCard(results_scroll, variant="elevated")
                unchanged_frame.pack(fill="x", padx=5, pady=5)
                
                ctk.CTkLabel(unchanged_frame, text=f"➖ Unchanged Records ({len(comparison['unchanged'])})",
                            font=ctk.CTkFont(size=13, weight="bold"),
                            text_color=COLORS['text_secondary']).pack(anchor="w", padx=15, pady=(10, 5))
                
                for record in list(comparison['unchanged'])[:10]:
                    ctk.CTkLabel(unchanged_frame, text=f"  {record}",
                        font=ctk.CTkFont(family="Consolas", size=11),
                        text_color=COLORS['text_secondary']).pack(anchor="w", padx=15)
                
                if len(comparison['unchanged']) > 10:
                    ctk.CTkLabel(unchanged_frame, 
                        text=f"  ... and {len(comparison['unchanged']) - 10} more",
                        font=ctk.CTkFont(size=11),
                        text_color=COLORS['text_secondary']).pack(anchor="w", padx=15)
                
                ctk.CTkFrame(unchanged_frame, height=10, fg_color="transparent").pack()
            
            self.show_toast("Comparison complete", "success")
        
        compare_btn.configure(command=do_comparison)
        
        StyledButton(comp_window, text="Close", command=comp_window.destroy,
                    variant="secondary").pack(pady=(0, 15))
    
    def show_traceroute_comparison(self):
        """Show traceroute comparison window"""
        traces = self.traceroute_manager.get_traces()
        
        if len(traces) < 2:
            messagebox.showinfo(
                "Traceroute Comparison", 
                "You need at least 2 saved traceroutes to compare.\n\n"
                "Run multiple traceroutes using the Traceroute tool first.\n"
                "Results are automatically saved to history."
            )
            return
        
        # Create comparison window
        comp_window = ctk.CTkToplevel(self)
        comp_window.title("Traceroute Comparison")
        comp_window.geometry("1000x750")
        comp_window.transient(self)
        comp_window.grab_set()
        
        # Center window
        comp_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - comp_window.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - comp_window.winfo_height()) // 2
        comp_window.geometry(f"+{x}+{y}")
        
        comp_window.lift()
        comp_window.focus_force()
        
        # Title
        title_label = ctk.CTkLabel(
            comp_window,
            text="🛤️ Traceroute Comparison",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['electric_violet']
        )
        title_label.pack(padx=20, pady=(20, 10))
        
        # Selection frame
        select_frame = ctk.CTkFrame(comp_window)
        select_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Prepare trace options
        trace_options = [
            f"{t['id']} - {t['target']} ({t['summary']['total_hops']} hops)" 
            for t in traces
        ]
        
        # Trace 1 selection
        ctk.CTkLabel(
            select_frame, text="Trace 1 (Baseline):", 
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        trace1_var = ctk.StringVar(value=trace_options[0])
        trace1_menu = ctk.CTkOptionMenu(select_frame, variable=trace1_var, values=trace_options, width=450)
        trace1_menu.grid(row=0, column=1, padx=10, pady=10)
        
        # Trace 2 selection
        ctk.CTkLabel(
            select_frame, text="Trace 2 (Compare):", 
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        trace2_var = ctk.StringVar(value=trace_options[-1] if len(trace_options) > 1 else trace_options[0])
        trace2_menu = ctk.CTkOptionMenu(select_frame, variable=trace2_var, values=trace_options, width=450)
        trace2_menu.grid(row=1, column=1, padx=10, pady=10)
        
        # Compare button
        compare_btn = StyledButton(
            select_frame,
            text="⚖️ Compare",
            variant="primary"
        )
        compare_btn.grid(row=0, column=2, rowspan=2, padx=20, pady=10)
        
        # Results area
        results_frame = ctk.CTkFrame(comp_window)
        results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        results_scroll = ctk.CTkScrollableFrame(results_frame)
        results_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        results_label = ctk.CTkLabel(
            results_scroll,
            text="Select two traceroutes and click 'Compare' to see differences",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        results_label.pack(pady=50)
        
        def do_comparison():
            """Perform the comparison"""
            trace1_id = trace1_var.get().split(" - ")[0]
            trace2_id = trace2_var.get().split(" - ")[0]
            
            if trace1_id == trace2_id:
                messagebox.showwarning("Same Trace", "Please select two different traceroutes to compare.")
                return
            
            comparison = self.traceroute_manager.compare_traces(trace1_id, trace2_id)
            
            if not comparison:
                messagebox.showerror("Error", "Could not load traceroute data.")
                return
            
            # Clear results
            for widget in results_scroll.winfo_children():
                widget.destroy()
            
            # Summary card
            summary_frame = StyledCard(results_scroll, variant="elevated")
            summary_frame.pack(fill="x", padx=5, pady=10)
            
            ctk.CTkLabel(
                summary_frame,
                text="📊 Comparison Summary",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(pady=(10, 5))
            
            # Trace info
            info_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=5)
            
            t1 = comparison["trace1"]
            t2 = comparison["trace2"]
            
            ctk.CTkLabel(
                info_frame,
                text=f"Baseline: {t1['target']} ({t1['total_hops']} hops, avg {t1['avg_latency'] or 'N/A'}ms) - {t1['timestamp'][:16]}",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['neon_cyan']
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                info_frame,
                text=f"Compare:  {t2['target']} ({t2['total_hops']} hops, avg {t2['avg_latency'] or 'N/A'}ms) - {t2['timestamp'][:16]}",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['electric_violet']
            ).pack(anchor="w")
            
            # Summary stats
            s = comparison["summary"]
            summary_text = f"🔄 Route Changes: {s['route_changes']}  |  "
            summary_text += f"📈 Improved: {s['latency_improved']}  |  "
            summary_text += f"📉 Degraded: {s['latency_degraded']}  |  "
            summary_text += f"⏱️ New Timeouts: {s['new_timeouts']}  |  "
            summary_text += f"✅ Resolved: {s['resolved_timeouts']}"
            
            ctk.CTkLabel(
                summary_frame,
                text=summary_text,
                font=ctk.CTkFont(size=11)
            ).pack(pady=(5, 10))
            
            # Hop comparison table header
            header_frame = ctk.CTkFrame(results_scroll, fg_color=COLORS['electric_violet'])
            header_frame.pack(fill="x", padx=5, pady=(10, 2))
            
            headers = [("Hop", 50), ("Baseline IP", 150), ("Compare IP", 150), 
                      ("Baseline (ms)", 100), ("Compare (ms)", 100), ("Δ Latency", 80), ("Status", 120)]
            
            header_inner = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_inner.pack(fill="x", padx=10, pady=8)
            
            for text, width in headers:
                ctk.CTkLabel(
                    header_inner, text=text,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="white", width=width, anchor="w"
                ).pack(side="left", padx=3)
            
            # Hop rows
            status_colors = {
                "unchanged": COLORS['text_secondary'],
                "route_changed": COLORS['warning'],
                "improved": COLORS['success'],
                "degraded": COLORS['danger'],
                "new_timeout": COLORS['danger'],
                "resolved_timeout": COLORS['success'],
                "new_hop": COLORS['neon_cyan'],
                "removed_hop": COLORS['warning']
            }
            
            status_icons = {
                "unchanged": "➖",
                "route_changed": "🔀",
                "improved": "📈",
                "degraded": "📉",
                "new_timeout": "⏱️",
                "resolved_timeout": "✅",
                "new_hop": "🆕",
                "removed_hop": "❌"
            }
            
            for i, hop in enumerate(comparison["hops"]):
                row_color = ("gray90", "gray25") if i % 2 == 0 else ("gray85", "gray20")
                row_frame = ctk.CTkFrame(results_scroll, fg_color=row_color, corner_radius=4)
                row_frame.pack(fill="x", padx=5, pady=1)
                
                row_inner = ctk.CTkFrame(row_frame, fg_color="transparent")
                row_inner.pack(fill="x", padx=10, pady=6)
                
                # Hop number
                ctk.CTkLabel(row_inner, text=str(hop['hop']), width=50, anchor="w",
                            font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=3)
                
                # Baseline IP
                ip1_color = COLORS['danger'] if hop['trace1_timeout'] else COLORS['text_primary']
                ctk.CTkLabel(row_inner, text=hop['trace1_ip'], width=150, anchor="w",
                            font=ctk.CTkFont(family="Consolas", size=10),
                            text_color=ip1_color).pack(side="left", padx=3)
                
                # Compare IP
                ip2_color = COLORS['danger'] if hop['trace2_timeout'] else COLORS['text_primary']
                ctk.CTkLabel(row_inner, text=hop['trace2_ip'], width=150, anchor="w",
                            font=ctk.CTkFont(family="Consolas", size=10),
                            text_color=ip2_color).pack(side="left", padx=3)
                
                # Latencies
                lat1 = f"{hop['trace1_latency']}" if hop['trace1_latency'] else "-"
                lat2 = f"{hop['trace2_latency']}" if hop['trace2_latency'] else "-"
                
                ctk.CTkLabel(row_inner, text=lat1, width=100, anchor="w",
                            font=ctk.CTkFont(size=10)).pack(side="left", padx=3)
                ctk.CTkLabel(row_inner, text=lat2, width=100, anchor="w",
                            font=ctk.CTkFont(size=10)).pack(side="left", padx=3)
                
                # Latency diff
                diff_text = f"{hop['latency_diff']:+.1f}" if hop['latency_diff'] is not None else "-"
                diff_color = COLORS['success'] if hop['latency_diff'] and hop['latency_diff'] < 0 else (
                    COLORS['danger'] if hop['latency_diff'] and hop['latency_diff'] > 0 else COLORS['text_secondary']
                )
                ctk.CTkLabel(row_inner, text=diff_text, width=80, anchor="w",
                            font=ctk.CTkFont(size=10), text_color=diff_color).pack(side="left", padx=3)
                
                # Status
                status = hop['status']
                status_text = f"{status_icons.get(status, '')} {status.replace('_', ' ').title()}"
                ctk.CTkLabel(row_inner, text=status_text, width=120, anchor="w",
                            font=ctk.CTkFont(size=10),
                            text_color=status_colors.get(status, COLORS['text_primary'])).pack(side="left", padx=3)
            
            self.show_toast("Comparison complete", "success")
        
        compare_btn.configure(command=do_comparison)
        
        # Close button
        close_btn = StyledButton(
            comp_window,
            text="Close",
            command=comp_window.destroy,
            variant="secondary"
        )
        close_btn.pack(pady=(0, 15))
    
    def open_live_ping_monitor(self):
        """Open the live ping monitor window"""
        # Now works without matplotlib!
        LivePingMonitorWindow(self)
    
    def change_grid_layout(self, choice):
        """This method is defined in LivePingMonitorWindow class"""
        pass
    
    def toggle_favorite(self, tool_id):
        """Toggle tool as favorite"""
        if tool_id in self.favorite_tools:
            self.favorite_tools.remove(tool_id)
        else:
            self.favorite_tools.add(tool_id)
        
        # Save and update UI
        self.save_window_state()
        self.update_favorites_ui()
        self.update_nav_button_stars()
    
    def update_favorites_ui(self):
        """Update favorites section in sidebar"""
        try:
            # Clear existing buttons
            for widget in self.favorites_buttons_frame.winfo_children():
                widget.destroy()
            
            if self.favorite_tools:
                # Pack frame before first category
                if hasattr(self, 'first_category_label') and self.first_category_label:
                    self.favorites_frame.pack(fill="x", padx=10, pady=(0, 10), before=self.first_category_label)
                else:
                    # Fallback: just pack normally  
                    self.favorites_frame.pack(fill="x", padx=10, pady=(0, 10))
                
                self.favorites_label.pack(anchor="w", pady=(5, 5))
                self.favorites_buttons_frame.pack(fill="x")
                
                # Tool names and icons mapping
                tool_info = {
                    "scanner": ("📡", "IPv4 Scanner"),
                    "portscan": ("🔌", "Port Scanner"),
                    "traceroute": ("🛤️", "Traceroute"),
                    "bandwidth": ("📶", "Bandwidth Test"),
                    "dns": ("🌐", "DNS Lookup"),
                    "subnet": ("🔢", "Subnet Calculator"),
                    "mac": ("🔗", "MAC Formatter"),
                    "compare": ("⚖️", "Scan Comparison"),
                    "profiles": ("📁", "Network Profiles"),
                    "panos": ("🛡️", "PAN-OS Generator"),
                    "phpipam": ("📊", "phpIPAM"),
                    "remote": ("🖥️", "Remote Tools"),
                }
                
                for tool_id in sorted(self.favorite_tools):
                    icon, label = tool_info.get(tool_id, ("•", tool_id))
                    btn = ctk.CTkButton(
                        self.favorites_buttons_frame,
                        text=f" {icon}  {label}",
                        command=lambda tid=tool_id: self.switch_tool(tid),
                        width=220,
                        height=36,
                        corner_radius=8,
                        anchor="w",
                        font=ctk.CTkFont(size=12),
                        fg_color=COLORS['neutral'],
                        hover_color=COLORS['neutral_hover'],
                        text_color="white"
                    )
                    btn.pack(fill="x", pady=2)
                    # Store for collapse/expand
                    btn._nav_icon = icon
                    btn._nav_label = label
                    btn._is_favorite = True
            else:
                # Completely hide frame when empty (no gap)
                self.favorites_frame.pack_forget()
        except Exception as e:
            print(f"Error updating favorites UI: {e}")
    
    def update_nav_button_stars(self):
        """Update star indicators on navigation buttons"""
        for tool_id, btn in self.nav_buttons.items():
            original_text = btn.cget("text").replace(" ⭐", "")
            if tool_id in self.favorite_tools:
                btn.configure(text=f"{original_text} ⭐")
            else:
                btn.configure(text=original_text)
    
    def show_tool_context_menu(self, event, tool_id):
        """Show context menu for tool (right-click)"""
        import tkinter as tk
        
        context_menu = tk.Menu(self, tearoff=0)
        
        # Favorite/Unfavorite option
        if tool_id in self.favorite_tools:
            context_menu.add_command(
                label="⭐ Remove from Favorites",
                command=lambda: self.toggle_favorite(tool_id)
            )
        else:
            context_menu.add_command(
                label="☆ Add to Favorites",
                command=lambda: self.toggle_favorite(tool_id)
            )
        
        # Show menu at cursor position
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def switch_tool(self, tool_id):
        """Switch to a tool"""
        try:
            # Switch to the page
            self.switch_page(tool_id)
        except Exception as e:
            print(f"Error switching tool: {e}")
    
    def on_enter_key(self, event):
        """Handle Enter key press"""
        # Note: Scanner Enter key is now handled within scanner UI
        if self.current_page == "mac":
            if self.format_entries[0].get():
                self.copy_to_clipboard(self.format_entries[0])


class LivePingMonitorWindow(ctk.CTkToplevel):
    """Live Ping Monitor Window with real-time graphs"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Live Ping Monitor")
        self.geometry("1000x600")
        
        # Monitor instance
        self.monitor = LivePingMonitor()
        self.host_widgets = {}  # {ip: {widgets}}
        self.update_interval = 1000  # Update UI every 1 second
        self.updating = False
        
        # Setup UI
        self.setup_ui()
        
        # Bring window to front and focus
        self.attributes('-topmost', True)  # Make window stay on top temporarily
        self.after(100, lambda: self.attributes('-topmost', False))  # Remove topmost after 100ms
        self.lift()
        self.focus_force()
        self.grab_set()  # Make window modal temporarily
        self.after(200, self.grab_release)  # Release after 200ms
    
    def setup_ui(self):
        """Setup the monitor window UI"""
        # Header with controls and legend
        header = ctk.CTkFrame(self, fg_color=COLORS['bg_card'])
        header.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])
        
        # Control buttons row
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="left", fill="x", expand=True)
        
        self.stop_btn = StyledButton(
            btn_frame,
            text="⏹ Stop",
            command=self.stop_monitoring,
            size="small",
            variant="danger",
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=(0, SPACING['sm']))
        
        self.pause_btn = StyledButton(
            btn_frame,
            text="⏸ Pause",
            command=self.pause_monitoring,
            size="small",
            variant="neutral",
            state="disabled"
        )
        self.pause_btn.pack(side="left", padx=(0, SPACING['sm']))
        
        self.resume_btn = StyledButton(
            btn_frame,
            text="▶ Resume",
            command=self.resume_monitoring,
            size="small",
            variant="success",
            state="disabled"
        )
        self.resume_btn.pack(side="left", padx=(0, SPACING['sm']))
        
        self.export_btn = StyledButton(
            btn_frame,
            text="📤 Export",
            command=self.export_data,
            size="small",
            variant="neutral",
            state="disabled"
        )
        self.export_btn.pack(side="left")
        
        # Latency legend on the right
        legend_frame = ctk.CTkFrame(header, fg_color="transparent")
        legend_frame.pack(side="right", padx=SPACING['sm'])
        
        # Green indicator
        green_box = ctk.CTkFrame(legend_frame, fg_color="#00ff00", width=60, height=25, corner_radius=4)
        green_box.pack(side="top", pady=2)
        green_label = ctk.CTkLabel(green_box, text="0-200 ms", font=ctk.CTkFont(size=9), text_color="black")
        green_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Yellow indicator
        yellow_box = ctk.CTkFrame(legend_frame, fg_color="#ffff00", width=60, height=25, corner_radius=4)
        yellow_box.pack(side="top", pady=2)
        yellow_label = ctk.CTkLabel(yellow_box, text="201-500 ms", font=ctk.CTkFont(size=9), text_color="black")
        yellow_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Red indicator
        red_box = ctk.CTkFrame(legend_frame, fg_color="#ff0000", width=60, height=25, corner_radius=4)
        red_box.pack(side="top", pady=2)
        red_label = ctk.CTkLabel(red_box, text="501+ ms", font=ctk.CTkFont(size=9), text_color="white")
        red_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Input section
        input_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_card'])
        input_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        
        self.hosts_entry = StyledEntry(
            input_frame,
            placeholder_text="IPs, CIDRs, Ranges: e.g., 192.168.1.0/24, 10.0.0.1-10.0.0.50, 8.8.8.8"
        )
        self.hosts_entry.pack(side="left", fill="x", expand=True, padx=SPACING['sm'], pady=SPACING['sm'])
        
        self.start_btn = StyledButton(
            input_frame,
            text="▶ Start",
            command=self.start_monitoring,
            size="small",
            variant="success"
        )
        self.start_btn.pack(side="right", padx=SPACING['sm'], pady=SPACING['sm'])
        
        # Table header (reduced height)
        table_header = ctk.CTkFrame(self, fg_color=("gray85", "gray25"), height=28)
        table_header.pack(fill="x", padx=SPACING['md'], pady=(0, 2))
        table_header.pack_propagate(False)
        
        # Column headers
        header_bar = ctk.CTkLabel(table_header, text="", width=8, fg_color="transparent")
        header_bar.pack(side="left", padx=(3, 0))
        
        header_ip = ctk.CTkLabel(table_header, text="IP Address", font=ctk.CTkFont(size=10, weight="bold"), width=140, anchor="w")
        header_ip.pack(side="left", padx=4)
        
        header_hostname = ctk.CTkLabel(table_header, text="Hostname", font=ctk.CTkFont(size=10, weight="bold"), width=180, anchor="w")
        header_hostname.pack(side="left", padx=4)
        
        header_avg = ctk.CTkLabel(table_header, text="Avg", font=ctk.CTkFont(size=10, weight="bold"), width=50, anchor="center")
        header_avg.pack(side="left", padx=4)
        
        header_min = ctk.CTkLabel(table_header, text="Min", font=ctk.CTkFont(size=10, weight="bold"), width=50, anchor="center")
        header_min.pack(side="left", padx=4)
        
        header_cur = ctk.CTkLabel(table_header, text="Current", font=ctk.CTkFont(size=10, weight="bold"), width=60, anchor="center")
        header_cur.pack(side="left", padx=4)
        
        header_graph = ctk.CTkLabel(table_header, text="Graph", font=ctk.CTkFont(size=10, weight="bold"), anchor="center")
        header_graph.pack(side="left", fill="x", expand=True, padx=4)
        
        # Scrollable content area for host rows
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=SPACING['md'], pady=(0, SPACING['md']))
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def parse_host_input(self, input_text):
        """Parse various input formats: IPs, CIDRs, ranges, hostnames"""
        hosts = []
        
        # Split by comma or space
        parts = re.split(r'[,\s]+', input_text)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            try:
                # Check if it's a CIDR notation (e.g., 192.168.1.0/24)
                if '/' in part:
                    try:
                        network = ipaddress.ip_network(part, strict=False)
                        # Limit to reasonable size to avoid memory issues
                        if network.num_addresses > 1000:
                            messagebox.showwarning(
                                "Too Many Hosts",
                                f"CIDR {part} contains {network.num_addresses} hosts.\n"
                                f"Maximum 1000 hosts allowed per input.\n"
                                f"Please use a smaller subnet."
                            )
                            continue
                        # Add all hosts in the network
                        for ip in network.hosts():
                            hosts.append(str(ip))
                        continue
                    except ValueError:
                        pass
                
                # Check if it's a range (e.g., 192.168.1.1-192.168.1.50)
                if '-' in part:
                    try:
                        start_ip, end_ip = part.split('-', 1)
                        start_ip = start_ip.strip()
                        end_ip = end_ip.strip()
                        
                        # Handle partial end IP (e.g., 192.168.1.1-50)
                        if '.' not in end_ip:
                            # Extract prefix from start IP
                            start_parts = start_ip.split('.')
                            if len(start_parts) == 4:
                                end_ip = '.'.join(start_parts[:3]) + '.' + end_ip
                        
                        # Convert to IP objects
                        start = ipaddress.ip_address(start_ip)
                        end = ipaddress.ip_address(end_ip)
                        
                        # Calculate range size
                        range_size = int(end) - int(start) + 1
                        
                        if range_size > 1000:
                            messagebox.showwarning(
                                "Too Many Hosts",
                                f"Range {part} contains {range_size} hosts.\n"
                                f"Maximum 1000 hosts allowed per input.\n"
                                f"Please use a smaller range."
                            )
                            continue
                        
                        if range_size < 1:
                            messagebox.showwarning(
                                "Invalid Range",
                                f"Invalid range {part}: start IP must be less than or equal to end IP"
                            )
                            continue
                        
                        # Add all IPs in range
                        current = start
                        while current <= end:
                            hosts.append(str(current))
                            current += 1
                        continue
                    except (ValueError, IndexError):
                        pass
                
                # Check if it's a single IP address
                try:
                    ip = ipaddress.ip_address(part)
                    hosts.append(str(ip))
                    continue
                except ValueError:
                    pass
                
                # Assume it's a hostname
                hosts.append(part)
                
            except Exception as e:
                messagebox.showerror("Parse Error", f"Error parsing '{part}':\n{str(e)}")
                continue
        
        return hosts
    
    def start_monitoring(self):
        """Start monitoring the hosts"""
        hosts_input = self.hosts_entry.get().strip()
        
        if not hosts_input:
            messagebox.showwarning("No Hosts", "Please enter at least one IP, CIDR, or range")
            return
        
        # Parse hosts with support for CIDR, ranges, and individual IPs
        hosts = self.parse_host_input(hosts_input)
        
        if not hosts:
            messagebox.showwarning("No Hosts", "No valid hosts found in input")
            return
        
        # Warn if too many hosts
        if len(hosts) > 100:
            result = messagebox.askyesno(
                "Many Hosts",
                f"You are about to monitor {len(hosts)} hosts.\n"
                f"This may impact performance.\n\n"
                f"Continue anyway?"
            )
            if not result:
                return
        
        # Add hosts to monitor
        added_count = 0
        for host in hosts:
            ip = self.monitor.add_host(host)
            if ip:
                self.create_host_widget(ip)
                added_count += 1
        
        if added_count == 0:
            messagebox.showwarning("No Hosts", "Could not add any hosts to monitor")
            return
        
        # Start monitoring
        self.monitor.start_monitoring()
        
        # Update button states
        self.start_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal")
        self.stop_btn.configure(state="normal")
        self.export_btn.configure(state="normal")
        self.hosts_entry.configure(state="disabled")
        
        # Start UI updates
        self.updating = True
        self.update_ui()
    
    def pause_monitoring(self):
        """Pause monitoring"""
        self.monitor.pause_monitoring()
        self.pause_btn.configure(state="disabled")
        self.resume_btn.configure(state="normal")
    
    def resume_monitoring(self):
        """Resume monitoring"""
        self.monitor.resume_monitoring()
        self.pause_btn.configure(state="normal")
        self.resume_btn.configure(state="disabled")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.updating = False
        self.monitor.stop_monitoring()
        
        # Update button states
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled")
        self.resume_btn.configure(state="disabled")
        self.stop_btn.configure(state="disabled")
        self.hosts_entry.configure(state="normal")
    
    def create_host_widget(self, ip):
        """Create table row widget for a host"""
        host_data = self.monitor.hosts[ip]
        
        # Row container (reduced height for more compact display)
        row = ctk.CTkFrame(self.scroll_frame, fg_color=("gray92", "gray20"), height=38)
        row.pack(fill="x", pady=1)
        row.pack_propagate(False)
        
        # Status bar (colored vertical bar on left)
        status_bar = ctk.CTkFrame(row, fg_color="#808080", width=8)
        status_bar.pack(side="left", fill="y", padx=(3, 0))
        
        # IP Address
        ip_label = ctk.CTkLabel(
            row,
            text=ip,
            font=ctk.CTkFont(size=10),
            width=140,
            anchor="w"
        )
        ip_label.pack(side="left", padx=4)
        
        # Hostname
        hostname_text = host_data.hostname if host_data.hostname else "---"
        hostname_label = ctk.CTkLabel(
            row,
            text=hostname_text,
            font=ctk.CTkFont(size=10),
            width=180,
            anchor="w",
            text_color=COLORS['text_secondary']
        )
        hostname_label.pack(side="left", padx=4)
        
        # Avg latency
        avg_label = ctk.CTkLabel(
            row,
            text="0",
            font=ctk.CTkFont(size=10),
            width=50,
            anchor="center"
        )
        avg_label.pack(side="left", padx=4)
        
        # Min latency
        min_label = ctk.CTkLabel(
            row,
            text="0",
            font=ctk.CTkFont(size=10),
            width=50,
            anchor="center"
        )
        min_label.pack(side="left", padx=4)
        
        # Current latency
        cur_label = ctk.CTkLabel(
            row,
            text="0",
            font=ctk.CTkFont(size=10),
            width=60,
            anchor="center"
        )
        cur_label.pack(side="left", padx=4)
        
        # Graph frame
        graph_frame = ctk.CTkFrame(row, fg_color="transparent")
        graph_frame.pack(side="left", fill="both", expand=True, padx=4)
        
        # Create inline graph using Tkinter Canvas (no matplotlib needed!)
        import tkinter as tk
        canvas = tk.Canvas(
            graph_frame,
            width=260,
            height=28,
            bg='white',
            highlightthickness=0
        )
        canvas.pack(fill="both", expand=True)
        
        # Store references
        self.host_widgets[ip] = {
            'row': row,
            'status_bar': status_bar,
            'ip_label': ip_label,
            'hostname_label': hostname_label,
            'avg_label': avg_label,
            'min_label': min_label,
            'cur_label': cur_label,
            'canvas': canvas,
            'min_value': float('inf'),
            'max_y': 500  # Track max y for scaling
        }
    
    def update_ui(self):
        """Update all host widgets with latest data"""
        if not self.updating:
            return
        
        try:
            all_hosts = self.monitor.get_all_hosts_data()
            
            for ip, host_data in all_hosts.items():
                if ip not in self.host_widgets:
                    continue
                
                widgets = self.host_widgets[ip]
                recent_pings = host_data.get_recent_pings()
                
                # Get current latency (last ping)
                current_latency = 0
                if recent_pings:
                    success, rtt = recent_pings[-1]
                    current_latency = rtt if success else 0
                
                # Calculate stats
                avg_latency = host_data.get_average_latency()
                
                # Track minimum
                if current_latency > 0 and current_latency < widgets['min_value']:
                    widgets['min_value'] = current_latency
                min_latency = widgets['min_value'] if widgets['min_value'] != float('inf') else 0
                
                # Determine status bar color based on current latency
                if current_latency == 0:
                    bar_color = "#ff0000"  # Red - offline
                elif current_latency <= 200:
                    bar_color = "#00ff00"  # Green - good
                elif current_latency <= 500:
                    bar_color = "#ffff00"  # Yellow - moderate
                else:
                    bar_color = "#ff0000"  # Red - high latency
                
                # Update status bar
                widgets['status_bar'].configure(fg_color=bar_color)
                
                # Update statistics labels
                widgets['avg_label'].configure(text=f"{int(avg_latency)}")
                widgets['min_label'].configure(text=f"{int(min_latency)}")
                widgets['cur_label'].configure(text=f"{int(current_latency)}")
                
                # Update graph using Canvas
                canvas = widgets['canvas']
                canvas.delete("all")  # Clear previous drawing
                
                if not recent_pings:
                    continue
                
                # Canvas dimensions
                width = 260
                height = 28
                padding = 2
                
                # Prepare data
                y_data = []
                for success, rtt in recent_pings:
                    if success:
                        y_data.append(rtt)
                    else:
                        y_data.append(None)
                
                # Auto-scale y-axis
                valid_y = [y for y in y_data if y is not None]
                if not valid_y:
                    continue
                
                max_y = max(valid_y)
                widgets['max_y'] = max(500, max_y * 1.1)
                
                # Draw graph
                points = []
                x_step = (width - 2 * padding) / max(len(y_data) - 1, 1)
                
                for i, y in enumerate(y_data):
                    if y is not None:
                        x = padding + i * x_step
                        # Invert y (canvas y=0 is top)
                        y_scaled = height - padding - (y / widgets['max_y']) * (height - 2 * padding)
                        points.append((x, y_scaled))
                
                # Draw line connecting points
                if len(points) > 1:
                    for i in range(len(points) - 1):
                        x1, y1 = points[i]
                        x2, y2 = points[i + 1]
                        canvas.create_line(x1, y1, x2, y2, fill='#0066cc', width=1.5, smooth=True)
                
                # Draw points
                for x, y in points:
                    canvas.create_oval(x-2, y-2, x+2, y+2, fill='#0066cc', outline='#0066cc')
            
            # Schedule next update
            self.after(self.update_interval, self.update_ui)
            
        except Exception as e:
            print(f"Error updating UI: {e}")
            if self.updating:
                self.after(self.update_interval, self.update_ui)
    
    def export_data(self):
        """Export monitoring data to file"""
        if not self.monitor.hosts:
            messagebox.showinfo("No Data", "No monitoring data to export")
            return
        
        # Get export data
        export_text = self.monitor.export_data()
        
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"ping_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(export_text)
                messagebox.showinfo("Export Successful", f"Data exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data:\n{str(e)}")
    
    def on_closing(self):
        """Handle window close"""
        self.updating = False
        self.monitor.stop_monitoring()
        self.destroy()


if __name__ == "__main__":
    app = NetToolsApp()
    app.mainloop()
