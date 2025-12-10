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
from tools.dnsdumpster import DNSDumpster


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
        
        # Lookup buttons
        button_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        button_frame.pack(pady=(0, SPACING['lg']))
        
        lookup_btn = StyledButton(
            button_frame,
            text="🔍 DNS Lookup",
            command=self.perform_dns_lookup,
            size="large",
            variant="success"
        )
        lookup_btn.pack(side="left", padx=(0, SPACING['sm']))
        
        dnsdumpster_btn = StyledButton(
            button_frame,
            text="🌐 DNSDumpster (Full Recon)",
            command=self.perform_dnsdumpster_lookup,
            size="large",
            variant="primary"
        )
        dnsdumpster_btn.pack(side="left")
        
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
        self.app.after(0, self.display_dns_results, results)
    
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
    

    def perform_dnsdumpster_lookup(self):
        """Perform DNSDumpster domain reconnaissance"""
        query = self.app.dns_query_entry.get().strip()
        
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a domain name")
            return
        
        # Extract domain from query (remove http://, www., etc.)
        domain = query.lower()
        domain = domain.replace('http://', '').replace('https://', '')
        domain = domain.replace('www.', '')
        domain = domain.split('/')[0]  # Remove path
        
        # Validate domain format
        if '.' not in domain:
            messagebox.showwarning("Invalid Domain", "Please enter a valid domain name (e.g., example.com)")
            return
        
        # Clear previous results
        for widget in self.dns_results_frame.winfo_children():
            widget.destroy()
        
        # Show loading
        loading_label = ctk.CTkLabel(
            self.dns_results_frame,
            text=f"🌐 Performing DNSDumpster reconnaissance on {domain}...\nThis may take 10-30 seconds...",
            font=ctk.CTkFont(size=12),
            justify="center"
        )
        loading_label.pack(pady=50)
        
        # Perform lookup in background
        lookup_thread = threading.Thread(
            target=self.run_dnsdumpster_lookup,
            args=(domain,),
            daemon=True
        )
        lookup_thread.start()
    
    def run_dnsdumpster_lookup(self, domain):
        """Run DNSDumpster lookup in background"""
        results = DNSDumpster.lookup(domain)
        self.app.after(0, self.display_dnsdumpster_results, results)
    
    def display_dnsdumpster_results(self, results):
        """Display DNSDumpster results"""
        # Clear frame
        for widget in self.dns_results_frame.winfo_children():
            widget.destroy()
        
        # Container
        container = ctk.CTkFrame(self.dns_results_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Header
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, SPACING['md']))
        
        title = ctk.CTkLabel(
            header_frame,
            text=f"🌐 DNSDumpster Report: {results.get('domain', 'Unknown')}",
            font=ctk.CTkFont(size=FONTS['heading'], weight="bold")
        )
        title.pack(anchor="w")
        
        if not results.get("success"):
            error_label = ctk.CTkLabel(
                container,
                text=f"❌ Error: {results.get('error', 'Unknown error')}",
                font=ctk.CTkFont(size=FONTS['body']),
                text_color=COLORS['danger']
            )
            error_label.pack(pady=SPACING['xl'])
            return
        
        # Statistics Card
        stats = results.get("statistics", {})
        if stats:
            stats_card = StyledCard(container)
            stats_card.pack(fill="x", pady=(0, SPACING['md']))
            
            stats_title = ctk.CTkLabel(
                stats_card,
                text="📊 Statistics",
                font=ctk.CTkFont(size=FONTS['body'], weight="bold")
            )
            stats_title.pack(anchor="w", padx=SPACING['md'], pady=(SPACING['md'], SPACING['xs']))
            
            stats_frame = ctk.CTkFrame(stats_card, fg_color="transparent")
            stats_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
            
            if "total_hosts" in stats:
                host_label = ctk.CTkLabel(
                    stats_frame,
                    text=f"Total Hosts: {stats['total_hosts']}",
                    font=ctk.CTkFont(size=FONTS['small'])
                )
                host_label.pack(anchor="w", pady=2)
            
            if "total_subdomains" in stats:
                subdomain_label = ctk.CTkLabel(
                    stats_frame,
                    text=f"Subdomains Found: {stats['total_subdomains']}",
                    font=ctk.CTkFont(size=FONTS['small'])
                )
                subdomain_label.pack(anchor="w", pady=2)
        
        # Subdomains Section
        subdomains = results.get("subdomains", [])
        if subdomains:
            subdomain_card = StyledCard(container)
            subdomain_card.pack(fill="x", pady=(0, SPACING['md']))
            
            subdomain_title = ctk.CTkLabel(
                subdomain_card,
                text=f"🔍 Discovered Subdomains ({len(subdomains)})",
                font=ctk.CTkFont(size=FONTS['body'], weight="bold")
            )
            subdomain_title.pack(anchor="w", padx=SPACING['md'], pady=(SPACING['md'], SPACING['xs']))
            
            # Scrollable subdomain list
            subdomain_scroll = ctk.CTkScrollableFrame(subdomain_card, height=150)
            subdomain_scroll.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
            
            for subdomain in subdomains[:50]:  # Limit to 50
                subdomain_label = ctk.CTkLabel(
                    subdomain_scroll,
                    text=f"• {subdomain}",
                    font=ctk.CTkFont(size=FONTS['small'], family="Courier New"),
                    anchor="w"
                )
                subdomain_label.pack(anchor="w", pady=1)
            
            if len(subdomains) > 50:
                more_label = ctk.CTkLabel(
                    subdomain_scroll,
                    text=f"... and {len(subdomains) - 50} more",
                    font=ctk.CTkFont(size=FONTS['small']),
                    text_color=COLORS['text_secondary']
                )
                more_label.pack(anchor="w", pady=2)
        
        # DNS Records Sections
        dns_records = results.get("dns_records", {})
        
        # Host Records (A Records)
        hosts = dns_records.get("host", [])
        if hosts:
            host_card = StyledCard(container)
            host_card.pack(fill="x", pady=(0, SPACING['md']))
            
            host_title = ctk.CTkLabel(
                host_card,
                text=f"🖥️ Host Records (A) - {len(hosts)}",
                font=ctk.CTkFont(size=FONTS['body'], weight="bold")
            )
            host_title.pack(anchor="w", padx=SPACING['md'], pady=(SPACING['md'], SPACING['xs']))
            
            for host in hosts[:20]:  # Limit to 20
                host_frame = ctk.CTkFrame(host_card, fg_color=COLORS['bg_card'])
                host_frame.pack(fill="x", padx=SPACING['md'], pady=2)
                
                host_label = ctk.CTkLabel(
                    host_frame,
                    text=f"{host['host']} → {host['ip']} ({host.get('provider', 'Unknown')})",
                    font=ctk.CTkFont(size=FONTS['small'], family="Courier New"),
                    anchor="w"
                )
                host_label.pack(anchor="w", padx=SPACING['sm'], pady=SPACING['xs'])
        
        # MX Records
        mx_records = dns_records.get("mx", [])
        if mx_records:
            mx_card = StyledCard(container)
            mx_card.pack(fill="x", pady=(0, SPACING['md']))
            
            mx_title = ctk.CTkLabel(
                mx_card,
                text=f"📧 Mail Servers (MX) - {len(mx_records)}",
                font=ctk.CTkFont(size=FONTS['body'], weight="bold")
            )
            mx_title.pack(anchor="w", padx=SPACING['md'], pady=(SPACING['md'], SPACING['xs']))
            
            for mx in mx_records:
                mx_frame = ctk.CTkFrame(mx_card, fg_color=COLORS['bg_card'])
                mx_frame.pack(fill="x", padx=SPACING['md'], pady=2)
                
                mx_label = ctk.CTkLabel(
                    mx_frame,
                    text=f"{mx['mx']} → {mx.get('ip', 'N/A')} ({mx.get('provider', 'Unknown')})",
                    font=ctk.CTkFont(size=FONTS['small'], family="Courier New"),
                    anchor="w"
                )
                mx_label.pack(anchor="w", padx=SPACING['sm'], pady=SPACING['xs'])
        
        # Name Servers
        ns_records = dns_records.get("ns", [])
        if ns_records:
            ns_card = StyledCard(container)
            ns_card.pack(fill="x", pady=(0, SPACING['md']))
            
            ns_title = ctk.CTkLabel(
                ns_card,
                text=f"🌍 Name Servers (NS) - {len(ns_records)}",
                font=ctk.CTkFont(size=FONTS['body'], weight="bold")
            )
            ns_title.pack(anchor="w", padx=SPACING['md'], pady=(SPACING['md'], SPACING['xs']))
            
            for ns in ns_records:
                ns_frame = ctk.CTkFrame(ns_card, fg_color=COLORS['bg_card'])
                ns_frame.pack(fill="x", padx=SPACING['md'], pady=2)
                
                ns_label = ctk.CTkLabel(
                    ns_frame,
                    text=f"{ns['ns']} → {ns.get('ip', 'N/A')}",
                    font=ctk.CTkFont(size=FONTS['small'], family="Courier New"),
                    anchor="w"
                )
                ns_label.pack(anchor="w", padx=SPACING['sm'], pady=SPACING['xs'])
        
        # TXT Records
        txt_records = dns_records.get("txt", [])
        if txt_records:
            txt_card = StyledCard(container)
            txt_card.pack(fill="x", pady=(0, SPACING['md']))
            
            txt_title = ctk.CTkLabel(
                txt_card,
                text=f"📝 TXT Records - {len(txt_records)}",
                font=ctk.CTkFont(size=FONTS['body'], weight="bold")
            )
            txt_title.pack(anchor="w", padx=SPACING['md'], pady=(SPACING['md'], SPACING['xs']))
            
            for txt in txt_records[:10]:  # Limit to 10
                txt_label = ctk.CTkLabel(
                    txt_card,
                    text=txt,
                    font=ctk.CTkFont(size=FONTS['small']),
                    anchor="w",
                    wraplength=600
                )
                txt_label.pack(anchor="w", padx=SPACING['md'], pady=2)
        
        # Success message
        success_label = ctk.CTkLabel(
            container,
            text="✅ DNSDumpster reconnaissance complete!",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold"),
            text_color=COLORS['success']
        )
        success_label.pack(pady=(SPACING['md'], 0))

