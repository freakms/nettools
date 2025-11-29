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
from datetime import datetime
from pathlib import Path
import platform
import os
from pythonping import ping
from PIL import Image, ImageDraw
import io

# Application metadata
APP_NAME = "NetTools Suite"
APP_VERSION = "1.0.0"
APP_COMPANY = "Malte Schad"

# Configure CustomTkinter
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


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
        self.geometry("1000x700")
        self.minsize(980, 680)
        
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
        
        # Create UI
        self.create_header()
        self.create_tabs()
        self.create_status_bar()
        
        # Bind keyboard shortcuts
        self.bind('<Return>', self.on_enter_key)
        self.bind('<Control-e>', self.export_csv)
        
    def create_header(self):
        """Create header with title and theme selector"""
        header = ctk.CTkFrame(self, height=80, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            header, 
            text="NetTools Suite",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=(15, 0), anchor="nw")
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header,
            text="IPv4 Scanner & MAC Formatter",
            font=ctk.CTkFont(size=12)
        )
        subtitle_label.place(x=20, y=50)
        
        # Theme selector (right side)
        theme_label = ctk.CTkLabel(header, text="Theme:", font=ctk.CTkFont(size=11))
        theme_label.pack(side="right", padx=(10, 20), pady=20)
        
        self.theme_selector = ctk.CTkOptionMenu(
            header,
            values=["Light", "Dark"],
            command=self.change_theme,
            width=120
        )
        self.theme_selector.set("Light")
        self.theme_selector.pack(side="right", padx=(0, 10), pady=20)
        
        # Toggle Commands button (for MAC formatter)
        self.toggle_commands_btn = ctk.CTkButton(
            header,
            text="Hide Switch Commands",
            width=180,
            command=self.toggle_commands
        )
        self.toggle_commands_btn.pack(side="right", padx=(0, 20), pady=20)
    
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
        
        self.cidr_entry = ctk.CTkEntry(input_frame, width=300, placeholder_text="e.g., 192.168.1.0/24")
        self.cidr_entry.grid(row=0, column=1, padx=15, pady=15, sticky="w")
        self.cidr_entry.bind('<KeyRelease>', self.update_host_count)
        
        self.host_count_label = ctk.CTkLabel(input_frame, text="", font=ctk.CTkFont(size=11))
        self.host_count_label.grid(row=0, column=2, padx=15, pady=15, sticky="w")
        
        # Aggression selector
        aggro_label = ctk.CTkLabel(input_frame, text="Aggressiveness:", font=ctk.CTkFont(size=12))
        aggro_label.grid(row=1, column=0, padx=15, pady=15, sticky="w")
        
        self.aggro_selector = ctk.CTkOptionMenu(
            input_frame,
            values=["Gentle (longer timeout)", "Medium", "Aggressive (short timeout)"],
            width=300
        )
        self.aggro_selector.set("Medium")
        self.aggro_selector.grid(row=1, column=1, padx=15, pady=15, sticky="w")
        
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
        self.only_responding_check.pack(side="left", padx=15, pady=15)
        
        self.export_btn = ctk.CTkButton(
            options_frame,
            text="Export as CSV (Ctrl+E)",
            command=self.export_csv,
            width=200,
            state="disabled"
        )
        self.export_btn.pack(side="right", padx=15, pady=15)
        
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
        # Input section
        input_frame = ctk.CTkFrame(self.tab_mac)
        input_frame.pack(fill="x", padx=15, pady=15)
        
        mac_label = ctk.CTkLabel(
            input_frame,
            text="Enter MAC Address:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        mac_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.mac_entry = ctk.CTkEntry(
            input_frame,
            width=400,
            placeholder_text="e.g., AA:BB:CC:DD:EE:FF or AABBCCDDEEFF"
        )
        self.mac_entry.pack(anchor="w", padx=15, pady=(0, 10))
        self.mac_entry.bind('<KeyRelease>', self.update_mac_formats)
        
        self.mac_warning_label = ctk.CTkLabel(
            input_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#dc3545"
        )
        self.mac_warning_label.pack(anchor="w", padx=15, pady=(0, 15))
        
        # MAC Formats section
        formats_frame = ctk.CTkFrame(self.tab_mac)
        formats_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        formats_title = ctk.CTkLabel(
            formats_frame,
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
            row_frame = ctk.CTkFrame(formats_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=15, pady=5)
            
            label = ctk.CTkLabel(row_frame, text=label_text, width=150, anchor="w")
            label.pack(side="left", padx=(0, 10))
            
            entry = ctk.CTkEntry(row_frame, width=400)
            entry.pack(side="left", padx=(0, 10))
            entry.configure(state="readonly")
            self.format_entries.append(entry)
            
            copy_btn = ctk.CTkButton(
                row_frame,
                text="Copy",
                width=80,
                command=lambda e=entry: self.copy_to_clipboard(e)
            )
            copy_btn.pack(side="left")
        
        formats_frame.pack_configure(pady=(0, 10))
        
        # Switch Commands section
        self.commands_frame = ctk.CTkFrame(self.tab_mac)
        self.commands_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
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
            row_frame.pack(fill="x", padx=15, pady=5)
            
            label = ctk.CTkLabel(row_frame, text=label_text, width=200, anchor="w")
            label.pack(side="left", padx=(0, 10))
            
            textbox = ctk.CTkTextbox(row_frame, height=50, width=400)
            textbox.pack(side="left", padx=(0, 10))
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
    
    def on_tab_change(self):
        """Handle tab change event"""
        current_tab = self.tabview.get()
        
        # Show/hide status bar elements based on tab
        if current_tab == "IPv4 Scanner":
            # Show status label and progress bar for scanner
            self.status_label.configure(text="Ready.")
        elif current_tab == "MAC Formatter":
            # Hide scanning-specific status
            self.status_label.configure(text="")
            self.progress_bar.pack_forget()
    
    def toggle_commands(self):
        """Toggle switch commands visibility"""
        if self.commands_visible:
            for textbox in self.command_textboxes:
                textbox.master.pack_forget()
            self.toggle_commands_btn.configure(text="Show Switch Commands")
            self.commands_visible = False
        else:
            for textbox in self.command_textboxes:
                textbox.master.pack(fill="x", padx=15, pady=5)
            self.toggle_commands_btn.configure(text="Hide Switch Commands")
            self.commands_visible = True
    
    def on_enter_key(self, event):
        """Handle Enter key press"""
        if self.tabview.get() == "IPv4 Scanner":
            if self.start_scan_btn.cget("state") == "normal":
                self.start_scan()
        elif self.tabview.get() == "MAC Formatter":
            if self.format_entries[0].get():
                self.copy_to_clipboard(self.format_entries[0])


if __name__ == "__main__":
    app = NetToolsApp()
    app.mainloop()
