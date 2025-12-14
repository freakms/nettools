"""
DNS Lookup UI Module
Contains the DNS lookup tool page implementation
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import socket

from design_constants import COLORS, SPACING, RADIUS, FONTS
from ui_components import StyledCard, StyledButton, StyledEntry, SubTitle, SectionTitle, LoadingSpinner, add_tooltip_to_widget
from tools.dns_lookup import DNSLookup
from tools.comparison_history import ComparisonHistory
from tools.dnsdumpster import DNSDumpster
from tools.mxtoolbox import MXToolbox


class DNSLookupUI:
    """DNS Lookup page UI implementation"""
    
    def __init__(self, app):
        """
        Initialize DNS Lookup UI
        
        Args:
            app: Reference to main NetToolsApp instance
        """
        self.app = app
        self.comparison_history = ComparisonHistory()

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
            text="DNS Server:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        dns_server_label.pack(pady=(0, SPACING['xs']), padx=SPACING['lg'], anchor="w")
        
        dns_server_info = SubTitle(
            input_frame,
            text="Select a preset or enter custom DNS server IP"
        )
        dns_server_info.pack(pady=(0, SPACING['xs']), padx=SPACING['lg'], anchor="w")
        
        dns_server_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        dns_server_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['sm']))
        
        self.dns_server_var = ctk.StringVar(value="system")
        
        # Row 1: System, Google, Cloudflare
        dns_row1 = ctk.CTkFrame(dns_server_frame, fg_color="transparent")
        dns_row1.pack(fill="x", pady=2)
        
        system_dns = ctk.CTkRadioButton(
            dns_row1,
            text="System Default",
            variable=self.dns_server_var,
            value="system",
            font=ctk.CTkFont(size=FONTS['small']),
            command=self._on_dns_preset_selected
        )
        system_dns.pack(side="left", padx=(0, SPACING['md']))
        
        google_dns = ctk.CTkRadioButton(
            dns_row1,
            text="Google (8.8.8.8)",
            variable=self.dns_server_var,
            value="8.8.8.8",
            font=ctk.CTkFont(size=FONTS['small']),
            command=self._on_dns_preset_selected
        )
        google_dns.pack(side="left", padx=(0, SPACING['md']))
        
        cloudflare_dns = ctk.CTkRadioButton(
            dns_row1,
            text="Cloudflare (1.1.1.1)",
            variable=self.dns_server_var,
            value="1.1.1.1",
            font=ctk.CTkFont(size=FONTS['small']),
            command=self._on_dns_preset_selected
        )
        cloudflare_dns.pack(side="left", padx=(0, SPACING['md']))
        
        # Row 2: Quad9, OpenDNS
        dns_row2 = ctk.CTkFrame(dns_server_frame, fg_color="transparent")
        dns_row2.pack(fill="x", pady=2)
        
        quad9_dns = ctk.CTkRadioButton(
            dns_row2,
            text="Quad9 (9.9.9.9)",
            variable=self.dns_server_var,
            value="9.9.9.9",
            font=ctk.CTkFont(size=FONTS['small']),
            command=self._on_dns_preset_selected
        )
        quad9_dns.pack(side="left", padx=(0, SPACING['md']))
        
        opendns_dns = ctk.CTkRadioButton(
            dns_row2,
            text="OpenDNS (208.67.222.222)",
            variable=self.dns_server_var,
            value="208.67.222.222",
            font=ctk.CTkFont(size=FONTS['small']),
            command=self._on_dns_preset_selected
        )
        opendns_dns.pack(side="left", padx=(0, SPACING['md']))
        
        # Row 3: Custom DNS input
        dns_row3 = ctk.CTkFrame(dns_server_frame, fg_color="transparent")
        dns_row3.pack(fill="x", pady=(SPACING['sm'], 0))
        
        custom_dns = ctk.CTkRadioButton(
            dns_row3,
            text="Custom:",
            variable=self.dns_server_var,
            value="custom",
            font=ctk.CTkFont(size=FONTS['small']),
            command=self._on_custom_dns_selected
        )
        custom_dns.pack(side="left", padx=(0, SPACING['sm']))
        
        self.custom_dns_entry = StyledEntry(
            dns_row3,
            placeholder_text="Enter DNS server IP (e.g., 192.168.1.1)",
            width=280
        )
        self.custom_dns_entry.pack(side="left")
        self.custom_dns_entry.bind('<FocusIn>', lambda e: self._on_custom_dns_focus())
        
        # Lookup buttons
        button_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        button_frame.pack(pady=(SPACING['sm'], SPACING['lg']))
        
        lookup_btn = StyledButton(
            button_frame,
            text="🔍 DNS Lookup",
            command=self.perform_dns_lookup,
            size="large",
            variant="success"
        )
        lookup_btn.pack(side="left", padx=(0, SPACING['sm']))
        
        mxtoolbox_btn = StyledButton(
            button_frame,
            text="🔧 MXToolbox (DNS Check)",
            command=self.perform_mxtoolbox_lookup,
            size="large",
            variant="primary"
        )
        mxtoolbox_btn.pack(side="left", padx=(0, SPACING['sm']))
        
        dnsdumpster_btn = StyledButton(
            button_frame,
            text="🌐 DNSDumpster",
            command=self.perform_dnsdumpster_lookup,
            size="large",
            variant="secondary"
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
    
    def _on_dns_preset_selected(self):
        """Called when a DNS preset radio button is selected"""
        # Clear custom DNS entry when selecting a preset
        if hasattr(self, 'custom_dns_entry'):
            self.custom_dns_entry.delete(0, 'end')
    
    def _on_custom_dns_selected(self):
        """Called when custom DNS radio button is selected"""
        # Focus the custom DNS entry
        if hasattr(self, 'custom_dns_entry'):
            self.custom_dns_entry.focus()
    
    def _on_custom_dns_focus(self):
        """Called when custom DNS entry receives focus"""
        # Auto-select the custom radio button
        self.dns_server_var.set("custom")
    
    def _get_selected_dns_server(self):
        """Get the selected DNS server (preset or custom)"""
        selected = self.dns_server_var.get()
        if selected == "custom":
            custom = self.custom_dns_entry.get().strip()
            if custom:
                return custom
            else:
                return "system"  # Fallback if no custom entered
        return selected
    
    def perform_dns_lookup(self):
        """Perform DNS lookup"""
        query = self.app.dns_query_entry.get().strip()
        if not query:
            messagebox.showwarning("Invalid Input", "Please enter a hostname or IP address")
            return
        
        dns_server = self._get_selected_dns_server()
        
        # Validate custom DNS server if provided
        if dns_server not in ["system", "8.8.8.8", "1.1.1.1", "9.9.9.9", "208.67.222.222"]:
            if not DNSLookup.validate_dns_server(dns_server):
                messagebox.showwarning("Invalid DNS Server", f"'{dns_server}' is not a valid IP address")
                return
        
        # Clear previous results
        for widget in self.dns_results_frame.winfo_children():
            widget.destroy()
        
        # Show loading spinner
        self.dns_loading_spinner = LoadingSpinner(self.dns_results_frame, text=f"Looking up {query}...")
        self.dns_loading_spinner.pack(pady=50)
        self.dns_loading_spinner.start()
        
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
        # Remove loading spinner
        if hasattr(self, 'dns_loading_spinner'):
            try:
                self.dns_loading_spinner.stop()
                self.dns_loading_spinner.destroy()
            except:
                pass
        
        # Save to comparison history
        if results.get("success"):
            try:
                self.comparison_history.save_dns_lookup(
                    results["query"],
                    results["type"],
                    results
                )
            except Exception as e:
                print(f"Error saving DNS lookup history: {e}")
        
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
        
        # Copy button
        def copy_result():
            self.app.clipboard_clear()
            self.app.clipboard_append(result_text)
            self.app.update()
            self.app.show_toast(f"Copied: {result_text[:50]}{'...' if len(result_text) > 50 else ''}", "success")
        
        copy_btn = StyledButton(
            result_frame,
            text="📋 Copy",
            command=copy_result,
            size="small",
            variant="neutral"
        )
        copy_btn.pack(side="left", padx=(10, 0))
        
        # Status icon
        status_text = "✅ Success" if results["success"] else "❌ Failed"
        status_label = ctk.CTkLabel(
            self.dns_results_frame,
            text=status_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=result_color
        )
        status_label.pack(pady=(10, 10), padx=20, anchor="w")
        
        # Copy All button
        def copy_all_results():
            all_text = f"DNS Lookup Results\n"
            all_text += f"{'='*50}\n"
            all_text += f"Type: {results['type']}\n"
            all_text += f"Query: {results['query']}\n"
            if "dns_server" in results:
                all_text += f"DNS Server: {results['dns_server']}\n"
            all_text += f"Result: {result_text}\n"
            all_text += f"Status: {status_text}\n"
            
            self.app.clipboard_clear()
            self.app.clipboard_append(all_text)
            self.app.update()
            self.app.show_toast("All results copied to clipboard", "success")
        
        # Button frame
        button_frame = ctk.CTkFrame(self.dns_results_frame, fg_color="transparent")
        button_frame.pack(pady=(10, 20), padx=20, anchor="w")
        
        copy_all_btn = StyledButton(
            button_frame,
            text="📄 Copy All Results",
            command=copy_all_results,
            size="medium",
            variant="primary"
        )
        copy_all_btn.pack(side="left", padx=(0, 10))
        
        # Compare button
        compare_btn = StyledButton(
            button_frame,
            text="⚖️ Compare Lookups",
            command=lambda: self.show_dns_comparison(results["query"]),
            size="medium",
            variant="neutral"
        )
        compare_btn.pack(side="left")
        add_tooltip_to_widget(compare_btn, "Compare this lookup with previous lookups")
    

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
            
            # Scrollable host list for many records
            host_scroll = ctk.CTkScrollableFrame(host_card, height=200)
            host_scroll.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
            
            for host in hosts[:30]:  # Limit to 30
                host_frame = ctk.CTkFrame(host_scroll, fg_color=COLORS['bg_card'])
                host_frame.pack(fill="x", pady=2)
                
                # Main host info
                host_text = f"{host['host']} → {host['ip']}"
                if host.get('ptr'):
                    host_text += f" (PTR: {host['ptr']})"
                
                host_label = ctk.CTkLabel(
                    host_frame,
                    text=host_text,
                    font=ctk.CTkFont(size=FONTS['small'], family="Courier New"),
                    anchor="w"
                )
                host_label.pack(anchor="w", padx=SPACING['sm'], pady=(SPACING['xs'], 0))
                
                # Provider/ASN info
                if host.get('provider'):
                    provider_label = ctk.CTkLabel(
                        host_frame,
                        text=f"   ASN: {host['provider']}",
                        font=ctk.CTkFont(size=FONTS['small']),
                        text_color=COLORS['text_secondary'],
                        anchor="w"
                    )
                    provider_label.pack(anchor="w", padx=SPACING['sm'], pady=0)
                
                # Services/banners info
                services = host.get('services', [])
                if services:
                    services_text = "   Services: " + ", ".join(services[:3])
                    if len(services) > 3:
                        services_text += f" (+{len(services)-3} more)"
                    services_label = ctk.CTkLabel(
                        host_frame,
                        text=services_text,
                        font=ctk.CTkFont(size=FONTS['small']),
                        text_color=COLORS['success'],
                        anchor="w"
                    )
                    services_label.pack(anchor="w", padx=SPACING['sm'], pady=(0, SPACING['xs']))
        
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
                    text=f"{mx['mx']} → {mx.get('ip', 'N/A')}",
                    font=ctk.CTkFont(size=FONTS['small'], family="Courier New"),
                    anchor="w"
                )
                mx_label.pack(anchor="w", padx=SPACING['sm'], pady=(SPACING['xs'], 0))
                
                if mx.get('provider'):
                    mx_provider = ctk.CTkLabel(
                        mx_frame,
                        text=f"   {mx['provider']}",
                        font=ctk.CTkFont(size=FONTS['small']),
                        text_color=COLORS['text_secondary'],
                        anchor="w"
                    )
                    mx_provider.pack(anchor="w", padx=SPACING['sm'], pady=(0, SPACING['xs']))
        
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
                ns_label.pack(anchor="w", padx=SPACING['sm'], pady=(SPACING['xs'], 0))
                
                if ns.get('provider'):
                    ns_provider = ctk.CTkLabel(
                        ns_frame,
                        text=f"   {ns['provider']}",
                        font=ctk.CTkFont(size=FONTS['small']),
                        text_color=COLORS['text_secondary'],
                        anchor="w"
                    )
                    ns_provider.pack(anchor="w", padx=SPACING['sm'], pady=(0, SPACING['xs']))
        
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

    # ==================== MXToolbox Methods ====================
    
    def perform_mxtoolbox_lookup(self):
        """Perform MXToolbox DNS check"""
        query = self.app.dns_query_entry.get().strip()
        
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a domain name")
            return
        
        # Extract domain from query
        domain = query.lower()
        domain = domain.replace('http://', '').replace('https://', '')
        domain = domain.replace('www.', '')
        domain = domain.split('/')[0]
        
        if '.' not in domain:
            messagebox.showwarning("Invalid Domain", "Please enter a valid domain name (e.g., example.com)")
            return
        
        # Clear previous results
        for widget in self.dns_results_frame.winfo_children():
            widget.destroy()
        
        # Show loading
        loading_label = ctk.CTkLabel(
            self.dns_results_frame,
            text=f"🔧 Performing MXToolbox DNS check on {domain}...\nThis uses 4 API calls (A, MX, NS, TXT)...",
            font=ctk.CTkFont(size=12),
            justify="center"
        )
        loading_label.pack(pady=50)
        
        # Perform lookup in background
        lookup_thread = threading.Thread(
            target=self.run_mxtoolbox_lookup,
            args=(domain,),
            daemon=True
        )
        lookup_thread.start()
    
    def run_mxtoolbox_lookup(self, domain):
        """Run MXToolbox lookup in background"""
        results = MXToolbox.full_dns_check(domain)
        self.app.after(0, self.display_mxtoolbox_results, results)
    
    def display_mxtoolbox_results(self, results):
        """Display MXToolbox results"""
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
            text=f"🔧 MXToolbox DNS Report: {results.get('domain', 'Unknown')}",
            font=ctk.CTkFont(size=FONTS['heading'], weight="bold")
        )
        title.pack(anchor="w")
        
        # API calls used info
        api_info = ctk.CTkLabel(
            header_frame,
            text=f"API calls used: {results.get('api_calls_used', 0)}/63 daily",
            font=ctk.CTkFont(size=FONTS['small']),
            text_color=COLORS['text_secondary']
        )
        api_info.pack(anchor="w")
        
        if not results.get("success"):
            error_label = ctk.CTkLabel(
                container,
                text=f"❌ Error: {results.get('error', 'Unknown error')}",
                font=ctk.CTkFont(size=FONTS['body']),
                text_color=COLORS['danger']
            )
            error_label.pack(pady=SPACING['xl'])
            return
        
        dns_records = results.get("dns_records", {})
        diagnostics = results.get("diagnostics", {})
        statistics = results.get("statistics", {})
        
        # Statistics Card
        stats_card = StyledCard(container)
        stats_card.pack(fill="x", pady=(0, SPACING['md']))
        
        stats_title = ctk.CTkLabel(
            stats_card,
            text="📊 Summary",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        stats_title.pack(anchor="w", padx=SPACING['md'], pady=(SPACING['md'], SPACING['xs']))
        
        stats_frame = ctk.CTkFrame(stats_card, fg_color="transparent")
        stats_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        
        stats_text = f"A Records: {statistics.get('a_records', 0)} | "
        stats_text += f"MX Records: {statistics.get('mx_records', 0)} | "
        stats_text += f"NS Records: {statistics.get('ns_records', 0)} | "
        stats_text += f"TXT Records: {statistics.get('txt_records', 0)}"
        
        stats_label = ctk.CTkLabel(
            stats_frame,
            text=stats_text,
            font=ctk.CTkFont(size=FONTS['small'])
        )
        stats_label.pack(anchor="w", pady=2)
        
        if results.get("reporting_nameserver"):
            ns_label = ctk.CTkLabel(
                stats_frame,
                text=f"Reporting NS: {results['reporting_nameserver']}",
                font=ctk.CTkFont(size=FONTS['small']),
                text_color=COLORS['text_secondary']
            )
            ns_label.pack(anchor="w", pady=2)
        
        # Diagnostics summary
        diag_text = f"✅ Passed: {statistics.get('passed_checks', 0)} | "
        diag_text += f"⚠️ Warnings: {statistics.get('warnings', 0)} | "
        diag_text += f"❌ Errors: {statistics.get('errors', 0)}"
        
        diag_label = ctk.CTkLabel(
            stats_frame,
            text=diag_text,
            font=ctk.CTkFont(size=FONTS['small'])
        )
        diag_label.pack(anchor="w", pady=2)
        
        # A Records
        a_records = dns_records.get("a", [])
        if a_records:
            a_card = StyledCard(container)
            a_card.pack(fill="x", pady=(0, SPACING['md']))
            
            a_title = ctk.CTkLabel(
                a_card,
                text=f"🖥️ A Records (IPv4) - {len(a_records)}",
                font=ctk.CTkFont(size=FONTS['body'], weight="bold")
            )
            a_title.pack(anchor="w", padx=SPACING['md'], pady=(SPACING['md'], SPACING['xs']))
            
            for record in a_records:
                a_frame = ctk.CTkFrame(a_card, fg_color=COLORS['bg_card'])
                a_frame.pack(fill="x", padx=SPACING['md'], pady=2)
                
                a_label = ctk.CTkLabel(
                    a_frame,
                    text=f"{record.get('host', '')} → {record.get('ip', '')}",
                    font=ctk.CTkFont(size=FONTS['small'], family="Courier New"),
                    anchor="w"
                )
                a_label.pack(anchor="w", padx=SPACING['sm'], pady=(SPACING['xs'], 0))
                
                extra_info = []
                if record.get('ttl'):
                    extra_info.append(f"TTL: {record['ttl']}")
                if record.get('asn'):
                    extra_info.append(record['asn'])
                
                if extra_info:
                    extra_label = ctk.CTkLabel(
                        a_frame,
                        text="   " + " | ".join(extra_info),
                        font=ctk.CTkFont(size=FONTS['small']),
                        text_color=COLORS['text_secondary'],
                        anchor="w"
                    )
                    extra_label.pack(anchor="w", padx=SPACING['sm'], pady=(0, SPACING['xs']))
        
        # MX Records
        mx_records = dns_records.get("mx", [])
        if mx_records:
            mx_card = StyledCard(container)
            mx_card.pack(fill="x", pady=(0, SPACING['md']))
            
            mx_title = ctk.CTkLabel(
                mx_card,
                text=f"📧 MX Records (Mail Servers) - {len(mx_records)}",
                font=ctk.CTkFont(size=FONTS['body'], weight="bold")
            )
            mx_title.pack(anchor="w", padx=SPACING['md'], pady=(SPACING['md'], SPACING['xs']))
            
            for record in mx_records:
                mx_frame = ctk.CTkFrame(mx_card, fg_color=COLORS['bg_card'])
                mx_frame.pack(fill="x", padx=SPACING['md'], pady=2)
                
                pref = record.get('preference', '')
                mx_text = f"[{pref}] " if pref else ""
                mx_text += f"{record.get('mx', '')} → {record.get('ip', '')}"
                if record.get('ipv6'):
                    mx_text += " (IPv6)"
                
                mx_label = ctk.CTkLabel(
                    mx_frame,
                    text=mx_text,
                    font=ctk.CTkFont(size=FONTS['small'], family="Courier New"),
                    anchor="w"
                )
                mx_label.pack(anchor="w", padx=SPACING['sm'], pady=(SPACING['xs'], 0))
                
                if record.get('asn'):
                    asn_label = ctk.CTkLabel(
                        mx_frame,
                        text=f"   {record['asn']}",
                        font=ctk.CTkFont(size=FONTS['small']),
                        text_color=COLORS['text_secondary'],
                        anchor="w"
                    )
                    asn_label.pack(anchor="w", padx=SPACING['sm'], pady=(0, SPACING['xs']))
        
        # NS Records
        ns_records = dns_records.get("ns", [])
        if ns_records:
            ns_card = StyledCard(container)
            ns_card.pack(fill="x", pady=(0, SPACING['md']))
            
            ns_title = ctk.CTkLabel(
                ns_card,
                text=f"🌍 NS Records (Name Servers) - {len(ns_records)}",
                font=ctk.CTkFont(size=FONTS['body'], weight="bold")
            )
            ns_title.pack(anchor="w", padx=SPACING['md'], pady=(SPACING['md'], SPACING['xs']))
            
            for record in ns_records:
                ns_frame = ctk.CTkFrame(ns_card, fg_color=COLORS['bg_card'])
                ns_frame.pack(fill="x", padx=SPACING['md'], pady=2)
                
                status = record.get('status', '')
                status_icon = "🟢" if status == "GREEN" else "🟡" if status == "YELLOW" else "🔴" if status == "RED" else ""
                
                ns_label = ctk.CTkLabel(
                    ns_frame,
                    text=f"{status_icon} {record.get('ns', '')} → {record.get('ip', '')}",
                    font=ctk.CTkFont(size=FONTS['small'], family="Courier New"),
                    anchor="w"
                )
                ns_label.pack(anchor="w", padx=SPACING['sm'], pady=(SPACING['xs'], 0))
                
                if record.get('asn'):
                    asn_label = ctk.CTkLabel(
                        ns_frame,
                        text=f"   {record['asn']}",
                        font=ctk.CTkFont(size=FONTS['small']),
                        text_color=COLORS['text_secondary'],
                        anchor="w"
                    )
                    asn_label.pack(anchor="w", padx=SPACING['sm'], pady=(0, SPACING['xs']))
        
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
            
            for record in txt_records[:10]:
                txt_text = record.get('txt', '') if isinstance(record, dict) else str(record)
                txt_label = ctk.CTkLabel(
                    txt_card,
                    text=txt_text,
                    font=ctk.CTkFont(size=FONTS['small']),
                    anchor="w",
                    wraplength=600
                )
                txt_label.pack(anchor="w", padx=SPACING['md'], pady=2)
        
        # Warnings Section
        warnings = diagnostics.get("warnings", [])
        if warnings:
            warn_card = StyledCard(container)
            warn_card.pack(fill="x", pady=(0, SPACING['md']))
            
            warn_title = ctk.CTkLabel(
                warn_card,
                text=f"⚠️ Warnings - {len(warnings)}",
                font=ctk.CTkFont(size=FONTS['body'], weight="bold"),
                text_color=COLORS['warning']
            )
            warn_title.pack(anchor="w", padx=SPACING['md'], pady=(SPACING['md'], SPACING['xs']))
            
            for warning in warnings[:5]:
                warn_frame = ctk.CTkFrame(warn_card, fg_color=COLORS['bg_card'])
                warn_frame.pack(fill="x", padx=SPACING['md'], pady=2)
                
                warn_label = ctk.CTkLabel(
                    warn_frame,
                    text=f"• {warning.get('info', '')}",
                    font=ctk.CTkFont(size=FONTS['small']),
                    anchor="w",
                    wraplength=550
                )
                warn_label.pack(anchor="w", padx=SPACING['sm'], pady=SPACING['xs'])
                
                details = warning.get('details', [])
                if details:
                    for detail in details[:2]:
                        detail_label = ctk.CTkLabel(
                            warn_frame,
                            text=f"  → {detail}",
                            font=ctk.CTkFont(size=FONTS['small']),
                            text_color=COLORS['text_secondary'],
                            anchor="w",
                            wraplength=530
                        )
                        detail_label.pack(anchor="w", padx=SPACING['sm'], pady=(0, 2))
        
        # Success message
        success_label = ctk.CTkLabel(
            container,
            text="✅ MXToolbox DNS check complete!",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold"),
            text_color=COLORS['success']
        )
        success_label.pack(pady=(SPACING['md'], 0))

