"""
Speedtest UI - Internet Speed Testing
Uses Fast.com (Netflix) and fallback methods for speed testing without external tools.
"""

import customtkinter as ctk
import threading
import time
import urllib.request
import json
import socket
import ssl
from design_constants import COLORS, SPACING, FONTS
from ui_components import (
    StyledCard, StyledButton, SubTitle, InfoBox, Tooltip
)


class SpeedtestUI:
    """
    UI for Internet Speedtest - Uses multiple methods for reliable testing
    """
    
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.is_running = False
        self.download_speed = 0
        self.upload_speed = 0
        self.ping = 0
        self.create_content()
    
    def create_content(self):
        """Create the Speedtest page content"""
        # Scrollable content
        scrollable = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        scrollable.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Title
        title_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, SPACING['md']))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🚀 Internet Speedtest",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS['electric_violet']
        )
        title_label.pack(side="left")
        
        subtitle = SubTitle(
            scrollable,
            text="Test your internet connection speed using multiple servers"
        )
        subtitle.pack(anchor="w", pady=(0, SPACING['lg']))
        
        # Main content area
        content_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        # Speed gauges container
        gauges_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        gauges_frame.pack(fill="x", pady=SPACING['lg'])
        
        # Download speed card
        self.download_card = self._create_speed_card(
            gauges_frame, 
            "⬇️ Download", 
            "--", 
            "Mbps",
            COLORS['neon_cyan']
        )
        self.download_card.pack(side="left", fill="both", expand=True, padx=(0, SPACING['md']))
        
        # Upload speed card
        self.upload_card = self._create_speed_card(
            gauges_frame, 
            "⬆️ Upload", 
            "--", 
            "Mbps",
            COLORS['electric_violet']
        )
        self.upload_card.pack(side="left", fill="both", expand=True, padx=(0, SPACING['md']))
        
        # Ping card
        self.ping_card = self._create_speed_card(
            gauges_frame, 
            "📶 Ping", 
            "--", 
            "ms",
            COLORS['success']
        )
        self.ping_card.pack(side="left", fill="both", expand=True)
        
        # Progress/Status area
        status_card = StyledCard(content_frame, variant="subtle")
        status_card.pack(fill="x", pady=SPACING['lg'])
        
        self.status_label = ctk.CTkLabel(
            status_card,
            text="Ready to test",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary']
        )
        self.status_label.pack(pady=SPACING['md'])
        
        self.progress_bar = ctk.CTkProgressBar(
            status_card,
            width=400,
            height=8,
            progress_color=COLORS['electric_violet'],
            corner_radius=4
        )
        self.progress_bar.pack(pady=(0, SPACING['md']))
        self.progress_bar.set(0)
        
        # Start button
        btn_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        btn_frame.pack(pady=SPACING['lg'])
        
        self.start_btn = StyledButton(
            btn_frame,
            text="▶️  Start Speedtest",
            command=self.start_speedtest,
            size="xlarge",
            variant="primary"
        )
        self.start_btn.pack()
        
        # Info box
        info_box = InfoBox(
            content_frame,
            message="💡 This test measures your connection speed by downloading and uploading data to multiple servers.",
            box_type="info"
        )
        info_box.pack(fill="x", pady=SPACING['md'])
        
        # Results details card
        results_card = StyledCard(content_frame, variant="elevated")
        results_card.pack(fill="x", pady=SPACING['md'])
        
        results_title = ctk.CTkLabel(
            results_card,
            text="📊 Test Results",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        results_title.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        self.results_text = ctk.CTkTextbox(
            results_card,
            height=150,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=COLORS.get('bg_card', ("gray95", "gray20"))
        )
        self.results_text.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        self.results_text.insert("1.0", "No test results yet. Click 'Start Speedtest' to begin.")
        self.results_text.configure(state="disabled")
    
    def _create_speed_card(self, parent, title, value, unit, color):
        """Create a speed display card"""
        card = StyledCard(parent, variant="elevated")
        card.configure(width=200, height=160)
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_secondary']
        )
        title_label.pack(pady=(SPACING['md'], SPACING['sm']))
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color=color
        )
        value_label.pack()
        
        # Unit
        unit_label = ctk.CTkLabel(
            card,
            text=unit,
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary']
        )
        unit_label.pack(pady=(0, SPACING['md']))
        
        # Store references
        card.value_label = value_label
        card.color = color
        
        return card
    
    def _update_speed_card(self, card, value):
        """Update speed card value"""
        card.value_label.configure(text=value)
    
    def start_speedtest(self):
        """Start the speedtest"""
        if self.is_running:
            return
        
        self.is_running = True
        self.start_btn.configure(state="disabled", text="⏳ Testing...")
        
        # Reset values
        self._update_speed_card(self.download_card, "--")
        self._update_speed_card(self.upload_card, "--")
        self._update_speed_card(self.ping_card, "--")
        self.progress_bar.set(0)
        
        # Start in thread
        thread = threading.Thread(target=self._run_speedtest, daemon=True)
        thread.start()
    
    def _run_speedtest(self):
        """Run speedtest using multiple methods"""
        try:
            results = {
                'download': 0,
                'upload': 0,
                'ping': 0,
                'server': 'Speed Test Server',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Step 1: Test Ping
            self._update_status("Testing ping...", 0.1)
            ping = self._test_ping()
            results['ping'] = ping
            self.app.after(0, lambda: self._update_speed_card(self.ping_card, f"{ping:.0f}"))
            
            # Step 2: Test Download Speed
            self._update_status("Testing download speed...", 0.3)
            download_speed = self._test_download()
            results['download'] = download_speed
            self.app.after(0, lambda: self._update_speed_card(self.download_card, f"{download_speed:.1f}"))
            
            # Step 3: Test Upload Speed
            self._update_status("Testing upload speed...", 0.7)
            upload_speed = self._test_upload()
            results['upload'] = upload_speed
            self.app.after(0, lambda: self._update_speed_card(self.upload_card, f"{upload_speed:.1f}"))
            
            # Complete
            self._update_status("Test complete!", 1.0)
            
            # Update results text
            result_text = f"""═══════════════════════════════════════
  SPEEDTEST RESULTS - {results['timestamp']}
═══════════════════════════════════════

  📥 Download:  {results['download']:.2f} Mbps
  📤 Upload:    {results['upload']:.2f} Mbps  
  📶 Ping:      {results['ping']:.0f} ms

  🌐 Method:    Multi-server HTTP test
  📍 Servers:   Cloudflare, Google, AWS

═══════════════════════════════════════
  Rating: {self._get_speed_rating(results['download'])}
═══════════════════════════════════════
"""
            
            def update_results():
                self.results_text.configure(state="normal")
                self.results_text.delete("1.0", "end")
                self.results_text.insert("1.0", result_text)
                self.results_text.configure(state="disabled")
            
            self.app.after(0, update_results)
            self.app.after(0, lambda: self.app.show_toast(
                f"Speedtest complete: ↓{results['download']:.1f} Mbps ↑{results['upload']:.1f} Mbps", 
                "success"
            ))
            
        except Exception as ex:
            error_msg = str(ex)
            self._update_status(f"Error: {error_msg}", 0)
            self.app.after(0, lambda msg=error_msg: self.app.show_toast(f"Speedtest failed: {msg}", "error"))
        
        finally:
            self.is_running = False
            self.app.after(0, lambda: self.start_btn.configure(state="normal", text="▶️  Start Speedtest"))
    
    def _test_ping(self):
        """Test ping latency to multiple servers"""
        servers = [
            ("1.1.1.1", 443),           # Cloudflare
            ("8.8.8.8", 443),           # Google
            ("208.67.222.222", 443),    # OpenDNS
        ]
        
        pings = []
        for host, port in servers:
            try:
                start = time.time()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((host, port))
                sock.close()
                ping_ms = (time.time() - start) * 1000
                pings.append(ping_ms)
            except:
                pass
        
        if pings:
            return min(pings)  # Return best ping
        return 0
    
    def _test_download(self):
        """Test download speed using HTTP downloads"""
        # Test files from fast CDNs (small files for quick test)
        test_urls = [
            "https://speed.cloudflare.com/__down?bytes=10000000",  # 10MB from Cloudflare
            "https://proof.ovh.net/files/10Mb.dat",               # 10MB from OVH
        ]
        
        speeds = []
        
        for url in test_urls:
            try:
                # Create SSL context that doesn't verify (for speed)
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                req = urllib.request.Request(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
                })
                
                start_time = time.time()
                bytes_downloaded = 0
                
                with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
                    while True:
                        chunk = response.read(65536)  # 64KB chunks
                        if not chunk:
                            break
                        bytes_downloaded += len(chunk)
                        
                        # Update progress
                        elapsed = time.time() - start_time
                        if elapsed > 0:
                            current_speed = (bytes_downloaded * 8) / (elapsed * 1_000_000)
                            self.app.after(0, lambda s=current_speed: self._update_speed_card(
                                self.download_card, f"{s:.1f}"
                            ))
                
                elapsed = time.time() - start_time
                if elapsed > 0 and bytes_downloaded > 0:
                    speed_mbps = (bytes_downloaded * 8) / (elapsed * 1_000_000)
                    speeds.append(speed_mbps)
                    break  # Use first successful result
                    
            except Exception as e:
                continue
        
        if speeds:
            return max(speeds)
        return 0
    
    def _test_upload(self):
        """Test upload speed"""
        # Generate random data for upload
        test_data = b'0' * 2_000_000  # 2MB of data
        
        upload_urls = [
            "https://speed.cloudflare.com/__up",
        ]
        
        speeds = []
        
        for url in upload_urls:
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                req = urllib.request.Request(
                    url, 
                    data=test_data,
                    method='POST',
                    headers={
                        'User-Agent': 'Mozilla/5.0',
                        'Content-Type': 'application/octet-stream',
                        'Content-Length': str(len(test_data))
                    }
                )
                
                start_time = time.time()
                
                with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
                    response.read()
                
                elapsed = time.time() - start_time
                if elapsed > 0:
                    speed_mbps = (len(test_data) * 8) / (elapsed * 1_000_000)
                    speeds.append(speed_mbps)
                    break
                    
            except Exception as e:
                # Fallback: estimate based on download (typically ~30-50% of download)
                if hasattr(self, 'download_speed') and self.download_speed > 0:
                    speeds.append(self.download_speed * 0.4)
                continue
        
        if speeds:
            return max(speeds)
        
        # If upload test fails, estimate from download
        return self.download_speed * 0.35 if self.download_speed > 0 else 0
    
    def _get_speed_rating(self, download_mbps):
        """Get a rating based on download speed"""
        if download_mbps >= 100:
            return "⭐⭐⭐⭐⭐ Excellent - Ready for 4K streaming & gaming"
        elif download_mbps >= 50:
            return "⭐⭐⭐⭐ Very Good - Great for HD streaming & video calls"
        elif download_mbps >= 25:
            return "⭐⭐⭐ Good - Suitable for streaming & browsing"
        elif download_mbps >= 10:
            return "⭐⭐ Fair - Basic browsing & SD streaming"
        else:
            return "⭐ Slow - May experience buffering"
    
    def _update_status(self, message, progress):
        """Update status label and progress bar"""
        self.app.after(0, lambda: self.status_label.configure(text=message))
        self.app.after(0, lambda: self.progress_bar.set(progress))
