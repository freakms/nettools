"""
SSL Certificate Checker UI - Check SSL certificate validity and details
"""

import customtkinter as ctk
import threading
import ssl
import socket
import datetime
from design_constants import COLORS, SPACING, FONTS
from ui_components import StyledCard, StyledButton, StyledEntry, SubTitle, StatusBadge


class SSLCheckerUI:
    """SSL Certificate Checker Tool"""
    
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.create_content()
    
    def create_content(self):
        """Create the SSL Checker page"""
        scrollable = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        scrollable.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Title
        title = ctk.CTkLabel(
            scrollable,
            text="🔒 SSL Certificate Checker",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS['electric_violet']
        )
        title.pack(anchor="w", pady=(0, SPACING['xs']))
        
        subtitle = SubTitle(scrollable, text="Check SSL/TLS certificate validity, expiration, and chain")
        subtitle.pack(anchor="w", pady=(0, SPACING['lg']))
        
        # Input card
        input_card = StyledCard(scrollable, variant="elevated")
        input_card.pack(fill="x", pady=(0, SPACING['md']))
        
        input_frame = ctk.CTkFrame(input_card, fg_color="transparent")
        input_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])
        
        ctk.CTkLabel(
            input_frame, text="Hostname:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=(0, 10))
        
        self.host_entry = StyledEntry(input_frame, placeholder_text="example.com")
        self.host_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.host_entry.bind('<Return>', lambda e: self.check_certificate())
        
        ctk.CTkLabel(input_frame, text="Port:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(0, 5))
        
        self.port_entry = StyledEntry(input_frame, placeholder_text="443")
        self.port_entry.configure(width=80)
        self.port_entry.pack(side="left", padx=(0, 10))
        
        self.check_btn = StyledButton(
            input_frame,
            text="🔍 Check",
            command=self.check_certificate,
            variant="primary"
        )
        self.check_btn.pack(side="left")
        
        # Status card
        self.status_card = StyledCard(scrollable, variant="elevated")
        self.status_card.pack(fill="x", pady=(0, SPACING['md']))
        
        status_frame = ctk.CTkFrame(self.status_card, fg_color="transparent")
        status_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])
        
        self.status_icon = ctk.CTkLabel(
            status_frame,
            text="🔐",
            font=ctk.CTkFont(size=48)
        )
        self.status_icon.pack(side="left", padx=(0, SPACING['md']))
        
        status_info = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_info.pack(side="left", fill="x", expand=True)
        
        self.status_label = ctk.CTkLabel(
            status_info,
            text="Enter a hostname to check",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        self.status_label.pack(fill="x")
        
        self.expiry_label = ctk.CTkLabel(
            status_info,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        self.expiry_label.pack(fill="x")
        
        # Details card
        details_card = StyledCard(scrollable, variant="elevated")
        details_card.pack(fill="both", expand=True, pady=(0, SPACING['md']))
        
        details_title = ctk.CTkLabel(
            details_card,
            text="📋 Certificate Details",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        details_title.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        self.details_text = ctk.CTkTextbox(
            details_card,
            height=300,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=COLORS.get('bg_card', ("gray95", "gray20"))
        )
        self.details_text.pack(fill="both", expand=True, padx=SPACING['md'], pady=(0, SPACING['md']))
    
    def check_certificate(self):
        """Check SSL certificate"""
        host = self.host_entry.get().strip()
        port = self.port_entry.get().strip() or "443"
        
        if not host:
            self.app.show_toast("Please enter a hostname", "warning")
            return
        
        try:
            port = int(port)
        except:
            self.app.show_toast("Invalid port number", "warning")
            return
        
        self.check_btn.configure(state="disabled", text="⏳ Checking...")
        self.status_label.configure(text="Checking certificate...")
        self.expiry_label.configure(text="")
        self.details_text.delete("1.0", "end")
        
        thread = threading.Thread(target=self._do_check, args=(host, port), daemon=True)
        thread.start()
    
    def _do_check(self, host, port):
        """Perform certificate check in background"""
        try:
            context = ssl.create_default_context()
            
            with socket.create_connection((host, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()
            
            # Parse certificate
            subject = dict(x[0] for x in cert.get('subject', []))
            issuer = dict(x[0] for x in cert.get('issuer', []))
            
            not_before = datetime.datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
            not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            
            now = datetime.datetime.utcnow()
            days_left = (not_after - now).days
            
            # Determine status
            if days_left < 0:
                status = "expired"
                status_text = "❌ EXPIRED"
                status_color = COLORS['danger']
            elif days_left < 30:
                status = "warning"
                status_text = f"⚠️ Expires in {days_left} days"
                status_color = COLORS['warning']
            else:
                status = "valid"
                status_text = f"✅ Valid ({days_left} days remaining)"
                status_color = COLORS['success']
            
            # Format details
            san = cert.get('subjectAltName', [])
            san_list = [x[1] for x in san if x[0] == 'DNS']
            
            details = f"""═══════════════════════════════════════════════════════
  SSL CERTIFICATE REPORT - {host}:{port}
═══════════════════════════════════════════════════════

📜 SUBJECT
   Common Name:     {subject.get('commonName', 'N/A')}
   Organization:    {subject.get('organizationName', 'N/A')}
   Country:         {subject.get('countryName', 'N/A')}

🏢 ISSUER
   Common Name:     {issuer.get('commonName', 'N/A')}
   Organization:    {issuer.get('organizationName', 'N/A')}

📅 VALIDITY
   Not Before:      {not_before.strftime('%Y-%m-%d %H:%M:%S')} UTC
   Not After:       {not_after.strftime('%Y-%m-%d %H:%M:%S')} UTC
   Days Remaining:  {days_left}

🔐 CONNECTION
   Protocol:        {version}
   Cipher:          {cipher[0] if cipher else 'N/A'}
   Key Size:        {cipher[2] if cipher else 'N/A'} bits

🌐 SUBJECT ALT NAMES ({len(san_list)})
   {chr(10) + '   '.join(san_list[:10])}
   {'...(and more)' if len(san_list) > 10 else ''}

📋 SERIAL NUMBER
   {cert.get('serialNumber', 'N/A')}
"""
            
            self.app.after(0, lambda: self._show_results(status_text, status_color, f"Expires: {not_after.strftime('%Y-%m-%d')}", details))
            
        except ssl.SSLCertVerificationError as e:
            err_msg = str(e)
            self.app.after(0, lambda msg=err_msg: self._show_results("❌ Certificate Verification Failed", COLORS['danger'], msg, f"SSL Error: {msg}"))
        except Exception as e:
            err_msg = str(e)
            self.app.after(0, lambda msg=err_msg: self._show_results("❌ Connection Failed", COLORS['danger'], "", f"Error: {msg}"))
        
        finally:
            self.app.after(0, lambda: self.check_btn.configure(state="normal", text="🔍 Check"))
    
    def _show_results(self, status_text, status_color, expiry, details):
        """Display results"""
        self.status_label.configure(text=status_text, text_color=status_color)
        self.expiry_label.configure(text=expiry)
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", details)
        self.app.show_toast("Certificate check complete", "success")
