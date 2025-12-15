"""
Remote Tools UI - PSExec and iPerf Interface
Provides UI for remote command execution and bandwidth testing.
"""

import customtkinter as ctk
import threading
from design_constants import COLORS, SPACING, RADIUS, FONTS
from ui_components import (
    StyledCard, StyledButton, StyledEntry, SectionTitle, SubTitle,
    InfoBox, Tooltip, LoadingSpinner
)
from tools.remote_tools import PSExecTool, IPerfTool, get_remote_tools


class RemoteToolsUI:
    """
    UI for Remote Tools (PSExec and iPerf integration)
    """
    
    def __init__(self, app):
        self.app = app
        self.psexec_tool, self.iperf_tool = get_remote_tools()
        
        # Credential storage (session only)
        self.saved_username = ""
        self.saved_password = ""
        self.saved_domain = ""
    
    def create_content(self, parent):
        """Create the Remote Tools page content"""
        # Scrollable content
        scrollable = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scrollable.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Title
        title_label = ctk.CTkLabel(
            scrollable,
            text="🖥️ Remote Tools",
            font=ctk.CTkFont(size=FONTS['title'], weight="bold"),
            text_color=COLORS['electric_violet']
        )
        title_label.pack(pady=(0, SPACING['xs']))
        
        subtitle = SubTitle(
            scrollable,
            text="Execute remote commands with PSExec and run bandwidth tests with iPerf3"
        )
        subtitle.pack(pady=(0, SPACING['lg']))
        
        # Tool availability status
        self._create_status_section(scrollable)
        
        # Credentials section
        self._create_credentials_section(scrollable)
        
        # PSExec section
        self._create_psexec_section(scrollable)
        
        # iPerf section
        self._create_iperf_section(scrollable)
    
    def _create_status_section(self, parent):
        """Create tool availability status section"""
        status_card = StyledCard(parent)
        status_card.pack(fill="x", pady=(0, SPACING['lg']))
        
        # Status title
        status_title = ctk.CTkLabel(
            status_card,
            text="📊 Tool Availability",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        status_title.pack(padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']), anchor="w")
        
        status_frame = ctk.CTkFrame(status_card, fg_color="transparent")
        status_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        
        # PSExec status
        psexec_icon = "✅" if self.psexec_tool.is_available else "❌"
        psexec_text = f"{psexec_icon} PSExec: {'Available' if self.psexec_tool.is_available else 'Not Found'}"
        if self.psexec_tool.is_available:
            psexec_text += f" ({self.psexec_tool.psexec_path})"
        
        psexec_label = ctk.CTkLabel(
            status_frame,
            text=psexec_text,
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        psexec_label.pack(fill="x", pady=2)
        
        # iPerf status
        iperf_icon = "✅" if self.iperf_tool.is_available else "❌"
        iperf_text = f"{iperf_icon} iPerf3: {'Available' if self.iperf_tool.is_available else 'Not Found'}"
        if self.iperf_tool.is_available:
            iperf_text += f" ({self.iperf_tool.iperf_path})"
        
        iperf_label = ctk.CTkLabel(
            status_frame,
            text=iperf_text,
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        iperf_label.pack(fill="x", pady=2)
        
        # Download links if not available
        if not self.psexec_tool.is_available or not self.iperf_tool.is_available:
            info_box = InfoBox(
                status_card,
                message="💡 Download: PSExec from Microsoft Sysinternals, iPerf3 from iperf.fr",
                box_type="info"
            )
            info_box.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
    
    def _create_credentials_section(self, parent):
        """Create credentials input section"""
        cred_card = StyledCard(parent)
        cred_card.pack(fill="x", pady=(0, SPACING['lg']))
        
        cred_title = ctk.CTkLabel(
            cred_card,
            text="🔐 Remote Credentials",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        cred_title.pack(padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']), anchor="w")
        
        cred_desc = ctk.CTkLabel(
            cred_card,
            text="Enter credentials for cross-domain remote access (uses 'net use' session)",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary']
        )
        cred_desc.pack(padx=SPACING['md'], pady=(0, SPACING['sm']), anchor="w")
        
        # Use current session checkbox
        self.use_current_session_var = ctk.BooleanVar(value=False)
        current_session_cb = ctk.CTkCheckBox(
            cred_card,
            text="Use current Windows session (same domain, app running as admin)",
            variable=self.use_current_session_var,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS['electric_violet'],
            command=self._toggle_cred_fields
        )
        current_session_cb.pack(padx=SPACING['md'], pady=(0, SPACING['sm']), anchor="w")
        
        self.cred_frame = ctk.CTkFrame(cred_card, fg_color="transparent")
        self.cred_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        
        # Domain
        domain_label = ctk.CTkLabel(self.cred_frame, text="Domain:", font=ctk.CTkFont(size=12), width=80, anchor="e")
        domain_label.grid(row=0, column=0, padx=(0, 10), pady=5)
        self.domain_entry = StyledEntry(self.cred_frame, placeholder_text="DOMAIN (e.g., CORP)")
        self.domain_entry.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Username
        user_label = ctk.CTkLabel(self.cred_frame, text="Username:", font=ctk.CTkFont(size=12), width=80, anchor="e")
        user_label.grid(row=1, column=0, padx=(0, 10), pady=5)
        self.username_entry = StyledEntry(self.cred_frame, placeholder_text="admin.user")
        self.username_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Password
        pass_label = ctk.CTkLabel(self.cred_frame, text="Password:", font=ctk.CTkFont(size=12), width=80, anchor="e")
        pass_label.grid(row=2, column=0, padx=(0, 10), pady=5)
        self.password_entry = StyledEntry(self.cred_frame, placeholder_text="••••••••")
        self.password_entry.configure(show="•")
        self.password_entry.grid(row=2, column=1, sticky="ew", pady=5)
        
        self.cred_frame.columnconfigure(1, weight=1)
        
        # Info about how it works
        info_label = ctk.CTkLabel(
            cred_card,
            text="💡 Credentials establish a network session via 'net use' before running PSExec",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['neon_cyan']
        )
        info_label.pack(padx=SPACING['md'], pady=(0, SPACING['md']), anchor="w")
        
        # Show credential fields by default (not using current session)
        self._toggle_cred_fields()
    
    def _toggle_cred_fields(self):
        """Toggle visibility of credential input fields"""
        if self.use_current_session_var.get():
            # Hide credential fields
            for widget in self.cred_frame.winfo_children():
                widget.grid_remove()
        else:
            # Show credential fields
            for widget in self.cred_frame.winfo_children():
                widget.grid()
    
    def _create_psexec_section(self, parent):
        """Create PSExec section"""
        psexec_card = StyledCard(parent)
        psexec_card.pack(fill="x", pady=(0, SPACING['lg']))
        
        # Title
        title_frame = ctk.CTkFrame(psexec_card, fg_color="transparent")
        title_frame.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        psexec_title = ctk.CTkLabel(
            title_frame,
            text="🖥️ PSExec - Remote Command Execution",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        psexec_title.pack(side="left")
        
        # Target host input
        target_frame = ctk.CTkFrame(psexec_card, fg_color="transparent")
        target_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))
        
        target_label = ctk.CTkLabel(target_frame, text="Target Host:", font=ctk.CTkFont(size=12))
        target_label.pack(side="left", padx=(0, 10))
        
        self.psexec_target_entry = StyledEntry(target_frame, placeholder_text="192.168.1.100 or hostname")
        self.psexec_target_entry.pack(side="left", fill="x", expand=True)
        
        # Command input
        cmd_frame = ctk.CTkFrame(psexec_card, fg_color="transparent")
        cmd_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))
        
        cmd_label = ctk.CTkLabel(cmd_frame, text="Command:", font=ctk.CTkFont(size=12))
        cmd_label.pack(side="left", padx=(0, 10))
        
        self.psexec_cmd_entry = StyledEntry(cmd_frame, placeholder_text="ipconfig /all")
        self.psexec_cmd_entry.pack(side="left", fill="x", expand=True)
        
        # Action buttons
        btn_frame = ctk.CTkFrame(psexec_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['sm'])
        
        self.run_cmd_btn = StyledButton(
            btn_frame,
            text="▶ Execute Command",
            command=self._run_psexec_command,
            variant="primary"
        )
        self.run_cmd_btn.pack(side="left", padx=(0, 10))
        Tooltip(self.run_cmd_btn, "Execute the command on the remote host")
        
        self.start_cmd_btn = StyledButton(
            btn_frame,
            text="🖥️ Remote CMD (PSExec)",
            command=self._start_remote_cmd,
            variant="neutral"
        )
        self.start_cmd_btn.pack(side="left", padx=(0, 10))
        Tooltip(self.start_cmd_btn, "Open an interactive CMD window using PSExec")
        
        self.start_ps_btn = StyledButton(
            btn_frame,
            text="💠 Remote PowerShell (WinRM)",
            command=self._start_ps_remoting,
            variant="neutral"
        )
        self.start_ps_btn.pack(side="left", padx=(0, 10))
        Tooltip(self.start_ps_btn, "Open PowerShell Remoting session (requires WinRM on target)")
        
        self.start_ssh_btn = StyledButton(
            btn_frame,
            text="🔐 SSH",
            command=self._start_ssh_session,
            variant="neutral"
        )
        self.start_ssh_btn.pack(side="left", padx=(0, 10))
        Tooltip(self.start_ssh_btn, "Connect via SSH (if OpenSSH is enabled on target)")
        
        # Second row of buttons - setup
        btn_frame2 = ctk.CTkFrame(psexec_card, fg_color="transparent")
        btn_frame2.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))
        
        self.setup_winrm_btn = StyledButton(
            btn_frame2,
            text="⚙️ Setup WinRM TrustedHosts (one-time)",
            command=self._setup_trustedhosts,
            variant="secondary"
        )
        self.setup_winrm_btn.pack(side="left", padx=(0, 10))
        Tooltip(self.setup_winrm_btn, "Set TrustedHosts to * to allow all connections (run as Admin)")
        
        # Output area
        output_label = ctk.CTkLabel(
            psexec_card,
            text="Output:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        output_label.pack(fill="x", padx=SPACING['md'], pady=(SPACING['sm'], SPACING['xs']))
        
        self.psexec_output = ctk.CTkTextbox(
            psexec_card,
            height=150,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=COLORS['bg_card']
        )
        self.psexec_output.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
    
    def _create_iperf_section(self, parent):
        """Create iPerf section"""
        iperf_card = StyledCard(parent)
        iperf_card.pack(fill="x", pady=(0, SPACING['lg']))
        
        # Title
        iperf_title = ctk.CTkLabel(
            iperf_card,
            text="📶 iPerf3 - Bandwidth Testing",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        iperf_title.pack(padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']), anchor="w")
        
        # Target input
        target_frame = ctk.CTkFrame(iperf_card, fg_color="transparent")
        target_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))
        
        target_label = ctk.CTkLabel(target_frame, text="Server Host:", font=ctk.CTkFont(size=12))
        target_label.pack(side="left", padx=(0, 10))
        
        self.iperf_target_entry = StyledEntry(target_frame, placeholder_text="192.168.1.100 or hostname")
        self.iperf_target_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        port_label = ctk.CTkLabel(target_frame, text="Port:", font=ctk.CTkFont(size=12))
        port_label.pack(side="left", padx=(0, 5))
        
        self.iperf_port_entry = StyledEntry(target_frame, placeholder_text="5201")
        self.iperf_port_entry.configure(width=80)
        self.iperf_port_entry.pack(side="left")
        
        # Options
        options_frame = ctk.CTkFrame(iperf_card, fg_color="transparent")
        options_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))
        
        duration_label = ctk.CTkLabel(options_frame, text="Duration (s):", font=ctk.CTkFont(size=12))
        duration_label.pack(side="left", padx=(0, 5))
        
        self.iperf_duration_entry = StyledEntry(options_frame, placeholder_text="10")
        self.iperf_duration_entry.configure(width=60)
        self.iperf_duration_entry.pack(side="left", padx=(0, 15))
        
        self.iperf_reverse_var = ctk.BooleanVar(value=False)
        reverse_check = ctk.CTkCheckBox(
            options_frame,
            text="Reverse (download)",
            variable=self.iperf_reverse_var,
            font=ctk.CTkFont(size=12)
        )
        reverse_check.pack(side="left", padx=(0, 15))
        
        self.iperf_udp_var = ctk.BooleanVar(value=False)
        udp_check = ctk.CTkCheckBox(
            options_frame,
            text="UDP mode",
            variable=self.iperf_udp_var,
            font=ctk.CTkFont(size=12)
        )
        udp_check.pack(side="left")
        
        # Action buttons
        btn_frame = ctk.CTkFrame(iperf_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['sm'])
        
        self.run_iperf_btn = StyledButton(
            btn_frame,
            text="▶ Run Bandwidth Test",
            command=self._run_iperf_test,
            variant="primary"
        )
        self.run_iperf_btn.pack(side="left", padx=(0, 10))
        
        self.start_server_btn = StyledButton(
            btn_frame,
            text="🖥️ Start Server",
            command=self._start_iperf_server,
            variant="neutral"
        )
        self.start_server_btn.pack(side="left", padx=(0, 10))
        Tooltip(self.start_server_btn, "Start iPerf3 server on this machine")
        
        self.copy_iperf_btn = StyledButton(
            btn_frame,
            text="📤 Copy iPerf to Remote",
            command=self._copy_iperf_to_remote,
            variant="neutral"
        )
        self.copy_iperf_btn.pack(side="left")
        Tooltip(self.copy_iperf_btn, "Copy iPerf3 to target host for testing")
        
        # Output area
        output_label = ctk.CTkLabel(
            iperf_card,
            text="Test Results:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        output_label.pack(fill="x", padx=SPACING['md'], pady=(SPACING['sm'], SPACING['xs']))
        
        self.iperf_output = ctk.CTkTextbox(
            iperf_card,
            height=150,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=COLORS['bg_card']
        )
        self.iperf_output.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
    
    def _get_credentials(self):
        """Get credentials from input fields"""
        return {
            'username': self.username_entry.get().strip() or None,
            'password': self.password_entry.get().strip() or None,
            'domain': self.domain_entry.get().strip() or None,
            'use_current_credentials': self.use_current_session_var.get()
        }
    
    def _run_psexec_command(self):
        """Execute PSExec command"""
        target = self.psexec_target_entry.get().strip()
        command = self.psexec_cmd_entry.get().strip()
        
        if not target:
            self.app.show_toast("Please enter a target host", "warning")
            return
        
        if not command:
            self.app.show_toast("Please enter a command to execute", "warning")
            return
        
        if not self.psexec_tool.is_available:
            self.app.show_toast("PSExec not found", "error")
            return
        
        creds = self._get_credentials()
        
        self.psexec_output.delete("1.0", "end")
        
        if creds['use_current_credentials']:
            self.psexec_output.insert("end", f"Executing on {target} using current session credentials: {command}\n")
            self.psexec_output.insert("end", "⚠️ Make sure this app is running as Administrator!\n\n")
        else:
            # Show debug info
            user_display = f"{creds['domain']}\\{creds['username']}" if creds['domain'] else creds['username']
            self.psexec_output.insert("end", f"Target: {target}\n")
            self.psexec_output.insert("end", f"User: {user_display}\n")
            self.psexec_output.insert("end", f"Command: {command}\n")
            self.psexec_output.insert("end", f"PSExec path: {self.psexec_tool.psexec_path}\n")
            self.psexec_output.insert("end", "-" * 50 + "\n\n")
        
        self.run_cmd_btn.configure(state="disabled")
        
        def run_command():
            def output_callback(line):
                self.app.after(0, lambda out=line: self._append_psexec_output(out + "\n"))
            
            result = self.psexec_tool.execute_remote_command(
                target, command,
                username=creds['username'],
                password=creds['password'],
                domain=creds['domain'],
                use_current_credentials=creds['use_current_credentials'],
                callback=output_callback
            )
            
            self.app.after(0, lambda: self._psexec_complete(result))
        
        thread = threading.Thread(target=run_command, daemon=True)
        thread.start()
    
    def _append_psexec_output(self, text):
        """Append text to PSExec output"""
        self.psexec_output.insert("end", text)
        self.psexec_output.see("end")
    
    def _psexec_complete(self, result):
        """Handle PSExec command completion"""
        self.run_cmd_btn.configure(state="normal")
        
        if result['error']:
            self.psexec_output.insert("end", f"\nError: {result['error']}")
        
        status = "success" if result['success'] else "error"
        self.app.show_toast(
            f"Command {'completed' if result['success'] else 'failed'} (code: {result['return_code']})",
            status
        )
    
    def _start_remote_cmd(self):
        """Start interactive remote CMD session"""
        target = self.psexec_target_entry.get().strip()
        
        if not target:
            self.app.show_toast("Please enter a target host", "warning")
            return
        
        if not self.psexec_tool.is_available:
            self.app.show_toast("PSExec not found", "error")
            return
        
        creds = self._get_credentials()
        
        # Show what we're doing in the output
        self.psexec_output.delete("1.0", "end")
        user_display = f"{creds['domain']}\\{creds['username']}" if creds['domain'] else creds['username']
        self.psexec_output.insert("end", f"Starting remote CMD session...\n")
        self.psexec_output.insert("end", f"Target: {target}\n")
        self.psexec_output.insert("end", f"User: {user_display}\n")
        self.psexec_output.insert("end", f"PSExec: {self.psexec_tool.psexec_path}\n")
        self.psexec_output.insert("end", "-" * 40 + "\n\n")
        
        result = self.psexec_tool.start_remote_cmd(
            target,
            username=creds['username'],
            password=creds['password'],
            domain=creds['domain'],
            use_current_credentials=creds['use_current_credentials']
        )
        
        if result['success']:
            self.psexec_output.insert("end", "✅ CMD window started successfully!\n")
            self.app.show_toast(f"Started remote CMD session to {target}", "success")
        else:
            error_msg = result.get('error', 'Unknown error')
            self.psexec_output.insert("end", f"❌ Error:\n{error_msg}\n")
            self.app.show_toast("Failed to start remote CMD - see output for details", "error")
    
    def _start_ps_remoting(self):
        """Start PowerShell Remoting session"""
        target = self.psexec_target_entry.get().strip()
        
        if not target:
            self.app.show_toast("Please enter a target host", "warning")
            return
        
        creds = self._get_credentials()
        
        # Show what we're doing in the output
        self.psexec_output.delete("1.0", "end")
        self.psexec_output.insert("end", f"Starting PowerShell Remoting session...\n")
        self.psexec_output.insert("end", f"Target: {target}\n")
        if not creds['use_current_credentials'] and creds['username']:
            user_display = f"{creds['domain']}\\{creds['username']}" if creds['domain'] else creds['username']
            self.psexec_output.insert("end", f"User: {user_display}\n")
        else:
            self.psexec_output.insert("end", f"User: (current session)\n")
        self.psexec_output.insert("end", "-" * 40 + "\n\n")
        
        result = self.psexec_tool.start_powershell_remoting(
            target,
            username=creds['username'] if not creds['use_current_credentials'] else None,
            password=creds['password'] if not creds['use_current_credentials'] else None,
            domain=creds['domain'] if not creds['use_current_credentials'] else None
        )
        
        if result['success']:
            self.psexec_output.insert("end", "✅ PowerShell window started!\n")
            self.psexec_output.insert("end", "\nNote: If connection fails, ensure WinRM is enabled on target:\n")
            self.psexec_output.insert("end", "  winrm quickconfig\n")
            self.app.show_toast(f"Started PowerShell Remoting to {target}", "success")
        else:
            error_msg = result.get('error', 'Unknown error')
            self.psexec_output.insert("end", f"❌ Error:\n{error_msg}\n")
            self.app.show_toast("Failed to start PowerShell Remoting", "error")
    
    def _start_ssh_session(self):
        """Start SSH session to remote host"""
        target = self.psexec_target_entry.get().strip()
        
        if not target:
            self.app.show_toast("Please enter a target host", "warning")
            return
        
        creds = self._get_credentials()
        
        self.psexec_output.delete("1.0", "end")
        self.psexec_output.insert("end", f"Starting SSH session to {target}...\n")
        
        try:
            # Build SSH command
            if not creds['use_current_credentials'] and creds['username']:
                if creds['domain']:
                    user_string = f"{creds['domain']}\\{creds['username']}"
                else:
                    user_string = creds['username']
                ssh_target = f"{user_string}@{target}"
            else:
                ssh_target = target
            
            self.psexec_output.insert("end", f"Target: {ssh_target}\n")
            self.psexec_output.insert("end", "-" * 40 + "\n\n")
            
            # Start SSH in new window
            import subprocess
            subprocess.Popen(
                ['cmd', '/c', 'start', 'cmd', '/k', f'ssh {ssh_target}'],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            self.psexec_output.insert("end", "✅ SSH window started!\n")
            self.psexec_output.insert("end", "\nNote: You'll be prompted for password in the new window.\n")
            self.psexec_output.insert("end", "If SSH fails, ensure OpenSSH is enabled on target:\n")
            self.psexec_output.insert("end", "  Add-WindowsCapability -Online -Name OpenSSH.Server\n")
            self.psexec_output.insert("end", "  Start-Service sshd\n")
            self.app.show_toast(f"Started SSH to {target}", "success")
            
        except Exception as e:
            self.psexec_output.insert("end", f"❌ Error: {str(e)}\n")
            self.app.show_toast("Failed to start SSH", "error")
    
    def _setup_trustedhosts(self):
        """Setup TrustedHosts to allow all connections"""
        # Check if running as admin
        if not self.app.is_admin():
            # Ask if user wants to restart as admin
            from tkinter import messagebox
            result = messagebox.askyesno(
                "Administrator Required",
                "Setting TrustedHosts requires Administrator privileges.\n\n"
                "Do you want to restart the application as Administrator?"
            )
            if result:
                self.app.restart_as_admin()
            return
        
        self.psexec_output.delete("1.0", "end")
        self.psexec_output.insert("end", "Setting up WinRM TrustedHosts...\n")
        self.psexec_output.insert("end", "-" * 40 + "\n\n")
        
        try:
            import subprocess
            import tempfile
            from pathlib import Path
            
            # Create a PowerShell script file to avoid escaping issues
            temp_dir = Path(tempfile.gettempdir())
            ps_file = temp_dir / "nettools_setup_trustedhosts.ps1"
            
            ps_script = '''
$ErrorActionPreference = "Stop"
try {
    Set-Item -Path WSMan:\localhost\Client\TrustedHosts -Value "*" -Force
    Write-Host "SUCCESS"
} catch {
    Write-Host "ERROR: $($_.Exception.Message)"
    exit 1
}
'''
            ps_file.write_text(ps_script, encoding='utf-8-sig')
            
            result = subprocess.run(
                ['powershell', '-ExecutionPolicy', 'Bypass', '-NoProfile', '-File', str(ps_file)],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            stdout = result.stdout.decode('utf-8', errors='replace').strip()
            stderr = result.stderr.decode('utf-8', errors='replace').strip()
            
            if 'SUCCESS' in stdout and result.returncode == 0:
                self.psexec_output.insert("end", "✅ TrustedHosts set to '*' successfully!\n\n")
                self.psexec_output.insert("end", "You can now use PowerShell Remoting to connect to any host.\n")
                self.app.show_toast("TrustedHosts configured successfully", "success")
            else:
                error_msg = stderr or stdout or "Unknown error"
                self.psexec_output.insert("end", f"❌ Error: {error_msg}\n")
                self.app.show_toast("Failed to set TrustedHosts", "error")
                
        except Exception as e:
            self.psexec_output.insert("end", f"❌ Error: {str(e)}\n")
            self.app.show_toast("Failed to setup TrustedHosts", "error")
    
    def _run_iperf_test(self):
        """Run iPerf bandwidth test"""
        target = self.iperf_target_entry.get().strip()
        port = self.iperf_port_entry.get().strip() or "5201"
        duration = self.iperf_duration_entry.get().strip() or "10"
        
        if not target:
            self.app.show_toast("Please enter a server host", "warning")
            return
        
        if not self.iperf_tool.is_available:
            self.app.show_toast("iPerf3 not found", "error")
            return
        
        try:
            port = int(port)
            duration = int(duration)
        except ValueError:
            self.app.show_toast("Invalid port or duration", "warning")
            return
        
        self.iperf_output.delete("1.0", "end")
        self.iperf_output.insert("end", f"Starting bandwidth test to {target}:{port}...\n\n")
        self.run_iperf_btn.configure(state="disabled")
        
        def run_test():
            def output_callback(line):
                self.app.after(0, lambda out=line: self._append_iperf_output(out + "\n"))
            
            result = self.iperf_tool.run_client_test(
                target,
                port=port,
                duration=duration,
                reverse=self.iperf_reverse_var.get(),
                udp=self.iperf_udp_var.get(),
                callback=output_callback
            )
            
            self.app.after(0, lambda: self._iperf_complete(result))
        
        thread = threading.Thread(target=run_test, daemon=True)
        thread.start()
    
    def _append_iperf_output(self, text):
        """Append text to iPerf output"""
        self.iperf_output.insert("end", text)
        self.iperf_output.see("end")
    
    def _iperf_complete(self, result):
        """Handle iPerf test completion"""
        self.run_iperf_btn.configure(state="normal")
        
        if result['results']:
            # Parse and display summary
            try:
                end_data = result['results'].get('end', {})
                sum_sent = end_data.get('sum_sent', {})
                sum_received = end_data.get('sum_received', {})
                
                if sum_sent:
                    bps = sum_sent.get('bits_per_second', 0)
                    mbps = bps / 1_000_000
                    self.iperf_output.insert("end", f"\n📊 Upload: {mbps:.2f} Mbps\n")
                
                if sum_received:
                    bps = sum_received.get('bits_per_second', 0)
                    mbps = bps / 1_000_000
                    self.iperf_output.insert("end", f"📊 Download: {mbps:.2f} Mbps\n")
            except Exception:
                pass
        
        if result['error']:
            self.iperf_output.insert("end", f"\nError: {result['error']}")
        
        status = "success" if result['success'] else "error"
        self.app.show_toast(
            f"Bandwidth test {'completed' if result['success'] else 'failed'}",
            status
        )
    
    def _start_iperf_server(self):
        """Start iPerf server locally"""
        port = self.iperf_port_entry.get().strip() or "5201"
        
        if not self.iperf_tool.is_available:
            self.app.show_toast("iPerf3 not found", "error")
            return
        
        try:
            port = int(port)
        except ValueError:
            self.app.show_toast("Invalid port", "warning")
            return
        
        result = self.iperf_tool.start_server(port=port, one_off=True)
        
        if result['success']:
            self.app.show_toast(f"iPerf3 server started on port {port}", "success")
            self.iperf_output.insert("end", f"\n🖥️ iPerf3 server running on port {port}...\n")
        else:
            self.app.show_toast(f"Failed to start server: {result.get('error', 'Unknown')}", "error")
    
    def _copy_iperf_to_remote(self):
        """Copy iPerf to remote host"""
        target = self.iperf_target_entry.get().strip() or self.psexec_target_entry.get().strip()
        
        if not target:
            self.app.show_toast("Please enter a target host", "warning")
            return
        
        if not self.iperf_tool.is_available:
            self.app.show_toast("iPerf3 not found locally", "error")
            return
        
        creds = self._get_credentials()
        
        # Use default remote path
        remote_path = "C:\\Tools"
        
        self.app.show_toast(f"Copying iPerf3 to {target}...", "info")
        
        def copy_file():
            result = self.iperf_tool.copy_to_remote(
                target,
                remote_path,
                psexec_tool=self.psexec_tool if self.psexec_tool.is_available else None,
                username=creds['username'],
                password=creds['password'],
                domain=creds['domain']
            )
            
            self.app.after(0, lambda: self._copy_complete(result))
        
        thread = threading.Thread(target=copy_file, daemon=True)
        thread.start()
    
    def _copy_complete(self, result):
        """Handle file copy completion"""
        if result['success']:
            self.app.show_toast(
                f"iPerf3 copied to {result['remote_iperf_path']}",
                "success"
            )
            self.iperf_output.insert(
                "end",
                f"\n✅ iPerf3 copied to remote: {result['remote_iperf_path']}\n"
            )
        else:
            self.app.show_toast(
                f"Copy failed: {result['error']}",
                "error"
            )
