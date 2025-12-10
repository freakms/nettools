"""
phpIPAM Integration UI Module
"""
import customtkinter as ctk
from tkinter import messagebox
import threading

from design_constants import COLORS, SPACING, RADIUS, FONTS
from ui_components import StyledCard, StyledButton, StyledEntry, SectionTitle, SubTitle

# phpIPAM imports
try:
    from phpipam_config import PHPIPAMConfig
    from phpipam_client import PHPIPAMClient
    from tools.phpipam_tool import PHPIPAMTool
    PHPIPAM_AVAILABLE = True
except ImportError:
    PHPIPAM_AVAILABLE = False
    PHPIPAMConfig = None
    PHPIPAMClient = None
    PHPIPAMTool = None


class PhpipamUI:
    """phpIPAM Integration UI Component"""
    
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        
        # Build UI
        self.create_content()
    
    def create_content(self):
        """Create phpIPAM integration page content"""
        if not PHPIPAM_AVAILABLE:
            # Show error if modules not available
            error_frame = ctk.CTkFrame(self.parent)
            error_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            error_label = ctk.CTkLabel(
                error_frame,
                text="⚠️ phpIPAM Integration Unavailable",
                font=ctk.CTkFont(size=24, weight="bold")
            )
            error_label.pack(pady=(50, 10))
            
            msg_label = ctk.CTkLabel(
                error_frame,
                text="Required modules are missing. Please install:\n\npip install cryptography requests",
                font=ctk.CTkFont(size=14)
            )
            msg_label.pack(pady=20)
            return
        
        # Initialize phpIPAM config
        self.phpipam_config = PHPIPAMConfig()
        self.phpipam_client = None
        
        # Scrollable content area
        scrollable = ctk.CTkScrollableFrame(self.parent)
        scrollable.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            scrollable,
            text="phpIPAM Integration",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 5))
        
        subtitle_label = SubTitle(
            scrollable,
            text="Manage IP addresses with phpIPAM API"
        )
        subtitle_label.pack(pady=(0, SPACING['lg']))
        
        # Status Section with styled card
        status_frame = StyledCard(scrollable)
        status_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        status_title = ctk.CTkLabel(
            status_frame,
            text="Connection Status",
            font=ctk.CTkFont(size=FONTS['subheading'], weight="bold")
        )
        status_title.pack(pady=(SPACING['lg'], SPACING['xs']), padx=SPACING['lg'], anchor="w")
        
        self.phpipam_status_label = ctk.CTkLabel(
            status_frame,
            text="⚪ Not configured" if not self.phpipam_config.is_enabled() else "🟢 Enabled",
            font=ctk.CTkFont(size=FONTS['body'])
        )
        self.phpipam_status_label.pack(pady=(0, SPACING['lg']), padx=SPACING['lg'], anchor="w")
        
        # Action buttons
        button_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        settings_btn = StyledButton(
            button_frame,
            text="⚙️ Settings",
            command=self.show_phpipam_settings,
            size="medium",
            variant="neutral"
        )
        settings_btn.pack(side="left", padx=(0, SPACING['md']))
        
        test_btn = StyledButton(
            button_frame,
            text="🔌 Test Connection",
            command=self.test_phpipam_connection,
            size="large",
            variant="primary"
        )
        test_btn.pack(side="left", padx=(0, SPACING['md']))
        
        auth_btn = StyledButton(
            button_frame,
            text="🔑 Authenticate",
            command=self.authenticate_phpipam,
            size="medium",
            variant="success"
        )
        auth_btn.pack(side="left")
        
        # Operations Section with styled card
        ops_frame = StyledCard(scrollable)
        ops_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        ops_title = SectionTitle(
            ops_frame,
            text="Operations"
        )
        ops_title.pack(pady=(SPACING['lg'], SPACING['md']), padx=SPACING['lg'], anchor="w")
        
        # IP Search
        search_frame = ctk.CTkFrame(ops_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="Search IP Address:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        search_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        search_entry_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_entry_frame.pack(fill="x")
        
        self.phpipam_search_entry = StyledEntry(
            search_entry_frame,
            placeholder_text="e.g., 192.168.1.10"
        )
        self.phpipam_search_entry.pack(side="left", fill="x", expand=True, padx=(0, SPACING['md']))
        
        search_btn = StyledButton(
            search_entry_frame,
            text="🔍 Search",
            command=self.search_phpipam_ip,
            size="medium",
            variant="primary"
        )
        search_btn.pack(side="left")
        
        # View Subnets
        subnet_btn_frame = ctk.CTkFrame(ops_frame, fg_color="transparent")
        subnet_btn_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        view_subnets_btn = StyledButton(
            subnet_btn_frame,
            text="📋 View All Subnets",
            command=self.view_phpipam_subnets,
            size="large",
            variant="primary"
        )
        view_subnets_btn.pack(side="left")
        
        # Results Section
        results_header_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        results_header_frame.pack(fill="x", pady=(SPACING['md'], SPACING['md']))
        
        results_title = SectionTitle(
            results_header_frame,
            text="Results"
        )
        results_title.pack(side="left", anchor="w")
        
        # Filter box for results
        filter_frame = ctk.CTkFrame(scrollable, corner_radius=6)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        filter_label = ctk.CTkLabel(
            filter_frame,
            text="Filter results:",
            font=ctk.CTkFont(size=11)
        )
        filter_label.pack(side="left", padx=(10, 5))
        
        self.phpipam_filter_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Type to filter displayed results...",
            height=32,
            width=300
        )
        self.phpipam_filter_entry.pack(side="left", padx=5)
        self.phpipam_filter_entry.bind('<KeyRelease>', self._filter_phpipam_results)
        
        clear_filter_btn = ctk.CTkButton(
            filter_frame,
            text="✕",
            command=lambda: (self.phpipam_filter_entry.delete(0, 'end'), self._filter_phpipam_results()),
            width=30,
            height=32,
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"]
        )
        clear_filter_btn.pack(side="left", padx=(0, 10))
        
        self.phpipam_results_frame = ctk.CTkFrame(scrollable, corner_radius=8)
        self.phpipam_results_frame.pack(fill="both", expand=True)
        
        # Initial message
        no_results_label = ctk.CTkLabel(
            self.phpipam_results_frame,
            text="No results yet. Configure settings and perform an operation.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        no_results_label.pack(pady=50)
    
    def show_phpipam_settings(self):
        """Show phpIPAM settings dialog"""
        if not PHPIPAM_AVAILABLE:
            messagebox.showerror("Error", "phpIPAM modules not available")
            return
        
        # Create settings dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("phpIPAM Settings")
        dialog.geometry("600x700")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center window
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Ensure dialog is on top and focused
        dialog.lift()
        dialog.focus_force()
        
        # Content
        content = ctk.CTkScrollableFrame(dialog)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            content,
            text="phpIPAM Configuration",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Enable/Disable
        enabled_var = ctk.BooleanVar(value=self.phpipam_config.is_enabled())
        enabled_check = ctk.CTkCheckBox(
            content,
            text="Enable phpIPAM Integration",
            variable=enabled_var,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        enabled_check.pack(anchor="w", pady=(0, 20))
        
        # phpIPAM URL
        url_label = ctk.CTkLabel(
            content,
            text="phpIPAM URL:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        url_label.pack(anchor="w", pady=(0, 5))
        
        url_entry = ctk.CTkEntry(
            content,
            placeholder_text="https://ipam.example.com",
            height=38
        )
        url_entry.insert(0, self.phpipam_config.get_phpipam_url())
        url_entry.pack(fill="x", pady=(0, 15))
        
        # App ID
        appid_label = ctk.CTkLabel(
            content,
            text="App ID:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        appid_label.pack(anchor="w", pady=(0, 5))
        
        appid_info = ctk.CTkLabel(
            content,
            text="Must match an API application created in phpIPAM (Administration → API)",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        )
        appid_info.pack(anchor="w", pady=(0, 5))
        
        appid_entry = ctk.CTkEntry(
            content,
            placeholder_text="MyApplication",
            height=38
        )
        appid_entry.insert(0, self.phpipam_config.get_app_id())
        appid_entry.pack(fill="x", pady=(0, 15))
        
        # Authentication Method
        auth_label = ctk.CTkLabel(
            content,
            text="Authentication Method:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        auth_label.pack(anchor="w", pady=(0, 5))
        
        auth_var = ctk.StringVar(value=self.phpipam_config.get_auth_method())
        
        dynamic_radio = ctk.CTkRadioButton(
            content,
            text="Dynamic (Username + Password)",
            variable=auth_var,
            value="dynamic"
        )
        dynamic_radio.pack(anchor="w", pady=2)
        
        static_radio = ctk.CTkRadioButton(
            content,
            text="Static Token",
            variable=auth_var,
            value="static"
        )
        static_radio.pack(anchor="w", pady=(2, 15))
        
        # Username (for dynamic)
        username_label = ctk.CTkLabel(
            content,
            text="Username (Dynamic Auth):",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        username_label.pack(anchor="w", pady=(0, 5))
        
        username_entry = ctk.CTkEntry(
            content,
            placeholder_text="admin",
            height=38
        )
        username_entry.insert(0, self.phpipam_config.get_username())
        username_entry.pack(fill="x", pady=(0, 15))
        
        # Password (for dynamic)
        password_label = ctk.CTkLabel(
            content,
            text="Password (Dynamic Auth):",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        password_label.pack(anchor="w", pady=(0, 5))
        
        password_entry = ctk.CTkEntry(
            content,
            placeholder_text="Enter password",
            height=38,
            show="*"
        )
        password_entry.pack(fill="x", pady=(0, 15))
        
        # Static Token
        token_label = ctk.CTkLabel(
            content,
            text="Static Token (Static Auth):",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        token_label.pack(anchor="w", pady=(0, 5))
        
        token_entry = ctk.CTkEntry(
            content,
            placeholder_text="Enter static API token",
            height=38,
            show="*"
        )
        token_entry.pack(fill="x", pady=(0, 15))
        
        # SSL Verify
        ssl_var = ctk.BooleanVar(value=self.phpipam_config.get_ssl_verify())
        ssl_check = ctk.CTkCheckBox(
            content,
            text="Verify SSL Certificates",
            variable=ssl_var
        )
        ssl_check.pack(anchor="w", pady=(0, 20))
        
        # Save function
        def save_settings():
            password = password_entry.get()
            token = token_entry.get()
            
            # Don't overwrite if fields are empty (means user didn't change them)
            if not password:
                password = self.phpipam_config.get_password()
            if not token:
                token = self.phpipam_config.get_static_token()
            
            success = self.phpipam_config.update_config(
                enabled=enabled_var.get(),
                phpipam_url=url_entry.get(),
                app_id=appid_entry.get(),
                auth_method=auth_var.get(),
                username=username_entry.get(),
                password=password,
                static_token=token,
                ssl_verify=ssl_var.get()
            )
            
            if success:
                # Update status label
                if self.phpipam_config.is_enabled():
                    self.phpipam_status_label.configure(text="🟢 Enabled")
                else:
                    self.phpipam_status_label.configure(text="⚪ Disabled")
                
                # Reset client to force re-auth
                self.phpipam_client = None
                
                dialog.destroy()
                messagebox.showinfo("Success", "Settings saved successfully!")
            else:
                messagebox.showerror("Error", "Failed to save settings")
        
        # Buttons
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save",
            command=save_settings,
            width=120,
            height=40,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"]
        )
        save_btn.pack(side="right", padx=(10, 0))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            width=100,
            height=40
        )
        cancel_btn.pack(side="right")
    
    def test_phpipam_connection(self):
        """Test connection to phpIPAM"""
        if not PHPIPAM_AVAILABLE:
            messagebox.showerror("Error", "phpIPAM modules not available")
            return
        
        if not self.phpipam_config.is_enabled():
            messagebox.showwarning("Not Enabled", "phpIPAM integration is disabled. Enable it in Settings.")
            return
        
        # Reload config to get latest SSL settings
        self.phpipam_config.config = self.phpipam_config.load_config()
        
        # Create fresh client with updated config and test
        client = PHPIPAMClient(self.phpipam_config)
        success, message = client.test_connection()
        
        if success:
            messagebox.showinfo("Connection Test - Success", message)
        else:
            messagebox.showerror("Connection Test - Failed", message)
    
    def authenticate_phpipam(self):
        """Authenticate with phpIPAM"""
        if not PHPIPAM_AVAILABLE:
            messagebox.showerror("Error", "phpIPAM modules not available")
            return
        
        if not self.phpipam_config.is_enabled():
            messagebox.showwarning("Not Enabled", "phpIPAM integration is disabled. Enable it in Settings.")
            return
        
        # Create/get client
        if not self.phpipam_client:
            self.phpipam_client = PHPIPAMClient(self.phpipam_config)
        
        success, message = self.phpipam_client.authenticate()
        
        if success:
            messagebox.showinfo("Success", f"✅ {message}")
        else:
            messagebox.showerror("Authentication Failed", f"❌ {message}")
    
    def search_phpipam_ip(self):
        """Search for IP address in phpIPAM"""
        if not PHPIPAM_AVAILABLE:
            messagebox.showerror("Error", "phpIPAM modules not available")
            return
        
        if not self.phpipam_config.is_enabled():
            messagebox.showwarning("Not Enabled", "phpIPAM integration is disabled. Enable it in Settings.")
            return
        
        ip_address = self.phpipam_search_entry.get().strip()
        if not ip_address:
            messagebox.showwarning("Input Required", "Please enter an IP address to search")
            return
        
        # Show loading message
        self.display_phpipam_loading("Searching for IP address...")
        
        # Create/get client
        if not self.phpipam_client:
            self.phpipam_client = PHPIPAMClient(self.phpipam_config)
        
        # Run search in background thread
        def search_thread():
            success, results = self.phpipam_client.search_ip(ip_address)
            # Update UI in main thread
            self.after(0, self.display_phpipam_results, "IP Search Results", results, success)
        
        thread = threading.Thread(target=search_thread, daemon=True)
        thread.start()
    
    def view_phpipam_subnets(self):
        """View all subnets from phpIPAM"""
        if not PHPIPAM_AVAILABLE:
            messagebox.showerror("Error", "phpIPAM modules not available")
            return
        
        if not self.phpipam_config.is_enabled():
            messagebox.showwarning("Not Enabled", "phpIPAM integration is disabled. Enable it in Settings.")
            return
        
        # Show loading message
        self.display_phpipam_loading("Loading subnets from phpIPAM...")
        
        # Create/get client
        if not self.phpipam_client:
            self.phpipam_client = PHPIPAMClient(self.phpipam_config)
        
        # Get subnets in background thread
        def subnets_thread():
            success, results = self.phpipam_client.get_all_subnets()
            # Update UI in main thread
            self.after(0, self.display_phpipam_results, "All Subnets", results, success)
        
        thread = threading.Thread(target=subnets_thread, daemon=True)
        thread.start()
    
    def display_phpipam_loading(self, message):
        """Display loading message"""
        # Clear existing results
        for widget in self.phpipam_results_frame.winfo_children():
            widget.destroy()
        
        loading_label = ctk.CTkLabel(
            self.phpipam_results_frame,
            text=f"⏳ {message}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["primary"]
        )
        loading_label.pack(pady=50)
    
    def display_phpipam_results(self, title, data, success):
        """Display phpIPAM operation results with pagination for large datasets"""
        # Clear existing results
        for widget in self.phpipam_results_frame.winfo_children():
            widget.destroy()
        
        # Title
        result_title = ctk.CTkLabel(
            self.phpipam_results_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        result_title.pack(pady=(15, 10), padx=15, anchor="w")
        
        if not success:
            error_label = ctk.CTkLabel(
                self.phpipam_results_frame,
                text=f"❌ Error: {data}",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["danger"]
            )
            error_label.pack(pady=20, padx=15)
            return
        
        if not data:
            no_data_label = ctk.CTkLabel(
                self.phpipam_results_frame,
                text="No results found",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"]
            )
            no_data_label.pack(pady=20, padx=15)
            return
        
        # Store data for pagination and filtering
        self.phpipam_all_results = data  # Keep original for filtering
        self.phpipam_current_results = data
        self.phpipam_current_page = 0
        self.phpipam_items_per_page = 50  # Show 50 items at a time
        
        # Info bar with count and warning for large datasets
        info_frame = ctk.CTkFrame(self.phpipam_results_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        count_text = f"Found {len(data)} result(s)"
        if len(data) > 100:
            count_text += f" • Showing {self.phpipam_items_per_page} per page for performance"
        
        count_label = ctk.CTkLabel(
            info_frame,
            text=count_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_secondary"]
        )
        count_label.pack(side="left")
        
        # Scrollable results container
        self.phpipam_results_scroll = ctk.CTkScrollableFrame(
            self.phpipam_results_frame, 
            height=300
        )
        self.phpipam_results_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        # Display first page
        self._display_phpipam_page()
        
        # Pagination controls if needed
        if len(data) > self.phpipam_items_per_page:
            self._create_pagination_controls()
    
    def _create_subnet_card(self, parent, subnet_data):
        """Create formatted card for subnet display"""
        # Main subnet info
        subnet_str = subnet_data.get("subnet", "N/A")
        mask = subnet_data.get("mask", "")
        cidr = f"{subnet_str}/{mask}" if mask else subnet_str
        
        # Header with CIDR
        header_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(12, 5))
        
        cidr_label = ctk.CTkLabel(
            header_frame,
            text=f"🌐 {cidr}",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        cidr_label.pack(side="left")
        
        # ID badge
        subnet_id = subnet_data.get("id", "")
        if subnet_id:
            id_label = ctk.CTkLabel(
                header_frame,
                text=f"ID: {subnet_id}",
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text_secondary"]
            )
            id_label.pack(side="right")
        
        # Description
        description = subnet_data.get("description", "")
        if description:
            desc_label = ctk.CTkLabel(
                parent,
                text=description,
                font=ctk.CTkFont(size=11),
                anchor="w",
                text_color=COLORS["text_secondary"]
            )
            desc_label.pack(fill="x", padx=12, pady=(0, 5))
        
        # Additional info in compact format
        info_items = []
        
        if "vlanId" in subnet_data and subnet_data["vlanId"]:
            info_items.append(f"VLAN: {subnet_data['vlanId']}")
        
        if "location" in subnet_data and subnet_data["location"]:
            info_items.append(f"Location: {subnet_data['location']}")
        
        if "isFolder" in subnet_data and subnet_data["isFolder"] == "1":
            info_items.append("📁 Folder")
        
        if info_items:
            info_text = " • ".join(info_items)
            info_label = ctk.CTkLabel(
                parent,
                text=info_text,
                font=ctk.CTkFont(size=10),
                anchor="w",
                text_color=COLORS["text_secondary"]
            )
            info_label.pack(fill="x", padx=12, pady=(0, 12))
        else:
            # Add bottom padding
            ctk.CTkFrame(self.parent, height=5, fg_color="transparent").pack()
    
    def _display_phpipam_page(self):
        """Display current page of phpIPAM results"""
        # Clear scroll frame
        for widget in self.phpipam_results_scroll.winfo_children():
            widget.destroy()
        
        # Calculate page boundaries
        start_idx = self.phpipam_current_page * self.phpipam_items_per_page
        end_idx = min(start_idx + self.phpipam_items_per_page, len(self.phpipam_current_results))
        
        # Get items for current page
        page_items = self.phpipam_current_results[start_idx:end_idx]
        
        # Display items
        for item in page_items:
            # Create card for each item
            item_card = ctk.CTkFrame(
                self.phpipam_results_scroll, 
                corner_radius=6, 
                fg_color=COLORS["bg_card"]
            )
            item_card.pack(fill="x", pady=3, padx=2)
            
            # Determine if this is a subnet or IP address
            is_subnet = "subnet" in item or "mask" in item
            
            if is_subnet:
                # Subnet card layout
                self._create_subnet_card(item_card, item)
            else:
                # IP address card layout
                self._create_ip_card(item_card, item)
    
    def _create_pagination_controls(self):
        """Create pagination controls for phpIPAM results"""
        total_items = len(self.phpipam_current_results)
        total_pages = (total_items + self.phpipam_items_per_page - 1) // self.phpipam_items_per_page
        
        pagination_frame = ctk.CTkFrame(self.phpipam_results_frame, fg_color="transparent")
        pagination_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        # Previous button
        prev_btn = ctk.CTkButton(
            pagination_frame,
            text="← Previous",
            command=self._prev_page,
            width=100,
            height=32,
            state="normal" if self.phpipam_current_page > 0 else "disabled",
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"]
        )
        prev_btn.pack(side="left", padx=(0, 10))
        
        # Page indicator
        start_idx = self.phpipam_current_page * self.phpipam_items_per_page + 1
        end_idx = min(start_idx + self.phpipam_items_per_page - 1, total_items)
        
        self.phpipam_page_label = ctk.CTkLabel(
            pagination_frame,
            text=f"Showing {start_idx}-{end_idx} of {total_items} • Page {self.phpipam_current_page + 1}/{total_pages}",
            font=ctk.CTkFont(size=11)
        )
        self.phpipam_page_label.pack(side="left", padx=10)
        
        # Next button
        next_btn = ctk.CTkButton(
            pagination_frame,
            text="Next →",
            command=self._next_page,
            width=100,
            height=32,
            state="normal" if self.phpipam_current_page < total_pages - 1 else "disabled",
            fg_color=COLORS["neutral"],
            hover_color=COLORS["neutral_hover"]
        )
        next_btn.pack(side="left")
        
        # Jump to page
        jump_label = ctk.CTkLabel(
            pagination_frame,
            text="Jump to:",
            font=ctk.CTkFont(size=11)
        )
        jump_label.pack(side="right", padx=(10, 5))
        
        self.phpipam_page_entry = ctk.CTkEntry(
            pagination_frame,
            width=60,
            height=32,
            placeholder_text="Page"
        )
        self.phpipam_page_entry.pack(side="right", padx=(0, 5))
        
        jump_btn = ctk.CTkButton(
            pagination_frame,
            text="Go",
            command=self._jump_to_page,
            width=50,
            height=32,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"]
        )
        jump_btn.pack(side="right")
    
    def _prev_page(self):
        """Go to previous page"""
        if self.phpipam_current_page > 0:
            self.phpipam_current_page -= 1
            # Clear and recreate
            for widget in self.phpipam_results_frame.winfo_children():
                if widget != self.phpipam_results_frame.winfo_children()[0]:  # Keep title
                    widget.destroy()
            
            # Recreate display
            self._display_phpipam_page()
            self._create_pagination_controls()
    
    def _next_page(self):
        """Go to next page"""
        total_pages = (len(self.phpipam_current_results) + self.phpipam_items_per_page - 1) // self.phpipam_items_per_page
        if self.phpipam_current_page < total_pages - 1:
            self.phpipam_current_page += 1
            # Clear and recreate
            for widget in self.phpipam_results_frame.winfo_children():
                if widget != self.phpipam_results_frame.winfo_children()[0]:  # Keep title
                    widget.destroy()
            
            # Recreate display
            self._display_phpipam_page()
            self._create_pagination_controls()
    
    def _jump_to_page(self):
        """Jump to specific page"""
        try:
            page_num = int(self.phpipam_page_entry.get())
            total_pages = (len(self.phpipam_current_results) + self.phpipam_items_per_page - 1) // self.phpipam_items_per_page
            
            if 1 <= page_num <= total_pages:
                self.phpipam_current_page = page_num - 1
                # Clear and recreate
                for widget in self.phpipam_results_frame.winfo_children():
                    if widget != self.phpipam_results_frame.winfo_children()[0]:  # Keep title
                        widget.destroy()
                
                # Recreate display
                self._display_phpipam_page()
                self._create_pagination_controls()
            else:
                messagebox.showwarning("Invalid Page", f"Please enter a page number between 1 and {total_pages}")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid page number")
    
    def _filter_phpipam_results(self, event=None):
        """Filter displayed phpIPAM results based on search text"""
        if not hasattr(self, 'phpipam_all_results'):
            return
        
        filter_text = self.phpipam_filter_entry.get().lower().strip()
        
        if not filter_text:
            # Show all results
            self.phpipam_current_results = self.phpipam_all_results
        else:
            # Filter results
            filtered = []
            for item in self.phpipam_all_results:
                # Search in all string values
                item_text = " ".join(str(v).lower() for v in item.values() if v)
                if filter_text in item_text:
                    filtered.append(item)
            
            self.phpipam_current_results = filtered
        
        # Reset to first page and redisplay
        self.phpipam_current_page = 0
        
        # Clear and recreate (keeping title)
        for widget in self.phpipam_results_frame.winfo_children():
            if widget != self.phpipam_results_frame.winfo_children()[0]:
                widget.destroy()
        
        # Update count label
        info_frame = ctk.CTkFrame(self.phpipam_results_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        count_text = f"Showing {len(self.phpipam_current_results)} of {len(self.phpipam_all_results)} result(s)"
        if len(self.phpipam_current_results) > self.phpipam_items_per_page:
            count_text += f" • {self.phpipam_items_per_page} per page"
        
        count_label = ctk.CTkLabel(
            info_frame,
            text=count_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_secondary"]
        )
        count_label.pack(side="left")
        
        # Recreate scroll frame
        self.phpipam_results_scroll = ctk.CTkScrollableFrame(
            self.phpipam_results_frame,
            height=300
        )
        self.phpipam_results_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        # Display page
        self._display_phpipam_page()
        
        # Add pagination if needed
        if len(self.phpipam_current_results) > self.phpipam_items_per_page:
            self._create_pagination_controls()
    
    def _create_ip_card(self, parent, ip_data):
        """Create formatted card for IP address display"""
        # IP address
        ip = ip_data.get("ip", "N/A")
        
        # Header with IP
        header_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(12, 5))
        
        ip_label = ctk.CTkLabel(
            header_frame,
            text=f"💻 {ip}",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        ip_label.pack(side="left")
        
        # Status badge if available
        if "state" in ip_data:
            state = ip_data["state"]
            state_color = COLORS["online"] if state == "1" else COLORS["offline"]
            state_text = "Active" if state == "1" else "Inactive"
            
            state_label = ctk.CTkLabel(
                header_frame,
                text=state_text,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=state_color
            )
            state_label.pack(side="right")
        
        # Hostname
        hostname = ip_data.get("hostname", "")
        if hostname:
            host_label = ctk.CTkLabel(
                parent,
                text=f"🏷️ {hostname}",
                font=ctk.CTkFont(size=11, weight="bold"),
                anchor="w"
            )
            host_label.pack(fill="x", padx=12, pady=(0, 5))
        
        # Description
        description = ip_data.get("description", "")
        if description:
            desc_label = ctk.CTkLabel(
                parent,
                text=description,
                font=ctk.CTkFont(size=10),
                anchor="w",
                text_color=COLORS["text_secondary"]
            )
            desc_label.pack(fill="x", padx=12, pady=(0, 5))
        
        # Additional details
        details = []
        
        if "mac" in ip_data and ip_data["mac"]:
            details.append(f"MAC: {ip_data['mac']}")
        
        if "owner" in ip_data and ip_data["owner"]:
            details.append(f"Owner: {ip_data['owner']}")
        
        if "port" in ip_data and ip_data["port"]:
            details.append(f"Port: {ip_data['port']}")
        
        if details:
            details_text = " • ".join(details)
            details_label = ctk.CTkLabel(
                parent,
                text=details_text,
                font=ctk.CTkFont(size=10),
                anchor="w",
                text_color=COLORS["text_secondary"]
            )
            details_label.pack(fill="x", padx=12, pady=(0, 12))
        else:
            # Add bottom padding
            ctk.CTkFrame(self.parent, height=5, fg_color="transparent").pack()
    
