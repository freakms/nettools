"""
Traceroute & Pathping UI Module
"""
import customtkinter as ctk
import threading
import platform
from tkinter import messagebox, filedialog
from pathlib import Path
from datetime import datetime

from design_constants import COLORS, FONTS, SPACING
from ui_components import StyledCard, StyledButton, StyledEntry, SectionTitle, SubTitle
from tools.traceroute import Traceroute
from tools.traceroute_manager import TracerouteManager


class TracerouteUI:
    """Traceroute & Pathping UI Component"""
    
    def __init__(self, app, parent):
        """
        Initialize Traceroute UI
        
        Args:
            app: Main application instance
            parent: Parent widget
        """
        self.app = app
        self.parent = parent
        
        # State tracking
        self.trace_running = False
        self.trace_process = None
        self.trace_results_text = ""
        self.current_target = ""
        
        # History manager
        self.trace_manager = TracerouteManager()
        
        # Build UI
        self.create_ui()
    
    def create_ui(self):
        """Create the Traceroute UI"""
        # Scrollable content area
        scrollable = ctk.CTkScrollableFrame(self.parent)
        scrollable.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            scrollable,
            text="Traceroute & Pathping",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 5))
        
        subtitle_label = ctk.CTkLabel(
            scrollable,
            text="Trace network path and analyze packet loss and latency",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        subtitle_label.pack(pady=(0, 5))
        
        # System info
        system_info = ctk.CTkLabel(
            scrollable,
            text=f"Platform: {platform.system()} | Note: Requires Windows for tracert/pathping commands",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        )
        system_info.pack(pady=(0, 15))
        
        # Input Section with styled card
        input_frame = StyledCard(scrollable)
        input_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        # Target input
        target_label = ctk.CTkLabel(
            input_frame,
            text="Target Host or IP:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        target_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        target_entry_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        target_entry_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        self.traceroute_target_entry = StyledEntry(
            target_entry_frame,
            placeholder_text="e.g., google.com or 8.8.8.8"
        )
        self.traceroute_target_entry.pack(side="left", fill="x", expand=True, padx=(0, SPACING['md']))
        
        # Tool Selection with styled card
        tool_frame = StyledCard(scrollable)
        tool_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        tool_label = ctk.CTkLabel(
            tool_frame,
            text="Select Tool:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        tool_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Tool radio buttons
        self.trace_tool_var = ctk.StringVar(value="tracert")
        
        tracert_frame = ctk.CTkFrame(tool_frame, fg_color="transparent")
        tracert_frame.pack(fill="x", padx=15, pady=(0, 5))
        
        tracert_radio = ctk.CTkRadioButton(
            tracert_frame,
            text="Traceroute (tracert)",
            variable=self.trace_tool_var,
            value="tracert",
            font=ctk.CTkFont(size=12)
        )
        tracert_radio.pack(side="left")
        
        tracert_info = ctk.CTkLabel(
            tracert_frame,
            text="Fast - Shows route path with latency per hop",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        )
        tracert_info.pack(side="left", padx=(10, 0))
        
        pathping_frame = ctk.CTkFrame(tool_frame, fg_color="transparent")
        pathping_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        pathping_radio = ctk.CTkRadioButton(
            pathping_frame,
            text="Pathping",
            variable=self.trace_tool_var,
            value="pathping",
            font=ctk.CTkFont(size=12)
        )
        pathping_radio.pack(side="left")
        
        pathping_info = ctk.CTkLabel(
            pathping_frame,
            text="Detailed - Includes packet loss statistics (takes ~5 minutes)",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        )
        pathping_info.pack(side="left", padx=(10, 0))
        
        # Options with styled card
        options_frame = StyledCard(scrollable)
        options_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        options_label = ctk.CTkLabel(
            options_frame,
            text="Options:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        options_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['md']))
        
        # Max hops option
        hops_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        hops_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        hops_label = ctk.CTkLabel(
            hops_frame,
            text="Max Hops:",
            font=ctk.CTkFont(size=FONTS['small'])
        )
        hops_label.pack(side="left")
        
        self.traceroute_maxhops_entry = StyledEntry(
            hops_frame,
            width=80,
            placeholder_text="30"
        )
        self.traceroute_maxhops_entry.insert(0, "30")
        self.traceroute_maxhops_entry.pack(side="left", padx=(SPACING['md'], 0))
        
        hops_info = ctk.CTkLabel(
            hops_frame,
            text="(Default: 30, Range: 1-255)",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        )
        hops_info.pack(side="left", padx=(10, 0))
        
        # Action Buttons
        button_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        self.trace_start_btn = StyledButton(
            button_frame,
            text="▶ Start Trace",
            command=self.start_traceroute,
            size="medium",
            variant="primary"
        )
        self.trace_start_btn.pack(side="left", padx=(0, SPACING['md']))
        
        self.trace_cancel_btn = StyledButton(
            button_frame,
            text="⏹ Cancel",
            command=self.cancel_traceroute,
            size="medium",
            variant="danger",
            state="disabled"
        )
        self.trace_cancel_btn.pack(side="left", padx=(0, SPACING['md']))
        
        self.trace_export_btn = StyledButton(
            button_frame,
            text="📤 Export Results",
            command=self.export_traceroute,
            size="medium",
            variant="success",
            state="disabled"
        )
        self.trace_export_btn.pack(side="left")
        
        # Progress label
        self.trace_progress_label = SubTitle(
            scrollable,
            text=""
        )
        self.trace_progress_label.pack(pady=(0, SPACING['md']))
        
        # Results Section
        results_title = SectionTitle(
            scrollable,
            text="Results"
        )
        results_title.pack(pady=(SPACING['md'], SPACING['md']), anchor="w")
        
        self.traceroute_results_frame = StyledCard(scrollable)
        self.traceroute_results_frame.pack(fill="both", expand=True)
        
        # Initial message
        no_results_label = ctk.CTkLabel(
            self.traceroute_results_frame,
            text="No results yet. Enter a target and start trace.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        no_results_label.pack(pady=50)
    
    def start_traceroute(self):
        """Start traceroute or pathping"""
        target = self.traceroute_target_entry.get().strip()
        if not target:
            messagebox.showwarning("Input Required", "Please enter a target host or IP address")
            return
        
        # Validate max hops
        try:
            max_hops = int(self.traceroute_maxhops_entry.get())
            if not 1 <= max_hops <= 255:
                raise ValueError()
        except:
            messagebox.showwarning("Invalid Input", "Max hops must be between 1 and 255")
            return
        
        # Update UI
        self.trace_start_btn.configure(state="disabled")
        self.trace_cancel_btn.configure(state="normal")
        self.trace_export_btn.configure(state="disabled")
        self.trace_running = True
        
        # Clear previous results
        for widget in self.traceroute_results_frame.winfo_children():
            widget.destroy()
        
        # Show progress
        tool_name = "Traceroute" if self.trace_tool_var.get() == "tracert" else "Pathping"
        time_estimate = "~30 seconds" if self.trace_tool_var.get() == "tracert" else "~5 minutes"
        self.trace_progress_label.configure(
            text=f"⏳ Running {tool_name} to {target}... (estimated time: {time_estimate})"
        )
        
        # Run in background thread using Traceroute module
        def trace_thread():
            tool = self.trace_tool_var.get()
            result = Traceroute.run(target, max_hops, tool, timeout=600)
            
            # Store results
            self.trace_results_text = result["output"]
            
            # Update UI in main thread
            self.app.after(0, self.display_traceroute_results, result["output"], result["success"])
        
        thread = threading.Thread(target=trace_thread, daemon=True)
        thread.start()
    
    def cancel_traceroute(self):
        """Cancel running trace"""
        self.trace_running = False
        if self.trace_process:
            try:
                self.trace_process.terminate()
            except:
                pass
        
        self.trace_start_btn.configure(state="normal")
        self.trace_cancel_btn.configure(state="disabled")
        self.trace_progress_label.configure(text="Trace cancelled")
    
    def display_traceroute_results(self, output, success):
        """Display traceroute/pathping results"""
        # Clear results frame
        for widget in self.traceroute_results_frame.winfo_children():
            widget.destroy()
        
        # Update UI state
        self.trace_start_btn.configure(state="normal")
        self.trace_cancel_btn.configure(state="disabled")
        self.trace_running = False
        
        if success:
            self.trace_progress_label.configure(text="✅ Trace complete")
            self.trace_export_btn.configure(state="normal")
        else:
            self.trace_progress_label.configure(text="❌ Trace failed or encountered errors")
            # Still allow export even if there are errors - might have partial results
            if output and len(output) > 50:
                self.trace_export_btn.configure(state="normal")
            else:
                self.trace_export_btn.configure(state="disabled")
        
        # Create info header
        info_frame = ctk.CTkFrame(self.traceroute_results_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=f"Output length: {len(output)} characters",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        info_label.pack(side="left")
        
        # Create scrollable text widget for results
        results_scroll = ctk.CTkScrollableFrame(self.traceroute_results_frame)
        results_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # If output is empty or very short, show helpful message
        if not output or len(output) < 10:
            error_label = ctk.CTkLabel(
                results_scroll,
                text="No output received from command.\n\nPossible causes:\n• Command not found on system\n• Insufficient permissions\n• Network adapter issue\n\nTry running NetTools as Administrator.",
                font=ctk.CTkFont(size=13),
                text_color=COLORS["danger"],
                justify="left"
            )
            error_label.pack(pady=20)
            return
        
        # Parse and display results with formatting
        lines = output.split('\n')
        
        # Show total line count
        line_count_label = ctk.CTkLabel(
            results_scroll,
            text=f"Total lines: {len(lines)}",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        line_count_label.pack(pady=(0, 10))
        
        for idx, line in enumerate(lines):
            # Keep empty lines for spacing but limit consecutive empties
            if not line.strip():
                ctk.CTkLabel(results_scroll, text=" ", height=5).pack()
                continue
            
            # Color code different types of lines
            text_color = COLORS["text_primary"]
            font_weight = "normal"
            
            # Headers
            if "Tracing" in line or "Computing" in line or "over a maximum" in line:
                text_color = COLORS["primary"]
                font_weight = "bold"
            # Hop numbers (lines starting with numbers)
            elif line.strip() and line.strip()[0].isdigit():
                text_color = COLORS["text_primary"]
            # Timeouts
            elif "*" in line or "Request timed out" in line or "timed out" in line.lower():
                text_color = COLORS["warning"]
            # Errors
            elif "error" in line.lower() or "failed" in line.lower() or "unable" in line.lower():
                text_color = COLORS["danger"]
                font_weight = "bold"
            # Summary lines (pathping)
            elif "%" in line or "Loss" in line or "Sent" in line:
                text_color = COLORS["success"]
            # Complete messages
            elif "complete" in line.lower():
                text_color = COLORS["success"]
                font_weight = "bold"
            
            line_label = ctk.CTkLabel(
                results_scroll,
                text=line,
                font=ctk.CTkFont(size=12, weight=font_weight, family="Courier New"),
                anchor="w",
                justify="left",
                text_color=text_color
            )
            line_label.pack(fill="x", pady=2)
    
    def export_traceroute(self):
        """Export traceroute results"""
        if not self.trace_results_text:
            messagebox.showinfo("No Data", "No traceroute data to export")
            return
        
        # Get desktop path
        desktop = Path.home() / "Desktop"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = self.traceroute_target_entry.get().strip().replace(".", "_")
        tool = "tracert" if self.trace_tool_var.get() == "tracert" else "pathping"
        default_filename = f"{tool}_{target}_{timestamp}.txt"
        
        # Ask for save location
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=desktop,
            initialfile=default_filename
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Traceroute/Pathping Results\n")
                f.write(f"=" * 60 + "\n")
                f.write(f"Target: {self.traceroute_target_entry.get()}\n")
                f.write(f"Tool: {self.trace_tool_var.get()}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"=" * 60 + "\n\n")
                f.write(self.trace_results_text)
            
            messagebox.showinfo(
                "Export Successful",
                f"Results exported to:\n{filepath}"
            )
        except Exception as e:
            messagebox.showerror(
                "Export Error",
                f"Error exporting results: {str(e)}"
            )
