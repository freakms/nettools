"""
Bandwidth Tester UI Module
"""
import customtkinter as ctk
from tkinter import messagebox

from design_constants import COLORS, SPACING, RADIUS, FONTS
from ui_components import StyledCard, StyledButton, StyledEntry, SectionTitle, SubTitle
from tools.bandwidth_tester import BandwidthTester


class BandwidthUI:
    """Bandwidth Tester UI Component"""
    
    def __init__(self, app, parent):
        """
        Initialize Bandwidth Tester UI
        
        Args:
            app: Main application instance
            parent: Parent widget
        """
        self.app = app
        self.parent = parent
        
        # Initialize bandwidth tester
        self.bandwidth_tester = BandwidthTester()
        
        # Build UI
        self.create_content()
    
    def create_content(self):
        """Create bandwidth testing page"""
        self.parent.pack(fill="both", expand=True)
        
        # Check if iperf3 is available
        if not self.bandwidth_tester.is_iperf3_available():
            self.show_iperf3_not_installed()
            return
        
        # Scroll container
        scroll = ctk.CTkScrollableFrame(self.parent)
        scroll.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Header
        header_card = StyledCard(scroll)
        header_card.pack(fill="x", pady=(0, SPACING['md']))
        
        title = ctk.CTkLabel(
            header_card,
            text="🚀 Bandwidth Testing (iperf3)",
            font=ctk.CTkFont(size=FONTS['heading'], weight="bold")
        )
        title.pack(padx=SPACING['lg'], pady=SPACING['lg'])
        
        subtitle = SubTitle(
            header_card,
            text="Test network throughput and speed using iperf3"
        )
        subtitle.pack(padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Test Configuration Card
        config_card = StyledCard(scroll)
        config_card.pack(fill="x", pady=(0, SPACING['md']))
        
        config_title = SectionTitle(config_card, text="Test Configuration")
        config_title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        # Server Host
        host_label = ctk.CTkLabel(config_card, text="iperf3 Server Host *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        host_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['xs']))
        
        self.bandwidth_host = StyledEntry(config_card, placeholder_text="e.g., iperf.example.com or 192.168.1.100")
        self.bandwidth_host.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Settings row
        settings_frame = ctk.CTkFrame(config_card, fg_color="transparent")
        settings_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Port
        port_label = ctk.CTkLabel(settings_frame, text="Port:", font=ctk.CTkFont(size=FONTS['body']))
        port_label.pack(side="left", padx=(0, SPACING['xs']))
        
        self.bandwidth_port = StyledEntry(settings_frame, placeholder_text="5201", width=80)
        self.bandwidth_port.insert(0, "5201")
        self.bandwidth_port.pack(side="left", padx=(0, SPACING['md']))
        
        # Duration
        duration_label = ctk.CTkLabel(settings_frame, text="Duration (sec):", font=ctk.CTkFont(size=FONTS['body']))
        duration_label.pack(side="left", padx=(0, SPACING['xs']))
        
        self.bandwidth_duration = StyledEntry(settings_frame, placeholder_text="10", width=60)
        self.bandwidth_duration.insert(0, "10")
        self.bandwidth_duration.pack(side="left")
        
        # Test buttons
        btn_frame = ctk.CTkFrame(config_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        self.bandwidth_upload_btn = StyledButton(
            btn_frame,
            text="⬆ Upload Test",
            command=self.run_upload_test,
            size="large",
            variant="primary"
        )
        self.bandwidth_upload_btn.pack(side="left", fill="x", expand=True, padx=(0, SPACING['xs']))
        
        self.bandwidth_download_btn = StyledButton(
            btn_frame,
            text="⬇ Download Test",
            command=self.run_download_test,
            size="large",
            variant="success"
        )
        self.bandwidth_download_btn.pack(side="left", fill="x", expand=True, padx=(SPACING['xs'], 0))
        
        # Results Card
        results_card = StyledCard(scroll)
        results_card.pack(fill="both", expand=True)
        
        results_title = SectionTitle(results_card, text="Test Results")
        results_title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        self.bandwidth_results_frame = ctk.CTkFrame(results_card, fg_color="transparent")
        self.bandwidth_results_frame.pack(fill="both", expand=True, padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Empty state
        self.show_bandwidth_empty_state()
        
        # Info box
        info_card = StyledCard(scroll)
        info_card.pack(fill="x", pady=(SPACING['md'], 0))
        
        info_title = ctk.CTkLabel(
            info_card,
            text="ℹ️ About iperf3 Testing",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        info_title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['xs']))
        
        info_text = ctk.CTkLabel(
            info_card,
            text="iperf3 requires a server to test against. You can:\n\n" +
                 "• Use a public iperf3 server (search online)\n" +
                 "• Set up your own server: iperf3 -s\n" +
                 "• Upload Test: Measures your upload speed to server\n" +
                 "• Download Test: Measures your download speed from server",
            font=ctk.CTkFont(size=FONTS['small']),
            text_color=COLORS['text_secondary'],
            justify="left"
        )
        info_text.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['md']))
    
    def show_iperf3_not_installed(self):
        """Show iperf3 not installed message with instructions"""
        scroll = ctk.CTkScrollableFrame(self.parent)
        scroll.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Warning card
        warning_card = StyledCard(scroll)
        warning_card.pack(fill="both", expand=True)
        
        # Icon and title
        title = ctk.CTkLabel(
            warning_card,
            text="⚠️ iperf3 Not Installed",
            font=ctk.CTkFont(size=FONTS['heading'], weight="bold"),
            text_color=COLORS['warning']
        )
        title.pack(pady=(SPACING['lg'], SPACING['md']))
        
        # Message
        message = ctk.CTkLabel(
            warning_card,
            text="The bandwidth testing feature requires iperf3 to be installed on your system.",
            font=ctk.CTkFont(size=FONTS['body']),
            wraplength=600
        )
        message.pack(pady=(0, SPACING['lg']))
        
        # Installation instructions
        instructions_frame = ctk.CTkFrame(warning_card, fg_color=COLORS['bg_card'])
        instructions_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        inst_title = ctk.CTkLabel(
            instructions_frame,
            text="📥 Installation Instructions for Windows:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        inst_title.pack(anchor="w", padx=SPACING['md'], pady=(SPACING['md'], SPACING['xs']))
        
        instructions = """
Option 1: Using Chocolatey (Recommended)
  1. Install Chocolatey: https://chocolatey.org/install
  2. Open PowerShell as Administrator
  3. Run: choco install iperf3
  4. Restart this application

Option 2: Using Scoop
  1. Install Scoop: https://scoop.sh
  2. Open PowerShell
  3. Run: scoop install iperf3
  4. Restart this application

Option 3: Manual Installation
  1. Download from: https://iperf.fr/iperf-download.php
  2. Extract iperf3.exe to a folder
  3. Add folder to PATH environment variable
  4. Restart this application

Option 4: Using WSL (Windows Subsystem for Linux)
  1. Install WSL2
  2. In WSL terminal: sudo apt install iperf3
  3. Use from WSL terminal instead
        """
        
        inst_text = ctk.CTkLabel(
            instructions_frame,
            text=instructions,
            font=ctk.CTkFont(size=FONTS['small'], family="Consolas"),
            justify="left",
            anchor="w"
        )
        inst_text.pack(anchor="w", padx=SPACING['md'], pady=(0, SPACING['md']))
        
        # Refresh button
        refresh_btn = StyledButton(
            warning_card,
            text="🔄 Check Again",
            command=self.refresh_bandwidth_page,
            size="large",
            variant="primary"
        )
        refresh_btn.pack(pady=(0, SPACING['lg']))
        
        # Alternative info
        alt_card = StyledCard(scroll)
        alt_card.pack(fill="x", pady=(SPACING['md'], 0))
        
        alt_title = ctk.CTkLabel(
            alt_card,
            text="💡 Alternative",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        alt_title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['xs']))
        
        alt_text = ctk.CTkLabel(
            alt_card,
            text="You can also use online speed test websites like:\n" +
                 "• Speedtest.net\n" +
                 "• Fast.com\n" +
                 "• Google Speed Test (search 'internet speed test')",
            font=ctk.CTkFont(size=FONTS['small']),
            text_color=COLORS['text_secondary'],
            justify="left"
        )
        alt_text.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['md']))
    
    def refresh_bandwidth_page(self):
        """Refresh bandwidth page after iperf3 installation"""
        # Clear the page
        if "bandwidth" in self.app.pages:
            self.app.pages["bandwidth"].destroy()
            del self.app.pages["bandwidth"]
            self.app.pages_loaded.remove("bandwidth")
        
        # Reload the page
        self.app.switch_page("bandwidth")
    
    def show_bandwidth_empty_state(self):
        """Show empty state for bandwidth results"""
        for widget in self.bandwidth_results_frame.winfo_children():
            widget.destroy()
        
        empty_frame = ctk.CTkFrame(self.bandwidth_results_frame, fg_color="transparent")
        empty_frame.pack(fill="both", expand=True, pady=SPACING['xl'])
        
        empty_label = ctk.CTkLabel(
            empty_frame,
            text="📊\n\nNo test results yet\n\nRun an upload or download test to see results",
            font=ctk.CTkFont(size=FONTS['body']),
            text_color=COLORS['text_secondary'],
            justify="center"
        )
        empty_label.pack(expand=True)
    
    def run_upload_test(self):
        """Run upload speed test"""
        host = self.bandwidth_host.get().strip()
        port = self.bandwidth_port.get().strip() or "5201"
        duration = self.bandwidth_duration.get().strip() or "10"
        
        if not host:
            messagebox.showerror("Error", "Please enter an iperf3 server host")
            return
        
        try:
            port = int(port)
            duration = int(duration)
        except ValueError:
            messagebox.showerror("Error", "Port and duration must be numbers")
            return
        
        # Disable buttons during test
        self.bandwidth_upload_btn.configure(state="disabled", text="⬆ Testing...")
        self.bandwidth_download_btn.configure(state="disabled")
        
        self.show_bandwidth_testing()
        
        def callback(results, error):
            if error:
                messagebox.showerror("Test Failed", f"Upload test failed:\n{error}")
                self.show_bandwidth_empty_state()
            else:
                self.show_bandwidth_results(results, "Upload")
            
            self.bandwidth_upload_btn.configure(state="normal", text="⬆ Upload Test")
            self.bandwidth_download_btn.configure(state="normal")
        
        self.bandwidth_tester.test_client(host, port, duration, reverse=False, callback=callback)
    
    def run_download_test(self):
        """Run download speed test"""
        host = self.bandwidth_host.get().strip()
        port = self.bandwidth_port.get().strip() or "5201"
        duration = self.bandwidth_duration.get().strip() or "10"
        
        if not host:
            messagebox.showerror("Error", "Please enter an iperf3 server host")
            return
        
        try:
            port = int(port)
            duration = int(duration)
        except ValueError:
            messagebox.showerror("Error", "Port and duration must be numbers")
            return
        
        # Disable buttons during test
        self.bandwidth_upload_btn.configure(state="disabled")
        self.bandwidth_download_btn.configure(state="disabled", text="⬇ Testing...")
        
        self.show_bandwidth_testing()
        
        def callback(results, error):
            if error:
                messagebox.showerror("Test Failed", f"Download test failed:\n{error}")
                self.show_bandwidth_empty_state()
            else:
                self.show_bandwidth_results(results, "Download")
            
            self.bandwidth_upload_btn.configure(state="normal")
            self.bandwidth_download_btn.configure(state="normal", text="⬇ Download Test")
        
        self.bandwidth_tester.test_client(host, port, duration, reverse=True, callback=callback)
    
    def show_bandwidth_testing(self):
        """Show testing in progress"""
        for widget in self.bandwidth_results_frame.winfo_children():
            widget.destroy()
        
        testing_frame = ctk.CTkFrame(self.bandwidth_results_frame, fg_color="transparent")
        testing_frame.pack(fill="both", expand=True, pady=SPACING['xl'])
        
        testing_label = ctk.CTkLabel(
            testing_frame,
            text="⏳\n\nTest in progress...\n\nPlease wait",
            font=ctk.CTkFont(size=FONTS['body']),
            justify="center"
        )
        testing_label.pack(expand=True)
    
    def show_bandwidth_results(self, results, test_type):
        """Display bandwidth test results"""
        for widget in self.bandwidth_results_frame.winfo_children():
            widget.destroy()
        
        summary = self.bandwidth_tester.get_summary(results)
        
        if not summary:
            self.show_bandwidth_empty_state()
            return
        
        # Test type header
        type_label = ctk.CTkLabel(
            self.bandwidth_results_frame,
            text=f"✅ {test_type} Test Complete",
            font=ctk.CTkFont(size=FONTS['subheading'], weight="bold"),
            text_color=COLORS['success']
        )
        type_label.pack(pady=(0, SPACING['md']))
        
        # Main speed display
        if test_type == "Upload":
            speed = summary['sent_mbps']
        else:
            speed = summary['received_mbps']
        
        speed_card = ctk.CTkFrame(self.bandwidth_results_frame, fg_color=COLORS['bg_card'])
        speed_card.pack(fill="x", pady=(0, SPACING['md']))
        
        speed_label = ctk.CTkLabel(
            speed_card,
            text=f"{speed:.2f} Mbps",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        speed_label.pack(pady=SPACING['lg'])
        
        # Detailed results
        details_data = [
            ("Sent (Upload)", f"{summary['sent_mbps']:.2f} Mbps", f"{summary['sent_bytes'] / 1_000_000:.2f} MB"),
            ("Received (Download)", f"{summary['received_mbps']:.2f} Mbps", f"{summary['received_bytes'] / 1_000_000:.2f} MB"),
            ("Local CPU Usage", f"{summary['cpu_utilization_local']:.1f}%", ""),
            ("Remote CPU Usage", f"{summary['cpu_utilization_remote']:.1f}%", ""),
        ]
        
        for label, value1, value2 in details_data:
            row = ctk.CTkFrame(self.bandwidth_results_frame, fg_color="transparent")
            row.pack(fill="x", pady=SPACING['xs'])
            
            label_widget = ctk.CTkLabel(row, text=f"{label}:", font=ctk.CTkFont(size=FONTS['body'], weight="bold"), width=150, anchor="w")
            label_widget.pack(side="left")
            
            value_widget = ctk.CTkLabel(row, text=value1, font=ctk.CTkFont(size=FONTS['body']), anchor="w")
            value_widget.pack(side="left", padx=SPACING['sm'])
            
            if value2:
                value2_widget = ctk.CTkLabel(row, text=value2, font=ctk.CTkFont(size=FONTS['small']), text_color=COLORS['text_secondary'], anchor="w")
                value2_widget.pack(side="left")
