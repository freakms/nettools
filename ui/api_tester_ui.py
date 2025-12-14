"""
HTTP/API Tester UI - Test REST APIs (mini-Postman)
"""

import customtkinter as ctk
import threading
import urllib.request
import urllib.parse
import json
import time
import ssl
from design_constants import COLORS, SPACING, FONTS
from ui_components import StyledCard, StyledButton, StyledEntry, SubTitle


class APITesterUI:
    """HTTP/API Tester Tool"""
    
    METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']
    
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.headers = {}
        self.create_content()
    
    def create_content(self):
        """Create the API Tester page"""
        scrollable = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        scrollable.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Title
        title = ctk.CTkLabel(
            scrollable,
            text="📡 HTTP/API Tester",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS['electric_violet']
        )
        title.pack(anchor="w", pady=(0, SPACING['xs']))
        
        subtitle = SubTitle(scrollable, text="Test REST APIs and HTTP endpoints")
        subtitle.pack(anchor="w", pady=(0, SPACING['lg']))
        
        # Request card
        request_card = StyledCard(scrollable, variant="elevated")
        request_card.pack(fill="x", pady=(0, SPACING['md']))
        
        # URL row
        url_frame = ctk.CTkFrame(request_card, fg_color="transparent")
        url_frame.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        self.method_var = ctk.StringVar(value="GET")
        self.method_menu = ctk.CTkOptionMenu(
            url_frame,
            values=self.METHODS,
            variable=self.method_var,
            width=100,
            fg_color=COLORS['electric_violet'],
            button_color=COLORS['electric_violet_hover'],
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.method_menu.pack(side="left", padx=(0, 10))
        
        self.url_entry = StyledEntry(url_frame, placeholder_text="https://api.example.com/endpoint")
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.url_entry.bind('<Return>', lambda e: self.send_request())
        
        self.send_btn = StyledButton(
            url_frame,
            text="▶️ Send",
            command=self.send_request,
            variant="primary"
        )
        self.send_btn.pack(side="left")
        
        # Tabs for Headers, Body, Params
        tabs_frame = ctk.CTkFrame(request_card, fg_color="transparent")
        tabs_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['sm'])
        
        self.active_tab = ctk.StringVar(value="headers")
        
        for tab_id, tab_label in [("headers", "Headers"), ("body", "Body"), ("params", "Params")]:
            btn = ctk.CTkButton(
                tabs_frame,
                text=tab_label,
                width=80,
                height=30,
                corner_radius=6,
                fg_color=COLORS['electric_violet'] if tab_id == "headers" else "transparent",
                hover_color=COLORS['electric_violet_hover'],
                command=lambda t=tab_id: self._switch_tab(t)
            )
            btn.pack(side="left", padx=(0, 5))
            setattr(self, f"{tab_id}_tab_btn", btn)
        
        # Headers input
        self.headers_frame = ctk.CTkFrame(request_card, fg_color="transparent")
        self.headers_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        
        self.headers_text = ctk.CTkTextbox(
            self.headers_frame, height=80,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=COLORS.get('bg_card', ("gray95", "gray20"))
        )
        self.headers_text.pack(fill="x")
        self.headers_text.insert("1.0", "Content-Type: application/json\nAccept: application/json")
        
        # Body input (hidden by default)
        self.body_frame = ctk.CTkFrame(request_card, fg_color="transparent")
        
        self.body_text = ctk.CTkTextbox(
            self.body_frame, height=120,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=COLORS.get('bg_card', ("gray95", "gray20"))
        )
        self.body_text.pack(fill="x")
        self.body_text.insert("1.0", '{\n  "key": "value"\n}')
        
        # Params input (hidden by default)
        self.params_frame = ctk.CTkFrame(request_card, fg_color="transparent")
        
        self.params_text = ctk.CTkTextbox(
            self.params_frame, height=80,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=COLORS.get('bg_card', ("gray95", "gray20"))
        )
        self.params_text.pack(fill="x")
        self.params_text.insert("1.0", "key1=value1\nkey2=value2")
        
        # Response card
        response_card = StyledCard(scrollable, variant="elevated")
        response_card.pack(fill="both", expand=True, pady=(0, SPACING['md']))
        
        response_header = ctk.CTkFrame(response_card, fg_color="transparent")
        response_header.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        ctk.CTkLabel(
            response_header, text="📥 Response",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        self.status_label = ctk.CTkLabel(
            response_header, text="",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.status_label.pack(side="left", padx=(15, 0))
        
        self.time_label = ctk.CTkLabel(
            response_header, text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary']
        )
        self.time_label.pack(side="right")
        
        # Response tabs
        resp_tabs = ctk.CTkFrame(response_card, fg_color="transparent")
        resp_tabs.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))
        
        self.resp_tab = ctk.StringVar(value="body")
        
        for tab_id, tab_label in [("body", "Body"), ("headers", "Headers")]:
            btn = ctk.CTkButton(
                resp_tabs,
                text=tab_label,
                width=80,
                height=28,
                corner_radius=6,
                fg_color=COLORS['neon_cyan'] if tab_id == "body" else "transparent",
                hover_color=COLORS['neon_cyan_hover'],
                command=lambda t=tab_id: self._switch_resp_tab(t)
            )
            btn.pack(side="left", padx=(0, 5))
            setattr(self, f"resp_{tab_id}_btn", btn)
        
        self.response_text = ctk.CTkTextbox(
            response_card, height=300,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=COLORS.get('bg_card', ("gray95", "gray20"))
        )
        self.response_text.pack(fill="both", expand=True, padx=SPACING['md'], pady=(0, SPACING['md']))
        
        self.response_headers_data = ""
        self.response_body_data = ""
    
    def _switch_tab(self, tab_id):
        """Switch request tabs"""
        self.active_tab.set(tab_id)
        
        for t in ["headers", "body", "params"]:
            btn = getattr(self, f"{t}_tab_btn")
            frame = getattr(self, f"{t}_frame")
            
            if t == tab_id:
                btn.configure(fg_color=COLORS['electric_violet'])
                frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
            else:
                btn.configure(fg_color="transparent")
                frame.pack_forget()
    
    def _switch_resp_tab(self, tab_id):
        """Switch response tabs"""
        self.resp_tab.set(tab_id)
        
        self.resp_body_btn.configure(fg_color=COLORS['neon_cyan'] if tab_id == "body" else "transparent")
        self.resp_headers_btn.configure(fg_color=COLORS['neon_cyan'] if tab_id == "headers" else "transparent")
        
        self.response_text.delete("1.0", "end")
        if tab_id == "body":
            self.response_text.insert("1.0", self.response_body_data)
        else:
            self.response_text.insert("1.0", self.response_headers_data)
    
    def send_request(self):
        """Send HTTP request"""
        url = self.url_entry.get().strip()
        if not url:
            self.app.show_toast("Please enter a URL", "warning")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        self.send_btn.configure(state="disabled", text="⏳ Sending...")
        self.status_label.configure(text="", text_color=COLORS['text_primary'])
        self.time_label.configure(text="")
        
        thread = threading.Thread(target=self._do_request, args=(url,), daemon=True)
        thread.start()
    
    def _do_request(self, url):
        """Perform request in background"""
        try:
            method = self.method_var.get()
            
            # Parse headers
            headers = {}
            for line in self.headers_text.get("1.0", "end").strip().split("\n"):
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
            
            # Parse params
            params = {}
            for line in self.params_text.get("1.0", "end").strip().split("\n"):
                if '=' in line:
                    key, value = line.split('=', 1)
                    params[key.strip()] = value.strip()
            
            if params:
                url += ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
            
            # Get body
            body = None
            if method in ['POST', 'PUT', 'PATCH']:
                body_text = self.body_text.get("1.0", "end").strip()
                if body_text:
                    body = body_text.encode('utf-8')
            
            # Create request
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            
            # SSL context
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            # Send request
            start_time = time.time()
            
            with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
                elapsed = (time.time() - start_time) * 1000
                
                status_code = response.status
                status_reason = response.reason
                resp_headers = dict(response.headers)
                resp_body = response.read().decode('utf-8', errors='ignore')
            
            # Format response headers
            headers_text = f"HTTP/{response.version/10:.1f} {status_code} {status_reason}\n\n"
            for k, v in resp_headers.items():
                headers_text += f"{k}: {v}\n"
            
            # Try to format JSON
            try:
                json_data = json.loads(resp_body)
                resp_body = json.dumps(json_data, indent=2)
            except:
                pass
            
            self.response_headers_data = headers_text
            self.response_body_data = resp_body
            
            # Determine status color
            if status_code < 300:
                color = COLORS['success']
            elif status_code < 400:
                color = COLORS['warning']
            else:
                color = COLORS['danger']
            
            self.app.after(0, lambda: self._show_response(status_code, status_reason, color, elapsed))
            
        except urllib.error.HTTPError as e:
            err_code = e.code
            err_reason = str(e.reason)
            self.response_headers_data = f"HTTP Error: {err_code}"
            self.response_body_data = e.read().decode('utf-8', errors='ignore') if e.fp else str(e)
            self.app.after(0, lambda c=err_code, r=err_reason: self._show_response(c, r, COLORS['danger'], 0))
            
        except Exception as e:
            self.response_body_data = f"Error: {str(e)}"
            self.response_headers_data = ""
            self.app.after(0, lambda: self._show_response(0, "Error", COLORS['danger'], 0))
        
        finally:
            self.app.after(0, lambda: self.send_btn.configure(state="normal", text="▶️ Send"))
    
    def _show_response(self, status_code, status_text, color, elapsed):
        """Display response"""
        if status_code:
            self.status_label.configure(text=f"{status_code} {status_text}", text_color=color)
        else:
            self.status_label.configure(text=status_text, text_color=color)
        
        if elapsed:
            self.time_label.configure(text=f"{elapsed:.0f} ms")
        
        self.response_text.delete("1.0", "end")
        self.response_text.insert("1.0", self.response_body_data)
        
        self.app.show_toast("Request completed", "success" if status_code and status_code < 400 else "error")
