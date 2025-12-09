"""
Port Scanner UI Module
Contains the port scanner page implementation
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import socket
import platform
try:
    import telnetlib
    TELNETLIB_AVAILABLE = True
except ImportError:
    TELNETLIB_AVAILABLE = False
import subprocess
import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime

from design_constants import COLORS, SPACING, RADIUS, FONTS
from ui_components import StyledCard, StyledButton, StyledEntry, ResultRow, SubTitle
from tools.port_scanner import PortScanner


class PortScannerUI:
    """Port Scanner page UI implementation"""
    
    def __init__(self, app):
        """
        Initialize Port Scanner UI
        
        Args:
            app: Reference to main NetToolsApp instance
        """
        self.app = app

    def create_content(self, parent):
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
        
        self.app.port_cancel_btn = StyledButton(
            button_frame,
            text="⏹ Cancel",
            command=self.cancel_port_scan,
            size="medium",
            variant="danger",
            state="disabled"
        )
        self.app.port_cancel_btn.pack(side="left")
        
        self.app.port_export_btn = StyledButton(
            button_frame,
            text="📤 Export Results",
            command=self.export_port_scan,
            size="large",
            variant="success",
            state="disabled"
        )
        self.app.port_export_btn.pack(side="left", padx=(SPACING['md'], 0))
        
        # Progress
        self.app.port_progress_label = SubTitle(
            scrollable,
            text=""
        )
        self.app.port_progress_label.pack(pady=(0, SPACING['xs']))
        
        self.app.port_progress_bar = ctk.CTkProgressBar(scrollable, width=400, height=20)
        self.app.port_progress_bar.pack(pady=(0, SPACING['lg']))
        self.app.port_progress_bar.set(0)
        
        # Results section
        results_title = SectionTitle(
            scrollable,
            text="Scan Results"
        )
        results_title.pack(pady=(SPACING['md'], SPACING['md']), anchor="w")
        
        # Results frame with styled card
        self.app.port_results_frame = StyledCard(scrollable)
        self.app.port_results_frame.pack(fill="both", expand=True)
        
        # Initial message
        no_results_label = ctk.CTkLabel(
            self.app.port_results_frame,
            text="No scan results yet. Enter a target and start scanning.",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        no_results_label.pack(pady=50)
        
        # Port scan state
        self.port_scan_running = False
        self.port_scan_cancelled = False
        self.port_scan_results = []  # Store port scan results for export
        self.app.port_scan_target = ""   # Store target for export
    
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
        self.app.port_cancel_btn.configure(state="normal")
        self.port_scan_running = True
        self.port_scan_cancelled = False
        self.app.port_progress_bar.set(0)
        self.app.port_progress_label.configure(text=f"Scanning {target} - {len(ports)} port(s)...")
        
        # Clear previous results
        for widget in self.app.port_results_frame.winfo_children():
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
        self.app.port_progress_label.configure(text="Cancelling scan...")
    
    def run_port_scan(self, target, ports, method):
        """Run port scan in background"""
        results = []
        total_ports = len(ports)
        
        for i, port in enumerate(ports):
            if self.port_scan_cancelled:
                break
            
            # Update progress
            progress = (i + 1) / total_ports
            self.after(0, self.app.port_progress_bar.set, progress)
            self.after(0, self.app.port_progress_label.configure, 
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
        self.app.port_scan_target = target
        
        # Clear frame
        for widget in self.app.port_results_frame.winfo_children():
            widget.destroy()
        
        # Reset UI state
        self.port_scan_btn.configure(state="normal")
        self.app.port_cancel_btn.configure(state="disabled")
        self.port_scan_running = False
        
        # Enable/disable export button
        if results and not was_cancelled:
            self.app.port_export_btn.configure(state="normal")
        else:
            self.app.port_export_btn.configure(state="disabled")
        
        if was_cancelled:
            self.app.port_progress_label.configure(text="Scan cancelled")
        else:
            self.app.port_progress_label.configure(text="Scan complete")
        
        if not results:
            no_results_label = ctk.CTkLabel(
                self.app.port_results_frame,
                text=f"No open ports found on {target}" if not was_cancelled else "Scan was cancelled",
                font=ctk.CTkFont(size=12),
                text_color=("gray60", "gray40")
            )
            no_results_label.pack(pady=50)
            return
        
        # Summary
        summary_frame = ctk.CTkFrame(self.app.port_results_frame, fg_color="transparent")
        summary_frame.pack(fill="x", padx=15, pady=15)
        
        summary_text = f"Found {len(results)} open port(s) on {target}"
        summary_label = ctk.CTkLabel(
            summary_frame,
            text=summary_text,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        summary_label.pack(anchor="w")
        
        # Results table header
        header_frame = ctk.CTkFrame(self.app.port_results_frame, corner_radius=0)
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
            row_frame = ctk.CTkFrame(self.app.port_results_frame, corner_radius=4)
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
    
    def export_port_scan(self):
        """Export port scan results in multiple formats"""
        if not self.port_scan_results:
            messagebox.showinfo("Information", "No port scan data to export.")
            return
        
        # Get desktop path
        desktop = Path.home() / "Desktop"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"PortScan_{self.app.port_scan_target.replace('.', '_')}_{timestamp}"
        
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
                    'target': self.app.port_scan_target,
                    'port': result['port'],
                    'state': result['state'],
                    'service': result['service']
                })
    
    def _export_port_scan_json(self, filepath):
        """Export port scan to JSON format"""
        export_data = {
            'scan_info': {
                'target': self.app.port_scan_target,
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
        ET.SubElement(info, 'target').text = self.app.port_scan_target
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
            f.write(f"Target: {self.app.port_scan_target}\n")
            f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Open Ports: {len(self.port_scan_results)}\n")
            f.write(f"=" * 60 + "\n\n")
            
            f.write(f"{'Port':<10} {'State':<10} {'Service':<20}\n")
            f.write(f"{'-' * 10} {'-' * 10} {'-' * 20}\n")
            
            for result in self.port_scan_results:
                f.write(f"{str(result['port']):<10} {result['state']:<10} {result['service']:<20}\n")
    
