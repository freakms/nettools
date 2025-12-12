"""
Subnet Calculator UI Module
Contains the subnet calculator tool page implementation
"""

import customtkinter as ctk
from tkinter import messagebox
import ipaddress

from design_constants import COLORS, SPACING, RADIUS, FONTS
from ui_components import StyledCard, StyledButton, StyledEntry, SubTitle, SectionTitle, ContextMenu
from tools.subnet_calculator import SubnetCalculator


class SubnetCalculatorUI:
    """Subnet Calculator page UI implementation"""
    
    def __init__(self, app):
        """
        Initialize Subnet Calculator UI
        
        Args:
            app: Reference to main NetToolsApp instance
        """
        self.app = app

    def create_content(self, parent):
        """Create Subnet Calculator page content"""
        # Scrollable content area
        scrollable = ctk.CTkScrollableFrame(parent)
        scrollable.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            scrollable,
            text="Subnet Calculator",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 5))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            scrollable,
            text="Calculate subnet information from CIDR notation",
            font=ctk.CTkFont(size=12)
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Input section with styled card
        input_frame = StyledCard(scrollable)
        input_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        # CIDR input
        cidr_label = ctk.CTkLabel(
            input_frame,
            text="Enter Network in CIDR Notation:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        cidr_label.pack(pady=(SPACING['lg'], SPACING['xs']), padx=SPACING['lg'], anchor="w")
        
        cidr_info = SubTitle(
            input_frame,
            text="Examples: 192.168.1.0/24, 10.0.0.0/8, 172.16.0.0/16"
        )
        cidr_info.pack(pady=(0, SPACING['xs']), padx=SPACING['lg'], anchor="w")
        
        self.subnet_cidr_entry = StyledEntry(
            input_frame,
            placeholder_text="192.168.1.0/24"
        )
        self.subnet_cidr_entry.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        self.subnet_cidr_entry.bind('<Return>', lambda e: self.calculate_subnet())
        
        # Calculate button
        button_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        button_frame.pack(pady=(0, SPACING['lg']))
        
        calc_btn = StyledButton(
            button_frame,
            text="🔢 Calculate",
            command=self.calculate_subnet,
            size="large",
            variant="warning"
        )
        calc_btn.pack(side="left", padx=(0, SPACING['sm']))
        
        # Subnet Splitter section
        split_frame = StyledCard(scrollable)
        split_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        split_title = ctk.CTkLabel(
            split_frame,
            text="🔀 Subnet Splitter",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        split_title.pack(pady=(SPACING['md'], SPACING['xs']), padx=SPACING['lg'], anchor="w")
        
        split_info = SubTitle(
            split_frame,
            text="Split a network into smaller subnets of equal size"
        )
        split_info.pack(pady=(0, SPACING['sm']), padx=SPACING['lg'], anchor="w")
        
        # Available subnets preview frame
        self.subnet_preview_frame = ctk.CTkFrame(split_frame, fg_color=COLORS['bg_card'])
        self.subnet_preview_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['sm']))
        
        preview_label = ctk.CTkLabel(
            self.subnet_preview_frame,
            text="Enter a network above and click 'Show Options' to see available splits",
            font=ctk.CTkFont(size=FONTS['small']),
            text_color=COLORS['text_secondary']
        )
        preview_label.pack(pady=SPACING['sm'])
        
        # Show options button
        show_options_btn = StyledButton(
            split_frame,
            text="📊 Show Split Options",
            command=self.show_split_options,
            size="small",
            variant="secondary"
        )
        show_options_btn.pack(padx=SPACING['lg'], pady=(0, SPACING['sm']), anchor="w")
        
        # Split controls row
        split_controls = ctk.CTkFrame(split_frame, fg_color="transparent")
        split_controls.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        split_label = ctk.CTkLabel(
            split_controls,
            text="Split into subnets with prefix:",
            font=ctk.CTkFont(size=FONTS['small'])
        )
        split_label.pack(side="left", padx=(0, SPACING['sm']))
        
        self.split_prefix_var = ctk.StringVar(value="25")
        self.split_prefix_entry = ctk.CTkComboBox(
            split_controls,
            values=[str(i) for i in range(8, 31)],
            variable=self.split_prefix_var,
            width=80
        )
        self.split_prefix_entry.pack(side="left", padx=(0, SPACING['sm']))
        
        split_btn = StyledButton(
            split_controls,
            text="Split Network",
            command=self.split_subnet,
            size="small",
            variant="primary"
        )
        split_btn.pack(side="left")
        
        # Results section
        results_title = SectionTitle(
            scrollable,
            text="Subnet Information"
        )
        results_title.pack(pady=(SPACING['md'], SPACING['md']), anchor="w")
        
        # Results frame with styled card
        self.subnet_results_frame = StyledCard(scrollable)
        self.subnet_results_frame.pack(fill="both", expand=True)
        
        # Initial message
        no_results_label = ctk.CTkLabel(
            self.subnet_results_frame,
            text="No calculation performed yet. Enter a network in CIDR notation and click Calculate.",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        no_results_label.pack(pady=50)
    
    def calculate_subnet(self):
        """Calculate subnet information"""
        cidr = self.subnet_cidr_entry.get().strip()
        
        if not cidr:
            messagebox.showwarning("Invalid Input", "Please enter a network in CIDR notation (e.g., 192.168.1.0/24)")
            return
        
        # Use SubnetCalculator from tools module
        result = SubnetCalculator.calculate(cidr)
        
        if result is None:
            messagebox.showerror("Error", "Please enter a CIDR notation")
            return
        
        if "error" in result:
            messagebox.showerror("Error", f"Invalid CIDR notation: {result['error']}")
            return
        
        # Display results using existing display method
        self.display_subnet_results(result)
        
        # Add to history
        self.app.history.add_cidr(cidr)
        
        self.app.status_label.configure(text=f"Calculated subnet information for {cidr}")
        
        # Auto-update split options preview
        self.show_split_options()
    
    def show_split_options(self):
        """Show available split options for the entered network"""
        cidr = self.subnet_cidr_entry.get().strip()
        
        if not cidr:
            messagebox.showwarning("Invalid Input", "Please enter a network in CIDR notation first")
            return
        
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            original_prefix = network.prefixlen
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid CIDR notation: {str(e)}")
            return
        
        # Clear preview frame
        for widget in self.subnet_preview_frame.winfo_children():
            widget.destroy()
        
        # Title
        title = ctk.CTkLabel(
            self.subnet_preview_frame,
            text=f"📊 Split Options for {network} (/{original_prefix})",
            font=ctk.CTkFont(size=FONTS['small'], weight="bold")
        )
        title.pack(anchor="w", padx=SPACING['sm'], pady=(SPACING['sm'], SPACING['xs']))
        
        # Create scrollable frame for options
        options_scroll = ctk.CTkScrollableFrame(
            self.subnet_preview_frame,
            height=150,
            fg_color="transparent"
        )
        options_scroll.pack(fill="x", padx=SPACING['xs'], pady=(0, SPACING['sm']))
        
        # Table header
        header_row = ctk.CTkFrame(options_scroll, fg_color=("gray85", "gray25"))
        header_row.pack(fill="x", pady=(0, 3))
        
        headers = [("Prefix", 60), ("# Subnets", 90), ("Hosts/Subnet", 100), ("Total Hosts", 100)]
        for header_text, width in headers:
            h_label = ctk.CTkLabel(
                header_row,
                text=header_text,
                font=ctk.CTkFont(size=10, weight="bold"),
                width=width,
                anchor="w"
            )
            h_label.pack(side="left", padx=3, pady=3)
        
        # Calculate options for each possible prefix
        max_prefix = min(30, original_prefix + 10)  # Limit to reasonable range
        
        for new_prefix in range(original_prefix + 1, max_prefix + 1):
            num_subnets = 2 ** (new_prefix - original_prefix)
            hosts_per_subnet = (2 ** (32 - new_prefix)) - 2  # Subtract network and broadcast
            total_usable = num_subnets * hosts_per_subnet
            
            # Skip if hosts per subnet is less than 2
            if hosts_per_subnet < 2:
                continue
            
            row_color = ("gray95", "gray20") if new_prefix % 2 == 0 else ("gray90", "gray17")
            row = ctk.CTkFrame(options_scroll, fg_color=row_color)
            row.pack(fill="x", pady=1)
            
            # Make row clickable to select this prefix
            def select_prefix(p=new_prefix):
                self.split_prefix_var.set(str(p))
            
            row_data = [
                (f"/{new_prefix}", 60),
                (f"{num_subnets:,}", 90),
                (f"{hosts_per_subnet:,}", 100),
                (f"{total_usable:,}", 100)
            ]
            
            for value, width in row_data:
                v_label = ctk.CTkLabel(
                    row,
                    text=value,
                    font=ctk.CTkFont(size=10),
                    width=width,
                    anchor="w"
                )
                v_label.pack(side="left", padx=3, pady=2)
                v_label.bind("<Button-1>", lambda e, p=new_prefix: self._select_and_highlight(p))
            
            row.bind("<Button-1>", lambda e, p=new_prefix: self._select_and_highlight(p))
        
        # Tip
        tip = ctk.CTkLabel(
            self.subnet_preview_frame,
            text="💡 Click a row to select that prefix",
            font=ctk.CTkFont(size=9),
            text_color=COLORS['text_secondary']
        )
        tip.pack(anchor="w", padx=SPACING['sm'], pady=(0, SPACING['xs']))
    
    def _select_and_highlight(self, prefix):
        """Select a prefix from the options table"""
        self.split_prefix_var.set(str(prefix))
        self.app.status_label.configure(text=f"Selected /{prefix} - Click 'Split Network' to see results")
    
    # get_network_class method removed - now handled by SubnetCalculator
    
    def display_subnet_results(self, info):
        """Display subnet calculation results"""
        # Clear frame
        for widget in self.subnet_results_frame.winfo_children():
            widget.destroy()
        
        # Create result rows
        results = [
            ("Network Address", info["network"]),
            ("Subnet Mask", info["netmask"]),
            ("CIDR Notation", info["cidr"]),
            ("Wildcard Mask", info["wildcard"]),
            ("Broadcast Address", info["broadcast"]),
            ("First Usable Host", info["first_host"]),
            ("Last Usable Host", info["last_host"]),
            ("Total Addresses", f"{info['total_hosts']:,}"),
            ("Usable Hosts", f"{info['usable_hosts']:,}"),
            ("Network Class", info["network_class"]),
            ("IP Type", info["type"]),
        ]
        
        for label, value in results:
            row_frame = ctk.CTkFrame(self.subnet_results_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=20, pady=5)
            
            label_widget = ctk.CTkLabel(
                row_frame,
                text=f"{label}:",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=180,
                anchor="w"
            )
            label_widget.pack(side="left")
            
            value_widget = ctk.CTkLabel(
                row_frame,
                text=value,
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            value_widget.pack(side="left", fill="x", expand=True)
    
    def split_subnet(self):
        """Split a subnet into smaller subnets"""
        cidr = self.subnet_cidr_entry.get().strip()
        
        if not cidr:
            messagebox.showwarning("Invalid Input", "Please enter a network in CIDR notation first")
            return
        
        try:
            new_prefix = int(self.split_prefix_var.get())
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid prefix length")
            return
        
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            original_prefix = network.prefixlen
            
            if new_prefix <= original_prefix:
                messagebox.showwarning(
                    "Invalid Split", 
                    f"New prefix (/{new_prefix}) must be larger than original prefix (/{original_prefix}).\n\n"
                    f"Example: To split /{original_prefix} network, use /{original_prefix + 1} or higher."
                )
                return
            
            if new_prefix > 30:
                messagebox.showwarning("Invalid Split", "Prefix cannot be larger than /30 (minimum 2 usable hosts)")
                return
            
            # Calculate subnets
            subnets = list(network.subnets(new_prefix=new_prefix))
            num_subnets = len(subnets)
            
            if num_subnets > 256:
                answer = messagebox.askyesno(
                    "Large Split",
                    f"This will create {num_subnets:,} subnets. Show only first 256?"
                )
                if answer:
                    subnets = subnets[:256]
                else:
                    return
            
            # Display results
            self.display_split_results(network, subnets, new_prefix)
            self.app.status_label.configure(text=f"Split {cidr} into {num_subnets} /{new_prefix} subnets")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid CIDR notation: {str(e)}")
    
    def display_split_results(self, original_network, subnets, new_prefix):
        """Display subnet split results"""
        # Clear frame
        for widget in self.subnet_results_frame.winfo_children():
            widget.destroy()
        
        # Header
        header_frame = ctk.CTkFrame(self.subnet_results_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        header_label = ctk.CTkLabel(
            header_frame,
            text=f"🔀 Split Results: {original_network} → /{new_prefix}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        header_label.pack(anchor="w")
        
        info_label = ctk.CTkLabel(
            header_frame,
            text=f"Created {len(subnets)} subnets, each with {subnets[0].num_addresses - 2} usable hosts",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary']
        )
        info_label.pack(anchor="w", pady=(2, 0))
        
        # Scrollable list of subnets
        subnets_scroll = ctk.CTkScrollableFrame(
            self.subnet_results_frame,
            height=300,
            fg_color=COLORS['bg_card']
        )
        subnets_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Table header
        header_row = ctk.CTkFrame(subnets_scroll, fg_color=("gray85", "gray25"))
        header_row.pack(fill="x", pady=(0, 5))
        
        headers = [("#", 40), ("Network", 150), ("First Host", 130), ("Last Host", 130), ("Broadcast", 130)]
        for header_text, width in headers:
            h_label = ctk.CTkLabel(
                header_row,
                text=header_text,
                font=ctk.CTkFont(size=11, weight="bold"),
                width=width,
                anchor="w"
            )
            h_label.pack(side="left", padx=5, pady=5)
        
        # Subnet rows
        for i, subnet in enumerate(subnets, 1):
            row_color = ("gray95", "gray20") if i % 2 == 0 else ("gray90", "gray17")
            row = ctk.CTkFrame(subnets_scroll, fg_color=row_color)
            row.pack(fill="x", pady=1)
            
            # Calculate hosts
            hosts = list(subnet.hosts())
            first_host = str(hosts[0]) if hosts else "N/A"
            last_host = str(hosts[-1]) if hosts else "N/A"
            
            row_data = [
                (str(i), 40),
                (str(subnet), 150),
                (first_host, 130),
                (last_host, 130),
                (str(subnet.broadcast_address), 130)
            ]
            
            for value, width in row_data:
                v_label = ctk.CTkLabel(
                    row,
                    text=value,
                    font=ctk.CTkFont(size=11, family="Courier New"),
                    width=width,
                    anchor="w"
                )
                v_label.pack(side="left", padx=5, pady=4)
        
        # Copy all button
        copy_btn = StyledButton(
            self.subnet_results_frame,
            text="📋 Copy All Subnets",
            command=lambda: self.copy_subnets_to_clipboard(subnets),
            size="small",
            variant="secondary"
        )
        copy_btn.pack(pady=(0, 15))
    
    def copy_subnets_to_clipboard(self, subnets):
        """Copy all subnet CIDRs to clipboard"""
        subnet_list = "\n".join([str(s) for s in subnets])
        self.app.clipboard_clear()
        self.app.clipboard_append(subnet_list)
        messagebox.showinfo("Copied", f"Copied {len(subnets)} subnets to clipboard")
    
