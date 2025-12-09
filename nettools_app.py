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
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Design system and UI components
from design_constants import COLORS, SPACING, RADIUS, FONTS, BUTTON_SIZES
from ui_components import (
    StyledCard, StyledButton, StyledEntry, SectionTitle, SubTitle,
    ResultRow, StatusBadge, SectionSeparator, LoadingSpinner, InfoBox, DataGrid
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
        self.current_page = 1
        self.results_per_page = 100
        self.total_pages = 1
        
        # Window persistence - MUST be set before loading favorites
        self.config_file = Path.home() / '.nettools_config.json'
        
        # Favorites only (recent removed as not useful)
        self.favorite_tools = self.load_favorites()
        
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
        
        # Load window state
        self.load_window_state()
        
        # Create UI (order matters: status bar must be packed before main content)
        self.create_sidebar()
        self.create_status_bar()
        self.create_main_content()
        
        # Bind keyboard shortcuts
        self.bind('<Return>', self.on_enter_key)
        self.bind('<Control-e>', self.export_csv)
        self.bind('<Control-k>', self.open_quick_switcher)  # Quick switcher
        
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
    
    def on_closing(self):
        """Handle window closing"""
        self.save_window_state()
        self.destroy()
    
    def open_quick_switcher(self, event=None):
        """Open quick tool switcher dialog (Ctrl+K)"""
        # Create dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Quick Tool Switcher")
        dialog.geometry("600x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 600) // 2
        y = self.winfo_y() + (self.winfo_height() - 400) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Content
        content = ctk.CTkFrame(dialog)
        content.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Search entry
        search_frame = ctk.CTkFrame(content, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, SPACING['md']))
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="🔍 Search Tools:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        search_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        search_entry = StyledEntry(
            search_frame,
            placeholder_text="Type to search..."
        )
        search_entry.pack(fill="x")
        search_entry.focus()
        
        # Results scrollable frame
        results_frame = ctk.CTkScrollableFrame(content)
        results_frame.pack(fill="both", expand=True, pady=SPACING['md'])
        
        # All tools list
        all_tools = [
            ("scann", "scanning", "IPv4 Scanner", "📡 Scan network for devices"),
            ("port", "scanning", "Port Scanner", "🔌 Scan ports on devices"),
            ("trace", "scanning", "Traceroute", "🛣️ Trace network paths"),
            ("ping", "scanning", "Live Ping Monitor", "📊 Monitor ping in real-time"),
            ("bandwidth", "scanning", "Bandwidth Test", "⚡ Test network speed"),
            ("dns", "utilities", "DNS Lookup", "🌐 Lookup DNS records"),
            ("subnet", "utilities", "Subnet Calculator", "🧮 Calculate subnets"),
            ("mac", "utilities", "MAC Formatter", "💻 Format MAC addresses"),
            ("compare", "management", "Scan Comparison", "📊 Compare scan results"),
            ("profiles", "management", "Network Profiles", "📁 Manage network profiles"),
            ("panos", "automation", "PAN-OS Generator", "🔥 Generate firewall configs"),
            ("phpipam", "automation", "phpIPAM Integration", "📦 Integrate with phpIPAM"),
        ]
        
        tool_buttons = []
        
        def filter_tools(event=None):
            """Filter tools based on search"""
            search_text = search_entry.get().lower()
            
            # Clear results
            for widget in results_frame.winfo_children():
                widget.destroy()
            
            # Show matching tools
            for tool_id, category, name, description in all_tools:
                if (search_text in name.lower() or 
                    search_text in description.lower() or
                    search_text in tool_id):
                    
                    tool_btn = StyledButton(
                        results_frame,
                        text=f"{name}\n{description}",
                        command=lambda tid=tool_id: switch_and_close(tid),
                        size="large",
                        variant="neutral"
                    )
                    tool_btn.pack(fill="x", pady=SPACING['xs'])
                    tool_buttons.append((tool_btn, tool_id))
        
        def switch_and_close(tool_id):
            """Switch to tool and close dialog"""
            self.switch_tool(tool_id)
            dialog.destroy()
        
        def on_key(event):
            """Handle keyboard navigation"""
            if event.keysym == 'Escape':
                dialog.destroy()
            elif event.keysym == 'Down':
                # Focus next button
                pass
            elif event.keysym == 'Up':
                # Focus previous button
                pass
        
        # Bind events
        search_entry.bind('<KeyRelease>', filter_tools)
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        dialog.bind('<Key>', on_key)
        
        # Initial filter (show all)
        filter_tools()
        
        return "break"  # Prevent default handling
    
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
        
        # Scrollable navigation container
        nav_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        nav_scroll.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Quick Access - Live Monitor (prominent button)
        self.live_monitor_btn = StyledButton(
            nav_scroll,
            text="📊 Live Ping Monitor",
            command=self.open_live_ping_monitor,
            size="large",
            variant="success"
        )
        self.live_monitor_btn.pack(fill="x", padx=10, pady=(5, 15))
        
        # Favorites section - create but don't pack yet (will pack when populated)
        self.favorites_frame = ctk.CTkFrame(nav_scroll, fg_color="transparent")
        self.favorites_label = ctk.CTkLabel(
            self.favorites_frame,
            text="⭐ FAVORITES",
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w"
        )
        self.favorites_buttons_frame = ctk.CTkFrame(self.favorites_frame, fg_color="transparent")
        
        # Navigation organized by categories
        self.nav_buttons = {}
        
        # Category structure: (category_name, [(page_id, label, tooltip), ...])
        nav_categories = [
            ("🔍 NETWORK SCANNING", [
                ("scanner", "   IPv4 Scanner", "Scan network for active hosts"),
                ("portscan", "   Port Scanner", "Scan for open ports on hosts"),
                ("traceroute", "   Traceroute", "Trace network path to host"),
                ("bandwidth", "   Bandwidth Test", "Test network speed with iperf3"),
            ]),
            ("🛠 NETWORK TOOLS", [
                ("dns", "   DNS Lookup", "Resolve hostnames and IP addresses"),
                ("subnet", "   Subnet Calculator", "Calculate subnet information"),
                ("mac", "   MAC Formatter", "Format and analyze MAC addresses"),
            ]),
            ("📊 MANAGEMENT", [
                ("compare", "   Scan Comparison", "Compare network scan results"),
                ("profiles", "   Network Profiles", "Manage network profiles"),
            ]),
            ("🛡 ADVANCED", [
                ("panos", "   PAN-OS Generator", "Generate PAN-OS CLI commands"),
                ("phpipam", "   phpIPAM", "Manage IP addresses with phpIPAM"),
            ]),
        ]
        
        self.current_page = "scanner"
        
        # Store first category for positioning
        self.first_category_label = None
        
        # Render navigation with categories
        for idx, (category_name, items) in enumerate(nav_categories):
            # Category header
            category_label = ctk.CTkLabel(
                nav_scroll,
                text=category_name,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("gray40", "gray60"),
                anchor="w"
            )
            category_label.pack(fill="x", padx=15, pady=(15, 5))
            
            # Store reference to first category
            if idx == 0:
                self.first_category_label = category_label
            
            # Category items
            for page_id, label, tooltip in items:
                btn = ctk.CTkButton(
                    nav_scroll,
                    text=label,
                    command=lambda p=page_id: self.switch_tool(p),
                    height=40,
                    corner_radius=6,
                    anchor="w",
                    font=ctk.CTkFont(size=13, family="Segoe UI"),
                    fg_color="transparent",
                    text_color=("gray10", "gray90"),
                    hover_color=("gray70", "gray30")
                )
                btn.pack(fill="x", padx=12, pady=2)
                
                # Add right-click context menu for favorites
                btn.bind("<Button-3>", lambda e, tid=page_id: self.show_tool_context_menu(e, tid))
                
                self.nav_buttons[page_id] = btn
        
        # Update initial button state
        self.nav_buttons["scanner"].configure(fg_color=("gray75", "gray25"))
        
        # Add some bottom padding to scroll area
        bottom_padding = ctk.CTkFrame(nav_scroll, fg_color="transparent", height=20)
        bottom_padding.pack(fill="x")
        
        # Theme selector at bottom (fixed position outside scroll)
        theme_frame = ctk.CTkFrame(self.sidebar, corner_radius=0, fg_color="transparent")
        theme_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
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
        
        # Initialize favorites UI
        self.update_favorites_ui()
        self.update_nav_button_stars()
    
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
            elif page_id == "panos":
                self.create_panos_content(self.pages[page_id])
            elif page_id == "subnet":
                self.create_subnet_content(self.pages[page_id])
            elif page_id == "phpipam":
                self.create_phpipam_content(self.pages[page_id])
            elif page_id == "bandwidth":
                self.create_bandwidth_content(self.pages[page_id])
            
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
        elif page_id == "panos":
            self.status_label.configure(text="Generate PAN-OS address object CLI commands")
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
            text="IPv4 / CIDR / Hostname:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        cidr_label.grid(row=0, column=0, padx=SPACING['md'], pady=SPACING['md'], sticky="w")
        
        self.cidr_entry = StyledEntry(
            input_card,
            placeholder_text="e.g., 192.168.1.0/24 or server.example.com"
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
            values=["Gentle (longer timeout)", "Medium", "Aggressive (short timeout)"],
            width=250
        )
        self.aggro_selector.set("Medium")
        self.aggro_selector.grid(row=1, column=1, padx=SPACING['md'], pady=SPACING['md'], sticky="ew")
        
        # Scan buttons (moved to separate row for better layout)
        button_frame = ctk.CTkFrame(input_card, fg_color="transparent")
        button_frame.grid(row=2, column=0, columnspan=4, padx=SPACING['md'], pady=SPACING['md'], sticky="ew")
        
        self.start_scan_btn = StyledButton(
            button_frame,
            text="▶ Start Scan",
            command=self.start_scan,
            size="medium",
            variant="primary"
        )
        self.start_scan_btn.pack(side="left", padx=SPACING['xs'])
        
        self.import_list_btn = StyledButton(
            button_frame,
            text="📋 Import IP List",
            command=self.import_ip_list,
            size="medium",
            variant="neutral"
        )
        self.import_list_btn.pack(side="left", padx=SPACING['xs'])
        
        self.live_monitor_btn = StyledButton(
            button_frame,
            text="📊 Live Monitor",
            command=self.open_live_ping_monitor,
            size="medium",
            variant="success"
        )
        self.live_monitor_btn.pack(side="left", padx=SPACING['xs'])
        
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
        
        headers = [("●", 50), ("IP Address", 180), ("Hostname/FQDN", 250), ("Status", 150), ("RTT (ms)", 100)]
        for text, width in headers:
            label = ctk.CTkLabel(
                header_frame,
                text=text,
                font=ctk.CTkFont(size=FONTS['body'], weight="bold"),
                text_color="white",
                width=width
            )
            label.pack(side="left", padx=SPACING['sm'], pady=SPACING['sm'])
        
        # Pagination controls
        pagination_frame = ctk.CTkFrame(results_card, fg_color="transparent")
        pagination_frame.pack(fill="x", padx=SPACING['lg'], pady=SPACING['xs'])
        
        self.pagination_label = ctk.CTkLabel(
            pagination_frame,
            text="No results",
            font=ctk.CTkFont(size=FONTS['small']),
            text_color=COLORS['text_secondary']
        )
        self.pagination_label.pack(side="left")
        
        # Pagination buttons
        pagination_buttons = ctk.CTkFrame(pagination_frame, fg_color="transparent")
        pagination_buttons.pack(side="right")
        
        self.first_page_btn = StyledButton(
            pagination_buttons,
            text="⏮ First",
            command=lambda: self.go_to_page(1),
            size="small",
            variant="neutral"
        )
        self.first_page_btn.pack(side="left", padx=SPACING['xs'])
        
        self.prev_page_btn = StyledButton(
            pagination_buttons,
            text="◀ Prev",
            command=self.previous_page,
            size="small",
            variant="neutral"
        )
        self.prev_page_btn.pack(side="left", padx=SPACING['xs'])
        
        self.page_indicator = ctk.CTkLabel(
            pagination_buttons,
            text="Page 1 of 1",
            font=ctk.CTkFont(size=FONTS['small']),
            text_color=COLORS['text_secondary']
        )
        self.page_indicator.pack(side="left", padx=SPACING['md'])
        
        self.next_page_btn = StyledButton(
            pagination_buttons,
            text="Next ▶",
            command=self.next_page,
            size="small",
            variant="neutral"
        )
        self.next_page_btn.pack(side="left", padx=SPACING['xs'])
        
        self.last_page_btn = StyledButton(
            pagination_buttons,
            text="Last ⏭",
            command=lambda: self.go_to_page(self.total_pages),
            size="small",
            variant="neutral"
        )
        self.last_page_btn.pack(side="left", padx=SPACING['xs'])
        
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
        # Scrollable content area
        scrollable = ctk.CTkScrollableFrame(parent)
        scrollable.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Title
        title_label = ctk.CTkLabel(
            scrollable,
            text="Port Scanner",
            font=ctk.CTkFont(size=FONTS['title'], weight="bold")
        )
        title_label.pack(pady=(0, SPACING['xs']))
        
        # Subtitle
        subtitle_label = SubTitle(
            scrollable,
            text="Scan for open ports on target hosts using multiple methods"
        )
        subtitle_label.pack(pady=(0, SPACING['lg']))
        
        # Input section with styled card
        input_frame = StyledCard(scrollable)
        input_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        # Target host
        target_label = ctk.CTkLabel(
            input_frame,
            text="Target Host:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        target_label.pack(pady=(SPACING['lg'], SPACING['xs']), padx=SPACING['lg'], anchor="w")
        
        target_info = SubTitle(
            input_frame,
            text="Enter IP address or hostname (e.g., 192.168.1.1 or example.com)"
        )
        target_info.pack(pady=(0, SPACING['xs']), padx=SPACING['lg'], anchor="w")
        
        self.port_target_entry = StyledEntry(
            input_frame,
            placeholder_text="192.168.1.1 or example.com"
        )
        self.port_target_entry.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Port selection
        port_label = ctk.CTkLabel(
            input_frame,
            text="Port Selection:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        port_label.pack(pady=(0, SPACING['xs']), padx=SPACING['lg'], anchor="w")
        
        # Port mode selection
        self.port_mode_var = ctk.StringVar(value="common")
        
        port_mode_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        port_mode_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        common_radio = ctk.CTkRadioButton(
            port_mode_frame,
            text="Common Ports (21,22,23,25,80,443,3389,...)",
            variable=self.port_mode_var,
            value="common",
            command=self.update_port_mode,
            font=ctk.CTkFont(size=FONTS['small'])
        )
        common_radio.pack(anchor="w", pady=2)
        
        range_radio = ctk.CTkRadioButton(
            port_mode_frame,
            text="Port Range (e.g., 1-1000)",
            variable=self.port_mode_var,
            value="range",
            command=self.update_port_mode,
            font=ctk.CTkFont(size=FONTS['small'])
        )
        range_radio.pack(anchor="w", pady=2)
        
        custom_radio = ctk.CTkRadioButton(
            port_mode_frame,
            text="Custom Ports (comma-separated, e.g., 80,443,8080)",
            variable=self.port_mode_var,
            value="custom",
            command=self.update_port_mode,
            font=ctk.CTkFont(size=FONTS['small'])
        )
        custom_radio.pack(anchor="w", pady=2)
        
        # Port input (changes based on mode)
        self.port_input_entry = StyledEntry(
            input_frame,
            placeholder_text="Will scan common ports",
            state="disabled"
        )
        self.port_input_entry.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Scan method
        method_label = ctk.CTkLabel(
            input_frame,
            text="Scan Method:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        method_label.pack(pady=(0, SPACING['xs']), padx=SPACING['lg'], anchor="w")
        
        self.scan_method_var = ctk.StringVar(value="socket")
        
        method_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        method_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        socket_radio = ctk.CTkRadioButton(
            method_frame,
            text="Socket Scan (Fast, recommended)",
            variable=self.scan_method_var,
            value="socket",
            font=ctk.CTkFont(size=FONTS['small'])
        )
        socket_radio.pack(anchor="w", pady=2)
        
        if TELNETLIB_AVAILABLE:
            telnet_radio = ctk.CTkRadioButton(
                method_frame,
                text="Telnet Test (Connection-based)",
                variable=self.scan_method_var,
                value="telnet",
                font=ctk.CTkFont(size=FONTS['small'])
            )
            telnet_radio.pack(anchor="w", pady=2)
        
        if platform.system() == "Windows":
            powershell_radio = ctk.CTkRadioButton(
                method_frame,
                text="PowerShell Test-NetConnection (Most reliable on Windows)",
                variable=self.scan_method_var,
                value="powershell",
                font=ctk.CTkFont(size=FONTS['small'])
            )
            powershell_radio.pack(anchor="w", pady=2)
        
        # Scan buttons
        button_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        self.port_scan_btn = StyledButton(
            button_frame,
            text="▶ Start Port Scan",
            command=self.start_port_scan,
            size="large",
            variant="primary"
        )
        self.port_scan_btn.pack(side="left", padx=(0, SPACING['md']))
        
        self.port_cancel_btn = StyledButton(
            button_frame,
            text="⏹ Cancel",
            command=self.cancel_port_scan,
            size="medium",
            variant="danger",
            state="disabled"
        )
        self.port_cancel_btn.pack(side="left")
        
        self.port_export_btn = StyledButton(
            button_frame,
            text="📤 Export Results",
            command=self.export_port_scan,
            size="large",
            variant="success",
            state="disabled"
        )
        self.port_export_btn.pack(side="left", padx=(SPACING['md'], 0))
        
        # Progress
        self.port_progress_label = SubTitle(
            scrollable,
            text=""
        )
        self.port_progress_label.pack(pady=(0, SPACING['xs']))
        
        self.port_progress_bar = ctk.CTkProgressBar(scrollable, width=400, height=20)
        self.port_progress_bar.pack(pady=(0, SPACING['lg']))
        self.port_progress_bar.set(0)
        
        # Results section
        results_title = SectionTitle(
            scrollable,
            text="Scan Results"
        )
        results_title.pack(pady=(SPACING['md'], SPACING['md']), anchor="w")
        
        # Results frame with styled card
        self.port_results_frame = StyledCard(scrollable)
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
            # Use PortScanner.get_common_ports()
            return PortScanner.get_common_ports()
        elif mode == "range":
            port_range = self.port_input_entry.get().strip()
            return PortScanner.parse_port_range(port_range)
        elif mode == "custom":
            ports_str = self.port_input_entry.get().strip()
            return PortScanner.parse_port_list(ports_str)
        
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
        """Scan port using socket - delegates to PortScanner"""
        return PortScanner.scan_port_socket(target, port, timeout=1)
    
    def scan_port_telnet(self, target, port):
        """Scan port using telnet - delegates to PortScanner"""
        return PortScanner.scan_port_telnet(target, port, timeout=2)
    
    def scan_port_powershell(self, target, port):
        """Scan port using PowerShell - delegates to PortScanner"""
        return PortScanner.scan_port_powershell(target, port, timeout=5)
    
    def get_service_name(self, port):
        """Get common service name for port - delegates to PortScanner"""
        return PortScanner.get_service_name(port)
    
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
        
        # Input section with styled card
        input_frame = StyledCard(scrollable)
        input_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        # Query input
        query_label = ctk.CTkLabel(
            input_frame,
            text="Enter Hostname or IP Address:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        query_label.pack(pady=(SPACING['lg'], SPACING['xs']), padx=SPACING['lg'], anchor="w")
        
        query_info = SubTitle(
            input_frame,
            text="Examples: google.com, 8.8.8.8, github.com, 192.168.1.1"
        )
        query_info.pack(pady=(0, SPACING['xs']), padx=SPACING['lg'], anchor="w")
        
        self.dns_query_entry = StyledEntry(
            input_frame,
            placeholder_text="google.com or 8.8.8.8"
        )
        self.dns_query_entry.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        self.dns_query_entry.bind('<Return>', lambda e: self.perform_dns_lookup())
        
        # DNS server selection
        dns_server_label = ctk.CTkLabel(
            input_frame,
            text="DNS Server (Optional):",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        dns_server_label.pack(pady=(0, SPACING['xs']), padx=SPACING['lg'], anchor="w")
        
        dns_server_info = SubTitle(
            input_frame,
            text="Leave empty to use system default, or specify custom DNS server"
        )
        dns_server_info.pack(pady=(0, SPACING['xs']), padx=SPACING['lg'], anchor="w")
        
        dns_server_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        dns_server_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        self.dns_server_var = ctk.StringVar(value="system")
        
        system_dns = ctk.CTkRadioButton(
            dns_server_frame,
            text="System Default",
            variable=self.dns_server_var,
            value="system",
            font=ctk.CTkFont(size=FONTS['small'])
        )
        system_dns.pack(anchor="w", pady=2)
        
        google_dns = ctk.CTkRadioButton(
            dns_server_frame,
            text="Google DNS (8.8.8.8)",
            variable=self.dns_server_var,
            value="8.8.8.8",
            font=ctk.CTkFont(size=FONTS['small'])
        )
        google_dns.pack(anchor="w", pady=2)
        
        cloudflare_dns = ctk.CTkRadioButton(
            dns_server_frame,
            text="Cloudflare DNS (1.1.1.1)",
            variable=self.dns_server_var,
            value="1.1.1.1",
            font=ctk.CTkFont(size=FONTS['small'])
        )
        cloudflare_dns.pack(anchor="w", pady=2)
        
        # Lookup button
        lookup_btn = StyledButton(
            scrollable,
            text="🔍 Lookup",
            command=self.perform_dns_lookup,
            size="large",
            variant="success"
        )
        lookup_btn.pack(pady=(0, SPACING['lg']))
        
        # Results section
        results_title = SectionTitle(
            scrollable,
            text="Results"
        )
        results_title.pack(pady=(SPACING['md'], SPACING['md']), anchor="w")
        
        # Results frame with styled card
        self.dns_results_frame = StyledCard(scrollable)
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
        # Use DNSLookup from tools module
        results = DNSLookup.lookup(query, dns_server)
        
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
        
        # Input section with styled card
        input_frame = StyledCard(scrollable)
        input_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        # CIDR input
        cidr_label = ctk.CTkLabel(
            input_frame,
            text="Enter Network in CIDR Notation:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        cidr_label.pack(pady=(SPACING['lg'], SPACING['xs']), padx=SPACING['lg'], anchor="w")
        
        cidr_info = SubTitle(
            input_frame,
            text="Examples: 192.168.1.0/24, 10.0.0.0/8, 172.16.0.0/16"
        )
        cidr_info.pack(pady=(0, SPACING['xs']), padx=SPACING['lg'], anchor="w")
        
        self.subnet_cidr_entry = StyledEntry(
            input_frame,
            placeholder_text="192.168.1.0/24"
        )
        self.subnet_cidr_entry.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        self.subnet_cidr_entry.bind('<Return>', lambda e: self.calculate_subnet())
        
        # Calculate button
        calc_btn = StyledButton(
            scrollable,
            text="🔢 Calculate",
            command=self.calculate_subnet,
            size="large",
            variant="warning"
        )
        calc_btn.pack(pady=(0, SPACING['lg']))
        
        # Results section
        results_title = SectionTitle(
            scrollable,
            text="Subnet Information"
        )
        results_title.pack(pady=(SPACING['md'], SPACING['md']), anchor="w")
        
        # Results frame with styled card
        self.subnet_results_frame = StyledCard(scrollable)
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
        
        # Use SubnetCalculator from tools module
        result = SubnetCalculator.calculate(cidr)
        
        if result is None:
            messagebox.showerror("Error", "Please enter a CIDR notation")
            return
        
        if "error" in result:
            messagebox.showerror("Error", f"Invalid CIDR notation: {result['error']}")
            return
        
        # Display results using existing display method
        self.display_subnet_results(result)
        
        # Add to history
        self.history.add_cidr(cidr)
        
        self.status_label.configure(text=f"Calculated subnet information for {cidr}")
    
    # get_network_class method removed - now handled by SubnetCalculator
    
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
    
    def create_bandwidth_content(self, parent):
        """Create bandwidth testing page"""
        parent.pack(fill="both", expand=True)
        
        # Initialize bandwidth tester
        self.bandwidth_tester = BandwidthTester()
        
        # Check if iperf3 is available
        if not self.bandwidth_tester.is_iperf3_available():
            self.show_iperf3_not_installed(parent)
            return
        
        # Scroll container
        scroll = ctk.CTkScrollableFrame(parent)
        scroll.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Header
        header_card = StyledCard(scroll)
        header_card.pack(fill="x", pady=(0, SPACING['md']))
        
        title = ctk.CTkLabel(
            header_card,
            text="🚀 Bandwidth Testing (iperf3)",
            font=ctk.CTkFont(size=FONTS['heading'], weight="bold")
        )
        title.pack(padx=SPACING['lg'], pady=SPACING['lg'])
        
        subtitle = SubTitle(
            header_card,
            text="Test network throughput and speed using iperf3"
        )
        subtitle.pack(padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Test Configuration Card
        config_card = StyledCard(scroll)
        config_card.pack(fill="x", pady=(0, SPACING['md']))
        
        config_title = SectionTitle(config_card, text="Test Configuration")
        config_title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        # Server Host
        host_label = ctk.CTkLabel(config_card, text="iperf3 Server Host *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        host_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['xs']))
        
        self.bandwidth_host = StyledEntry(config_card, placeholder_text="e.g., iperf.example.com or 192.168.1.100")
        self.bandwidth_host.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Settings row
        settings_frame = ctk.CTkFrame(config_card, fg_color="transparent")
        settings_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Port
        port_label = ctk.CTkLabel(settings_frame, text="Port:", font=ctk.CTkFont(size=FONTS['body']))
        port_label.pack(side="left", padx=(0, SPACING['xs']))
        
        self.bandwidth_port = StyledEntry(settings_frame, placeholder_text="5201", width=80)
        self.bandwidth_port.insert(0, "5201")
        self.bandwidth_port.pack(side="left", padx=(0, SPACING['md']))
        
        # Duration
        duration_label = ctk.CTkLabel(settings_frame, text="Duration (sec):", font=ctk.CTkFont(size=FONTS['body']))
        duration_label.pack(side="left", padx=(0, SPACING['xs']))
        
        self.bandwidth_duration = StyledEntry(settings_frame, placeholder_text="10", width=60)
        self.bandwidth_duration.insert(0, "10")
        self.bandwidth_duration.pack(side="left")
        
        # Test buttons
        btn_frame = ctk.CTkFrame(config_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        self.bandwidth_upload_btn = StyledButton(
            btn_frame,
            text="⬆ Upload Test",
            command=self.run_upload_test,
            size="large",
            variant="primary"
        )
        self.bandwidth_upload_btn.pack(side="left", fill="x", expand=True, padx=(0, SPACING['xs']))
        
        self.bandwidth_download_btn = StyledButton(
            btn_frame,
            text="⬇ Download Test",
            command=self.run_download_test,
            size="large",
            variant="success"
        )
        self.bandwidth_download_btn.pack(side="left", fill="x", expand=True, padx=(SPACING['xs'], 0))
        
        # Results Card
        results_card = StyledCard(scroll)
        results_card.pack(fill="both", expand=True)
        
        results_title = SectionTitle(results_card, text="Test Results")
        results_title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        self.bandwidth_results_frame = ctk.CTkFrame(results_card, fg_color="transparent")
        self.bandwidth_results_frame.pack(fill="both", expand=True, padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Empty state
        self.show_bandwidth_empty_state()
        
        # Info box
        info_card = StyledCard(scroll)
        info_card.pack(fill="x", pady=(SPACING['md'], 0))
        
        info_title = ctk.CTkLabel(
            info_card,
            text="ℹ️ About iperf3 Testing",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        info_title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['xs']))
        
        info_text = ctk.CTkLabel(
            info_card,
            text="iperf3 requires a server to test against. You can:\n\n" +
                 "• Use a public iperf3 server (search online)\n" +
                 "• Set up your own server: iperf3 -s\n" +
                 "• Upload Test: Measures your upload speed to server\n" +
                 "• Download Test: Measures your download speed from server",
            font=ctk.CTkFont(size=FONTS['small']),
            text_color=COLORS['text_secondary'],
            justify="left"
        )
        info_text.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['md']))
    
    def show_iperf3_not_installed(self, parent):
        """Show iperf3 not installed message with instructions"""
        scroll = ctk.CTkScrollableFrame(parent)
        scroll.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Warning card
        warning_card = StyledCard(scroll)
        warning_card.pack(fill="both", expand=True)
        
        # Icon and title
        title = ctk.CTkLabel(
            warning_card,
            text="⚠️ iperf3 Not Installed",
            font=ctk.CTkFont(size=FONTS['heading'], weight="bold"),
            text_color=COLORS['warning']
        )
        title.pack(pady=(SPACING['lg'], SPACING['md']))
        
        # Message
        message = ctk.CTkLabel(
            warning_card,
            text="The bandwidth testing feature requires iperf3 to be installed on your system.",
            font=ctk.CTkFont(size=FONTS['body']),
            wraplength=600
        )
        message.pack(pady=(0, SPACING['lg']))
        
        # Installation instructions
        instructions_frame = ctk.CTkFrame(warning_card, fg_color=COLORS['bg_card'])
        instructions_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        inst_title = ctk.CTkLabel(
            instructions_frame,
            text="📥 Installation Instructions for Windows:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        inst_title.pack(anchor="w", padx=SPACING['md'], pady=(SPACING['md'], SPACING['xs']))
        
        instructions = """
Option 1: Using Chocolatey (Recommended)
  1. Install Chocolatey: https://chocolatey.org/install
  2. Open PowerShell as Administrator
  3. Run: choco install iperf3
  4. Restart this application

Option 2: Using Scoop
  1. Install Scoop: https://scoop.sh
  2. Open PowerShell
  3. Run: scoop install iperf3
  4. Restart this application

Option 3: Manual Installation
  1. Download from: https://iperf.fr/iperf-download.php
  2. Extract iperf3.exe to a folder
  3. Add folder to PATH environment variable
  4. Restart this application

Option 4: Using WSL (Windows Subsystem for Linux)
  1. Install WSL2
  2. In WSL terminal: sudo apt install iperf3
  3. Use from WSL terminal instead
        """
        
        inst_text = ctk.CTkLabel(
            instructions_frame,
            text=instructions,
            font=ctk.CTkFont(size=FONTS['small'], family="Consolas"),
            justify="left",
            anchor="w"
        )
        inst_text.pack(anchor="w", padx=SPACING['md'], pady=(0, SPACING['md']))
        
        # Refresh button
        refresh_btn = StyledButton(
            warning_card,
            text="🔄 Check Again",
            command=lambda: self.refresh_bandwidth_page(),
            size="large",
            variant="primary"
        )
        refresh_btn.pack(pady=(0, SPACING['lg']))
        
        # Alternative info
        alt_card = StyledCard(scroll)
        alt_card.pack(fill="x", pady=(SPACING['md'], 0))
        
        alt_title = ctk.CTkLabel(
            alt_card,
            text="💡 Alternative",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        alt_title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['xs']))
        
        alt_text = ctk.CTkLabel(
            alt_card,
            text="You can also use online speed test websites like:\n" +
                 "• Speedtest.net\n" +
                 "• Fast.com\n" +
                 "• Google Speed Test (search 'internet speed test')",
            font=ctk.CTkFont(size=FONTS['small']),
            text_color=COLORS['text_secondary'],
            justify="left"
        )
        alt_text.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['md']))
    
    def refresh_bandwidth_page(self):
        """Refresh bandwidth page after iperf3 installation"""
        # Clear the page
        if "bandwidth" in self.pages:
            self.pages["bandwidth"].destroy()
            del self.pages["bandwidth"]
            self.pages_loaded.remove("bandwidth")
        
        # Reload the page
        self.switch_page("bandwidth")
    
    def show_bandwidth_empty_state(self):
        """Show empty state for bandwidth results"""
        for widget in self.bandwidth_results_frame.winfo_children():
            widget.destroy()
        
        empty_frame = ctk.CTkFrame(self.bandwidth_results_frame, fg_color="transparent")
        empty_frame.pack(fill="both", expand=True, pady=SPACING['xl'])
        
        empty_label = ctk.CTkLabel(
            empty_frame,
            text="📊\n\nNo test results yet\n\nRun an upload or download test to see results",
            font=ctk.CTkFont(size=FONTS['body']),
            text_color=COLORS['text_secondary'],
            justify="center"
        )
        empty_label.pack(expand=True)
    
    def run_upload_test(self):
        """Run upload speed test"""
        host = self.bandwidth_host.get().strip()
        port = self.bandwidth_port.get().strip() or "5201"
        duration = self.bandwidth_duration.get().strip() or "10"
        
        if not host:
            messagebox.showerror("Error", "Please enter an iperf3 server host")
            return
        
        try:
            port = int(port)
            duration = int(duration)
        except ValueError:
            messagebox.showerror("Error", "Port and duration must be numbers")
            return
        
        # Disable buttons during test
        self.bandwidth_upload_btn.configure(state="disabled", text="⬆ Testing...")
        self.bandwidth_download_btn.configure(state="disabled")
        
        self.show_bandwidth_testing()
        
        def callback(results, error):
            if error:
                messagebox.showerror("Test Failed", f"Upload test failed:\n{error}")
                self.show_bandwidth_empty_state()
            else:
                self.show_bandwidth_results(results, "Upload")
            
            self.bandwidth_upload_btn.configure(state="normal", text="⬆ Upload Test")
            self.bandwidth_download_btn.configure(state="normal")
        
        self.bandwidth_tester.test_client(host, port, duration, reverse=False, callback=callback)
    
    def run_download_test(self):
        """Run download speed test"""
        host = self.bandwidth_host.get().strip()
        port = self.bandwidth_port.get().strip() or "5201"
        duration = self.bandwidth_duration.get().strip() or "10"
        
        if not host:
            messagebox.showerror("Error", "Please enter an iperf3 server host")
            return
        
        try:
            port = int(port)
            duration = int(duration)
        except ValueError:
            messagebox.showerror("Error", "Port and duration must be numbers")
            return
        
        # Disable buttons during test
        self.bandwidth_upload_btn.configure(state="disabled")
        self.bandwidth_download_btn.configure(state="disabled", text="⬇ Testing...")
        
        self.show_bandwidth_testing()
        
        def callback(results, error):
            if error:
                messagebox.showerror("Test Failed", f"Download test failed:\n{error}")
                self.show_bandwidth_empty_state()
            else:
                self.show_bandwidth_results(results, "Download")
            
            self.bandwidth_upload_btn.configure(state="normal")
            self.bandwidth_download_btn.configure(state="normal", text="⬇ Download Test")
        
        self.bandwidth_tester.test_client(host, port, duration, reverse=True, callback=callback)
    
    def show_bandwidth_testing(self):
        """Show testing in progress"""
        for widget in self.bandwidth_results_frame.winfo_children():
            widget.destroy()
        
        testing_frame = ctk.CTkFrame(self.bandwidth_results_frame, fg_color="transparent")
        testing_frame.pack(fill="both", expand=True, pady=SPACING['xl'])
        
        testing_label = ctk.CTkLabel(
            testing_frame,
            text="⏳\n\nTest in progress...\n\nPlease wait",
            font=ctk.CTkFont(size=FONTS['body']),
            justify="center"
        )
        testing_label.pack(expand=True)
    
    def show_bandwidth_results(self, results, test_type):
        """Display bandwidth test results"""
        for widget in self.bandwidth_results_frame.winfo_children():
            widget.destroy()
        
        summary = self.bandwidth_tester.get_summary(results)
        
        if not summary:
            self.show_bandwidth_empty_state()
            return
        
        # Test type header
        type_label = ctk.CTkLabel(
            self.bandwidth_results_frame,
            text=f"✅ {test_type} Test Complete",
            font=ctk.CTkFont(size=FONTS['subheading'], weight="bold"),
            text_color=COLORS['success']
        )
        type_label.pack(pady=(0, SPACING['md']))
        
        # Main speed display
        if test_type == "Upload":
            speed = summary['sent_mbps']
        else:
            speed = summary['received_mbps']
        
        speed_card = ctk.CTkFrame(self.bandwidth_results_frame, fg_color=COLORS['bg_card'])
        speed_card.pack(fill="x", pady=(0, SPACING['md']))
        
        speed_label = ctk.CTkLabel(
            speed_card,
            text=f"{speed:.2f} Mbps",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        speed_label.pack(pady=SPACING['lg'])
        
        # Detailed results
        details_data = [
            ("Sent (Upload)", f"{summary['sent_mbps']:.2f} Mbps", f"{summary['sent_bytes'] / 1_000_000:.2f} MB"),
            ("Received (Download)", f"{summary['received_mbps']:.2f} Mbps", f"{summary['received_bytes'] / 1_000_000:.2f} MB"),
            ("Local CPU Usage", f"{summary['cpu_utilization_local']:.1f}%", ""),
            ("Remote CPU Usage", f"{summary['cpu_utilization_remote']:.1f}%", ""),
        ]
        
        for label, value1, value2 in details_data:
            row = ctk.CTkFrame(self.bandwidth_results_frame, fg_color="transparent")
            row.pack(fill="x", pady=SPACING['xs'])
            
            label_widget = ctk.CTkLabel(row, text=f"{label}:", font=ctk.CTkFont(size=FONTS['body'], weight="bold"), width=150, anchor="w")
            label_widget.pack(side="left")
            
            value_widget = ctk.CTkLabel(row, text=value1, font=ctk.CTkFont(size=FONTS['body']), anchor="w")
            value_widget.pack(side="left", padx=SPACING['sm'])
            
            if value2:
                value2_widget = ctk.CTkLabel(row, text=value2, font=ctk.CTkFont(size=FONTS['small']), text_color=COLORS['text_secondary'], anchor="w")
                value2_widget.pack(side="left")
    
    def create_panos_content(self, parent):
        """Create PAN-OS CLI Generator content"""
        # Initialize storage
        self.panos_commands = []
        self.panos_generated_names = []
        
        # Main container with scrollable area
        main_container = ctk.CTkFrame(parent)
        main_container.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Left side - Input forms
        left_frame = ctk.CTkFrame(main_container)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, SPACING['md']))
        
        # Tab buttons
        tab_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        tab_frame.pack(fill="x", pady=(0, SPACING['md']))
        
        self.panos_addresses_btn = StyledButton(
            tab_frame,
            text="📍 Addresses",
            command=lambda: self.switch_panos_tab("addresses"),
            size="medium",
            variant="primary"
        )
        self.panos_addresses_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        self.panos_policies_btn = StyledButton(
            tab_frame,
            text="🛡️ Policies",
            command=lambda: self.switch_panos_tab("policies"),
            size="medium",
            variant="neutral"
        )
        self.panos_policies_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        self.panos_service_btn = StyledButton(
            tab_frame,
            text="🔌 Services",
            command=lambda: self.switch_panos_tab("service"),
            size="medium",
            variant="neutral"
        )
        self.panos_service_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        # Advanced tabs (second row)
        tab_frame2 = ctk.CTkFrame(left_frame, fg_color="transparent")
        tab_frame2.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        
        self.panos_schedule_btn = StyledButton(
            tab_frame2,
            text="🕐 Schedule",
            command=lambda: self.switch_panos_tab("schedule"),
            size="medium",
            variant="neutral"
        )
        self.panos_schedule_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        self.panos_appfilter_btn = StyledButton(
            tab_frame2,
            text="📱 App Filter",
            command=lambda: self.switch_panos_tab("appfilter"),
            size="medium",
            variant="neutral"
        )
        self.panos_appfilter_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        self.panos_urlcat_btn = StyledButton(
            tab_frame2,
            text="🌐 URL Category",
            command=lambda: self.switch_panos_tab("urlcat"),
            size="medium",
            variant="neutral"
        )
        self.panos_urlcat_btn.pack(side="left")
        
        # Tab content area
        self.panos_tab_content = ctk.CTkFrame(left_frame)
        self.panos_tab_content.pack(fill="both", expand=True)
        
        # Create tabs
        self.create_panos_addresses_tab()
        self.create_panos_policies_tab()
        self.create_panos_schedule_tab()
        self.create_panos_appfilter_tab()
        self.create_panos_urlcat_tab()
        self.create_panos_service_tab()
        
        # Show name generator by default
        self.panos_current_tab = "name"
        self.panos_name_gen_tab.pack(fill="both", expand=True)
        
        # Right side - Output panel
        self.create_panos_output_panel(main_container)
    
    def switch_panos_tab(self, tab_name):
        """Switch between PAN-OS Generator tabs"""
        # Hide all tabs
        self.panos_addresses_tab.pack_forget()
        self.panos_policies_tab.pack_forget()
        self.panos_service_tab.pack_forget()
        self.panos_schedule_tab.pack_forget()
        self.panos_appfilter_tab.pack_forget()
        self.panos_urlcat_tab.pack_forget()
        
        # Reset all button colors
        self.panos_addresses_btn.configure(fg_color=COLORS['neutral'])
        self.panos_policies_btn.configure(fg_color=COLORS['neutral'])
        self.panos_service_btn.configure(fg_color=COLORS['neutral'])
        self.panos_schedule_btn.configure(fg_color=COLORS['neutral'])
        self.panos_appfilter_btn.configure(fg_color=COLORS['neutral'])
        self.panos_urlcat_btn.configure(fg_color=COLORS['neutral'])
        
        # Show selected tab and highlight button
        if tab_name == "addresses":
            self.panos_addresses_btn.configure(fg_color=COLORS['primary'])
            self.panos_addresses_tab.pack(fill="both", expand=True)
        elif tab_name == "policies":
            self.panos_policies_btn.configure(fg_color=COLORS['primary'])
            self.panos_policies_tab.pack(fill="both", expand=True)
        elif tab_name == "schedule":
            self.panos_schedule_btn.configure(fg_color=COLORS['primary'])
            self.panos_schedule_tab.pack(fill="both", expand=True)
        elif tab_name == "appfilter":
            self.panos_appfilter_btn.configure(fg_color=COLORS['primary'])
            self.panos_appfilter_tab.pack(fill="both", expand=True)
        elif tab_name == "urlcat":
            self.panos_urlcat_btn.configure(fg_color=COLORS['primary'])
            self.panos_urlcat_tab.pack(fill="both", expand=True)
        elif tab_name == "service":
            self.panos_service_btn.configure(fg_color=COLORS['primary'])
            self.panos_service_tab.pack(fill="both", expand=True)
        
        self.panos_current_tab = tab_name
    
    def create_panos_name_generator_tab(self):
        """Create Name Generator tab"""
        self.panos_name_gen_tab = ctk.CTkFrame(self.panos_addresses_tab, fg_color="transparent")
        
        # Card
        card = StyledCard(self.panos_name_gen_tab)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        # Title
        title = SectionTitle(card, text="Address Name Generator")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(
            card,
            text="Generate address object names from base names and IPs, then create CLI commands"
        )
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Step 1
        step1_label = ctk.CTkLabel(
            card,
            text="Step 1: Input Data",
            font=ctk.CTkFont(size=FONTS['subheading'], weight="bold")
        )
        step1_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['sm']))
        
        # Base Names
        name_label = ctk.CTkLabel(
            card,
            text="Base Names (one per line):",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        name_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['sm'], SPACING['xs']))
        
        self.panos_gen_names = ctk.CTkTextbox(
            card,
            height=120,
            font=ctk.CTkFont(size=FONTS['body'], family="Consolas")
        )
        self.panos_gen_names.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Setup placeholder
        self.panos_gen_names_placeholder = "Server1\nServer2\nWebServer"
        self.panos_gen_names.insert("1.0", self.panos_gen_names_placeholder)
        self.panos_gen_names.configure(text_color=COLORS['text_secondary'])
        self.panos_gen_names.bind("<FocusIn>", lambda e: self.on_textbox_focus_in(self.panos_gen_names, self.panos_gen_names_placeholder))
        self.panos_gen_names.bind("<FocusOut>", lambda e: self.on_textbox_focus_out(self.panos_gen_names, self.panos_gen_names_placeholder))
        
        # IP Addresses
        ip_label = ctk.CTkLabel(
            card,
            text="IP Addresses/Netmasks (one per line):",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        ip_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_gen_ips = ctk.CTkTextbox(
            card,
            height=120,
            font=ctk.CTkFont(size=FONTS['body'], family="Consolas")
        )
        self.panos_gen_ips.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Setup placeholder
        self.panos_gen_ips_placeholder = "192.168.1.10\n192.168.1.20\n10.0.0.10"
        self.panos_gen_ips.insert("1.0", self.panos_gen_ips_placeholder)
        self.panos_gen_ips.configure(text_color=COLORS['text_secondary'])
        self.panos_gen_ips.bind("<FocusIn>", lambda e: self.on_textbox_focus_in(self.panos_gen_ips, self.panos_gen_ips_placeholder))
        self.panos_gen_ips.bind("<FocusOut>", lambda e: self.on_textbox_focus_out(self.panos_gen_ips, self.panos_gen_ips_placeholder))
        
        # Options row
        options_frame = ctk.CTkFrame(card, fg_color="transparent")
        options_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Separator
        sep_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        sep_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        sep_label = ctk.CTkLabel(sep_frame, text="Separator:", font=ctk.CTkFont(size=FONTS['body']))
        sep_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_gen_separator = ctk.CTkComboBox(
            sep_frame,
            values=["_ (Underscore)", "- (Dash)", ". (Dot)"],
            state="readonly"
        )
        self.panos_gen_separator.set("_ (Underscore)")
        self.panos_gen_separator.pack(fill="x")
        
        # Format
        format_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        format_frame.pack(side="left", fill="x", expand=True)
        
        format_label = ctk.CTkLabel(format_frame, text="Format:", font=ctk.CTkFont(size=FONTS['body']))
        format_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_gen_format = ctk.CTkComboBox(
            format_frame,
            values=["Name_IP", "IP_Name", "Name Only", "Custom"],
            state="readonly",
            command=self.on_panos_format_change
        )
        self.panos_gen_format.set("Name_IP")
        self.panos_gen_format.pack(fill="x")
        
        # Custom format (hidden by default)
        self.panos_custom_format_frame = ctk.CTkFrame(card, fg_color="transparent")
        
        custom_label = ctk.CTkLabel(
            self.panos_custom_format_frame,
            text="Custom Format Pattern:",
            font=ctk.CTkFont(size=FONTS['body'])
        )
        custom_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_gen_custom = StyledEntry(
            self.panos_custom_format_frame,
            placeholder_text="e.g., {name}-{ip} or Host_{name}_{ip}"
        )
        self.panos_gen_custom.pack(fill="x", pady=(0, SPACING['xs']))
        
        custom_help = SubTitle(
            self.panos_custom_format_frame,
            text="Use {name} for base name and {ip} for IP address"
        )
        custom_help.pack(anchor="w")
        
        # Generate Names and Reset buttons
        gen_buttons_frame = ctk.CTkFrame(card, fg_color="transparent")
        gen_buttons_frame.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['lg']))
        
        gen_names_btn = StyledButton(
            gen_buttons_frame,
            text="🎯 Generate Object Names",
            command=self.generate_panos_names,
            size="large",
            variant="primary"
        )
        gen_names_btn.pack(side="left", fill="x", expand=True, padx=(0, SPACING['xs']))
        
        reset_btn = StyledButton(
            gen_buttons_frame,
            text="🔄 Reset",
            command=self.reset_panos_name_generator,
            size="large",
            variant="neutral"
        )
        reset_btn.pack(side="left", padx=(SPACING['xs'], 0))
        
        # Preview section (hidden initially)
        self.panos_preview_frame = ctk.CTkFrame(card, fg_color="transparent")
        
        preview_label = ctk.CTkLabel(
            self.panos_preview_frame,
            text="Generated Names Preview:",
            font=ctk.CTkFont(size=FONTS['subheading'], weight="bold")
        )
        preview_label.pack(anchor="w", pady=(0, SPACING['sm']))
        
        self.panos_preview_text = ctk.CTkTextbox(
            self.panos_preview_frame,
            height=150,
            font=ctk.CTkFont(size=FONTS['small'], family="Consolas")
        )
        self.panos_preview_text.pack(fill="x", pady=(0, SPACING['md']))
        
        # Step 2 (hidden initially)
        self.panos_step2_frame = ctk.CTkFrame(self.panos_preview_frame, fg_color="transparent")
        
        step2_label = ctk.CTkLabel(
            self.panos_step2_frame,
            text="Step 2: Generate CLI Commands",
            font=ctk.CTkFont(size=FONTS['subheading'], weight="bold")
        )
        step2_label.pack(anchor="w", pady=(0, SPACING['sm']))
        
        self.panos_gen_shared = ctk.CTkCheckBox(
            self.panos_step2_frame,
            text="Create as Shared Objects (available to all virtual systems)",
            font=ctk.CTkFont(size=FONTS['body'])
        )
        self.panos_gen_shared.select()
        self.panos_gen_shared.pack(anchor="w", pady=(0, SPACING['md']))
        
        gen_commands_btn = StyledButton(
            self.panos_step2_frame,
            text="💻 Generate CLI Commands",
            command=self.generate_panos_from_names,
            size="large",
            variant="success"
        )
        gen_commands_btn.pack(fill="x")
        
        # Help box
        help_box = InfoBox(
            card,
            message="💡 How it Works:\n"
                   "• Both lists must have the same number of lines\n"
                   "• Each name pairs with corresponding IP (line by line)\n"
                   "• Choose format to create object names automatically\n"
                   "• Example: 'Server1' + '192.168.1.10' → 'Server1_192_168_1_10'",
            box_type="info"
        )
        help_box.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['lg']))
    
    def create_panos_single_address_tab(self):
        """Create single address object tab"""
        self.panos_single_addr_tab = ctk.CTkFrame(self.panos_addresses_tab, fg_color="transparent")
        
        # Card
        card = StyledCard(self.panos_single_addr_tab)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        # Title
        title = SectionTitle(card, text="Single Address Object")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(
            card,
            text="Create a single address object with optional description"
        )
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Object Name
        name_label = ctk.CTkLabel(
            card,
            text="Object Name *",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        name_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['sm'], SPACING['xs']))
        
        self.panos_single_name = StyledEntry(
            card,
            placeholder_text="e.g., Server_192.168.1.10"
        )
        self.panos_single_name.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # IP Address
        ip_label = ctk.CTkLabel(
            card,
            text="IP Address/Netmask *",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        ip_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_single_ip = StyledEntry(
            card,
            placeholder_text="192.168.1.0/24 or 192.168.1.10"
        )
        self.panos_single_ip.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Description
        desc_label = ctk.CTkLabel(
            card,
            text="Description (optional)",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        desc_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_single_desc = StyledEntry(
            card,
            placeholder_text="Optional description"
        )
        self.panos_single_desc.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Shared checkbox
        self.panos_single_shared = ctk.CTkCheckBox(
            card,
            text="Shared Object (available to all virtual systems)",
            font=ctk.CTkFont(size=FONTS['body'])
        )
        self.panos_single_shared.select()
        self.panos_single_shared.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Generate button
        gen_btn = StyledButton(
            card,
            text="💻 Generate Command",
            command=self.generate_single_address,
            size="large",
            variant="primary"
        )
        gen_btn.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['lg']))
    
    def create_panos_address_group_tab(self):
        """Create Address Group tab"""
        self.panos_group_tab = ctk.CTkFrame(self.panos_addresses_tab, fg_color="transparent")
        
        # Initialize members list
        self.panos_group_members = []
        
        # Card
        card = StyledCard(self.panos_group_tab)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        # Title
        title = SectionTitle(card, text="Address Group")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(
            card,
            text="Create address groups to organize multiple address objects"
        )
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Virtual System and Type row
        options_frame = ctk.CTkFrame(card, fg_color="transparent")
        options_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        vsys_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        vsys_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        vsys_label = ctk.CTkLabel(vsys_frame, text="Virtual System:", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        vsys_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_group_vsys = ctk.CTkComboBox(
            vsys_frame,
            values=["shared", "vsys1", "vsys2", "vsys3"],
            state="readonly"
        )
        self.panos_group_vsys.set("shared")
        self.panos_group_vsys.pack(fill="x")
        
        type_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        type_frame.pack(side="left", fill="x", expand=True)
        
        type_label = ctk.CTkLabel(type_frame, text="Type:", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        type_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_group_type = ctk.CTkComboBox(
            type_frame,
            values=["Static", "Dynamic"],
            state="readonly"
        )
        self.panos_group_type.set("Static")
        self.panos_group_type.pack(fill="x")
        
        # Group Name
        name_label = ctk.CTkLabel(
            card,
            text="Group Name *",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        name_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_group_name = StyledEntry(
            card,
            placeholder_text="e.g., Internal_Networks"
        )
        self.panos_group_name.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Members
        members_label = ctk.CTkLabel(
            card,
            text="Members *",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        members_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        # Add member input
        add_frame = ctk.CTkFrame(card, fg_color="transparent")
        add_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['sm']))
        
        self.panos_group_member_input = StyledEntry(
            add_frame,
            placeholder_text="Add address object name"
        )
        self.panos_group_member_input.pack(side="left", fill="x", expand=True, padx=(0, SPACING['xs']))
        
        add_btn = StyledButton(
            add_frame,
            text="Add",
            command=self.add_group_member,
            size="small",
            variant="neutral"
        )
        add_btn.pack(side="right")
        
        # Bulk paste section
        bulk_label = ctk.CTkLabel(
            card,
            text="Or paste multiple members (one per line):",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        bulk_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['sm'], SPACING['xs']))
        
        self.panos_group_bulk_paste = ctk.CTkTextbox(
            card,
            height=80,
            font=ctk.CTkFont(size=FONTS['body'])
        )
        self.panos_group_bulk_paste.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        bulk_add_btn = StyledButton(
            card,
            text="Add All from List",
            command=self.add_bulk_group_members,
            size="small",
            variant="neutral"
        )
        bulk_add_btn.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Members display
        self.panos_group_members_display = ctk.CTkFrame(card, fg_color=COLORS['bg_card'])
        self.panos_group_members_display.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        self.panos_group_members_display.configure(height=100)
        
        # Description
        desc_label = ctk.CTkLabel(
            card,
            text="Description (optional)",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        desc_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_group_desc = StyledEntry(
            card,
            placeholder_text="Optional description"
        )
        self.panos_group_desc.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Generate button
        gen_btn = StyledButton(
            card,
            text="💻 Generate Command",
            command=self.generate_address_group,
            size="large",
            variant="primary"
        )
        gen_btn.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['lg']))
    
    def create_panos_addresses_tab(self):
        """Create unified Addresses tab with subtabs"""
        self.panos_addresses_tab = ctk.CTkScrollableFrame(self.panos_tab_content)
        
        # Create subtabs: Name Generator, Single Address, Address Groups
        subtab_frame = ctk.CTkFrame(self.panos_addresses_tab, fg_color="transparent")
        subtab_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])
        
        self.addr_namegen_btn = StyledButton(
            subtab_frame,
            text="🎯 Name Generator",
            command=lambda: self.switch_address_subtab("namegen"),
            size="small",
            variant="primary"
        )
        self.addr_namegen_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        self.addr_single_btn = StyledButton(
            subtab_frame,
            text="🌐 Single Address",
            command=lambda: self.switch_address_subtab("single"),
            size="small",
            variant="neutral"
        )
        self.addr_single_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        self.addr_group_btn = StyledButton(
            subtab_frame,
            text="📦 Address Groups",
            command=lambda: self.switch_address_subtab("group"),
            size="small",
            variant="neutral"
        )
        self.addr_group_btn.pack(side="left")
        
        # Name Generator Content
        self.create_panos_name_generator_tab()
        
        # Single Address Content  
        self.create_panos_single_address_tab()
        self.panos_single_addr_tab.pack_forget()
        
        # Address Groups Content
        self.create_panos_address_group_tab()
        self.panos_group_tab.pack_forget()
    
    def switch_address_subtab(self, subtab):
        """Switch between address subtabs"""
        # Hide all
        self.panos_name_gen_tab.pack_forget()
        self.panos_single_addr_tab.pack_forget()
        self.panos_group_tab.pack_forget()
        
        # Reset button colors
        self.addr_namegen_btn.configure(fg_color=COLORS['neutral'])
        self.addr_single_btn.configure(fg_color=COLORS['neutral'])
        self.addr_group_btn.configure(fg_color=COLORS['neutral'])
        
        # Show selected
        if subtab == "namegen":
            self.addr_namegen_btn.configure(fg_color=COLORS['primary'])
            self.panos_name_gen_tab.pack(fill="both", expand=True)
        elif subtab == "single":
            self.addr_single_btn.configure(fg_color=COLORS['primary'])
            self.panos_single_addr_tab.pack(fill="both", expand=True)
        elif subtab == "group":
            self.addr_group_btn.configure(fg_color=COLORS['primary'])
            self.panos_group_tab.pack(fill="both", expand=True)
    
    def create_panos_nat_tab(self):
        """Create NAT Rule tab"""
        self.panos_nat_tab = ctk.CTkFrame(self.panos_policies_tab, fg_color="transparent")
        
        # Card
        card = StyledCard(self.panos_nat_tab)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        # Title
        title = SectionTitle(card, text="NAT Rule")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(
            card,
            text="Create DNAT or SNAT rules for network address translation"
        )
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # NAT Type
        type_label = ctk.CTkLabel(
            card,
            text="NAT Type:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        type_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        type_frame = ctk.CTkFrame(card, fg_color="transparent")
        type_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        self.panos_nat_type_var = ctk.StringVar(value="dnat")
        
        dnat_radio = ctk.CTkRadioButton(
            type_frame,
            text="DNAT (Destination NAT)",
            variable=self.panos_nat_type_var,
            value="dnat"
        )
        dnat_radio.pack(side="left", padx=(0, SPACING['lg']))
        
        snat_radio = ctk.CTkRadioButton(
            type_frame,
            text="SNAT (Source NAT)",
            variable=self.panos_nat_type_var,
            value="snat"
        )
        snat_radio.pack(side="left")
        
        # Virtual System and Rule Name row
        row1_frame = ctk.CTkFrame(card, fg_color="transparent")
        row1_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        vsys_frame = ctk.CTkFrame(row1_frame, fg_color="transparent")
        vsys_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        vsys_label = ctk.CTkLabel(vsys_frame, text="Virtual System:", font=ctk.CTkFont(size=FONTS['body']))
        vsys_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_nat_vsys = ctk.CTkComboBox(
            vsys_frame,
            values=["shared", "vsys1", "vsys2", "vsys3"],
            state="readonly"
        )
        self.panos_nat_vsys.set("shared")
        self.panos_nat_vsys.pack(fill="x")
        
        name_frame = ctk.CTkFrame(row1_frame, fg_color="transparent")
        name_frame.pack(side="left", fill="x", expand=True)
        
        name_label = ctk.CTkLabel(name_frame, text="Rule Name *:", font=ctk.CTkFont(size=FONTS['body']))
        name_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_nat_name = StyledEntry(name_frame, placeholder_text="e.g., NAT_DMZ_Web")
        self.panos_nat_name.pack(fill="x")
        
        # From/To Zones row
        row2_frame = ctk.CTkFrame(card, fg_color="transparent")
        row2_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        from_frame = ctk.CTkFrame(row2_frame, fg_color="transparent")
        from_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        from_label = ctk.CTkLabel(from_frame, text="From Zone *:", font=ctk.CTkFont(size=FONTS['body']))
        from_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_nat_from = StyledEntry(from_frame, placeholder_text="e.g., untrust")
        self.panos_nat_from.pack(fill="x")
        
        to_frame = ctk.CTkFrame(row2_frame, fg_color="transparent")
        to_frame.pack(side="left", fill="x", expand=True)
        
        to_label = ctk.CTkLabel(to_frame, text="To Zone *:", font=ctk.CTkFont(size=FONTS['body']))
        to_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_nat_to = StyledEntry(to_frame, placeholder_text="e.g., trust")
        self.panos_nat_to.pack(fill="x")
        
        # Source/Destination row
        row3_frame = ctk.CTkFrame(card, fg_color="transparent")
        row3_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        src_frame = ctk.CTkFrame(row3_frame, fg_color="transparent")
        src_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        src_label = ctk.CTkLabel(src_frame, text="Source Address:", font=ctk.CTkFont(size=FONTS['body']))
        src_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_nat_source = StyledEntry(src_frame, placeholder_text="any")
        self.panos_nat_source.insert(0, "any")
        self.panos_nat_source.pack(fill="x")
        
        dest_frame = ctk.CTkFrame(row3_frame, fg_color="transparent")
        dest_frame.pack(side="left", fill="x", expand=True)
        
        dest_label = ctk.CTkLabel(dest_frame, text="Destination Address *:", font=ctk.CTkFont(size=FONTS['body']))
        dest_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_nat_dest = StyledEntry(dest_frame, placeholder_text="e.g., Public_IP")
        self.panos_nat_dest.pack(fill="x")
        
        # Service/Translated Address row
        row4_frame = ctk.CTkFrame(card, fg_color="transparent")
        row4_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        svc_frame = ctk.CTkFrame(row4_frame, fg_color="transparent")
        svc_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        svc_label = ctk.CTkLabel(svc_frame, text="Service:", font=ctk.CTkFont(size=FONTS['body']))
        svc_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_nat_service = StyledEntry(svc_frame, placeholder_text="any")
        self.panos_nat_service.insert(0, "any")
        self.panos_nat_service.pack(fill="x")
        
        trans_frame = ctk.CTkFrame(row4_frame, fg_color="transparent")
        trans_frame.pack(side="left", fill="x", expand=True)
        
        trans_label = ctk.CTkLabel(trans_frame, text="Translated Address *:", font=ctk.CTkFont(size=FONTS['body']))
        trans_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_nat_translated = StyledEntry(trans_frame, placeholder_text="e.g., Private_IP")
        self.panos_nat_translated.pack(fill="x")
        
        # Translated Port
        port_label = ctk.CTkLabel(
            card,
            text="Translated Port (DNAT only):",
            font=ctk.CTkFont(size=FONTS['body'])
        )
        port_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_nat_port = StyledEntry(card, placeholder_text="e.g., 8080")
        self.panos_nat_port.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Description
        desc_label = ctk.CTkLabel(
            card,
            text="Description (optional):",
            font=ctk.CTkFont(size=FONTS['body'])
        )
        desc_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_nat_desc = StyledEntry(card, placeholder_text="Optional description")
        self.panos_nat_desc.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Generate button
        gen_btn = StyledButton(
            card,
            text="💻 Generate Command",
            command=self.generate_nat_rule,
            size="large",
            variant="primary"
        )
        gen_btn.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['lg']))
    
    def create_panos_policy_tab(self):
        """Create Security Policy Rule tab"""
        self.panos_policy_tab = ctk.CTkFrame(self.panos_policies_tab, fg_color="transparent")
        
        # Card
        card = StyledCard(self.panos_policy_tab)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        # Title
        title = SectionTitle(card, text="Security Policy Rule")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(
            card,
            text="Create security policy rules to control traffic flow"
        )
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Virtual System and Rule Name row
        row1_frame = ctk.CTkFrame(card, fg_color="transparent")
        row1_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        vsys_frame = ctk.CTkFrame(row1_frame, fg_color="transparent")
        vsys_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        vsys_label = ctk.CTkLabel(vsys_frame, text="Virtual System:", font=ctk.CTkFont(size=FONTS['body']))
        vsys_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_vsys = ctk.CTkComboBox(
            vsys_frame,
            values=["shared", "vsys1", "vsys2", "vsys3"],
            state="readonly"
        )
        self.panos_policy_vsys.set("shared")
        self.panos_policy_vsys.pack(fill="x")
        
        name_frame = ctk.CTkFrame(row1_frame, fg_color="transparent")
        name_frame.pack(side="left", fill="x", expand=True)
        
        name_label = ctk.CTkLabel(name_frame, text="Rule Name *:", font=ctk.CTkFont(size=FONTS['body']))
        name_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_name = StyledEntry(name_frame, placeholder_text="e.g., Allow_Web_Traffic")
        self.panos_policy_name.pack(fill="x")
        
        # From/To Zones row
        row2_frame = ctk.CTkFrame(card, fg_color="transparent")
        row2_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        from_frame = ctk.CTkFrame(row2_frame, fg_color="transparent")
        from_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        from_label = ctk.CTkLabel(from_frame, text="From Zone *:", font=ctk.CTkFont(size=FONTS['body']))
        from_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_from = StyledEntry(from_frame, placeholder_text="e.g., trust")
        self.panos_policy_from.pack(fill="x")
        
        to_frame = ctk.CTkFrame(row2_frame, fg_color="transparent")
        to_frame.pack(side="left", fill="x", expand=True)
        
        to_label = ctk.CTkLabel(to_frame, text="To Zone *:", font=ctk.CTkFont(size=FONTS['body']))
        to_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_to = StyledEntry(to_frame, placeholder_text="e.g., untrust")
        self.panos_policy_to.pack(fill="x")
        
        # Source/Destination row
        row3_frame = ctk.CTkFrame(card, fg_color="transparent")
        row3_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        src_frame = ctk.CTkFrame(row3_frame, fg_color="transparent")
        src_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        src_label = ctk.CTkLabel(src_frame, text="Source Address:", font=ctk.CTkFont(size=FONTS['body']))
        src_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_source = StyledEntry(src_frame, placeholder_text="any")
        self.panos_policy_source.insert(0, "any")
        self.panos_policy_source.pack(fill="x")
        
        dest_frame = ctk.CTkFrame(row3_frame, fg_color="transparent")
        dest_frame.pack(side="left", fill="x", expand=True)
        
        dest_label = ctk.CTkLabel(dest_frame, text="Destination Address:", font=ctk.CTkFont(size=FONTS['body']))
        dest_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_dest = StyledEntry(dest_frame, placeholder_text="any")
        self.panos_policy_dest.insert(0, "any")
        self.panos_policy_dest.pack(fill="x")
        
        # Application/Service row
        row4_frame = ctk.CTkFrame(card, fg_color="transparent")
        row4_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        app_frame = ctk.CTkFrame(row4_frame, fg_color="transparent")
        app_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        app_label = ctk.CTkLabel(app_frame, text="Application:", font=ctk.CTkFont(size=FONTS['body']))
        app_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_app = StyledEntry(app_frame, placeholder_text="any")
        self.panos_policy_app.insert(0, "any")
        self.panos_policy_app.pack(fill="x")
        
        svc_frame = ctk.CTkFrame(row4_frame, fg_color="transparent")
        svc_frame.pack(side="left", fill="x", expand=True)
        
        svc_label = ctk.CTkLabel(svc_frame, text="Service:", font=ctk.CTkFont(size=FONTS['body']))
        svc_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_service = StyledEntry(svc_frame, placeholder_text="application-default")
        self.panos_policy_service.insert(0, "application-default")
        self.panos_policy_service.pack(fill="x")
        
        # Action/Profile row
        row5_frame = ctk.CTkFrame(card, fg_color="transparent")
        row5_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        action_frame = ctk.CTkFrame(row5_frame, fg_color="transparent")
        action_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        action_label = ctk.CTkLabel(action_frame, text="Action:", font=ctk.CTkFont(size=FONTS['body']))
        action_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_action = ctk.CTkComboBox(
            action_frame,
            values=["allow", "deny", "drop"],
            state="readonly"
        )
        self.panos_policy_action.set("allow")
        self.panos_policy_action.pack(fill="x")
        
        profile_frame = ctk.CTkFrame(row5_frame, fg_color="transparent")
        profile_frame.pack(side="left", fill="x", expand=True)
        
        profile_label = ctk.CTkLabel(profile_frame, text="Security Profile Group:", font=ctk.CTkFont(size=FONTS['body']))
        profile_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_profile = StyledEntry(profile_frame, placeholder_text="e.g., default")
        self.panos_policy_profile.pack(fill="x")
        
        # Description
        desc_label = ctk.CTkLabel(
            card,
            text="Description (optional):",
            font=ctk.CTkFont(size=FONTS['body'])
        )
        desc_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_policy_desc = StyledEntry(card, placeholder_text="Optional description")
        self.panos_policy_desc.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Generate button
        gen_btn = StyledButton(
            card,
            text="💻 Generate Command",
            command=self.generate_policy_rule,
            size="large",
            variant="primary"
        )
        gen_btn.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['lg']))
    
    def create_panos_output_panel(self, parent):
        """Create command output panel"""
        # Right side - Output
        output_frame = ctk.CTkFrame(parent)
        output_frame.pack(side="right", fill="both", expand=False, padx=(0, 0))
        output_frame.configure(width=400)
        
        output_card = StyledCard(output_frame)
        output_card.pack(fill="both", expand=True)
        
        # Header
        header_frame = ctk.CTkFrame(output_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['md']))
        
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True)
        
        title = ctk.CTkLabel(
            title_frame,
            text="💻 Command Output",
            font=ctk.CTkFont(size=FONTS['heading'], weight="bold")
        )
        title.pack(anchor="w")
        
        self.panos_cmd_count = ctk.CTkLabel(
            title_frame,
            text="0 commands generated",
            font=ctk.CTkFont(size=FONTS['small']),
            text_color=COLORS['text_secondary']
        )
        self.panos_cmd_count.pack(anchor="w", pady=(SPACING['xs'], 0))
        
        clear_btn = StyledButton(
            header_frame,
            text="🗑️ Clear All",
            command=self.clear_panos_commands,
            size="small",
            variant="neutral"
        )
        clear_btn.pack(side="right", padx=(SPACING['md'], 0))
        
        # Commands list
        self.panos_commands_list = ctk.CTkScrollableFrame(output_card, height=400)
        self.panos_commands_list.pack(fill="both", expand=True, padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Action buttons (create before render so it exists)
        self.panos_action_frame = ctk.CTkFrame(output_card, fg_color="transparent")
        self.panos_action_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        self.panos_action_frame.pack_forget()  # Hidden initially
        
        copy_btn = StyledButton(
            self.panos_action_frame,
            text="📋 Copy All",
            command=self.copy_panos_commands,
            size="medium",
            variant="neutral"
        )
        copy_btn.pack(fill="x", pady=(0, SPACING['xs']))
        
        download_btn = StyledButton(
            self.panos_action_frame,
            text="⬇️ Download",
            command=self.download_panos_commands,
            size="medium",
            variant="primary"
        )
        download_btn.pack(fill="x")
        
        # Render initial empty state
        self.render_panos_commands()
    
    def create_panos_policies_tab(self):
        """Create unified Policies tab with subtabs"""
        self.panos_policies_tab = ctk.CTkScrollableFrame(self.panos_tab_content)
        
        # Create subtabs: NAT Rules, Security Policies
        subtab_frame = ctk.CTkFrame(self.panos_policies_tab, fg_color="transparent")
        subtab_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])
        
        self.policy_nat_btn = StyledButton(
            subtab_frame,
            text="🔄 NAT Rules",
            command=lambda: self.switch_policy_subtab("nat"),
            size="small",
            variant="primary"
        )
        self.policy_nat_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        self.policy_security_btn = StyledButton(
            subtab_frame,
            text="🔐 Security Policies",
            command=lambda: self.switch_policy_subtab("security"),
            size="small",
            variant="neutral"
        )
        self.policy_security_btn.pack(side="left")
        
        # NAT Rules Content
        self.create_panos_nat_tab()
        
        # Security Policies Content
        self.create_panos_policy_tab()
        self.panos_policy_tab.pack_forget()
    
    def switch_policy_subtab(self, subtab):
        """Switch between policy subtabs"""
        # Hide all
        self.panos_nat_tab.pack_forget()
        self.panos_policy_tab.pack_forget()
        
        # Reset button colors
        self.policy_nat_btn.configure(fg_color=COLORS['neutral'])
        self.policy_security_btn.configure(fg_color=COLORS['neutral'])
        
        # Show selected
        if subtab == "nat":
            self.policy_nat_btn.configure(fg_color=COLORS['primary'])
            self.panos_nat_tab.pack(fill="both", expand=True)
        elif subtab == "security":
            self.policy_security_btn.configure(fg_color=COLORS['primary'])
            self.panos_policy_tab.pack(fill="both", expand=True)
    
    def create_panos_schedule_tab(self):
        """Create Schedule Object tab"""
        self.panos_schedule_tab = ctk.CTkScrollableFrame(self.panos_tab_content)
        
        card = StyledCard(self.panos_schedule_tab)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        title = SectionTitle(card, text="Schedule Object")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(card, text="Create time-based schedule objects for policy rules")
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Schedule Name
        name_label = ctk.CTkLabel(card, text="Schedule Name *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        name_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_schedule_name = StyledEntry(card, placeholder_text="e.g., Business_Hours")
        self.panos_schedule_name.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Schedule Type
        type_label = ctk.CTkLabel(card, text="Schedule Type *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        type_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_schedule_type = ctk.CTkComboBox(card, values=["recurring", "non-recurring"], state="readonly")
        self.panos_schedule_type.set("recurring")
        self.panos_schedule_type.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Time Range
        time_frame = ctk.CTkFrame(card, fg_color="transparent")
        time_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        start_label = ctk.CTkLabel(time_frame, text="Start Time (HH:MM):", font=ctk.CTkFont(size=FONTS['body']))
        start_label.pack(side="left", padx=(0, SPACING['xs']))
        
        self.panos_schedule_start = StyledEntry(time_frame, placeholder_text="08:00", width=80)
        self.panos_schedule_start.pack(side="left", padx=(0, SPACING['md']))
        
        end_label = ctk.CTkLabel(time_frame, text="End Time (HH:MM):", font=ctk.CTkFont(size=FONTS['body']))
        end_label.pack(side="left", padx=(0, SPACING['xs']))
        
        self.panos_schedule_end = StyledEntry(time_frame, placeholder_text="18:00", width=80)
        self.panos_schedule_end.pack(side="left")
        
        # Days (for recurring)
        days_label = ctk.CTkLabel(card, text="Days (for recurring):", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        days_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        days_frame = ctk.CTkFrame(card, fg_color="transparent")
        days_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        self.panos_schedule_days = {}
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in days:
            var = ctk.BooleanVar(value=True if day not in ["Saturday", "Sunday"] else False)
            cb = ctk.CTkCheckBox(days_frame, text=day[:3], variable=var, width=60)
            cb.pack(side="left", padx=SPACING['xs'])
            self.panos_schedule_days[day.lower()] = var
        
        # Generate button
        gen_btn = StyledButton(card, text="💻 Generate Command", command=self.generate_schedule_object, size="large", variant="primary")
        gen_btn.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['lg']))
    
    def create_panos_appfilter_tab(self):
        """Create Application Filter tab"""
        self.panos_appfilter_tab = ctk.CTkScrollableFrame(self.panos_tab_content)
        
        card = StyledCard(self.panos_appfilter_tab)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        title = SectionTitle(card, text="Application Filter")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(card, text="Create custom application groups and filters")
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Filter Name
        name_label = ctk.CTkLabel(card, text="Filter Name *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        name_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_appfilter_name = StyledEntry(card, placeholder_text="e.g., Social_Media_Apps")
        self.panos_appfilter_name.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Category
        cat_label = ctk.CTkLabel(card, text="Category *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        cat_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_appfilter_category = ctk.CTkComboBox(
            card,
            values=["business-systems", "collaboration", "general-internet", "media", "networking", "unknown"],
            state="readonly"
        )
        self.panos_appfilter_category.set("general-internet")
        self.panos_appfilter_category.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Subcategory
        subcat_label = ctk.CTkLabel(card, text="Subcategory", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        subcat_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_appfilter_subcategory = StyledEntry(card, placeholder_text="e.g., social-networking")
        self.panos_appfilter_subcategory.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Technology
        tech_label = ctk.CTkLabel(card, text="Technology", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        tech_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_appfilter_technology = ctk.CTkComboBox(
            card,
            values=["browser-based", "client-server", "network-protocol", "peer-to-peer"],
            state="readonly"
        )
        self.panos_appfilter_technology.set("browser-based")
        self.panos_appfilter_technology.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Risk Level
        risk_label = ctk.CTkLabel(card, text="Risk Level", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        risk_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        risk_frame = ctk.CTkFrame(card, fg_color="transparent")
        risk_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        self.panos_appfilter_risk = {}
        for level in [1, 2, 3, 4, 5]:
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(risk_frame, text=str(level), variable=var, width=50)
            cb.pack(side="left", padx=SPACING['xs'])
            self.panos_appfilter_risk[level] = var
        
        # Generate button
        gen_btn = StyledButton(card, text="💻 Generate Command", command=self.generate_appfilter, size="large", variant="primary")
        gen_btn.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['lg']))
    
    def create_panos_urlcat_tab(self):
        """Create Custom URL Category tab"""
        self.panos_urlcat_tab = ctk.CTkScrollableFrame(self.panos_tab_content)
        
        card = StyledCard(self.panos_urlcat_tab)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        title = SectionTitle(card, text="Custom URL Category")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(card, text="Create custom URL categories for URL filtering")
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Category Name
        name_label = ctk.CTkLabel(card, text="Category Name *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        name_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_urlcat_name = StyledEntry(card, placeholder_text="e.g., Blocked_Sites")
        self.panos_urlcat_name.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Description
        desc_label = ctk.CTkLabel(card, text="Description", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        desc_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_urlcat_desc = StyledEntry(card, placeholder_text="Optional description")
        self.panos_urlcat_desc.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # URL List
        url_label = ctk.CTkLabel(card, text="URLs (one per line) *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        url_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_urlcat_urls = ctk.CTkTextbox(card, height=150, font=ctk.CTkFont(size=FONTS['body'], family="Consolas"))
        self.panos_urlcat_urls.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        self.panos_urlcat_urls.insert("1.0", "example.com\n*.example.com\nexample.org/path")
        self.panos_urlcat_urls.configure(text_color=COLORS['text_secondary'])
        self.panos_urlcat_urls.bind("<FocusIn>", lambda e: self.on_textbox_focus_in(self.panos_urlcat_urls, "example.com\n*.example.com\nexample.org/path"))
        self.panos_urlcat_urls.bind("<FocusOut>", lambda e: self.on_textbox_focus_out(self.panos_urlcat_urls, "example.com\n*.example.com\nexample.org/path"))
        
        help_text = SubTitle(card, text="Supports domains, wildcards (*.domain.com), and paths")
        help_text.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Type
        type_label = ctk.CTkLabel(card, text="Type", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        type_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_urlcat_type = ctk.CTkComboBox(card, values=["URL List", "Category Match"], state="readonly")
        self.panos_urlcat_type.set("URL List")
        self.panos_urlcat_type.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Generate button
        gen_btn = StyledButton(card, text="💻 Generate Command", command=self.generate_urlcat, size="large", variant="primary")
        gen_btn.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['lg']))
    
    def create_panos_service_tab(self):
        """Create Service Objects tab"""
        self.panos_service_tab = ctk.CTkScrollableFrame(self.panos_tab_content)
        
        # Create two subtabs: Single Service and Service Group
        subtab_frame = ctk.CTkFrame(self.panos_service_tab, fg_color="transparent")
        subtab_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])
        
        self.service_single_btn = StyledButton(
            subtab_frame,
            text="Single Service",
            command=lambda: self.switch_service_subtab("single"),
            size="small",
            variant="primary"
        )
        self.service_single_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        self.service_group_btn = StyledButton(
            subtab_frame,
            text="Service Group",
            command=lambda: self.switch_service_subtab("group"),
            size="small",
            variant="neutral"
        )
        self.service_group_btn.pack(side="left")
        
        # Single Service Tab
        self.service_single_content = self.create_single_service_content(self.panos_service_tab)
        
        # Service Group Tab
        self.service_group_content = self.create_service_group_content(self.panos_service_tab)
        self.service_group_content.pack_forget()
    
    def create_single_service_content(self, parent):
        """Create single service object content"""
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="both", expand=True)
        
        card = StyledCard(content)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        title = SectionTitle(card, text="Service Object")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(card, text="Create TCP/UDP service objects")
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Service Name
        name_label = ctk.CTkLabel(card, text="Service Name *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        name_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_service_name = StyledEntry(card, placeholder_text="e.g., Web_Service")
        self.panos_service_name.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Port
        port_label = ctk.CTkLabel(card, text="Port Number *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        port_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_service_port = StyledEntry(card, placeholder_text="e.g., 8080 or 8080-8090")
        self.panos_service_port.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Protocol Selection with Checkbox
        protocol_label = ctk.CTkLabel(card, text="Protocol *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        protocol_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        protocol_frame = ctk.CTkFrame(card, fg_color="transparent")
        protocol_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        self.panos_service_protocol = ctk.CTkComboBox(
            protocol_frame,
            values=["tcp", "udp"],
            state="readonly",
            width=100
        )
        self.panos_service_protocol.set("tcp")
        self.panos_service_protocol.pack(side="left", padx=(0, SPACING['md']))
        
        # Checkbox for creating both TCP and UDP
        self.panos_service_both = ctk.BooleanVar(value=False)
        both_checkbox = ctk.CTkCheckBox(
            protocol_frame,
            text="Create both TCP and UDP services",
            variable=self.panos_service_both,
            font=ctk.CTkFont(size=FONTS['body'])
        )
        both_checkbox.pack(side="left")
        
        # Description
        desc_label = ctk.CTkLabel(card, text="Description", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        desc_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_service_desc = StyledEntry(card, placeholder_text="Optional description")
        self.panos_service_desc.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Generate button
        gen_btn = StyledButton(card, text="💻 Generate Command", command=self.generate_service_object, size="large", variant="primary")
        gen_btn.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        return content
    
    def create_service_group_content(self, parent):
        """Create service group content"""
        content = ctk.CTkFrame(parent, fg_color="transparent")
        
        card = StyledCard(content)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        title = SectionTitle(card, text="Service Group")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(card, text="Create service groups")
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Group Name
        name_label = ctk.CTkLabel(card, text="Group Name *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        name_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_service_group_name = StyledEntry(card, placeholder_text="e.g., Web_Services")
        self.panos_service_group_name.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Members
        member_label = ctk.CTkLabel(card, text="Add Members", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        member_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        member_frame = ctk.CTkFrame(card, fg_color="transparent")
        member_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_service_group_member = StyledEntry(member_frame, placeholder_text="Service name")
        self.panos_service_group_member.pack(side="left", fill="x", expand=True, padx=(0, SPACING['xs']))
        
        add_btn = StyledButton(
            member_frame,
            text="Add",
            command=self.add_service_group_member,
            size="small",
            variant="neutral"
        )
        add_btn.pack(side="left")
        
        # Bulk paste
        bulk_label = ctk.CTkLabel(card, text="Or paste multiple services (one per line):", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        bulk_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['sm'], SPACING['xs']))
        
        self.panos_service_group_bulk = ctk.CTkTextbox(card, height=80, font=ctk.CTkFont(size=FONTS['body']))
        self.panos_service_group_bulk.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        bulk_add_btn = StyledButton(
            card,
            text="Add All from List",
            command=self.add_bulk_service_members,
            size="small",
            variant="neutral"
        )
        bulk_add_btn.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Members display
        self.panos_service_group_members = []
        self.panos_service_group_display = ctk.CTkFrame(card, fg_color=COLORS['bg_card'])
        self.panos_service_group_display.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        self.panos_service_group_display.configure(height=100)
        
        # Generate button
        gen_btn = StyledButton(card, text="💻 Generate Command", command=self.generate_service_group, size="large", variant="primary")
        gen_btn.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        return content
    
    def switch_service_subtab(self, subtab):
        """Switch between service subtabs"""
        if subtab == "single":
            self.service_single_btn.configure(fg_color=COLORS['primary'])
            self.service_group_btn.configure(fg_color=COLORS['neutral'])
            self.service_group_content.pack_forget()
            self.service_single_content.pack(fill="both", expand=True)
        else:
            self.service_single_btn.configure(fg_color=COLORS['neutral'])
            self.service_group_btn.configure(fg_color=COLORS['primary'])
            self.service_single_content.pack_forget()
            self.service_group_content.pack(fill="both", expand=True)
    
    def validate_panos_ip(self, ip):
        """Validate IP address or network with CIDR notation"""
        pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})(\/(\d{1,2}))?$'
        match = re.match(pattern, ip)
        
        if not match:
            return False
        
        # Validate each octet is 0-255
        octets = [int(match.group(i)) for i in range(1, 5)]
        if any(octet > 255 for octet in octets):
            return False
        
        # Validate CIDR prefix if present
        if match.group(5):  # Has CIDR
            cidr = int(match.group(6))
            if cidr > 32:
                return False
        
        return True
    
    def on_textbox_focus_in(self, textbox, placeholder):
        """Handle textbox focus in - clear placeholder if present"""
        current_text = textbox.get("1.0", "end-1c")
        if current_text == placeholder:
            textbox.delete("1.0", "end")
            textbox.configure(text_color=COLORS['text'])
    
    def on_textbox_focus_out(self, textbox, placeholder):
        """Handle textbox focus out - restore placeholder if empty"""
        current_text = textbox.get("1.0", "end-1c").strip()
        if not current_text:
            textbox.insert("1.0", placeholder)
            textbox.configure(text_color=COLORS['text_secondary'])
    
    def on_panos_format_change(self, choice):
        """Show/hide custom format input"""
        if choice == "Custom":
            self.panos_custom_format_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        else:
            self.panos_custom_format_frame.pack_forget()
    
    def generate_panos_names(self):
        """Generate object names from base names and IPs"""
        names_text = self.panos_gen_names.get("1.0", "end").strip()
        ips_text = self.panos_gen_ips.get("1.0", "end").strip()
        
        # Check if placeholder text is still present
        if names_text == self.panos_gen_names_placeholder or ips_text == self.panos_gen_ips_placeholder:
            messagebox.showerror("Error", "Please replace the placeholder text with your actual data")
            return
        
        if not names_text or not ips_text:
            messagebox.showerror("Error", "Please fill in both base names and IPs")
            return
        
        names = [n.strip() for n in names_text.split('\n') if n.strip()]
        ips = [i.strip() for i in ips_text.split('\n') if i.strip()]
        
        if len(names) != len(ips):
            messagebox.showerror("Error", f"Number of names ({len(names)}) doesn't match number of IPs ({len(ips)})")
            return
        
        # Get separator
        sep_map = {"_ (Underscore)": "_", "- (Dash)": "-", ". (Dot)": "."}
        separator = sep_map.get(self.panos_gen_separator.get(), "_")
        
        # Get format
        format_choice = self.panos_gen_format.get()
        
        self.panos_generated_names = []
        
        for i in range(len(names)):
            name = names[i]
            ip = ips[i]
            
            # Validate IP
            if not self.validate_panos_ip(ip):
                messagebox.showerror("Error", f"Invalid IP address or format: {ip}\nExpected format: 192.168.1.10 or 192.168.1.0/24")
                return
            
            # Generate name based on format
            # Keep dots in IPs, only replace slashes
            ip_formatted = ip.replace('/', separator)
            
            if format_choice == "Name_IP":
                generated_name = f"{name}{separator}{ip_formatted}"
            elif format_choice == "IP_Name":
                generated_name = f"{ip_formatted}{separator}{name}"
            elif format_choice == "Name Only":
                generated_name = name
            elif format_choice == "Custom":
                custom_pattern = self.panos_gen_custom.get().strip()
                if not custom_pattern:
                    messagebox.showerror("Error", "Please provide a custom format pattern")
                    return
                generated_name = custom_pattern.replace('{name}', name).replace('{ip}', ip_formatted)
            else:
                generated_name = f"{name}{separator}{ip_formatted}"
            
            self.panos_generated_names.append({
                'name': name,
                'ip': ip,
                'generated_name': generated_name
            })
        
        # Show popup with generated names
        self.show_generated_names_popup()
    
    def show_generated_names_popup(self):
        """Show popup window with generated names"""
        popup = ctk.CTkToplevel(self)
        popup.title("Generated Names")
        popup.geometry("600x500")
        
        # Title
        title_label = ctk.CTkLabel(
            popup,
            text=f"✅ Generated {len(self.panos_generated_names)} Names",
            font=ctk.CTkFont(size=FONTS['heading'], weight="bold")
        )
        title_label.pack(pady=SPACING['lg'])
        
        # Names list in textbox
        names_text = '\n'.join([item['generated_name'] for item in self.panos_generated_names])
        
        textbox = ctk.CTkTextbox(
            popup,
            font=ctk.CTkFont(size=FONTS['body'], family="Consolas"),
            wrap="none"
        )
        textbox.pack(fill="both", expand=True, padx=SPACING['lg'], pady=(0, SPACING['md']))
        textbox.insert("1.0", names_text)
        textbox.configure(state="disabled")  # Read-only
        
        # Button frame
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Copy button
        copy_btn = StyledButton(
            btn_frame,
            text="📋 Copy to Clipboard",
            command=lambda: self.copy_generated_names(names_text, popup),
            size="medium",
            variant="primary"
        )
        copy_btn.pack(side="left", fill="x", expand=True, padx=(0, SPACING['xs']))
        
        # Close button
        close_btn = StyledButton(
            btn_frame,
            text="✓ OK",
            command=popup.destroy,
            size="medium",
            variant="success"
        )
        close_btn.pack(side="left", fill="x", expand=True, padx=(SPACING['xs'], 0))
        
        # Center the popup
        popup.transient(self)
        popup.grab_set()
        popup.focus()
    
    def copy_generated_names(self, text, popup):
        """Copy generated names to clipboard"""
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "Generated names copied to clipboard!", parent=popup)
    
    def reset_panos_name_generator(self):
        """Reset all fields in the Name Generator tab"""
        # Clear and restore placeholders for textboxes
        self.panos_gen_names.delete("1.0", "end")
        self.panos_gen_names.insert("1.0", self.panos_gen_names_placeholder)
        self.panos_gen_names.configure(text_color=COLORS['text_secondary'])
        
        self.panos_gen_ips.delete("1.0", "end")
        self.panos_gen_ips.insert("1.0", self.panos_gen_ips_placeholder)
        self.panos_gen_ips.configure(text_color=COLORS['text_secondary'])
        
        # Reset dropdown selections
        self.panos_gen_separator.set("_ (Underscore)")
        self.panos_gen_format.set("Name_IP")
        
        # Clear custom format if visible
        self.panos_gen_custom.delete(0, 'end')
        self.panos_custom_format_frame.pack_forget()
        
        # Clear preview
        self.panos_preview_text.delete("1.0", "end")
        
        # Hide preview and step 2
        self.panos_preview_frame.pack_forget()
        self.panos_step2_frame.pack_forget()
        
        # Clear generated names
        self.panos_generated_names = []
        
        messagebox.showinfo("Reset Complete", "Name Generator has been reset")
    
    def generate_panos_from_names(self):
        """Generate CLI commands from generated names"""
        if not self.panos_generated_names:
            messagebox.showerror("Error", "Please generate names first")
            return
        
        is_shared = self.panos_gen_shared.get()
        base_path = "shared" if is_shared else "vsys vsys1"
        
        commands = []
        for item in self.panos_generated_names:
            cmd = f'set {base_path} address "{item["generated_name"]}" ip-netmask {item["ip"]}'
            commands.append(cmd)
        
        full_cmd = "configure\n" + '\n'.join(commands) + "\ncommit"
        self.panos_commands.append(full_cmd)
        self.render_panos_commands()
        messagebox.showinfo("Success", f"Generated {len(commands)} address object commands!")
    
    def generate_single_address(self):
        """Generate single address object command"""
        name = self.panos_single_name.get().strip()
        ip = self.panos_single_ip.get().strip()
        desc = self.panos_single_desc.get().strip()
        is_shared = self.panos_single_shared.get()
        
        if not name or not ip:
            messagebox.showerror("Error", "Please fill in Object Name and IP Address")
            return
        
        # Validate IP
        if not self.validate_panos_ip(ip):
            messagebox.showerror("Error", f"Invalid IP address or format: {ip}\nExpected format: 192.168.1.10 or 192.168.1.0/24")
            return
        
        base_path = "shared" if is_shared else "vsys vsys1"
        cmd = f'configure\nset {base_path} address "{name}" ip-netmask {ip}'
        if desc:
            cmd += f' description "{desc}"'
        cmd += '\ncommit'
        
        self.panos_commands.append(cmd)
        self.render_panos_commands()
        
        # Clear form
        self.panos_single_name.delete(0, 'end')
        self.panos_single_ip.delete(0, 'end')
        self.panos_single_desc.delete(0, 'end')
        
        messagebox.showinfo("Success", "Address object command generated!")
    
    def add_group_member(self):
        """Add member to address group"""
        member = self.panos_group_member_input.get().strip()
        if member and member not in self.panos_group_members:
            self.panos_group_members.append(member)
            self.render_group_members()
            self.panos_group_member_input.delete(0, 'end')
    
    def add_bulk_group_members(self):
        """Add multiple members from bulk paste text area"""
        bulk_text = self.panos_group_bulk_paste.get("1.0", "end-1c").strip()
        if not bulk_text:
            return
        
        # Parse lines and add each member
        lines = bulk_text.split('\n')
        added_count = 0
        for line in lines:
            member = line.strip()
            if member and member not in self.panos_group_members:
                self.panos_group_members.append(member)
                added_count += 1
        
        if added_count > 0:
            self.render_group_members()
            self.panos_group_bulk_paste.delete("1.0", "end")
            messagebox.showinfo("Success", f"Added {added_count} member(s) to the group")
    
    def remove_group_member(self, member):
        """Remove member from address group"""
        if member in self.panos_group_members:
            self.panos_group_members.remove(member)
            self.render_group_members()
    
    def render_group_members(self):
        """Render group members display"""
        # Clear existing
        for widget in self.panos_group_members_display.winfo_children():
            widget.destroy()
        
        if not self.panos_group_members:
            empty_label = ctk.CTkLabel(
                self.panos_group_members_display,
                text="No members added yet",
                text_color=COLORS['text_secondary'],
                font=ctk.CTkFont(size=FONTS['small'])
            )
            empty_label.pack(pady=SPACING['lg'])
            return
        
        # Create scrollable frame for members
        members_frame = ctk.CTkFrame(self.panos_group_members_display, fg_color="transparent")
        members_frame.pack(fill="both", expand=True, padx=SPACING['sm'], pady=SPACING['sm'])
        
        for member in self.panos_group_members:
            member_frame = ctk.CTkFrame(members_frame, fg_color=COLORS['neutral'], corner_radius=15)
            member_frame.pack(side="left", padx=(0, SPACING['xs']), pady=SPACING['xs'])
            
            member_label = ctk.CTkLabel(
                member_frame,
                text=member,
                font=ctk.CTkFont(size=FONTS['small'])
            )
            member_label.pack(side="left", padx=(SPACING['sm'], SPACING['xs']))
            
            remove_btn = ctk.CTkButton(
                member_frame,
                text="×",
                width=20,
                height=20,
                fg_color="transparent",
                hover_color=COLORS['danger'],
                command=lambda m=member: self.remove_group_member(m),
                font=ctk.CTkFont(size=14, weight="bold")
            )
            remove_btn.pack(side="right", padx=(0, SPACING['xs']))
    
    def generate_address_group(self):
        """Generate address group command"""
        if not self.panos_group_members:
            messagebox.showerror("Error", "Please add at least one member")
            return
        
        vsys = self.panos_group_vsys.get()
        name = self.panos_group_name.get().strip()
        desc = self.panos_group_desc.get().strip()
        group_type = self.panos_group_type.get().lower()
        
        if not name:
            messagebox.showerror("Error", "Please enter a group name")
            return
        
        # Set correct base path - "shared" or "vsys vsysX"
        base_path = "shared" if vsys == "shared" else f"vsys {vsys}"
        
        cmd = 'configure\n'
        for member in self.panos_group_members:
            cmd += f'set {base_path} address-group "{name}" {group_type} "{member}"\n'
        
        if desc:
            cmd += f'set {base_path} address-group "{name}" description "{desc}"\n'
        
        cmd += 'commit'
        
        self.panos_commands.append(cmd)
        self.render_panos_commands()
        
        # Clear form
        self.panos_group_name.delete(0, 'end')
        self.panos_group_desc.delete(0, 'end')
        self.panos_group_members = []
        self.render_group_members()
        
        messagebox.showinfo("Success", "Address group command generated!")
    
    def generate_nat_rule(self):
        """Generate NAT rule command"""
        nat_type = self.panos_nat_type_var.get()
        vsys = self.panos_nat_vsys.get()
        name = self.panos_nat_name.get().strip()
        from_zone = self.panos_nat_from.get().strip()
        to_zone = self.panos_nat_to.get().strip()
        source = self.panos_nat_source.get().strip()
        dest = self.panos_nat_dest.get().strip()
        service = self.panos_nat_service.get().strip()
        translated = self.panos_nat_translated.get().strip()
        port = self.panos_nat_port.get().strip()
        desc = self.panos_nat_desc.get().strip()
        
        if not all([name, from_zone, to_zone, dest, translated]):
            messagebox.showerror("Error", "Please fill in all required fields (marked with *)")
            return
        
        # Set correct base path - "shared" or "vsys vsysX"
        base_path = "shared" if vsys == "shared" else f"vsys {vsys}"
        base = f'set {base_path} rulebase nat rules "{name}"'
        cmd = 'configure\n'
        cmd += f'{base} from "{from_zone}"\n'
        cmd += f'{base} to "{to_zone}"\n'
        cmd += f'{base} source "{source}"\n'
        cmd += f'{base} destination "{dest}"\n'
        cmd += f'{base} service "{service}"\n'
        
        if nat_type == "dnat":
            cmd += f'{base} destination-translation translated-address "{translated}"'
            if port:
                cmd += f' translated-port {port}'
            cmd += '\n'
        else:
            cmd += f'{base} source-translation dynamic-ip-and-port translated-address "{translated}"\n'
        
        if desc:
            cmd += f'{base} description "{desc}"\n'
        
        cmd += 'commit'
        
        self.panos_commands.append(cmd)
        self.render_panos_commands()
        
        # Clear form
        self.panos_nat_name.delete(0, 'end')
        self.panos_nat_from.delete(0, 'end')
        self.panos_nat_to.delete(0, 'end')
        self.panos_nat_dest.delete(0, 'end')
        self.panos_nat_translated.delete(0, 'end')
        self.panos_nat_port.delete(0, 'end')
        self.panos_nat_desc.delete(0, 'end')
        
        messagebox.showinfo("Success", "NAT rule command generated!")
    
    def generate_policy_rule(self):
        """Generate security policy rule command"""
        vsys = self.panos_policy_vsys.get()
        name = self.panos_policy_name.get().strip()
        from_zone = self.panos_policy_from.get().strip()
        to_zone = self.panos_policy_to.get().strip()
        source = self.panos_policy_source.get().strip()
        dest = self.panos_policy_dest.get().strip()
        app = self.panos_policy_app.get().strip()
        service = self.panos_policy_service.get().strip()
        action = self.panos_policy_action.get()
        profile = self.panos_policy_profile.get().strip()
        desc = self.panos_policy_desc.get().strip()
        
        if not all([name, from_zone, to_zone]):
            messagebox.showerror("Error", "Please fill in all required fields (marked with *)")
            return
        
        # Set correct base path - "shared" or "vsys vsysX"
        base_path = "shared" if vsys == "shared" else f"vsys {vsys}"
        base = f'set {base_path} rulebase security rules "{name}"'
        cmd = 'configure\n'
        cmd += f'{base} from "{from_zone}"\n'
        cmd += f'{base} to "{to_zone}"\n'
        cmd += f'{base} source "{source}"\n'
        cmd += f'{base} destination "{dest}"\n'
        cmd += f'{base} application "{app}"\n'
        cmd += f'{base} service "{service}"\n'
        cmd += f'{base} action {action}\n'
        
        if profile:
            cmd += f'{base} profile-setting group "{profile}"\n'
        
        if desc:
            cmd += f'{base} description "{desc}"\n'
        
        cmd += 'commit'
        
        self.panos_commands.append(cmd)
        self.render_panos_commands()
        
        # Clear form
        self.panos_policy_name.delete(0, 'end')
        self.panos_policy_from.delete(0, 'end')
        self.panos_policy_to.delete(0, 'end')
        self.panos_policy_profile.delete(0, 'end')
        self.panos_policy_desc.delete(0, 'end')
        
        messagebox.showinfo("Success", "Security policy rule command generated!")
    
    def generate_panos_address_objects(self):
        """Generate address object commands"""
        names_text = self.panos_addr_names.get("1.0", "end").strip()
        ips_text = self.panos_addr_ips.get("1.0", "end").strip()
        
        if not names_text or not ips_text:
            messagebox.showerror("Error", "Please fill in both names and IPs")
            return
        
        names = [n.strip() for n in names_text.split('\n') if n.strip()]
        ips = [i.strip() for i in ips_text.split('\n') if i.strip()]
        
        if len(names) != len(ips):
            messagebox.showerror("Error", f"Number of names ({len(names)}) doesn't match number of IPs ({len(ips)})")
            return
        
        is_shared = self.panos_addr_shared.get()
        base_path = "shared" if is_shared else "vsys vsys1"
        
        commands = []
        for i in range(len(names)):
            name = names[i]
            ip = ips[i]
            
            # Validate IP
            if not self.validate_panos_ip(ip):
                messagebox.showerror("Error", f"Invalid IP address or format: {ip}\nExpected format: 192.168.1.10 or 192.168.1.0/24")
                return
            
            cmd = f'set {base_path} address "{name}" ip-netmask {ip}'
            commands.append(cmd)
        
        full_cmd = "configure\n" + '\n'.join(commands) + "\ncommit"
        self.panos_commands.append(full_cmd)
        self.render_panos_commands()
        messagebox.showinfo("Success", f"Generated {len(commands)} address object commands!")
    
    def generate_schedule_object(self):
        """Generate schedule object command"""
        name = self.panos_schedule_name.get().strip()
        schedule_type = self.panos_schedule_type.get()
        start_time = self.panos_schedule_start.get().strip()
        end_time = self.panos_schedule_end.get().strip()
        
        if not all([name, start_time, end_time]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        # Build command
        cmd = 'configure\n'
        cmd += f'set schedule "{name}" schedule-type {schedule_type}\n'
        
        if schedule_type == "recurring":
            # Get selected days
            selected_days = [day for day, var in self.panos_schedule_days.items() if var.get()]
            if selected_days:
                days_str = " ".join(selected_days)
                cmd += f'set schedule "{name}" recurring daily {days_str} {start_time}-{end_time}\n'
        else:
            # Non-recurring would need date range (simplified here)
            cmd += f'set schedule "{name}" non-recurring {start_time}-{end_time}\n'
        
        cmd += 'commit'
        
        self.panos_commands.append(cmd)
        self.render_panos_commands()
        messagebox.showinfo("Success", "Schedule object command generated!")
    
    def generate_appfilter(self):
        """Generate application filter command"""
        name = self.panos_appfilter_name.get().strip()
        category = self.panos_appfilter_category.get()
        subcategory = self.panos_appfilter_subcategory.get().strip()
        technology = self.panos_appfilter_technology.get()
        
        if not name:
            messagebox.showerror("Error", "Please enter a filter name")
            return
        
        # Build command
        cmd = 'configure\n'
        cmd += f'set profiles custom-url-category "{name}" type "URL List"\n'
        
        # Add category filter
        cmd += f'set application-filter "{name}" category {category}\n'
        
        if subcategory:
            cmd += f'set application-filter "{name}" subcategory {subcategory}\n'
        
        cmd += f'set application-filter "{name}" technology {technology}\n'
        
        # Add risk levels
        selected_risks = [str(level) for level, var in self.panos_appfilter_risk.items() if var.get()]
        if selected_risks:
            for risk in selected_risks:
                cmd += f'set application-filter "{name}" risk {risk}\n'
        
        cmd += 'commit'
        
        self.panos_commands.append(cmd)
        self.render_panos_commands()
        messagebox.showinfo("Success", "Application filter command generated!")
    
    def generate_urlcat(self):
        """Generate custom URL category command"""
        name = self.panos_urlcat_name.get().strip()
        desc = self.panos_urlcat_desc.get().strip()
        urls_text = self.panos_urlcat_urls.get("1.0", "end-1c").strip()
        url_type = self.panos_urlcat_type.get()
        
        # Check if placeholder
        if urls_text == "example.com\n*.example.com\nexample.org/path":
            messagebox.showerror("Error", "Please replace placeholder text with actual URLs")
            return
        
        if not name or not urls_text:
            messagebox.showerror("Error", "Please fill in name and URLs")
            return
        
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        if not urls:
            messagebox.showerror("Error", "Please enter at least one URL")
            return
        
        # Build command
        cmd = 'configure\n'
        cmd += f'set profiles custom-url-category "{name}" type "{url_type}"\n'
        
        if desc:
            cmd += f'set profiles custom-url-category "{name}" description "{desc}"\n'
        
        # Add URLs
        for url in urls:
            cmd += f'set profiles custom-url-category "{name}" list {url}\n'
        
        cmd += 'commit'
        
        self.panos_commands.append(cmd)
        self.render_panos_commands()
        messagebox.showinfo("Success", f"URL category command generated with {len(urls)} URLs!")
    
    def generate_service_object(self):
        """Generate service object command"""
        name = self.panos_service_name.get().strip()
        port = self.panos_service_port.get().strip()
        protocol = self.panos_service_protocol.get()
        desc = self.panos_service_desc.get().strip()
        create_both = self.panos_service_both.get()
        
        if not name or not port:
            messagebox.showerror("Error", "Please enter service name and port")
            return
        
        commands = []
        
        if create_both:
            # Create TCP service
            tcp_name = f"TCP-{name}"
            cmd_tcp = 'configure\n'
            cmd_tcp += f'set service "{tcp_name}" protocol tcp port {port}\n'
            if desc:
                cmd_tcp += f'set service "{tcp_name}" description "{desc} (TCP)"\n'
            cmd_tcp += 'commit'
            commands.append(cmd_tcp)
            
            # Create UDP service
            udp_name = f"UDP-{name}"
            cmd_udp = 'configure\n'
            cmd_udp += f'set service "{udp_name}" protocol udp port {port}\n'
            if desc:
                cmd_udp += f'set service "{udp_name}" description "{desc} (UDP)"\n'
            cmd_udp += 'commit'
            commands.append(cmd_udp)
            
            self.panos_commands.extend(commands)
            self.render_panos_commands()
            messagebox.showinfo("Success", f"Generated 2 service commands (TCP and UDP)!")
        else:
            # Create single service
            cmd = 'configure\n'
            cmd += f'set service "{name}" protocol {protocol} port {port}\n'
            if desc:
                cmd += f'set service "{name}" description "{desc}"\n'
            cmd += 'commit'
            
            self.panos_commands.append(cmd)
            self.render_panos_commands()
            messagebox.showinfo("Success", "Service object command generated!")
    
    def add_service_group_member(self):
        """Add member to service group"""
        member = self.panos_service_group_member.get().strip()
        if member and member not in self.panos_service_group_members:
            self.panos_service_group_members.append(member)
            self.render_service_group_members()
            self.panos_service_group_member.delete(0, 'end')
    
    def add_bulk_service_members(self):
        """Add multiple service members from bulk paste"""
        bulk_text = self.panos_service_group_bulk.get("1.0", "end-1c").strip()
        if not bulk_text:
            return
        
        lines = bulk_text.split('\n')
        added_count = 0
        for line in lines:
            member = line.strip()
            if member and member not in self.panos_service_group_members:
                self.panos_service_group_members.append(member)
                added_count += 1
        
        if added_count > 0:
            self.render_service_group_members()
            self.panos_service_group_bulk.delete("1.0", "end")
            messagebox.showinfo("Success", f"Added {added_count} service(s) to the group")
    
    def render_service_group_members(self):
        """Render service group members"""
        for widget in self.panos_service_group_display.winfo_children():
            widget.destroy()
        
        if not self.panos_service_group_members:
            empty_label = ctk.CTkLabel(
                self.panos_service_group_display,
                text="No members added yet",
                text_color=COLORS['text_secondary']
            )
            empty_label.pack(pady=SPACING['md'])
            return
        
        for member in self.panos_service_group_members:
            member_frame = ctk.CTkFrame(self.panos_service_group_display, fg_color="transparent")
            member_frame.pack(fill="x", padx=SPACING['sm'], pady=SPACING['xs'])
            
            member_label = ctk.CTkLabel(
                member_frame,
                text=member,
                font=ctk.CTkFont(size=FONTS['body'])
            )
            member_label.pack(side="left", fill="x", expand=True)
            
            remove_btn = ctk.CTkButton(
                member_frame,
                text="✕",
                command=lambda m=member: self.remove_service_group_member(m),
                width=30,
                height=25,
                fg_color="transparent",
                hover_color=COLORS['danger'],
                text_color=COLORS['danger']
            )
            remove_btn.pack(side="right")
    
    def remove_service_group_member(self, member):
        """Remove member from service group"""
        if member in self.panos_service_group_members:
            self.panos_service_group_members.remove(member)
            self.render_service_group_members()
    
    def generate_service_group(self):
        """Generate service group command"""
        name = self.panos_service_group_name.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter group name")
            return
        
        if not self.panos_service_group_members:
            messagebox.showerror("Error", "Please add at least one service member")
            return
        
        cmd = 'configure\n'
        for member in self.panos_service_group_members:
            cmd += f'set service-group "{name}" members {member}\n'
        cmd += 'commit'
        
        self.panos_commands.append(cmd)
        self.render_panos_commands()
        messagebox.showinfo("Success", f"Service group command generated with {len(self.panos_service_group_members)} members!")
    
    def render_panos_commands(self):
        """Render commands in output panel"""
        # Clear existing
        for widget in self.panos_commands_list.winfo_children():
            widget.destroy()
        
        # Update count
        self.panos_cmd_count.configure(text=f"{len(self.panos_commands)} command{'s' if len(self.panos_commands) != 1 else ''} generated")
        
        if len(self.panos_commands) == 0:
            empty_state = ctk.CTkFrame(self.panos_commands_list, fg_color="transparent")
            empty_state.pack(fill="both", expand=True, pady=SPACING['xl'])
            
            empty_text = ctk.CTkLabel(
                empty_state,
                text="📋\n\nNo commands generated yet\n\nFill out the form to generate CLI commands",
                font=ctk.CTkFont(size=FONTS['body']),
                text_color=COLORS['text_secondary']
            )
            empty_text.pack(expand=True)
            self.panos_action_frame.pack_forget()
            return
        
        self.panos_action_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        for i, cmd in enumerate(self.panos_commands):
            cmd_frame = ctk.CTkFrame(self.panos_commands_list, fg_color=COLORS['bg_card'])
            cmd_frame.pack(fill="x", pady=(0, SPACING['xs']))
            
            cmd_text = ctk.CTkTextbox(
                cmd_frame,
                height=100,
                font=ctk.CTkFont(size=FONTS['small'], family="Consolas"),
                wrap="none"
            )
            cmd_text.pack(fill="both", expand=True, padx=SPACING['sm'], pady=SPACING['sm'])
            cmd_text.insert("1.0", cmd)
            cmd_text.configure(state="disabled")
            
            # Remove button
            remove_btn = StyledButton(
                cmd_frame,
                text="✗",
                command=lambda idx=i: self.remove_panos_command(idx),
                size="small",
                variant="danger"
            )
            remove_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-SPACING['sm'], y=SPACING['sm'])
    
    def remove_panos_command(self, index):
        """Remove a command"""
        if 0 <= index < len(self.panos_commands):
            self.panos_commands.pop(index)
            self.render_panos_commands()
    
    def clear_panos_commands(self):
        """Clear all commands"""
        if self.panos_commands and messagebox.askyesno("Clear Commands", "Clear all generated commands?"):
            self.panos_commands = []
            self.render_panos_commands()
    
    def copy_panos_commands(self):
        """Copy all commands to clipboard"""
        if not self.panos_commands:
            return
        
        text = '\n\n'.join(self.panos_commands)
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Success", "Commands copied to clipboard!")
    
    def download_panos_commands(self):
        """Download commands to file"""
        if not self.panos_commands:
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"panos-commands.txt"
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write('\n\n'.join(self.panos_commands))
                messagebox.showinfo("Success", f"Commands saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
    
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
                "Please enter an IPv4 address, hostname, or CIDR format."
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
            # Not a valid IP/CIDR, try as hostname
            resolved_ip = self.scanner.resolve_hostname_to_ip(cidr)
            if resolved_ip:
                # Replace the input with resolved IP and show message
                messagebox.showinfo(
                    "Hostname Resolved",
                    f"Hostname '{cidr}' resolved to {resolved_ip}"
                )
                cidr = resolved_ip  # Use resolved IP for scanning
            else:
                messagebox.showerror(
                    "Invalid Input",
                    f"Could not resolve '{cidr}' as hostname or parse as IP/CIDR."
                )
                return
        
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
    
    def import_ip_list(self):
        """Import and scan IP list from text or file"""
        # Create dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Import IP List")
        dialog.geometry("600x500")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Content frame
        content = ctk.CTkFrame(dialog)
        content.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Title
        title = ctk.CTkLabel(
            content,
            text="Import IP Address List",
            font=ctk.CTkFont(size=FONTS['heading'], weight="bold")
        )
        title.pack(pady=(0, SPACING['md']))
        
        # Instructions
        instructions = ctk.CTkLabel(
            content,
            text="Enter one per line or load from file\nSupports: IP addresses, CIDR notation, hostnames/FQDNs, comments (#)",
            font=ctk.CTkFont(size=FONTS['small']),
            text_color=COLORS['text_secondary']
        )
        instructions.pack(pady=(0, SPACING['md']))
        
        # Text area
        text_frame = ctk.CTkFrame(content)
        text_frame.pack(fill="both", expand=True, pady=(0, SPACING['md']))
        
        ip_textbox = ctk.CTkTextbox(
            text_frame,
            font=ctk.CTkFont(size=FONTS['body'], family="Consolas"),
            wrap="none"
        )
        ip_textbox.pack(fill="both", expand=True)
        
        # Placeholder text
        placeholder = """# Example IP list (supports IPs, CIDR, and hostnames):
192.168.1.1
server1.domain.com
192.168.1.10
10.0.0.0/24
workstation.local
gateway.home.lan
172.16.5.100
# This is a comment"""
        ip_textbox.insert("1.0", placeholder)
        
        # Button frame - organized in rows for better visibility
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(SPACING['md'], 0))
        
        # Top row: Load from file
        top_button_row = ctk.CTkFrame(button_frame, fg_color="transparent")
        top_button_row.pack(fill="x", pady=(0, SPACING['xs']))
        
        # Load from file button
        def load_file():
            filepath = filedialog.askopenfilename(
                title="Select IP List File",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )
            if filepath:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    ip_textbox.delete("1.0", "end")
                    ip_textbox.insert("1.0", content)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load file: {e}")
        
        load_btn = StyledButton(
            top_button_row,
            text="📁 Load from File",
            command=load_file,
            size="medium",
            variant="neutral"
        )
        load_btn.pack(side="left", fill="x", expand=True, padx=(0, SPACING['xs']))
        
        # Bottom row: action buttons
        bottom_button_row = ctk.CTkFrame(button_frame, fg_color="transparent")
        bottom_button_row.pack(fill="x")
        
        # Preview/Validate button
        def preview_list():
            ip_text = ip_textbox.get("1.0", "end")
            
            if not ip_text.strip() or ip_text.strip() == placeholder.strip():
                messagebox.showwarning("Warning", "Please enter IP addresses or load a file")
                return
            
            # Show processing message
            scan_btn.configure(text="⏳ Resolving...", state="disabled")
            preview_btn.configure(state="disabled")
            dialog.update()
            
            # Parse IPs (with hostname resolution)
            ip_list, resolved_info = self.scanner.parse_ip_list(ip_text, resolve_hostnames=True)
            
            # Show resolution results
            result_text = "Resolution Results:\n" + "="*50 + "\n\n"
            success_count = 0
            fail_count = 0
            
            for original, resolved, success in resolved_info:
                if success:
                    if original == resolved:
                        result_text += f"✓ {original}\n"
                    else:
                        result_text += f"✓ {original} → {resolved}\n"
                    success_count += 1
                else:
                    result_text += f"✗ {original} - {resolved}\n"
                    fail_count += 1
            
            result_text += "\n" + "="*50 + "\n"
            result_text += f"Total: {success_count} resolved, {fail_count} failed\n"
            result_text += f"Ready to scan {len(ip_list)} IP addresses"
            
            # Show results dialog
            result_dialog = ctk.CTkToplevel(dialog)
            result_dialog.title("Resolution Results")
            result_dialog.geometry("600x400")
            result_dialog.transient(dialog)
            
            result_frame = ctk.CTkFrame(result_dialog)
            result_frame.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
            
            result_display = ctk.CTkTextbox(
                result_frame,
                font=ctk.CTkFont(size=FONTS['small'], family="Consolas"),
                wrap="none"
            )
            result_display.pack(fill="both", expand=True)
            result_display.insert("1.0", result_text)
            result_display.configure(state="disabled")
            
            btn_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
            btn_frame.pack(fill="x", pady=(SPACING['md'], 0))
            
            def proceed_scan():
                result_dialog.destroy()
                if ip_list:
                    dialog.destroy()
                    
                    # Clear previous results
                    self.result_rows = []
                    self.all_results = []
                    self.current_page = 1
                    for widget in self.results_scrollable.winfo_children():
                        widget.destroy()
                    
                    # Pre-populate table with all IPs before scanning
                    for ip_addr in ip_list:
                        placeholder_result = {
                            'ip': ip_addr,
                            'hostname': '...',
                            'status': 'Pending',
                            'rtt': '---',
                            'responding': False
                        }
                        self.add_result_row(placeholder_result)
                    
                    # Update UI
                    self.start_scan_btn.configure(state="disabled")
                    self.import_list_btn.configure(state="disabled")
                    self.cancel_scan_btn.configure(state="normal")
                    self.export_btn.configure(state="disabled")
                    self.compare_btn.configure(state="disabled")
                    self.progress_bar.set(0)
                    self.status_label.configure(text=f"Scanning {len(ip_list)} imported addresses...")
                    self.cidr_entry.delete(0, 'end')
                    self.cidr_entry.insert(0, f"IP List ({len(ip_list)} addresses)")
                    
                    # Store IP list and create mapping for updates
                    self.current_scan_list = ip_list
                    self.ip_to_row_index = {ip: idx for idx, ip in enumerate(ip_list)}
                    
                    # Set scanner callbacks (CRITICAL!)
                    self.scanner.progress_callback = self.on_scan_progress
                    self.scanner.complete_callback = self.on_scan_complete
                    
                    # Start scan in background
                    aggression = self.aggro_selector.get()  # Use the correct selector
                    
                    threading.Thread(
                        target=self.scanner.scan_ip_list,
                        args=(ip_list, aggression),
                        daemon=True
                    ).start()
                else:
                    messagebox.showwarning("Warning", "No valid IP addresses to scan")
            
            StyledButton(
                btn_frame,
                text="✗ Cancel",
                command=result_dialog.destroy,
                size="medium",
                variant="neutral"
            ).pack(side="left")
            
            if ip_list:
                StyledButton(
                    btn_frame,
                    text=f"▶ Scan {len(ip_list)} IPs",
                    command=proceed_scan,
                    size="large",
                    variant="primary"
                ).pack(side="right")
            
            # Re-enable buttons
            scan_btn.configure(text="▶ Scan IP List", state="normal")
            preview_btn.configure(state="normal")
        
        # Define buttons first (referenced in preview_list)
        preview_btn = None
        scan_btn = None
        
        # Cancel button
        cancel_btn = StyledButton(
            bottom_button_row,
            text="✗ Cancel",
            command=dialog.destroy,
            size="medium",
            variant="neutral"
        )
        cancel_btn.pack(side="left", fill="x", expand=True, padx=(0, SPACING['xs']))
        
        # Preview button
        preview_btn = StyledButton(
            bottom_button_row,
            text="🔍 Preview & Resolve",
            command=preview_list,
            size="medium",
            variant="neutral"
        )
        preview_btn.pack(side="left", fill="x", expand=True, padx=(0, SPACING['xs']))
        
        # Scan button
        scan_btn = StyledButton(
            bottom_button_row,
            text="▶ Scan IP List",
            command=preview_list,
            size="large",
            variant="primary"
        )
        scan_btn.pack(side="left", fill="x", expand=True)
    
    def on_scan_progress(self, completed, total, result):
        """Handle scan progress update with batching for performance"""
        # Add to buffer
        self.update_buffer.append((completed, total, result))
        
        # Update immediately if buffer is full OR it's the last result
        if len(self.update_buffer) >= self.UPDATE_BATCH_SIZE or completed == total:
            self._flush_update_buffer()
        else:
            # Schedule delayed flush if not already scheduled
            if self.update_timer is None:
                self.update_timer = self.after(self.UPDATE_INTERVAL_MS, self._flush_update_buffer)
    
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
    
    def _update_scan_progress(self, completed, total, result):
        """Update scan progress in main thread"""
        # Update progress bar
        progress = completed / total if total > 0 else 0
        self.progress_bar.set(progress)
        
        # Show current IP being scanned if available
        current_ip = result['ip'] if result else "..."
        status_text = f"Scanning {current_ip}... ({completed} / {total})"
        
        # Add result to all_results list
        self.all_results.append(result)
        
        # Check if this is from an imported list
        if hasattr(self, 'current_scan_list') and self.current_scan_list and hasattr(self, 'ip_to_row_index'):
            status_text = f"Scanning imported addresses: {current_ip} ({completed}/{total})"
            self.status_label.configure(text=status_text)
            
            # Update existing row instead of adding new one
            ip_addr = result.get('ip', '').strip()
            if ip_addr in self.ip_to_row_index:
                row_index = self.ip_to_row_index[ip_addr]
                if row_index < len(self.result_rows):
                    self.update_result_row(row_index, result)
                    # Update pagination UI
                    self.update_pagination_ui()
                    return  # Don't add a new row
            else:
                # IP not in mapping - this shouldn't happen, but handle it
                print(f"Warning: IP {ip_addr} not found in mapping. Available IPs: {list(self.ip_to_row_index.keys())[:5]}")
        else:
            self.status_label.configure(text=status_text)
        
        # Only add row if on current page and within page limit
        current_page_start = (self.current_page - 1) * self.results_per_page
        current_page_end = self.current_page * self.results_per_page
        result_index = len(self.all_results) - 1
        
        if current_page_start <= result_index < current_page_end:
            # Add result row (for regular scans or if IP not found in mapping)
            self.add_result_row(result)
        
        # Update pagination UI
        self.update_pagination_ui()
    
    def on_scan_complete(self, results, message):
        """Handle scan completion"""
        self.after(0, self._finalize_scan, results, message)
    
    def _finalize_scan(self, results, message):
        """Finalize scan in main thread"""
        self.start_scan_btn.configure(state="normal")
        self.cancel_scan_btn.configure(state="disabled")
        
        # Clear imported list flags
        if hasattr(self, 'current_scan_list'):
            self.current_scan_list = None
        if hasattr(self, 'ip_to_row_index'):
            self.ip_to_row_index = None
        
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
            width=180,
            anchor="w",
            font=ctk.CTkFont(size=FONTS['body'])
        )
        ip_label.pack(side="left", padx=SPACING['sm'])
        
        # Hostname/FQDN column (NEW)
        hostname = result.get('hostname', '')
        hostname_label = ctk.CTkLabel(
            row_frame,
            text=hostname if hostname else "-",
            width=250,
            anchor="w",
            font=ctk.CTkFont(size=FONTS['small']),
            text_color=COLORS["text_secondary"] if hostname else ("gray70", "gray40")
        )
        hostname_label.pack(side="left", padx=SPACING['sm'])
        
        # Status with color and bold font
        status_label = ctk.CTkLabel(
            row_frame,
            text=result['status'],
            width=150,
            anchor="w",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold"),
            text_color=status_color
        )
        status_label.pack(side="left", padx=SPACING['sm'])
        
        # RTT with subtle color
        rtt_text = result.get('rtt', result.get('response_time', '---'))
        rtt_label = ctk.CTkLabel(
            row_frame,
            text=rtt_text,
            width=100,
            anchor="w",
            font=ctk.CTkFont(size=FONTS['small']),
            text_color=COLORS["text_secondary"]
        )
        rtt_label.pack(side="left", padx=SPACING['sm'])
        
        # Store reference
        row_frame.result_data = result
        # Store references to labels for updating
        row_frame.dot_label = dot_label
        row_frame.ip_label = ip_label
        row_frame.hostname_label = hostname_label
        row_frame.status_label = status_label
        row_frame.rtt_label = rtt_label
        self.result_rows.append(row_frame)
    
    def update_result_row(self, row_index, result):
        """Update an existing result row with new data"""
        if row_index >= len(self.result_rows):
            return
        
        row_frame = self.result_rows[row_index]
        
        # Update status dot color
        status_color = COLORS["online"] if result['status'] == 'Online' else COLORS["offline"]
        row_frame.dot_label.configure(text_color=status_color)
        
        # Update IP (shouldn't change but for consistency)
        row_frame.ip_label.configure(text=result['ip'])
        
        # Update hostname
        hostname = result.get('hostname', '')
        row_frame.hostname_label.configure(
            text=hostname if hostname else "-",
            text_color=COLORS["text_secondary"] if hostname else ("gray70", "gray40")
        )
        
        # Update status
        row_frame.status_label.configure(
            text=result['status'],
            text_color=status_color
        )
        
        # Update RTT
        rtt_text = result.get('rtt', '---')
        row_frame.rtt_label.configure(text=rtt_text)
        
        # Update stored data
        row_frame.result_data = result
    
    def go_to_page(self, page_num):
        """Go to specific page"""
        if page_num < 1 or page_num > self.total_pages:
            return
        
        self.current_page = page_num
        self.render_current_page()
    
    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.go_to_page(self.current_page + 1)
    
    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.go_to_page(self.current_page - 1)
    
    def render_current_page(self):
        """Render results for current page"""
        # Clear existing rows
        for widget in self.results_scrollable.winfo_children():
            widget.destroy()
        self.result_rows.clear()
        
        # Calculate slice
        start_idx = (self.current_page - 1) * self.results_per_page
        end_idx = start_idx + self.results_per_page
        page_results = self.all_results[start_idx:end_idx]
        
        # Render page results
        for result in page_results:
            self.add_result_row(result)
        
        # Update pagination UI
        self.update_pagination_ui()
    
    def update_pagination_ui(self):
        """Update pagination controls"""
        total_results = len(self.all_results)
        self.total_pages = max(1, (total_results + self.results_per_page - 1) // self.results_per_page)
        
        # Update labels
        start_idx = (self.current_page - 1) * self.results_per_page + 1
        end_idx = min(self.current_page * self.results_per_page, total_results)
        
        if total_results == 0:
            self.pagination_label.configure(text="No results")
            self.page_indicator.configure(text="Page 0 of 0")
        else:
            self.pagination_label.configure(text=f"Showing {start_idx}-{end_idx} of {total_results} results")
            self.page_indicator.configure(text=f"Page {self.current_page} of {self.total_pages}")
        
        # Enable/disable buttons
        self.first_page_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.prev_page_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.next_page_btn.configure(state="normal" if self.current_page < self.total_pages else "disabled")
        self.last_page_btn.configure(state="normal" if self.current_page < self.total_pages else "disabled")
    
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
        """Export scanner results in multiple formats with options"""
        if not self.all_results:
            messagebox.showinfo("Information", "No data to export.")
            return
        
        # Show export options dialog
        self.show_export_dialog()
    
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
            ("xlsx", "Excel - Microsoft Excel (requires openpyxl)"),
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
            "xlsx": ".xlsx",
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
            elif format_type == "xlsx":
                self._export_as_excel(filepath, results_to_export)
            elif format_type == "html":
                self._export_as_html(filepath, results_to_export)
            elif format_type == "txt":
                self._export_as_txt(filepath, results_to_export)
            elif format_type == "xml":
                self._export_as_xml(filepath, results_to_export)
            
            messagebox.showinfo(
                "Export Successful",
                f"{len(results_to_export)} results exported to:\n{filepath}"
            )
        except Exception as e:
            messagebox.showerror(
                "Export Error",
                f"Error exporting scan results: {str(e)}"
            )
    
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
    
    def _export_as_excel(self, filepath, results):
        """Export results as Excel (requires openpyxl)"""
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment
            
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Scan Results"
            
            # Header
            headers = ['IP Address', 'Hostname', 'Status', 'Response Time']
            ws.append(headers)
            
            # Style header
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")
            
            # Data
            for result in results:
                ws.append([
                    result.get('ip', ''),
                    result.get('hostname', ''),
                    result.get('status', ''),
                    result.get('rtt', '')
                ])
            
            # Auto-adjust column widths
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                ws.column_dimensions[column_letter].width = max_length + 2
            
            wb.save(filepath)
        except ImportError:
            messagebox.showerror(
                "Module Not Found",
                "Excel export requires 'openpyxl' module.\n\nInstall with: pip install openpyxl"
            )
    
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
    
    def _export_scan_csv(self, filepath):
        """Export IP scan to CSV format"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['ip', 'hostname', 'status', 'rtt'])
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
            ET.SubElement(host, 'hostname').text = result.get('hostname', '')
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
            
            f.write(f"{'IP Address':<18} {'Hostname':<40} {'Status':<10} {'RTT (ms)':<15}\n")
            f.write(f"{'-' * 18} {'-' * 40} {'-' * 10} {'-' * 15}\n")
            
            for result in self.scanner.results:
                rtt_str = str(result.get('rtt', 'N/A'))
                hostname_str = result.get('hostname', '-')
                f.write(f"{result['ip']:<18} {hostname_str:<40} {result['status']:<10} {rtt_str:<15}\n")
    
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
        
        # Input Section with styled card
        input_frame = StyledCard(scrollable)
        input_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        # Target input
        target_label = ctk.CTkLabel(
            input_frame,
            text="Target Host or IP:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        target_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        target_entry_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        target_entry_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        self.traceroute_target_entry = StyledEntry(
            target_entry_frame,
            placeholder_text="e.g., google.com or 8.8.8.8"
        )
        self.traceroute_target_entry.pack(side="left", fill="x", expand=True, padx=(0, SPACING['md']))
        
        # Tool Selection with styled card
        tool_frame = StyledCard(scrollable)
        tool_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
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
        
        # Options with styled card
        options_frame = StyledCard(scrollable)
        options_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        options_label = ctk.CTkLabel(
            options_frame,
            text="Options:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        options_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['md']))
        
        # Max hops option
        hops_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        hops_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        hops_label = ctk.CTkLabel(
            hops_frame,
            text="Max Hops:",
            font=ctk.CTkFont(size=FONTS['small'])
        )
        hops_label.pack(side="left")
        
        self.traceroute_maxhops_entry = StyledEntry(
            hops_frame,
            width=80,
            placeholder_text="30"
        )
        self.traceroute_maxhops_entry.insert(0, "30")
        self.traceroute_maxhops_entry.pack(side="left", padx=(SPACING['md'], 0))
        
        hops_info = ctk.CTkLabel(
            hops_frame,
            text="(Default: 30, Range: 1-255)",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        )
        hops_info.pack(side="left", padx=(10, 0))
        
        # Action Buttons
        button_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        self.trace_start_btn = StyledButton(
            button_frame,
            text="▶ Start Trace",
            command=self.start_traceroute,
            size="medium",
            variant="primary"
        )
        self.trace_start_btn.pack(side="left", padx=(0, SPACING['md']))
        
        self.trace_cancel_btn = StyledButton(
            button_frame,
            text="⏹ Cancel",
            command=self.cancel_traceroute,
            size="medium",
            variant="danger",
            state="disabled"
        )
        self.trace_cancel_btn.pack(side="left", padx=(0, SPACING['md']))
        
        self.trace_export_btn = StyledButton(
            button_frame,
            text="📤 Export Results",
            command=self.export_traceroute,
            size="medium",
            variant="success",
            state="disabled"
        )
        self.trace_export_btn.pack(side="left")
        
        # Progress label
        self.trace_progress_label = SubTitle(
            scrollable,
            text=""
        )
        self.trace_progress_label.pack(pady=(0, SPACING['md']))
        
        # Results Section
        results_title = SectionTitle(
            scrollable,
            text="Results"
        )
        results_title.pack(pady=(SPACING['md'], SPACING['md']), anchor="w")
        
        self.traceroute_results_frame = StyledCard(scrollable)
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
        
        # Run in background thread using Traceroute module
        def trace_thread():
            tool = self.trace_tool_var.get()
            result = Traceroute.run(target, max_hops, tool, timeout=600)
            
            # Store results
            self.trace_results_text = result["output"]
            
            # Update UI in main thread
            self.after(0, self.display_traceroute_results, result["output"], result["success"])
        
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
        
        subtitle_label = SubTitle(
            scrollable,
            text="Manage IP addresses with phpIPAM API"
        )
        subtitle_label.pack(pady=(0, SPACING['lg']))
        
        # Status Section with styled card
        status_frame = StyledCard(scrollable)
        status_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        status_title = ctk.CTkLabel(
            status_frame,
            text="Connection Status",
            font=ctk.CTkFont(size=FONTS['subheading'], weight="bold")
        )
        status_title.pack(pady=(SPACING['lg'], SPACING['xs']), padx=SPACING['lg'], anchor="w")
        
        self.phpipam_status_label = ctk.CTkLabel(
            status_frame,
            text="⚪ Not configured" if not self.phpipam_config.is_enabled() else "🟢 Enabled",
            font=ctk.CTkFont(size=FONTS['body'])
        )
        self.phpipam_status_label.pack(pady=(0, SPACING['lg']), padx=SPACING['lg'], anchor="w")
        
        # Action buttons
        button_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        settings_btn = StyledButton(
            button_frame,
            text="⚙️ Settings",
            command=self.show_phpipam_settings,
            size="medium",
            variant="neutral"
        )
        settings_btn.pack(side="left", padx=(0, SPACING['md']))
        
        test_btn = StyledButton(
            button_frame,
            text="🔌 Test Connection",
            command=self.test_phpipam_connection,
            size="large",
            variant="primary"
        )
        test_btn.pack(side="left", padx=(0, SPACING['md']))
        
        auth_btn = StyledButton(
            button_frame,
            text="🔑 Authenticate",
            command=self.authenticate_phpipam,
            size="medium",
            variant="success"
        )
        auth_btn.pack(side="left")
        
        # Operations Section with styled card
        ops_frame = StyledCard(scrollable)
        ops_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        ops_title = SectionTitle(
            ops_frame,
            text="Operations"
        )
        ops_title.pack(pady=(SPACING['lg'], SPACING['md']), padx=SPACING['lg'], anchor="w")
        
        # IP Search
        search_frame = ctk.CTkFrame(ops_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="Search IP Address:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        search_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        search_entry_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_entry_frame.pack(fill="x")
        
        self.phpipam_search_entry = StyledEntry(
            search_entry_frame,
            placeholder_text="e.g., 192.168.1.10"
        )
        self.phpipam_search_entry.pack(side="left", fill="x", expand=True, padx=(0, SPACING['md']))
        
        search_btn = StyledButton(
            search_entry_frame,
            text="🔍 Search",
            command=self.search_phpipam_ip,
            size="medium",
            variant="primary"
        )
        search_btn.pack(side="left")
        
        # View Subnets
        subnet_btn_frame = ctk.CTkFrame(ops_frame, fg_color="transparent")
        subnet_btn_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        view_subnets_btn = StyledButton(
            subnet_btn_frame,
            text="📋 View All Subnets",
            command=self.view_phpipam_subnets,
            size="large",
            variant="primary"
        )
        view_subnets_btn.pack(side="left")
        
        # Results Section
        results_header_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        results_header_frame.pack(fill="x", pady=(SPACING['md'], SPACING['md']))
        
        results_title = SectionTitle(
            results_header_frame,
            text="Results"
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
    
    def open_live_ping_monitor(self):
        """Open the live ping monitor window"""
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
            print(f"DEBUG: update_favorites_ui called with {len(self.favorite_tools)} favorites")
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
                
                # Tool names mapping
                tool_names = {
                    "scanner": "📡 IPv4 Scanner",
                    "portscan": "🔌 Port Scanner",
                    "traceroute": "🛣️ Traceroute",
                    "bandwidth": "⚡ Bandwidth Test",
                    "dns": "🌐 DNS Lookup",
                    "subnet": "🧮 Subnet Calculator",
                    "mac": "💻 MAC Formatter",
                    "compare": "📊 Scan Comparison",
                    "profiles": "📁 Network Profiles",
                    "panos": "🔥 PAN-OS Generator",
                    "phpipam": "📦 phpIPAM",
                }
                
                for tool_id in sorted(self.favorite_tools):
                    btn = StyledButton(
                        self.favorites_buttons_frame,
                        text=tool_names.get(tool_id, tool_id),
                        command=lambda tid=tool_id: self.switch_tool(tid),
                        size="medium",
                        variant="neutral"
                    )
                    btn.pack(fill="x", pady=2)
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
        if self.current_page == "scanner":
            if self.start_scan_btn.cget("state") == "normal":
                self.start_scan()
        elif self.current_page == "mac":
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
            placeholder_text="Enter IPs or Hostnames (comma/space separated): e.g., 8.8.8.8 google.com 1.1.1.1"
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
    
    def start_monitoring(self):
        """Start monitoring the hosts"""
        hosts_input = self.hosts_entry.get().strip()
        
        if not hosts_input:
            messagebox.showwarning("No Hosts", "Please enter at least one IP or hostname")
            return
        
        # Parse hosts (comma or space separated)
        hosts = re.split(r'[,\s]+', hosts_input)
        hosts = [h.strip() for h in hosts if h.strip()]
        
        if not hosts:
            messagebox.showwarning("No Hosts", "Please enter at least one IP or hostname")
            return
        
        # Add hosts to monitor
        for host in hosts:
            ip = self.monitor.add_host(host)
            if ip:
                self.create_host_widget(ip)
        
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
        
        # Create inline graph with matplotlib (smaller for compact rows)
        fig = Figure(figsize=(3.5, 0.38), dpi=75, facecolor='white')
        ax = fig.add_subplot(111)
        ax.set_facecolor('white')
        ax.set_ylim(0, 500)
        ax.set_xlim(0, 30)
        ax.axis('off')  # Hide axes for cleaner look
        
        # No margins
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        
        line, = ax.plot([], [], color='#0066cc', linewidth=1.2, marker='o', markersize=2)
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Store references
        self.host_widgets[ip] = {
            'row': row,
            'status_bar': status_bar,
            'ip_label': ip_label,
            'hostname_label': hostname_label,
            'avg_label': avg_label,
            'min_label': min_label,
            'cur_label': cur_label,
            'figure': fig,
            'axis': ax,
            'line': line,
            'canvas': canvas,
            'min_value': float('inf')
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
                
                # Update graph
                x_data = list(range(1, len(recent_pings) + 1))
                y_data = []
                
                for success, rtt in recent_pings:
                    if success:
                        y_data.append(rtt)
                    else:
                        y_data.append(None)  # Show gaps for timeouts
                
                # Update line data
                widgets['line'].set_data(x_data, y_data)
                
                # Auto-scale y-axis
                valid_y = [y for y in y_data if y is not None]
                if valid_y:
                    max_y = max(valid_y)
                    widgets['axis'].set_ylim(0, max(500, max_y * 1.1))
                
                # Redraw canvas
                widgets['canvas'].draw_idle()
            
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
