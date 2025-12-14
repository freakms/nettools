"""
Speedtest UI - Ookla Speedtest Integration
Provides internet speed testing using speedtest-cli (Ookla servers).
"""

import customtkinter as ctk
import threading
import time
from design_constants import COLORS, SPACING, FONTS
from ui_components import (
    StyledCard, StyledButton, SubTitle, InfoBox, Tooltip
)

try:
    import speedtest
    SPEEDTEST_AVAILABLE = True
except ImportError:
    SPEEDTEST_AVAILABLE = False


class SpeedtestUI:
    """
    UI for Ookla Speedtest integration
    """
    
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.is_running = False
        self.current_test = None
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
            text="Test your internet connection speed using Ookla servers"
        )
        subtitle.pack(anchor="w", pady=(0, SPACING['lg']))
        
        # Check availability
        if not SPEEDTEST_AVAILABLE:
            error_box = InfoBox(
                scrollable,
                message="speedtest-cli not installed. Run: pip install speedtest-cli",
                box_type="error"
            )
            error_box.pack(fill="x", pady=SPACING['md'])
            return
        
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
        
        # Server info card
        server_card = StyledCard(content_frame, variant="subtle")
        server_card.pack(fill="x", pady=SPACING['md'])
        
        server_title = ctk.CTkLabel(
            server_card,
            text="🌐 Server Information",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        server_title.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        self.server_info_label = ctk.CTkLabel(
            server_card,
            text="Server will be selected automatically",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        self.server_info_label.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        
        # Results history
        history_card = StyledCard(content_frame, variant="elevated")
        history_card.pack(fill="x", pady=SPACING['md'])
        
        history_title = ctk.CTkLabel(
            history_card,
            text="📊 Last Result Details",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        history_title.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        self.results_text = ctk.CTkTextbox(
            history_card,
            height=120,
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
        """Run speedtest in background thread"""
        try:
            # Initialize
            self._update_status("Initializing speedtest...", 0.1)
            st = speedtest.Speedtest()
            
            # Get best server
            self._update_status("Finding best server...", 0.2)
            st.get_best_server()
            
            server = st.best
            server_info = f"{server['sponsor']} - {server['name']}, {server['country']}\nHost: {server['host']}\nLatency: {server['latency']:.2f} ms"
            self.app.after(0, lambda: self.server_info_label.configure(text=server_info))
            
            # Test ping
            self._update_status("Testing ping...", 0.3)
            ping = server['latency']
            self.app.after(0, lambda: self._update_speed_card(self.ping_card, f"{ping:.1f}"))
            
            # Test download
            self._update_status("Testing download speed...", 0.4)
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            self.app.after(0, lambda: self._update_speed_card(self.download_card, f"{download_speed:.1f}"))
            self._update_status("Download complete", 0.7)
            
            # Test upload
            self._update_status("Testing upload speed...", 0.75)
            upload_speed = st.upload() / 1_000_000  # Convert to Mbps
            self.app.after(0, lambda: self._update_speed_card(self.upload_card, f"{upload_speed:.1f}"))
            
            # Complete
            self._update_status("Test complete!", 1.0)
            
            # Update results text
            results = st.results.dict()
            result_text = f"""═══════════════════════════════════════
  SPEEDTEST RESULTS - {time.strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════

  📥 Download:  {download_speed:.2f} Mbps
  📤 Upload:    {upload_speed:.2f} Mbps  
  📶 Ping:      {ping:.2f} ms

  🌐 Server:    {server['sponsor']}
  📍 Location:  {server['name']}, {server['country']}
  🔗 Host:      {server['host']}

  🖥️ Client IP: {results.get('client', {}).get('ip', 'N/A')}
  🏢 ISP:       {results.get('client', {}).get('isp', 'N/A')}
"""
            
            def update_results():
                self.results_text.configure(state="normal")
                self.results_text.delete("1.0", "end")
                self.results_text.insert("1.0", result_text)
                self.results_text.configure(state="disabled")
            
            self.app.after(0, update_results)
            self.app.after(0, lambda: self.app.show_toast(f"Speedtest complete: ↓{download_speed:.1f} Mbps ↑{upload_speed:.1f} Mbps", "success"))
            
        except Exception as ex:
            error_msg = str(ex)
            self._update_status(f"Error: {error_msg}", 0)
            self.app.after(0, lambda msg=error_msg: self.app.show_toast(f"Speedtest failed: {msg}", "error"))
        
        finally:
            self.is_running = False
            self.app.after(0, lambda: self.start_btn.configure(state="normal", text="▶️  Start Speedtest"))
    
    def _update_status(self, message, progress):
        """Update status label and progress bar"""
        self.app.after(0, lambda: self.status_label.configure(text=message))
        self.app.after(0, lambda: self.progress_bar.set(progress))
