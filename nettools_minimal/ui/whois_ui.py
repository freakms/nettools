"""
WHOIS Lookup UI - Query domain/IP ownership information
"""

import customtkinter as ctk
import threading
import socket
from design_constants import COLORS, SPACING, FONTS
from ui_components import StyledCard, StyledButton, StyledEntry, SubTitle, InfoBox


class WhoisUI:
    """WHOIS Lookup Tool"""
    
    # WHOIS servers for different TLDs
    WHOIS_SERVERS = {
        'com': 'whois.verisign-grs.com',
        'net': 'whois.verisign-grs.com',
        'org': 'whois.pir.org',
        'info': 'whois.afilias.net',
        'io': 'whois.nic.io',
        'co': 'whois.nic.co',
        'de': 'whois.denic.de',
        'uk': 'whois.nic.uk',
        'fr': 'whois.nic.fr',
        'eu': 'whois.eu',
        'ru': 'whois.tcinet.ru',
        'default': 'whois.iana.org'
    }
    
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.create_content()
    
    def create_content(self):
        """Create the WHOIS Lookup page"""
        scrollable = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        scrollable.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Title
        title = ctk.CTkLabel(
            scrollable,
            text="🔍 WHOIS Lookup",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS['electric_violet']
        )
        title.pack(anchor="w", pady=(0, SPACING['xs']))
        
        subtitle = SubTitle(scrollable, text="Query domain and IP ownership information")
        subtitle.pack(anchor="w", pady=(0, SPACING['lg']))
        
        # Input card
        input_card = StyledCard(scrollable, variant="elevated")
        input_card.pack(fill="x", pady=(0, SPACING['md']))
        
        input_frame = ctk.CTkFrame(input_card, fg_color="transparent")
        input_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])
        
        ctk.CTkLabel(
            input_frame, text="Domain or IP:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=(0, 10))
        
        self.query_entry = StyledEntry(input_frame, placeholder_text="example.com or 8.8.8.8")
        self.query_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.query_entry.bind('<Return>', lambda e: self.perform_lookup())
        
        self.lookup_btn = StyledButton(
            input_frame,
            text="🔍 Lookup",
            command=self.perform_lookup,
            variant="primary"
        )
        self.lookup_btn.pack(side="left")
        
        # Results
        results_card = StyledCard(scrollable, variant="elevated")
        results_card.pack(fill="both", expand=True, pady=(0, SPACING['md']))
        
        results_title = ctk.CTkLabel(
            results_card,
            text="📋 WHOIS Results",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        results_title.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        self.results_text = ctk.CTkTextbox(
            results_card,
            height=400,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=COLORS.get('bg_card', ("gray95", "gray20"))
        )
        self.results_text.pack(fill="both", expand=True, padx=SPACING['md'], pady=(0, SPACING['md']))
        self.results_text.insert("1.0", "Enter a domain or IP address and click 'Lookup'")
    
    def perform_lookup(self):
        """Perform WHOIS lookup"""
        query = self.query_entry.get().strip()
        if not query:
            self.app.show_toast("Please enter a domain or IP", "warning")
            return
        
        self.lookup_btn.configure(state="disabled", text="⏳ Looking up...")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", f"Looking up {query}...")
        
        thread = threading.Thread(target=self._do_lookup, args=(query,), daemon=True)
        thread.start()
    
    def _do_lookup(self, query):
        """Perform lookup in background"""
        try:
            # Determine WHOIS server
            if self._is_ip(query):
                server = 'whois.arin.net'
            else:
                tld = query.split('.')[-1].lower()
                server = self.WHOIS_SERVERS.get(tld, self.WHOIS_SERVERS['default'])
            
            # Connect and query
            result = self._query_whois(query, server)
            
            # Check for referral
            if 'Registrar WHOIS Server:' in result:
                for line in result.split('\n'):
                    if 'Registrar WHOIS Server:' in line:
                        referral = line.split(':')[1].strip()
                        if referral:
                            result = self._query_whois(query, referral)
                        break
            
            self.app.after(0, lambda: self._show_results(result))
            
        except Exception as e:
            self.app.after(0, lambda: self._show_results(f"Error: {str(e)}"))
        
        finally:
            self.app.after(0, lambda: self.lookup_btn.configure(state="normal", text="🔍 Lookup"))
    
    def _query_whois(self, query, server, port=43):
        """Query a WHOIS server"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((server, port))
        sock.send((query + "\r\n").encode())
        
        response = b""
        while True:
            data = sock.recv(4096)
            if not data:
                break
            response += data
        sock.close()
        
        return response.decode('utf-8', errors='ignore')
    
    def _is_ip(self, query):
        """Check if query is an IP address"""
        try:
            socket.inet_aton(query)
            return True
        except:
            return False
    
    def _show_results(self, result):
        """Display results"""
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", result)
        self.app.show_toast("WHOIS lookup complete", "success")
