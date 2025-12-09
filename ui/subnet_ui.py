"""
Subnet Calculator UI Module
Contains the subnet calculator tool page implementation
"""

import customtkinter as ctk
from tkinter import messagebox
import ipaddress

from design_constants import COLORS, SPACING, RADIUS, FONTS
from ui_components import StyledCard, StyledButton, StyledEntry, SubTitle


class SubnetCalculatorUI:
    """Subnet Calculator page UI implementation"""
    
    def __init__(self, app):
        """
        Initialize Subnet Calculator UI
        
        Args:
            app: Reference to main NetToolsApp instance
        """
        self.app = app

    def create_subnet_content(self, parent):
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
        calc_btn = StyledButton(
            scrollable,
            text="🔢 Calculate",
            command=self.calculate_subnet,
            size="large",
            variant="warning"
        )
        calc_btn.pack(pady=(0, SPACING['lg']))
        
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
        self.history.add_cidr(cidr)
        
        self.status_label.configure(text=f"Calculated subnet information for {cidr}")
    
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
    
