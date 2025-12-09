"""
DNS Lookup UI Module
Contains the DNS lookup tool page implementation
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import socket

from design_constants import COLORS, SPACING, RADIUS, FONTS
from ui_components import StyledCard, StyledButton, StyledEntry, SubTitle, SectionTitle
from tools.dns_lookup import DNSLookup


class DNSLookupUI:
    """DNS Lookup page UI implementation"""
    
    def __init__(self, app):
        """
        Initialize DNS Lookup UI
        
        Args:
            app: Reference to main NetToolsApp instance
        """
        self.app = app

    def create_content(self, parent):
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
        
        self.app.dns_query_entry = StyledEntry(
            input_frame,
            placeholder_text="google.com or 8.8.8.8"
        )
        self.app.dns_query_entry.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        self.app.dns_query_entry.bind('<Return>', lambda e: self.perform_dns_lookup())
        
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
        query = self.app.dns_query_entry.get().strip()
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
    
