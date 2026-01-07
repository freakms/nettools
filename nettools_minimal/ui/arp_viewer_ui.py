"""
ARP Table Viewer UI - View local ARP cache entries
"""

import customtkinter as ctk
import threading
import subprocess
import platform
import re
from design_constants import COLORS, SPACING, FONTS
from ui_components import StyledCard, StyledButton, SubTitle, ResultRow


class ARPViewerUI:
    """ARP Table Viewer Tool"""
    
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.arp_entries = []
        self.create_content()
    
    def create_content(self):
        """Create the ARP Viewer page"""
        scrollable = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        scrollable.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Title
        title = ctk.CTkLabel(
            scrollable,
            text="📊 ARP Table Viewer",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS['electric_violet']
        )
        title.pack(anchor="w", pady=(0, SPACING['xs']))
        
        subtitle = SubTitle(scrollable, text="View Address Resolution Protocol cache entries")
        subtitle.pack(anchor="w", pady=(0, SPACING['lg']))
        
        # Controls
        controls_card = StyledCard(scrollable, variant="elevated")
        controls_card.pack(fill="x", pady=(0, SPACING['md']))
        
        controls_frame = ctk.CTkFrame(controls_card, fg_color="transparent")
        controls_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])
        
        self.refresh_btn = StyledButton(
            controls_frame,
            text="🔄 Refresh ARP Table",
            command=self.refresh_arp,
            variant="primary"
        )
        self.refresh_btn.pack(side="left", padx=(0, 10))
        
        self.clear_btn = StyledButton(
            controls_frame,
            text="🗑️ Clear ARP Cache",
            command=self.clear_arp_cache,
            variant="danger"
        )
        self.clear_btn.pack(side="left", padx=(0, 10))
        
        self.export_btn = StyledButton(
            controls_frame,
            text="📋 Copy to Clipboard",
            command=self.copy_to_clipboard,
            variant="secondary"
        )
        self.export_btn.pack(side="left")
        
        # Stats
        self.stats_label = ctk.CTkLabel(
            controls_frame,
            text="Entries: 0",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        self.stats_label.pack(side="right")
        
        # Filter
        filter_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, SPACING['md']))
        
        ctk.CTkLabel(
            filter_frame, text="🔍 Filter:",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=(0, 10))
        
        self.filter_var = ctk.StringVar()
        self.filter_var.trace_add("write", lambda *args: self._apply_filter())
        
        self.filter_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.filter_var,
            placeholder_text="Filter by IP or MAC...",
            width=250
        )
        self.filter_entry.pack(side="left")
        
        # Table header
        header_card = StyledCard(scrollable, variant="subtle")
        header_card.pack(fill="x", pady=(0, 2))
        header_card.configure(fg_color=COLORS['electric_violet'])
        
        header_frame = ctk.CTkFrame(header_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['sm'])
        
        headers = [
            ("IP Address", 180),
            ("MAC Address", 180),
            ("Type", 100),
            ("Interface", 150)
        ]
        
        for text, width in headers:
            ctk.CTkLabel(
                header_frame,
                text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white",
                width=width,
                anchor="w"
            ).pack(side="left", padx=5)
        
        # Results container
        self.results_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True)
        
        # Auto-refresh on load
        self.refresh_arp()
    
    def refresh_arp(self):
        """Refresh ARP table"""
        self.refresh_btn.configure(state="disabled", text="⏳ Loading...")
        
        thread = threading.Thread(target=self._get_arp_table, daemon=True)
        thread.start()
    
    def _get_arp_table(self):
        """Get ARP table from system"""
        try:
            system = platform.system()
            
            if system == "Windows":
                result = subprocess.run(
                    ['arp', '-a'],
                    capture_output=True,
                    text=True,
                    encoding='cp1252',
                    errors='ignore',
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                entries = self._parse_windows_arp(result.stdout)
            else:
                result = subprocess.run(
                    ['arp', '-a'],
                    capture_output=True,
                    text=True
                )
                entries = self._parse_unix_arp(result.stdout)
            
            self.arp_entries = entries
            self.app.after(0, self._display_results)
            
        except Exception as e:
            self.app.after(0, lambda msg=str(e): self.app.show_toast(f"Error: {msg}", "error"))
        
        finally:
            self.app.after(0, lambda: self.refresh_btn.configure(state="normal", text="🔄 Refresh ARP Table"))
    
    def _parse_windows_arp(self, output):
        """Parse Windows ARP output"""
        entries = []
        current_interface = "Unknown"
        
        for line in output.split('\n'):
            line = line.strip()
            
            # Check for interface line
            if 'Interface:' in line or 'Schnittstelle:' in line:
                match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                if match:
                    current_interface = match.group(1)
                continue
            
            # Parse entry line
            parts = line.split()
            if len(parts) >= 3:
                ip = parts[0]
                # Validate IP format
                if re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
                    mac = parts[1]
                    entry_type = parts[2] if len(parts) > 2 else "unknown"
                    
                    # Normalize MAC format
                    mac = mac.replace('-', ':').lower()
                    
                    entries.append({
                        'ip': ip,
                        'mac': mac,
                        'type': entry_type,
                        'interface': current_interface
                    })
        
        return entries
    
    def _parse_unix_arp(self, output):
        """Parse Unix/Linux ARP output"""
        entries = []
        
        for line in output.split('\n'):
            # Format: hostname (IP) at MAC [ether] on interface
            match = re.search(r'\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-fA-F:]+)\s+.*on\s+(\S+)', line)
            if match:
                entries.append({
                    'ip': match.group(1),
                    'mac': match.group(2).lower(),
                    'type': 'dynamic',
                    'interface': match.group(3)
                })
        
        return entries
    
    def _display_results(self):
        """Display ARP entries"""
        # Clear existing
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Apply filter
        filter_text = self.filter_var.get().lower()
        filtered = [e for e in self.arp_entries 
                   if filter_text in e['ip'].lower() or filter_text in e['mac'].lower()]
        
        # Update stats
        self.stats_label.configure(text=f"Entries: {len(filtered)} / {len(self.arp_entries)}")
        
        # Display entries
        for i, entry in enumerate(filtered):
            row = ResultRow(self.results_frame, striped=(i % 2 == 1))
            row.pack(fill="x", pady=1)
            
            row_frame = ctk.CTkFrame(row, fg_color="transparent")
            row_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['xs'])
            
            # IP
            ctk.CTkLabel(
                row_frame,
                text=entry['ip'],
                font=ctk.CTkFont(family="Consolas", size=12),
                width=180,
                anchor="w"
            ).pack(side="left", padx=5)
            
            # MAC
            ctk.CTkLabel(
                row_frame,
                text=entry['mac'],
                font=ctk.CTkFont(family="Consolas", size=12),
                width=180,
                anchor="w",
                text_color=COLORS['neon_cyan']
            ).pack(side="left", padx=5)
            
            # Type
            type_color = COLORS['success'] if entry['type'] == 'dynamic' else COLORS['warning']
            ctk.CTkLabel(
                row_frame,
                text=entry['type'],
                font=ctk.CTkFont(size=11),
                width=100,
                anchor="w",
                text_color=type_color
            ).pack(side="left", padx=5)
            
            # Interface
            ctk.CTkLabel(
                row_frame,
                text=entry['interface'],
                font=ctk.CTkFont(size=11),
                width=150,
                anchor="w",
                text_color=COLORS['text_secondary']
            ).pack(side="left", padx=5)
        
        if not filtered:
            no_data = ctk.CTkLabel(
                self.results_frame,
                text="No ARP entries found",
                font=ctk.CTkFont(size=14),
                text_color=COLORS['text_secondary']
            )
            no_data.pack(pady=SPACING['xl'])
        
        self.app.show_toast(f"Found {len(self.arp_entries)} ARP entries", "success")
    
    def _apply_filter(self):
        """Apply filter to results"""
        if self.arp_entries:
            self._display_results()
    
    def clear_arp_cache(self):
        """Clear ARP cache (requires admin)"""
        try:
            system = platform.system()
            
            if system == "Windows":
                result = subprocess.run(
                    ['netsh', 'interface', 'ip', 'delete', 'arpcache'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                result = subprocess.run(
                    ['sudo', 'ip', '-s', '-s', 'neigh', 'flush', 'all'],
                    capture_output=True,
                    text=True
                )
            
            if result.returncode == 0:
                self.app.show_toast("ARP cache cleared", "success")
                self.refresh_arp()
            else:
                self.app.show_toast("Failed to clear cache (admin required)", "warning")
                
        except Exception as e:
            self.app.show_toast(f"Error: {str(e)}", "error")
    
    def copy_to_clipboard(self):
        """Copy ARP table to clipboard"""
        if not self.arp_entries:
            self.app.show_toast("No data to copy", "warning")
            return
        
        text = "IP Address\tMAC Address\tType\tInterface\n"
        for entry in self.arp_entries:
            text += f"{entry['ip']}\t{entry['mac']}\t{entry['type']}\t{entry['interface']}\n"
        
        try:
            self.app.clipboard_clear()
            self.app.clipboard_append(text)
            self.app.show_toast("Copied to clipboard", "success")
        except Exception as e:
            self.app.show_toast(f"Copy failed: {str(e)}", "error")
