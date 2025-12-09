"""
PAN-OS CLI Generator UI Module
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
import re

from design_constants import COLORS, FONTS, SPACING
from ui_components import StyledCard, StyledButton, StyledEntry, SectionTitle, SubTitle, InfoBox


class PANOSUI:
    """PAN-OS CLI Generator UI Component"""
    
    def __init__(self, app, parent):
        """
        Initialize PAN-OS UI
        
        Args:
            app: Main application instance
            parent: Parent widget
        """
        self.app = app
        self.parent = parent
        
        # Initialize storage
        self.panos_commands = []
        self.panos_generated_names = []
        
        # Build UI
        self.create_ui()
    
    def create_ui(self):
        """Create PAN-OS CLI Generator content"""
        # Main container with scrollable area
        main_container = ctk.CTkFrame(self.parent)
        main_container.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Left side - Input forms
        left_frame = ctk.CTkFrame(main_container)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, SPACING['md']))
        
        # Tab buttons
        tab_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        tab_frame.pack(fill="x", pady=(0, SPACING['md']))
        
        self.panos_addresses_btn = StyledButton(
            tab_frame,
            text="📍 Addresses",
            command=lambda: self.switch_panos_tab("addresses"),
            size="medium",
            variant="primary"
        )
        self.panos_addresses_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        self.panos_policies_btn = StyledButton(
            tab_frame,
            text="🛡️ Policies",
            command=lambda: self.switch_panos_tab("policies"),
            size="medium",
            variant="neutral"
        )
        self.panos_policies_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        self.panos_service_btn = StyledButton(
            tab_frame,
            text="🔌 Services",
            command=lambda: self.switch_panos_tab("service"),
            size="medium",
            variant="neutral"
        )
        self.panos_service_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        # Advanced tabs (second row)
        tab_frame2 = ctk.CTkFrame(left_frame, fg_color="transparent")
        tab_frame2.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        
        self.panos_schedule_btn = StyledButton(
            tab_frame2,
            text="🕐 Schedule",
            command=lambda: self.switch_panos_tab("schedule"),
            size="medium",
            variant="neutral"
        )
        self.panos_schedule_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        self.panos_appfilter_btn = StyledButton(
            tab_frame2,
            text="📱 App Filter",
            command=lambda: self.switch_panos_tab("appfilter"),
            size="medium",
            variant="neutral"
        )
        self.panos_appfilter_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        self.panos_urlcat_btn = StyledButton(
            tab_frame2,
            text="🌐 URL Category",
            command=lambda: self.switch_panos_tab("urlcat"),
            size="medium",
            variant="neutral"
        )
        self.panos_urlcat_btn.pack(side="left")
        
        # Tab content area
        self.panos_tab_content = ctk.CTkFrame(left_frame)
        self.panos_tab_content.pack(fill="both", expand=True)
        
        # Create tabs
        self.create_panos_addresses_tab()
        self.create_panos_policies_tab()
        self.create_panos_schedule_tab()
        self.create_panos_appfilter_tab()
        self.create_panos_urlcat_tab()
        self.create_panos_service_tab()
        
        # Show name generator by default
        self.panos_current_tab = "name"
        self.panos_name_gen_tab.pack(fill="both", expand=True)
        
        # Right side - Output panel
        self.create_panos_output_panel(main_container)
    
    def switch_panos_tab(self, tab_name):
        """Switch between PAN-OS Generator tabs"""
        # Hide all tabs
        self.panos_addresses_tab.pack_forget()
        self.panos_policies_tab.pack_forget()
        self.panos_service_tab.pack_forget()
        self.panos_schedule_tab.pack_forget()
        self.panos_appfilter_tab.pack_forget()
        self.panos_urlcat_tab.pack_forget()
        
        # Reset all button colors
        self.panos_addresses_btn.configure(fg_color=COLORS['neutral'])
        self.panos_policies_btn.configure(fg_color=COLORS['neutral'])
        self.panos_service_btn.configure(fg_color=COLORS['neutral'])
        self.panos_schedule_btn.configure(fg_color=COLORS['neutral'])
        self.panos_appfilter_btn.configure(fg_color=COLORS['neutral'])
        self.panos_urlcat_btn.configure(fg_color=COLORS['neutral'])
        
        # Show selected tab and highlight button
        if tab_name == "addresses":
            self.panos_addresses_btn.configure(fg_color=COLORS['primary'])
            self.panos_addresses_tab.pack(fill="both", expand=True)
        elif tab_name == "policies":
            self.panos_policies_btn.configure(fg_color=COLORS['primary'])
            self.panos_policies_tab.pack(fill="both", expand=True)
        elif tab_name == "schedule":
            self.panos_schedule_btn.configure(fg_color=COLORS['primary'])
            self.panos_schedule_tab.pack(fill="both", expand=True)
        elif tab_name == "appfilter":
            self.panos_appfilter_btn.configure(fg_color=COLORS['primary'])
            self.panos_appfilter_tab.pack(fill="both", expand=True)
        elif tab_name == "urlcat":
            self.panos_urlcat_btn.configure(fg_color=COLORS['primary'])
            self.panos_urlcat_tab.pack(fill="both", expand=True)
        elif tab_name == "service":
            self.panos_service_btn.configure(fg_color=COLORS['primary'])
            self.panos_service_tab.pack(fill="both", expand=True)
        
        self.panos_current_tab = tab_name
    
    def create_panos_name_generator_tab(self):
        """Create Name Generator tab"""
        self.panos_name_gen_tab = ctk.CTkFrame(self.panos_addresses_tab, fg_color="transparent")
        
        # Card
        card = StyledCard(self.panos_name_gen_tab)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        # Title
        title = SectionTitle(card, text="Address Name Generator")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(
            card,
            text="Generate address object names from base names and IPs, then create CLI commands"
        )
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Step 1
        step1_label = ctk.CTkLabel(
            card,
            text="Step 1: Input Data",
            font=ctk.CTkFont(size=FONTS['subheading'], weight="bold")
        )
        step1_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['sm']))
        
        # Base Names
        name_label = ctk.CTkLabel(
            card,
            text="Base Names (one per line):",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        name_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['sm'], SPACING['xs']))
        
        self.panos_gen_names = ctk.CTkTextbox(
            card,
            height=120,
            font=ctk.CTkFont(size=FONTS['body'], family="Consolas")
        )
        self.panos_gen_names.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Setup placeholder
        self.panos_gen_names_placeholder = "Server1\nServer2\nWebServer"
        self.panos_gen_names.insert("1.0", self.panos_gen_names_placeholder)
        self.panos_gen_names.configure(text_color=COLORS['text_secondary'])
        self.panos_gen_names.bind("<FocusIn>", lambda e: self.on_textbox_focus_in(self.panos_gen_names, self.panos_gen_names_placeholder))
        self.panos_gen_names.bind("<FocusOut>", lambda e: self.on_textbox_focus_out(self.panos_gen_names, self.panos_gen_names_placeholder))
        
        # IP Addresses
        ip_label = ctk.CTkLabel(
            card,
            text="IP Addresses/Netmasks (one per line):",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        ip_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_gen_ips = ctk.CTkTextbox(
            card,
            height=120,
            font=ctk.CTkFont(size=FONTS['body'], family="Consolas")
        )
        self.panos_gen_ips.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Setup placeholder
        self.panos_gen_ips_placeholder = "192.168.1.10\n192.168.1.20\n10.0.0.10"
        self.panos_gen_ips.insert("1.0", self.panos_gen_ips_placeholder)
        self.panos_gen_ips.configure(text_color=COLORS['text_secondary'])
        self.panos_gen_ips.bind("<FocusIn>", lambda e: self.on_textbox_focus_in(self.panos_gen_ips, self.panos_gen_ips_placeholder))
        self.panos_gen_ips.bind("<FocusOut>", lambda e: self.on_textbox_focus_out(self.panos_gen_ips, self.panos_gen_ips_placeholder))
        
        # Options row
        options_frame = ctk.CTkFrame(card, fg_color="transparent")
        options_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Separator
        sep_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        sep_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        sep_label = ctk.CTkLabel(sep_frame, text="Separator:", font=ctk.CTkFont(size=FONTS['body']))
        sep_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_gen_separator = ctk.CTkComboBox(
            sep_frame,
            values=["_ (Underscore)", "- (Dash)", ". (Dot)"],
            state="readonly"
        )
        self.panos_gen_separator.set("_ (Underscore)")
        self.panos_gen_separator.pack(fill="x")
        
        # Format
        format_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        format_frame.pack(side="left", fill="x", expand=True)
        
        format_label = ctk.CTkLabel(format_frame, text="Format:", font=ctk.CTkFont(size=FONTS['body']))
        format_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_gen_format = ctk.CTkComboBox(
            format_frame,
            values=["Name_IP", "IP_Name", "Name Only", "Custom"],
            state="readonly",
            command=self.on_panos_format_change
        )
        self.panos_gen_format.set("Name_IP")
        self.panos_gen_format.pack(fill="x")
        
        # Custom format (hidden by default)
        self.panos_custom_format_frame = ctk.CTkFrame(card, fg_color="transparent")
        
        custom_label = ctk.CTkLabel(
            self.panos_custom_format_frame,
            text="Custom Format Pattern:",
            font=ctk.CTkFont(size=FONTS['body'])
        )
        custom_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_gen_custom = StyledEntry(
            self.panos_custom_format_frame,
            placeholder_text="e.g., {name}-{ip} or Host_{name}_{ip}"
        )
        self.panos_gen_custom.pack(fill="x", pady=(0, SPACING['xs']))
        
        custom_help = SubTitle(
            self.panos_custom_format_frame,
            text="Use {name} for base name and {ip} for IP address"
        )
        custom_help.pack(anchor="w")
        
        # Generate Names and Reset buttons
        gen_buttons_frame = ctk.CTkFrame(card, fg_color="transparent")
        gen_buttons_frame.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['lg']))
        
        gen_names_btn = StyledButton(
            gen_buttons_frame,
            text="🎯 Generate Object Names",
            command=self.generate_panos_names,
            size="large",
            variant="primary"
        )
        gen_names_btn.pack(side="left", fill="x", expand=True, padx=(0, SPACING['xs']))
        
        reset_btn = StyledButton(
            gen_buttons_frame,
            text="🔄 Reset",
            command=self.reset_panos_name_generator,
            size="large",
            variant="neutral"
        )
        reset_btn.pack(side="left", padx=(SPACING['xs'], 0))
        
        # Preview section (hidden initially)
        self.panos_preview_frame = ctk.CTkFrame(card, fg_color="transparent")
        
        preview_label = ctk.CTkLabel(
            self.panos_preview_frame,
            text="Generated Names Preview:",
            font=ctk.CTkFont(size=FONTS['subheading'], weight="bold")
        )
        preview_label.pack(anchor="w", pady=(0, SPACING['sm']))
        
        self.panos_preview_text = ctk.CTkTextbox(
            self.panos_preview_frame,
            height=150,
            font=ctk.CTkFont(size=FONTS['small'], family="Consolas")
        )
        self.panos_preview_text.pack(fill="x", pady=(0, SPACING['md']))
        
        # Step 2 (hidden initially)
        self.panos_step2_frame = ctk.CTkFrame(self.panos_preview_frame, fg_color="transparent")
        
        step2_label = ctk.CTkLabel(
            self.panos_step2_frame,
            text="Step 2: Generate CLI Commands",
            font=ctk.CTkFont(size=FONTS['subheading'], weight="bold")
        )
        step2_label.pack(anchor="w", pady=(0, SPACING['sm']))
        
        self.panos_gen_shared = ctk.CTkCheckBox(
            self.panos_step2_frame,
            text="Create as Shared Objects (available to all virtual systems)",
            font=ctk.CTkFont(size=FONTS['body'])
        )
        self.panos_gen_shared.select()
        self.panos_gen_shared.pack(anchor="w", pady=(0, SPACING['md']))
        
        gen_commands_btn = StyledButton(
            self.panos_step2_frame,
            text="💻 Generate CLI Commands",
            command=self.generate_panos_from_names,
            size="large",
            variant="success"
        )
        gen_commands_btn.pack(fill="x")
        
        # Help box
        help_box = InfoBox(
            card,
            message="💡 How it Works:\n"
                   "• Both lists must have the same number of lines\n"
                   "• Each name pairs with corresponding IP (line by line)\n"
                   "• Choose format to create object names automatically\n"
                   "• Example: 'Server1' + '192.168.1.10' → 'Server1_192_168_1_10'",
            box_type="info"
        )
        help_box.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['lg']))
    
    def create_panos_single_address_tab(self):
        """Create single address object tab"""
        self.panos_single_addr_tab = ctk.CTkFrame(self.panos_addresses_tab, fg_color="transparent")
        
        # Card
        card = StyledCard(self.panos_single_addr_tab)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        # Title
        title = SectionTitle(card, text="Single Address Object")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(
            card,
            text="Create a single address object with optional description"
        )
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Object Name
        name_label = ctk.CTkLabel(
            card,
            text="Object Name *",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        name_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['sm'], SPACING['xs']))
        
        self.panos_single_name = StyledEntry(
            card,
            placeholder_text="e.g., Server_192.168.1.10"
        )
        self.panos_single_name.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # IP Address
        ip_label = ctk.CTkLabel(
            card,
            text="IP Address/Netmask *",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        ip_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_single_ip = StyledEntry(
            card,
            placeholder_text="192.168.1.0/24 or 192.168.1.10"
        )
        self.panos_single_ip.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Description
        desc_label = ctk.CTkLabel(
            card,
            text="Description (optional)",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        desc_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_single_desc = StyledEntry(
            card,
            placeholder_text="Optional description"
        )
        self.panos_single_desc.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Shared checkbox
        self.panos_single_shared = ctk.CTkCheckBox(
            card,
            text="Shared Object (available to all virtual systems)",
            font=ctk.CTkFont(size=FONTS['body'])
        )
        self.panos_single_shared.select()
        self.panos_single_shared.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Generate button
        gen_btn = StyledButton(
            card,
            text="💻 Generate Command",
            command=self.generate_single_address,
            size="large",
            variant="primary"
        )
        gen_btn.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['lg']))
    
    def create_panos_address_group_tab(self):
        """Create Address Group tab"""
        self.panos_group_tab = ctk.CTkFrame(self.panos_addresses_tab, fg_color="transparent")
        
        # Initialize members list
        self.panos_group_members = []
        
        # Card
        card = StyledCard(self.panos_group_tab)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        # Title
        title = SectionTitle(card, text="Address Group")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(
            card,
            text="Create address groups to organize multiple address objects"
        )
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Virtual System and Type row
        options_frame = ctk.CTkFrame(card, fg_color="transparent")
        options_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        vsys_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        vsys_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        vsys_label = ctk.CTkLabel(vsys_frame, text="Virtual System:", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        vsys_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_group_vsys = ctk.CTkComboBox(
            vsys_frame,
            values=["shared", "vsys1", "vsys2", "vsys3"],
            state="readonly"
        )
        self.panos_group_vsys.set("shared")
        self.panos_group_vsys.pack(fill="x")
        
        type_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        type_frame.pack(side="left", fill="x", expand=True)
        
        type_label = ctk.CTkLabel(type_frame, text="Type:", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        type_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_group_type = ctk.CTkComboBox(
            type_frame,
            values=["Static", "Dynamic"],
            state="readonly"
        )
        self.panos_group_type.set("Static")
        self.panos_group_type.pack(fill="x")
        
        # Group Name
        name_label = ctk.CTkLabel(
            card,
            text="Group Name *",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        name_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_group_name = StyledEntry(
            card,
            placeholder_text="e.g., Internal_Networks"
        )
        self.panos_group_name.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Members
        members_label = ctk.CTkLabel(
            card,
            text="Members *",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        members_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        # Add member input
        add_frame = ctk.CTkFrame(card, fg_color="transparent")
        add_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['sm']))
        
        self.panos_group_member_input = StyledEntry(
            add_frame,
            placeholder_text="Add address object name"
        )
        self.panos_group_member_input.pack(side="left", fill="x", expand=True, padx=(0, SPACING['xs']))
        
        add_btn = StyledButton(
            add_frame,
            text="Add",
            command=self.add_group_member,
            size="small",
            variant="neutral"
        )
        add_btn.pack(side="right")
        
        # Bulk paste section
        bulk_label = ctk.CTkLabel(
            card,
            text="Or paste multiple members (one per line):",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        bulk_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['sm'], SPACING['xs']))
        
        self.panos_group_bulk_paste = ctk.CTkTextbox(
            card,
            height=80,
            font=ctk.CTkFont(size=FONTS['body'])
        )
        self.panos_group_bulk_paste.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        bulk_add_btn = StyledButton(
            card,
            text="Add All from List",
            command=self.add_bulk_group_members,
            size="small",
            variant="neutral"
        )
        bulk_add_btn.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Members display
        self.panos_group_members_display = ctk.CTkFrame(card, fg_color=COLORS['bg_card'])
        self.panos_group_members_display.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        self.panos_group_members_display.configure(height=100)
        
        # Description
        desc_label = ctk.CTkLabel(
            card,
            text="Description (optional)",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        desc_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_group_desc = StyledEntry(
            card,
            placeholder_text="Optional description"
        )
        self.panos_group_desc.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Generate button
        gen_btn = StyledButton(
            card,
            text="💻 Generate Command",
            command=self.generate_address_group,
            size="large",
            variant="primary"
        )
        gen_btn.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['lg']))
    
    def create_panos_addresses_tab(self):
        """Create unified Addresses tab with subtabs"""
        self.panos_addresses_tab = ctk.CTkScrollableFrame(self.panos_tab_content)
        
        # Create subtabs: Name Generator, Single Address, Address Groups
        subtab_frame = ctk.CTkFrame(self.panos_addresses_tab, fg_color="transparent")
        subtab_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])
        
        self.addr_namegen_btn = StyledButton(
            subtab_frame,
            text="🎯 Name Generator",
            command=lambda: self.switch_address_subtab("namegen"),
            size="small",
            variant="primary"
        )
        self.addr_namegen_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        self.addr_single_btn = StyledButton(
            subtab_frame,
            text="🌐 Single Address",
            command=lambda: self.switch_address_subtab("single"),
            size="small",
            variant="neutral"
        )
        self.addr_single_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        self.addr_group_btn = StyledButton(
            subtab_frame,
            text="📦 Address Groups",
            command=lambda: self.switch_address_subtab("group"),
            size="small",
            variant="neutral"
        )
        self.addr_group_btn.pack(side="left")
        
        # Name Generator Content
        self.create_panos_name_generator_tab()
        
        # Single Address Content  
        self.create_panos_single_address_tab()
        self.panos_single_addr_tab.pack_forget()
        
        # Address Groups Content
        self.create_panos_address_group_tab()
        self.panos_group_tab.pack_forget()
    
    def switch_address_subtab(self, subtab):
        """Switch between address subtabs"""
        # Hide all
        self.panos_name_gen_tab.pack_forget()
        self.panos_single_addr_tab.pack_forget()
        self.panos_group_tab.pack_forget()
        
        # Reset button colors
        self.addr_namegen_btn.configure(fg_color=COLORS['neutral'])
        self.addr_single_btn.configure(fg_color=COLORS['neutral'])
        self.addr_group_btn.configure(fg_color=COLORS['neutral'])
        
        # Show selected
        if subtab == "namegen":
            self.addr_namegen_btn.configure(fg_color=COLORS['primary'])
            self.panos_name_gen_tab.pack(fill="both", expand=True)
        elif subtab == "single":
            self.addr_single_btn.configure(fg_color=COLORS['primary'])
            self.panos_single_addr_tab.pack(fill="both", expand=True)
        elif subtab == "group":
            self.addr_group_btn.configure(fg_color=COLORS['primary'])
            self.panos_group_tab.pack(fill="both", expand=True)
    
    def create_panos_nat_tab(self):
        """Create NAT Rule tab"""
        self.panos_nat_tab = ctk.CTkFrame(self.panos_policies_tab, fg_color="transparent")
        
        # Card
        card = StyledCard(self.panos_nat_tab)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        # Title
        title = SectionTitle(card, text="NAT Rule")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(
            card,
            text="Create DNAT or SNAT rules for network address translation"
        )
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # NAT Type
        type_label = ctk.CTkLabel(
            card,
            text="NAT Type:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        type_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        type_frame = ctk.CTkFrame(card, fg_color="transparent")
        type_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        self.panos_nat_type_var = ctk.StringVar(value="dnat")
        
        dnat_radio = ctk.CTkRadioButton(
            type_frame,
            text="DNAT (Destination NAT)",
            variable=self.panos_nat_type_var,
            value="dnat"
        )
        dnat_radio.pack(side="left", padx=(0, SPACING['lg']))
        
        snat_radio = ctk.CTkRadioButton(
            type_frame,
            text="SNAT (Source NAT)",
            variable=self.panos_nat_type_var,
            value="snat"
        )
        snat_radio.pack(side="left")
        
        # Virtual System and Rule Name row
        row1_frame = ctk.CTkFrame(card, fg_color="transparent")
        row1_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        vsys_frame = ctk.CTkFrame(row1_frame, fg_color="transparent")
        vsys_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        vsys_label = ctk.CTkLabel(vsys_frame, text="Virtual System:", font=ctk.CTkFont(size=FONTS['body']))
        vsys_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_nat_vsys = ctk.CTkComboBox(
            vsys_frame,
            values=["shared", "vsys1", "vsys2", "vsys3"],
            state="readonly"
        )
        self.panos_nat_vsys.set("shared")
        self.panos_nat_vsys.pack(fill="x")
        
        name_frame = ctk.CTkFrame(row1_frame, fg_color="transparent")
        name_frame.pack(side="left", fill="x", expand=True)
        
        name_label = ctk.CTkLabel(name_frame, text="Rule Name *:", font=ctk.CTkFont(size=FONTS['body']))
        name_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_nat_name = StyledEntry(name_frame, placeholder_text="e.g., NAT_DMZ_Web")
        self.panos_nat_name.pack(fill="x")
        
        # From/To Zones row
        row2_frame = ctk.CTkFrame(card, fg_color="transparent")
        row2_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        from_frame = ctk.CTkFrame(row2_frame, fg_color="transparent")
        from_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        from_label = ctk.CTkLabel(from_frame, text="From Zone *:", font=ctk.CTkFont(size=FONTS['body']))
        from_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_nat_from = StyledEntry(from_frame, placeholder_text="e.g., untrust")
        self.panos_nat_from.pack(fill="x")
        
        to_frame = ctk.CTkFrame(row2_frame, fg_color="transparent")
        to_frame.pack(side="left", fill="x", expand=True)
        
        to_label = ctk.CTkLabel(to_frame, text="To Zone *:", font=ctk.CTkFont(size=FONTS['body']))
        to_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_nat_to = StyledEntry(to_frame, placeholder_text="e.g., trust")
        self.panos_nat_to.pack(fill="x")
        
        # Source/Destination row
        row3_frame = ctk.CTkFrame(card, fg_color="transparent")
        row3_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        src_frame = ctk.CTkFrame(row3_frame, fg_color="transparent")
        src_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        src_label = ctk.CTkLabel(src_frame, text="Source Address:", font=ctk.CTkFont(size=FONTS['body']))
        src_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_nat_source = StyledEntry(src_frame, placeholder_text="any")
        self.panos_nat_source.insert(0, "any")
        self.panos_nat_source.pack(fill="x")
        
        dest_frame = ctk.CTkFrame(row3_frame, fg_color="transparent")
        dest_frame.pack(side="left", fill="x", expand=True)
        
        dest_label = ctk.CTkLabel(dest_frame, text="Destination Address *:", font=ctk.CTkFont(size=FONTS['body']))
        dest_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_nat_dest = StyledEntry(dest_frame, placeholder_text="e.g., Public_IP")
        self.panos_nat_dest.pack(fill="x")
        
        # Service/Translated Address row
        row4_frame = ctk.CTkFrame(card, fg_color="transparent")
        row4_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        svc_frame = ctk.CTkFrame(row4_frame, fg_color="transparent")
        svc_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        svc_label = ctk.CTkLabel(svc_frame, text="Service:", font=ctk.CTkFont(size=FONTS['body']))
        svc_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_nat_service = StyledEntry(svc_frame, placeholder_text="any")
        self.panos_nat_service.insert(0, "any")
        self.panos_nat_service.pack(fill="x")
        
        trans_frame = ctk.CTkFrame(row4_frame, fg_color="transparent")
        trans_frame.pack(side="left", fill="x", expand=True)
        
        trans_label = ctk.CTkLabel(trans_frame, text="Translated Address *:", font=ctk.CTkFont(size=FONTS['body']))
        trans_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_nat_translated = StyledEntry(trans_frame, placeholder_text="e.g., Private_IP")
        self.panos_nat_translated.pack(fill="x")
        
        # Translated Port
        port_label = ctk.CTkLabel(
            card,
            text="Translated Port (DNAT only):",
            font=ctk.CTkFont(size=FONTS['body'])
        )
        port_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_nat_port = StyledEntry(card, placeholder_text="e.g., 8080")
        self.panos_nat_port.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Description
        desc_label = ctk.CTkLabel(
            card,
            text="Description (optional):",
            font=ctk.CTkFont(size=FONTS['body'])
        )
        desc_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_nat_desc = StyledEntry(card, placeholder_text="Optional description")
        self.panos_nat_desc.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Generate button
        gen_btn = StyledButton(
            card,
            text="💻 Generate Command",
            command=self.generate_nat_rule,
            size="large",
            variant="primary"
        )
        gen_btn.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['lg']))
    
    def create_panos_policy_tab(self):
        """Create Security Policy Rule tab"""
        self.panos_policy_tab = ctk.CTkFrame(self.panos_policies_tab, fg_color="transparent")
        
        # Card
        card = StyledCard(self.panos_policy_tab)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        # Title
        title = SectionTitle(card, text="Security Policy Rule")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(
            card,
            text="Create security policy rules to control traffic flow"
        )
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Virtual System and Rule Name row
        row1_frame = ctk.CTkFrame(card, fg_color="transparent")
        row1_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        vsys_frame = ctk.CTkFrame(row1_frame, fg_color="transparent")
        vsys_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        vsys_label = ctk.CTkLabel(vsys_frame, text="Virtual System:", font=ctk.CTkFont(size=FONTS['body']))
        vsys_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_vsys = ctk.CTkComboBox(
            vsys_frame,
            values=["shared", "vsys1", "vsys2", "vsys3"],
            state="readonly"
        )
        self.panos_policy_vsys.set("shared")
        self.panos_policy_vsys.pack(fill="x")
        
        name_frame = ctk.CTkFrame(row1_frame, fg_color="transparent")
        name_frame.pack(side="left", fill="x", expand=True)
        
        name_label = ctk.CTkLabel(name_frame, text="Rule Name *:", font=ctk.CTkFont(size=FONTS['body']))
        name_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_name = StyledEntry(name_frame, placeholder_text="e.g., Allow_Web_Traffic")
        self.panos_policy_name.pack(fill="x")
        
        # From/To Zones row
        row2_frame = ctk.CTkFrame(card, fg_color="transparent")
        row2_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        from_frame = ctk.CTkFrame(row2_frame, fg_color="transparent")
        from_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        from_label = ctk.CTkLabel(from_frame, text="From Zone *:", font=ctk.CTkFont(size=FONTS['body']))
        from_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_from = StyledEntry(from_frame, placeholder_text="e.g., trust")
        self.panos_policy_from.pack(fill="x")
        
        to_frame = ctk.CTkFrame(row2_frame, fg_color="transparent")
        to_frame.pack(side="left", fill="x", expand=True)
        
        to_label = ctk.CTkLabel(to_frame, text="To Zone *:", font=ctk.CTkFont(size=FONTS['body']))
        to_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_to = StyledEntry(to_frame, placeholder_text="e.g., untrust")
        self.panos_policy_to.pack(fill="x")
        
        # Source/Destination row
        row3_frame = ctk.CTkFrame(card, fg_color="transparent")
        row3_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        src_frame = ctk.CTkFrame(row3_frame, fg_color="transparent")
        src_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        src_label = ctk.CTkLabel(src_frame, text="Source Address:", font=ctk.CTkFont(size=FONTS['body']))
        src_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_source = StyledEntry(src_frame, placeholder_text="any")
        self.panos_policy_source.insert(0, "any")
        self.panos_policy_source.pack(fill="x")
        
        dest_frame = ctk.CTkFrame(row3_frame, fg_color="transparent")
        dest_frame.pack(side="left", fill="x", expand=True)
        
        dest_label = ctk.CTkLabel(dest_frame, text="Destination Address:", font=ctk.CTkFont(size=FONTS['body']))
        dest_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_dest = StyledEntry(dest_frame, placeholder_text="any")
        self.panos_policy_dest.insert(0, "any")
        self.panos_policy_dest.pack(fill="x")
        
        # Application/Service row
        row4_frame = ctk.CTkFrame(card, fg_color="transparent")
        row4_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        app_frame = ctk.CTkFrame(row4_frame, fg_color="transparent")
        app_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        app_label = ctk.CTkLabel(app_frame, text="Application:", font=ctk.CTkFont(size=FONTS['body']))
        app_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_app = StyledEntry(app_frame, placeholder_text="any")
        self.panos_policy_app.insert(0, "any")
        self.panos_policy_app.pack(fill="x")
        
        svc_frame = ctk.CTkFrame(row4_frame, fg_color="transparent")
        svc_frame.pack(side="left", fill="x", expand=True)
        
        svc_label = ctk.CTkLabel(svc_frame, text="Service:", font=ctk.CTkFont(size=FONTS['body']))
        svc_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_service = StyledEntry(svc_frame, placeholder_text="application-default")
        self.panos_policy_service.insert(0, "application-default")
        self.panos_policy_service.pack(fill="x")
        
        # Action/Profile row
        row5_frame = ctk.CTkFrame(card, fg_color="transparent")
        row5_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        action_frame = ctk.CTkFrame(row5_frame, fg_color="transparent")
        action_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        action_label = ctk.CTkLabel(action_frame, text="Action:", font=ctk.CTkFont(size=FONTS['body']))
        action_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_action = ctk.CTkComboBox(
            action_frame,
            values=["allow", "deny", "drop"],
            state="readonly"
        )
        self.panos_policy_action.set("allow")
        self.panos_policy_action.pack(fill="x")
        
        profile_frame = ctk.CTkFrame(row5_frame, fg_color="transparent")
        profile_frame.pack(side="left", fill="x", expand=True)
        
        profile_label = ctk.CTkLabel(profile_frame, text="Security Profile Group:", font=ctk.CTkFont(size=FONTS['body']))
        profile_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.panos_policy_profile = StyledEntry(profile_frame, placeholder_text="e.g., default")
        self.panos_policy_profile.pack(fill="x")
        
        # Description
        desc_label = ctk.CTkLabel(
            card,
            text="Description (optional):",
            font=ctk.CTkFont(size=FONTS['body'])
        )
        desc_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_policy_desc = StyledEntry(card, placeholder_text="Optional description")
        self.panos_policy_desc.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Generate button
        gen_btn = StyledButton(
            card,
            text="💻 Generate Command",
            command=self.generate_policy_rule,
            size="large",
            variant="primary"
        )
        gen_btn.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['lg']))
    
    def create_panos_output_panel(self, parent):
        """Create command output panel"""
        # Right side - Output
        output_frame = ctk.CTkFrame(parent)
        output_frame.pack(side="right", fill="both", expand=False, padx=(0, 0))
        output_frame.configure(width=400)
        
        output_card = StyledCard(output_frame)
        output_card.pack(fill="both", expand=True)
        
        # Header
        header_frame = ctk.CTkFrame(output_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['md']))
        
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True)
        
        title = ctk.CTkLabel(
            title_frame,
            text="💻 Command Output",
            font=ctk.CTkFont(size=FONTS['heading'], weight="bold")
        )
        title.pack(anchor="w")
        
        self.panos_cmd_count = ctk.CTkLabel(
            title_frame,
            text="0 commands generated",
            font=ctk.CTkFont(size=FONTS['small']),
            text_color=COLORS['text_secondary']
        )
        self.panos_cmd_count.pack(anchor="w", pady=(SPACING['xs'], 0))
        
        clear_btn = StyledButton(
            header_frame,
            text="🗑️ Clear All",
            command=self.clear_panos_commands,
            size="small",
            variant="neutral"
        )
        clear_btn.pack(side="right", padx=(SPACING['md'], 0))
        
        # Commands list
        self.panos_commands_list = ctk.CTkScrollableFrame(output_card, height=400)
        self.panos_commands_list.pack(fill="both", expand=True, padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Action buttons (create before render so it exists)
        self.panos_action_frame = ctk.CTkFrame(output_card, fg_color="transparent")
        self.panos_action_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        self.panos_action_frame.pack_forget()  # Hidden initially
        
        copy_btn = StyledButton(
            self.panos_action_frame,
            text="📋 Copy All",
            command=self.copy_panos_commands,
            size="medium",
            variant="neutral"
        )
        copy_btn.pack(fill="x", pady=(0, SPACING['xs']))
        
        download_btn = StyledButton(
            self.panos_action_frame,
            text="⬇️ Download",
            command=self.download_panos_commands,
            size="medium",
            variant="primary"
        )
        download_btn.pack(fill="x")
        
        # Render initial empty state
        self.render_panos_commands()
    
    def create_panos_policies_tab(self):
        """Create unified Policies tab with subtabs"""
        self.panos_policies_tab = ctk.CTkScrollableFrame(self.panos_tab_content)
        
        # Create subtabs: NAT Rules, Security Policies
        subtab_frame = ctk.CTkFrame(self.panos_policies_tab, fg_color="transparent")
        subtab_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])
        
        self.policy_nat_btn = StyledButton(
            subtab_frame,
            text="🔄 NAT Rules",
            command=lambda: self.switch_policy_subtab("nat"),
            size="small",
            variant="primary"
        )
        self.policy_nat_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        self.policy_security_btn = StyledButton(
            subtab_frame,
            text="🔐 Security Policies",
            command=lambda: self.switch_policy_subtab("security"),
            size="small",
            variant="neutral"
        )
        self.policy_security_btn.pack(side="left")
        
        # NAT Rules Content
        self.create_panos_nat_tab()
        
        # Security Policies Content
        self.create_panos_policy_tab()
        self.panos_policy_tab.pack_forget()
    
    def switch_policy_subtab(self, subtab):
        """Switch between policy subtabs"""
        # Hide all
        self.panos_nat_tab.pack_forget()
        self.panos_policy_tab.pack_forget()
        
        # Reset button colors
        self.policy_nat_btn.configure(fg_color=COLORS['neutral'])
        self.policy_security_btn.configure(fg_color=COLORS['neutral'])
        
        # Show selected
        if subtab == "nat":
            self.policy_nat_btn.configure(fg_color=COLORS['primary'])
            self.panos_nat_tab.pack(fill="both", expand=True)
        elif subtab == "security":
            self.policy_security_btn.configure(fg_color=COLORS['primary'])
            self.panos_policy_tab.pack(fill="both", expand=True)
    
    def create_panos_schedule_tab(self):
        """Create Schedule Object tab"""
        self.panos_schedule_tab = ctk.CTkScrollableFrame(self.panos_tab_content)
        
        card = StyledCard(self.panos_schedule_tab)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        title = SectionTitle(card, text="Schedule Object")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(card, text="Create time-based schedule objects for policy rules")
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Schedule Name
        name_label = ctk.CTkLabel(card, text="Schedule Name *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        name_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_schedule_name = StyledEntry(card, placeholder_text="e.g., Business_Hours")
        self.panos_schedule_name.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Schedule Type
        type_label = ctk.CTkLabel(card, text="Schedule Type *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        type_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_schedule_type = ctk.CTkComboBox(card, values=["recurring", "non-recurring"], state="readonly")
        self.panos_schedule_type.set("recurring")
        self.panos_schedule_type.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Time Range
        time_frame = ctk.CTkFrame(card, fg_color="transparent")
        time_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        start_label = ctk.CTkLabel(time_frame, text="Start Time (HH:MM):", font=ctk.CTkFont(size=FONTS['body']))
        start_label.pack(side="left", padx=(0, SPACING['xs']))
        
        self.panos_schedule_start = StyledEntry(time_frame, placeholder_text="08:00", width=80)
        self.panos_schedule_start.pack(side="left", padx=(0, SPACING['md']))
        
        end_label = ctk.CTkLabel(time_frame, text="End Time (HH:MM):", font=ctk.CTkFont(size=FONTS['body']))
        end_label.pack(side="left", padx=(0, SPACING['xs']))
        
        self.panos_schedule_end = StyledEntry(time_frame, placeholder_text="18:00", width=80)
        self.panos_schedule_end.pack(side="left")
        
        # Days (for recurring)
        days_label = ctk.CTkLabel(card, text="Days (for recurring):", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        days_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        days_frame = ctk.CTkFrame(card, fg_color="transparent")
        days_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        self.panos_schedule_days = {}
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in days:
            var = ctk.BooleanVar(value=True if day not in ["Saturday", "Sunday"] else False)
            cb = ctk.CTkCheckBox(days_frame, text=day[:3], variable=var, width=60)
            cb.pack(side="left", padx=SPACING['xs'])
            self.panos_schedule_days[day.lower()] = var
        
        # Generate button
        gen_btn = StyledButton(card, text="💻 Generate Command", command=self.generate_schedule_object, size="large", variant="primary")
        gen_btn.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['lg']))
    
    def create_panos_appfilter_tab(self):
        """Create Application Filter tab"""
        self.panos_appfilter_tab = ctk.CTkScrollableFrame(self.panos_tab_content)
        
        card = StyledCard(self.panos_appfilter_tab)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        title = SectionTitle(card, text="Application Filter")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(card, text="Create custom application groups and filters")
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Filter Name
        name_label = ctk.CTkLabel(card, text="Filter Name *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        name_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_appfilter_name = StyledEntry(card, placeholder_text="e.g., Social_Media_Apps")
        self.panos_appfilter_name.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Category
        cat_label = ctk.CTkLabel(card, text="Category *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        cat_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_appfilter_category = ctk.CTkComboBox(
            card,
            values=["business-systems", "collaboration", "general-internet", "media", "networking", "unknown"],
            state="readonly"
        )
        self.panos_appfilter_category.set("general-internet")
        self.panos_appfilter_category.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Subcategory
        subcat_label = ctk.CTkLabel(card, text="Subcategory", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        subcat_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_appfilter_subcategory = StyledEntry(card, placeholder_text="e.g., social-networking")
        self.panos_appfilter_subcategory.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Technology
        tech_label = ctk.CTkLabel(card, text="Technology", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        tech_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_appfilter_technology = ctk.CTkComboBox(
            card,
            values=["browser-based", "client-server", "network-protocol", "peer-to-peer"],
            state="readonly"
        )
        self.panos_appfilter_technology.set("browser-based")
        self.panos_appfilter_technology.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Risk Level
        risk_label = ctk.CTkLabel(card, text="Risk Level", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        risk_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        risk_frame = ctk.CTkFrame(card, fg_color="transparent")
        risk_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        self.panos_appfilter_risk = {}
        for level in [1, 2, 3, 4, 5]:
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(risk_frame, text=str(level), variable=var, width=50)
            cb.pack(side="left", padx=SPACING['xs'])
            self.panos_appfilter_risk[level] = var
        
        # Generate button
        gen_btn = StyledButton(card, text="💻 Generate Command", command=self.generate_appfilter, size="large", variant="primary")
        gen_btn.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['lg']))
    
    def create_panos_urlcat_tab(self):
        """Create Custom URL Category tab"""
        self.panos_urlcat_tab = ctk.CTkScrollableFrame(self.panos_tab_content)
        
        card = StyledCard(self.panos_urlcat_tab)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        title = SectionTitle(card, text="Custom URL Category")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(card, text="Create custom URL categories for URL filtering")
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Category Name
        name_label = ctk.CTkLabel(card, text="Category Name *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        name_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_urlcat_name = StyledEntry(card, placeholder_text="e.g., Blocked_Sites")
        self.panos_urlcat_name.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Description
        desc_label = ctk.CTkLabel(card, text="Description", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        desc_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_urlcat_desc = StyledEntry(card, placeholder_text="Optional description")
        self.panos_urlcat_desc.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # URL List
        url_label = ctk.CTkLabel(card, text="URLs (one per line) *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        url_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_urlcat_urls = ctk.CTkTextbox(card, height=150, font=ctk.CTkFont(size=FONTS['body'], family="Consolas"))
        self.panos_urlcat_urls.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        self.panos_urlcat_urls.insert("1.0", "example.com\n*.example.com\nexample.org/path")
        self.panos_urlcat_urls.configure(text_color=COLORS['text_secondary'])
        self.panos_urlcat_urls.bind("<FocusIn>", lambda e: self.on_textbox_focus_in(self.panos_urlcat_urls, "example.com\n*.example.com\nexample.org/path"))
        self.panos_urlcat_urls.bind("<FocusOut>", lambda e: self.on_textbox_focus_out(self.panos_urlcat_urls, "example.com\n*.example.com\nexample.org/path"))
        
        help_text = SubTitle(card, text="Supports domains, wildcards (*.domain.com), and paths")
        help_text.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Type
        type_label = ctk.CTkLabel(card, text="Type", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        type_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_urlcat_type = ctk.CTkComboBox(card, values=["URL List", "Category Match"], state="readonly")
        self.panos_urlcat_type.set("URL List")
        self.panos_urlcat_type.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Generate button
        gen_btn = StyledButton(card, text="💻 Generate Command", command=self.generate_urlcat, size="large", variant="primary")
        gen_btn.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['lg']))
    
    def create_panos_service_tab(self):
        """Create Service Objects tab"""
        self.panos_service_tab = ctk.CTkScrollableFrame(self.panos_tab_content)
        
        # Create two subtabs: Single Service and Service Group
        subtab_frame = ctk.CTkFrame(self.panos_service_tab, fg_color="transparent")
        subtab_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])
        
        self.service_single_btn = StyledButton(
            subtab_frame,
            text="Single Service",
            command=lambda: self.switch_service_subtab("single"),
            size="small",
            variant="primary"
        )
        self.service_single_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        self.service_group_btn = StyledButton(
            subtab_frame,
            text="Service Group",
            command=lambda: self.switch_service_subtab("group"),
            size="small",
            variant="neutral"
        )
        self.service_group_btn.pack(side="left")
        
        # Single Service Tab
        self.service_single_content = self.create_single_service_content(self.panos_service_tab)
        
        # Service Group Tab
        self.service_group_content = self.create_service_group_content(self.panos_service_tab)
        self.service_group_content.pack_forget()
    
    def create_single_service_content(self, parent):
        """Create single service object content"""
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="both", expand=True)
        
        card = StyledCard(content)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        title = SectionTitle(card, text="Service Object")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(card, text="Create TCP/UDP service objects")
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Service Name
        name_label = ctk.CTkLabel(card, text="Service Name *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        name_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_service_name = StyledEntry(card, placeholder_text="e.g., Web_Service")
        self.panos_service_name.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Port
        port_label = ctk.CTkLabel(card, text="Port Number *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        port_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_service_port = StyledEntry(card, placeholder_text="e.g., 8080 or 8080-8090")
        self.panos_service_port.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Protocol Selection with Checkbox
        protocol_label = ctk.CTkLabel(card, text="Protocol *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        protocol_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        protocol_frame = ctk.CTkFrame(card, fg_color="transparent")
        protocol_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        self.panos_service_protocol = ctk.CTkComboBox(
            protocol_frame,
            values=["tcp", "udp"],
            state="readonly",
            width=100
        )
        self.panos_service_protocol.set("tcp")
        self.panos_service_protocol.pack(side="left", padx=(0, SPACING['md']))
        
        # Checkbox for creating both TCP and UDP
        self.panos_service_both = ctk.BooleanVar(value=False)
        both_checkbox = ctk.CTkCheckBox(
            protocol_frame,
            text="Create both TCP and UDP services",
            variable=self.panos_service_both,
            font=ctk.CTkFont(size=FONTS['body'])
        )
        both_checkbox.pack(side="left")
        
        # Description
        desc_label = ctk.CTkLabel(card, text="Description", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        desc_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_service_desc = StyledEntry(card, placeholder_text="Optional description")
        self.panos_service_desc.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Generate button
        gen_btn = StyledButton(card, text="💻 Generate Command", command=self.generate_service_object, size="large", variant="primary")
        gen_btn.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        return content
    
    def create_service_group_content(self, parent):
        """Create service group content"""
        content = ctk.CTkFrame(parent, fg_color="transparent")
        
        card = StyledCard(content)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        title = SectionTitle(card, text="Service Group")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(card, text="Create service groups")
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Group Name
        name_label = ctk.CTkLabel(card, text="Group Name *", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        name_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_service_group_name = StyledEntry(card, placeholder_text="e.g., Web_Services")
        self.panos_service_group_name.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Members
        member_label = ctk.CTkLabel(card, text="Add Members", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        member_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        member_frame = ctk.CTkFrame(card, fg_color="transparent")
        member_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.panos_service_group_member = StyledEntry(member_frame, placeholder_text="Service name")
        self.panos_service_group_member.pack(side="left", fill="x", expand=True, padx=(0, SPACING['xs']))
        
        add_btn = StyledButton(
            member_frame,
            text="Add",
            command=self.add_service_group_member,
            size="small",
            variant="neutral"
        )
        add_btn.pack(side="left")
        
        # Bulk paste
        bulk_label = ctk.CTkLabel(card, text="Or paste multiple services (one per line):", font=ctk.CTkFont(size=FONTS['body'], weight="bold"))
        bulk_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['sm'], SPACING['xs']))
        
        self.panos_service_group_bulk = ctk.CTkTextbox(card, height=80, font=ctk.CTkFont(size=FONTS['body']))
        self.panos_service_group_bulk.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        bulk_add_btn = StyledButton(
            card,
            text="Add All from List",
            command=self.add_bulk_service_members,
            size="small",
            variant="neutral"
        )
        bulk_add_btn.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Members display
        self.panos_service_group_members = []
        self.panos_service_group_display = ctk.CTkFrame(card, fg_color=COLORS['bg_card'])
        self.panos_service_group_display.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        self.panos_service_group_display.configure(height=100)
        
        # Generate button
        gen_btn = StyledButton(card, text="💻 Generate Command", command=self.generate_service_group, size="large", variant="primary")
        gen_btn.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        return content
    
    def switch_service_subtab(self, subtab):
        """Switch between service subtabs"""
        if subtab == "single":
            self.service_single_btn.configure(fg_color=COLORS['primary'])
            self.service_group_btn.configure(fg_color=COLORS['neutral'])
            self.service_group_content.pack_forget()
            self.service_single_content.pack(fill="both", expand=True)
        else:
            self.service_single_btn.configure(fg_color=COLORS['neutral'])
            self.service_group_btn.configure(fg_color=COLORS['primary'])
            self.service_single_content.pack_forget()
            self.service_group_content.pack(fill="both", expand=True)
    
    def validate_panos_ip(self, ip):
        """Validate IP address or network with CIDR notation"""
        pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})(\/(\d{1,2}))?$'
        match = re.match(pattern, ip)
        
        if not match:
            return False
        
        # Validate each octet is 0-255
        octets = [int(match.group(i)) for i in range(1, 5)]
        if any(octet > 255 for octet in octets):
            return False
        
        # Validate CIDR prefix if present
        if match.group(5):  # Has CIDR
            cidr = int(match.group(6))
            if cidr > 32:
                return False
        
        return True
    
    def on_textbox_focus_in(self, textbox, placeholder):
        """Handle textbox focus in - clear placeholder if present"""
        current_text = textbox.get("1.0", "end-1c")
        if current_text == placeholder:
            textbox.delete("1.0", "end")
            textbox.configure(text_color=COLORS['text'])
    
    def on_textbox_focus_out(self, textbox, placeholder):
        """Handle textbox focus out - restore placeholder if empty"""
        current_text = textbox.get("1.0", "end-1c").strip()
        if not current_text:
            textbox.insert("1.0", placeholder)
            textbox.configure(text_color=COLORS['text_secondary'])
    
    def on_panos_format_change(self, choice):
        """Show/hide custom format input"""
        if choice == "Custom":
            self.panos_custom_format_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        else:
            self.panos_custom_format_frame.pack_forget()
    
    def generate_panos_names(self):
        """Generate object names from base names and IPs"""
        names_text = self.panos_gen_names.get("1.0", "end").strip()
        ips_text = self.panos_gen_ips.get("1.0", "end").strip()
        
        # Check if placeholder text is still present
        if names_text == self.panos_gen_names_placeholder or ips_text == self.panos_gen_ips_placeholder:
            messagebox.showerror("Error", "Please replace the placeholder text with your actual data")
            return
        
        if not names_text or not ips_text:
            messagebox.showerror("Error", "Please fill in both base names and IPs")
            return
        
        names = [n.strip() for n in names_text.split('\n') if n.strip()]
        ips = [i.strip() for i in ips_text.split('\n') if i.strip()]
        
        if len(names) != len(ips):
            messagebox.showerror("Error", f"Number of names ({len(names)}) doesn't match number of IPs ({len(ips)})")
            return
        
        # Get separator
        sep_map = {"_ (Underscore)": "_", "- (Dash)": "-", ". (Dot)": "."}
        separator = sep_map.get(self.panos_gen_separator.get(), "_")
        
        # Get format
        format_choice = self.panos_gen_format.get()
        
        self.panos_generated_names = []
        
        for i in range(len(names)):
            name = names[i]
            ip = ips[i]
            
            # Validate IP
            if not self.validate_panos_ip(ip):
                messagebox.showerror("Error", f"Invalid IP address or format: {ip}\nExpected format: 192.168.1.10 or 192.168.1.0/24")
                return
            
            # Generate name based on format
            # Keep dots in IPs, only replace slashes
            ip_formatted = ip.replace('/', separator)
            
            if format_choice == "Name_IP":
                generated_name = f"{name}{separator}{ip_formatted}"
            elif format_choice == "IP_Name":
                generated_name = f"{ip_formatted}{separator}{name}"
            elif format_choice == "Name Only":
                generated_name = name
            elif format_choice == "Custom":
                custom_pattern = self.panos_gen_custom.get().strip()
                if not custom_pattern:
                    messagebox.showerror("Error", "Please provide a custom format pattern")
                    return
                generated_name = custom_pattern.replace('{name}', name).replace('{ip}', ip_formatted)
            else:
                generated_name = f"{name}{separator}{ip_formatted}"
            
            self.panos_generated_names.append({
                'name': name,
                'ip': ip,
                'generated_name': generated_name
            })
        
        # Show popup with generated names
        self.show_generated_names_popup()
    
    def show_generated_names_popup(self):
        """Show popup window with generated names"""
        popup = ctk.CTkToplevel(self)
        popup.title("Generated Names")
        popup.geometry("600x500")
        
        # Title
        title_label = ctk.CTkLabel(
            popup,
            text=f"✅ Generated {len(self.panos_generated_names)} Names",
            font=ctk.CTkFont(size=FONTS['heading'], weight="bold")
        )
        title_label.pack(pady=SPACING['lg'])
        
        # Names list in textbox
        names_text = '\n'.join([item['generated_name'] for item in self.panos_generated_names])
        
        textbox = ctk.CTkTextbox(
            popup,
            font=ctk.CTkFont(size=FONTS['body'], family="Consolas"),
            wrap="none"
        )
        textbox.pack(fill="both", expand=True, padx=SPACING['lg'], pady=(0, SPACING['md']))
        textbox.insert("1.0", names_text)
        textbox.configure(state="disabled")  # Read-only
        
        # Button frame
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Copy button
        copy_btn = StyledButton(
            btn_frame,
            text="📋 Copy to Clipboard",
            command=lambda: self.copy_generated_names(names_text, popup),
            size="medium",
            variant="primary"
        )
        copy_btn.pack(side="left", fill="x", expand=True, padx=(0, SPACING['xs']))
        
        # Close button
        close_btn = StyledButton(
            btn_frame,
            text="✓ OK",
            command=popup.destroy,
            size="medium",
            variant="success"
        )
        close_btn.pack(side="left", fill="x", expand=True, padx=(SPACING['xs'], 0))
        
        # Center the popup
        popup.transient(self)
        popup.grab_set()
        popup.focus()
    
    def copy_generated_names(self, text, popup):
        """Copy generated names to clipboard"""
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "Generated names copied to clipboard!", parent=popup)
    
    def reset_panos_name_generator(self):
        """Reset all fields in the Name Generator tab"""
        # Clear and restore placeholders for textboxes
        self.panos_gen_names.delete("1.0", "end")
        self.panos_gen_names.insert("1.0", self.panos_gen_names_placeholder)
        self.panos_gen_names.configure(text_color=COLORS['text_secondary'])
        
        self.panos_gen_ips.delete("1.0", "end")
        self.panos_gen_ips.insert("1.0", self.panos_gen_ips_placeholder)
        self.panos_gen_ips.configure(text_color=COLORS['text_secondary'])
        
        # Reset dropdown selections
        self.panos_gen_separator.set("_ (Underscore)")
        self.panos_gen_format.set("Name_IP")
        
        # Clear custom format if visible
        self.panos_gen_custom.delete(0, 'end')
        self.panos_custom_format_frame.pack_forget()
        
        # Clear preview
        self.panos_preview_text.delete("1.0", "end")
        
        # Hide preview and step 2
        self.panos_preview_frame.pack_forget()
        self.panos_step2_frame.pack_forget()
        
        # Clear generated names
        self.panos_generated_names = []
        
        messagebox.showinfo("Reset Complete", "Name Generator has been reset")
    
    def generate_panos_from_names(self):
        """Generate CLI commands from generated names"""
        if not self.panos_generated_names:
            messagebox.showerror("Error", "Please generate names first")
            return
        
        is_shared = self.panos_gen_shared.get()
        base_path = "shared" if is_shared else "vsys vsys1"
        
        commands = []
        for item in self.panos_generated_names:
            cmd = f'set {base_path} address "{item["generated_name"]}" ip-netmask {item["ip"]}'
            commands.append(cmd)
        
        full_cmd = "configure\n" + '\n'.join(commands) + "\ncommit"
        self.panos_commands.append(full_cmd)
        self.render_panos_commands()
        messagebox.showinfo("Success", f"Generated {len(commands)} address object commands!")
    
    def generate_single_address(self):
        """Generate single address object command"""
        name = self.panos_single_name.get().strip()
        ip = self.panos_single_ip.get().strip()
        desc = self.panos_single_desc.get().strip()
        is_shared = self.panos_single_shared.get()
        
        if not name or not ip:
            messagebox.showerror("Error", "Please fill in Object Name and IP Address")
            return
        
        # Validate IP
        if not self.validate_panos_ip(ip):
            messagebox.showerror("Error", f"Invalid IP address or format: {ip}\nExpected format: 192.168.1.10 or 192.168.1.0/24")
            return
        
        base_path = "shared" if is_shared else "vsys vsys1"
        cmd = f'configure\nset {base_path} address "{name}" ip-netmask {ip}'
        if desc:
            cmd += f' description "{desc}"'
        cmd += '\ncommit'
        
        self.panos_commands.append(cmd)
        self.render_panos_commands()
        
        # Clear form
        self.panos_single_name.delete(0, 'end')
        self.panos_single_ip.delete(0, 'end')
        self.panos_single_desc.delete(0, 'end')
        
        messagebox.showinfo("Success", "Address object command generated!")
    
    def add_group_member(self):
        """Add member to address group"""
        member = self.panos_group_member_input.get().strip()
        if member and member not in self.panos_group_members:
            self.panos_group_members.append(member)
            self.render_group_members()
            self.panos_group_member_input.delete(0, 'end')
    
    def add_bulk_group_members(self):
        """Add multiple members from bulk paste text area"""
        bulk_text = self.panos_group_bulk_paste.get("1.0", "end-1c").strip()
        if not bulk_text:
            return
        
        # Parse lines and add each member
        lines = bulk_text.split('\n')
        added_count = 0
        for line in lines:
            member = line.strip()
            if member and member not in self.panos_group_members:
                self.panos_group_members.append(member)
                added_count += 1
        
        if added_count > 0:
            self.render_group_members()
            self.panos_group_bulk_paste.delete("1.0", "end")
            messagebox.showinfo("Success", f"Added {added_count} member(s) to the group")
    
    def remove_group_member(self, member):
        """Remove member from address group"""
        if member in self.panos_group_members:
            self.panos_group_members.remove(member)
            self.render_group_members()
    
    def render_group_members(self):
        """Render group members display"""
        # Clear existing
        for widget in self.panos_group_members_display.winfo_children():
            widget.destroy()
        
        if not self.panos_group_members:
            empty_label = ctk.CTkLabel(
                self.panos_group_members_display,
                text="No members added yet",
                text_color=COLORS['text_secondary'],
                font=ctk.CTkFont(size=FONTS['small'])
            )
            empty_label.pack(pady=SPACING['lg'])
            return
        
        # Create scrollable frame for members
        members_frame = ctk.CTkFrame(self.panos_group_members_display, fg_color="transparent")
        members_frame.pack(fill="both", expand=True, padx=SPACING['sm'], pady=SPACING['sm'])
        
        for member in self.panos_group_members:
            member_frame = ctk.CTkFrame(members_frame, fg_color=COLORS['neutral'], corner_radius=15)
            member_frame.pack(side="left", padx=(0, SPACING['xs']), pady=SPACING['xs'])
            
            member_label = ctk.CTkLabel(
                member_frame,
                text=member,
                font=ctk.CTkFont(size=FONTS['small'])
            )
            member_label.pack(side="left", padx=(SPACING['sm'], SPACING['xs']))
            
            remove_btn = ctk.CTkButton(
                member_frame,
                text="×",
                width=20,
                height=20,
                fg_color="transparent",
                hover_color=COLORS['danger'],
                command=lambda m=member: self.remove_group_member(m),
                font=ctk.CTkFont(size=14, weight="bold")
            )
            remove_btn.pack(side="right", padx=(0, SPACING['xs']))
    
    def generate_address_group(self):
        """Generate address group command"""
        if not self.panos_group_members:
            messagebox.showerror("Error", "Please add at least one member")
            return
        
        vsys = self.panos_group_vsys.get()
        name = self.panos_group_name.get().strip()
        desc = self.panos_group_desc.get().strip()
        group_type = self.panos_group_type.get().lower()
        
        if not name:
            messagebox.showerror("Error", "Please enter a group name")
            return
        
        # Set correct base path - "shared" or "vsys vsysX"
        base_path = "shared" if vsys == "shared" else f"vsys {vsys}"
        
        cmd = 'configure\n'
        for member in self.panos_group_members:
            cmd += f'set {base_path} address-group "{name}" {group_type} "{member}"\n'
        
        if desc:
            cmd += f'set {base_path} address-group "{name}" description "{desc}"\n'
        
        cmd += 'commit'
        
        self.panos_commands.append(cmd)
        self.render_panos_commands()
        
        # Clear form
        self.panos_group_name.delete(0, 'end')
        self.panos_group_desc.delete(0, 'end')
        self.panos_group_members = []
        self.render_group_members()
        
        messagebox.showinfo("Success", "Address group command generated!")
    
    def generate_nat_rule(self):
        """Generate NAT rule command"""
        nat_type = self.panos_nat_type_var.get()
        vsys = self.panos_nat_vsys.get()
        name = self.panos_nat_name.get().strip()
        from_zone = self.panos_nat_from.get().strip()
        to_zone = self.panos_nat_to.get().strip()
        source = self.panos_nat_source.get().strip()
        dest = self.panos_nat_dest.get().strip()
        service = self.panos_nat_service.get().strip()
        translated = self.panos_nat_translated.get().strip()
        port = self.panos_nat_port.get().strip()
        desc = self.panos_nat_desc.get().strip()
        
        if not all([name, from_zone, to_zone, dest, translated]):
            messagebox.showerror("Error", "Please fill in all required fields (marked with *)")
            return
        
        # Set correct base path - "shared" or "vsys vsysX"
        base_path = "shared" if vsys == "shared" else f"vsys {vsys}"
        base = f'set {base_path} rulebase nat rules "{name}"'
        cmd = 'configure\n'
        cmd += f'{base} from "{from_zone}"\n'
        cmd += f'{base} to "{to_zone}"\n'
        cmd += f'{base} source "{source}"\n'
        cmd += f'{base} destination "{dest}"\n'
        cmd += f'{base} service "{service}"\n'
        
        if nat_type == "dnat":
            cmd += f'{base} destination-translation translated-address "{translated}"'
            if port:
                cmd += f' translated-port {port}'
            cmd += '\n'
        else:
            cmd += f'{base} source-translation dynamic-ip-and-port translated-address "{translated}"\n'
        
        if desc:
            cmd += f'{base} description "{desc}"\n'
        
        cmd += 'commit'
        
        self.panos_commands.append(cmd)
        self.render_panos_commands()
        
        # Clear form
        self.panos_nat_name.delete(0, 'end')
        self.panos_nat_from.delete(0, 'end')
        self.panos_nat_to.delete(0, 'end')
        self.panos_nat_dest.delete(0, 'end')
        self.panos_nat_translated.delete(0, 'end')
        self.panos_nat_port.delete(0, 'end')
        self.panos_nat_desc.delete(0, 'end')
        
        messagebox.showinfo("Success", "NAT rule command generated!")
    
    def generate_policy_rule(self):
        """Generate security policy rule command"""
        vsys = self.panos_policy_vsys.get()
        name = self.panos_policy_name.get().strip()
        from_zone = self.panos_policy_from.get().strip()
        to_zone = self.panos_policy_to.get().strip()
        source = self.panos_policy_source.get().strip()
        dest = self.panos_policy_dest.get().strip()
        app = self.panos_policy_app.get().strip()
        service = self.panos_policy_service.get().strip()
        action = self.panos_policy_action.get()
        profile = self.panos_policy_profile.get().strip()
        desc = self.panos_policy_desc.get().strip()
        
        if not all([name, from_zone, to_zone]):
            messagebox.showerror("Error", "Please fill in all required fields (marked with *)")
            return
        
        # Set correct base path - "shared" or "vsys vsysX"
        base_path = "shared" if vsys == "shared" else f"vsys {vsys}"
        base = f'set {base_path} rulebase security rules "{name}"'
        cmd = 'configure\n'
        cmd += f'{base} from "{from_zone}"\n'
        cmd += f'{base} to "{to_zone}"\n'
        cmd += f'{base} source "{source}"\n'
        cmd += f'{base} destination "{dest}"\n'
        cmd += f'{base} application "{app}"\n'
        cmd += f'{base} service "{service}"\n'
        cmd += f'{base} action {action}\n'
        
        if profile:
            cmd += f'{base} profile-setting group "{profile}"\n'
        
        if desc:
            cmd += f'{base} description "{desc}"\n'
        
        cmd += 'commit'
        
        self.panos_commands.append(cmd)
        self.render_panos_commands()
        
        # Clear form
        self.panos_policy_name.delete(0, 'end')
        self.panos_policy_from.delete(0, 'end')
        self.panos_policy_to.delete(0, 'end')
        self.panos_policy_profile.delete(0, 'end')
        self.panos_policy_desc.delete(0, 'end')
        
        messagebox.showinfo("Success", "Security policy rule command generated!")
    
    def generate_panos_address_objects(self):
        """Generate address object commands"""
        names_text = self.panos_addr_names.get("1.0", "end").strip()
        ips_text = self.panos_addr_ips.get("1.0", "end").strip()
        
        if not names_text or not ips_text:
            messagebox.showerror("Error", "Please fill in both names and IPs")
            return
        
        names = [n.strip() for n in names_text.split('\n') if n.strip()]
        ips = [i.strip() for i in ips_text.split('\n') if i.strip()]
        
        if len(names) != len(ips):
            messagebox.showerror("Error", f"Number of names ({len(names)}) doesn't match number of IPs ({len(ips)})")
            return
        
        is_shared = self.panos_addr_shared.get()
        base_path = "shared" if is_shared else "vsys vsys1"
        
        commands = []
        for i in range(len(names)):
            name = names[i]
            ip = ips[i]
            
            # Validate IP
            if not self.validate_panos_ip(ip):
                messagebox.showerror("Error", f"Invalid IP address or format: {ip}\nExpected format: 192.168.1.10 or 192.168.1.0/24")
                return
            
            cmd = f'set {base_path} address "{name}" ip-netmask {ip}'
            commands.append(cmd)
        
        full_cmd = "configure\n" + '\n'.join(commands) + "\ncommit"
        self.panos_commands.append(full_cmd)
        self.render_panos_commands()
        messagebox.showinfo("Success", f"Generated {len(commands)} address object commands!")
    
    def generate_schedule_object(self):
        """Generate schedule object command"""
        name = self.panos_schedule_name.get().strip()
        schedule_type = self.panos_schedule_type.get()
        start_time = self.panos_schedule_start.get().strip()
        end_time = self.panos_schedule_end.get().strip()
        
        if not all([name, start_time, end_time]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        # Build command
        cmd = 'configure\n'
        cmd += f'set schedule "{name}" schedule-type {schedule_type}\n'
        
        if schedule_type == "recurring":
            # Get selected days
            selected_days = [day for day, var in self.panos_schedule_days.items() if var.get()]
            if selected_days:
                days_str = " ".join(selected_days)
                cmd += f'set schedule "{name}" recurring daily {days_str} {start_time}-{end_time}\n'
        else:
            # Non-recurring would need date range (simplified here)
            cmd += f'set schedule "{name}" non-recurring {start_time}-{end_time}\n'
        
        cmd += 'commit'
        
        self.panos_commands.append(cmd)
        self.render_panos_commands()
        messagebox.showinfo("Success", "Schedule object command generated!")
    
    def generate_appfilter(self):
        """Generate application filter command"""
        name = self.panos_appfilter_name.get().strip()
        category = self.panos_appfilter_category.get()
        subcategory = self.panos_appfilter_subcategory.get().strip()
        technology = self.panos_appfilter_technology.get()
        
        if not name:
            messagebox.showerror("Error", "Please enter a filter name")
            return
        
        # Build command
        cmd = 'configure\n'
        cmd += f'set profiles custom-url-category "{name}" type "URL List"\n'
        
        # Add category filter
        cmd += f'set application-filter "{name}" category {category}\n'
        
        if subcategory:
            cmd += f'set application-filter "{name}" subcategory {subcategory}\n'
        
        cmd += f'set application-filter "{name}" technology {technology}\n'
        
        # Add risk levels
        selected_risks = [str(level) for level, var in self.panos_appfilter_risk.items() if var.get()]
        if selected_risks:
            for risk in selected_risks:
                cmd += f'set application-filter "{name}" risk {risk}\n'
        
        cmd += 'commit'
        
        self.panos_commands.append(cmd)
        self.render_panos_commands()
        messagebox.showinfo("Success", "Application filter command generated!")
    
    def generate_urlcat(self):
        """Generate custom URL category command"""
        name = self.panos_urlcat_name.get().strip()
        desc = self.panos_urlcat_desc.get().strip()
        urls_text = self.panos_urlcat_urls.get("1.0", "end-1c").strip()
        url_type = self.panos_urlcat_type.get()
        
        # Check if placeholder
        if urls_text == "example.com\n*.example.com\nexample.org/path":
            messagebox.showerror("Error", "Please replace placeholder text with actual URLs")
            return
        
        if not name or not urls_text:
            messagebox.showerror("Error", "Please fill in name and URLs")
            return
        
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        if not urls:
            messagebox.showerror("Error", "Please enter at least one URL")
            return
        
        # Build command
        cmd = 'configure\n'
        cmd += f'set profiles custom-url-category "{name}" type "{url_type}"\n'
        
        if desc:
            cmd += f'set profiles custom-url-category "{name}" description "{desc}"\n'
        
        # Add URLs
        for url in urls:
            cmd += f'set profiles custom-url-category "{name}" list {url}\n'
        
        cmd += 'commit'
        
        self.panos_commands.append(cmd)
        self.render_panos_commands()
        messagebox.showinfo("Success", f"URL category command generated with {len(urls)} URLs!")
    
    def generate_service_object(self):
        """Generate service object command"""
        name = self.panos_service_name.get().strip()
        port = self.panos_service_port.get().strip()
        protocol = self.panos_service_protocol.get()
        desc = self.panos_service_desc.get().strip()
        create_both = self.panos_service_both.get()
        
        if not name or not port:
            messagebox.showerror("Error", "Please enter service name and port")
            return
        
        commands = []
        
        if create_both:
            # Create TCP service
            tcp_name = f"TCP-{name}"
            cmd_tcp = 'configure\n'
            cmd_tcp += f'set service "{tcp_name}" protocol tcp port {port}\n'
            if desc:
                cmd_tcp += f'set service "{tcp_name}" description "{desc} (TCP)"\n'
            cmd_tcp += 'commit'
            commands.append(cmd_tcp)
            
            # Create UDP service
            udp_name = f"UDP-{name}"
            cmd_udp = 'configure\n'
            cmd_udp += f'set service "{udp_name}" protocol udp port {port}\n'
            if desc:
                cmd_udp += f'set service "{udp_name}" description "{desc} (UDP)"\n'
            cmd_udp += 'commit'
            commands.append(cmd_udp)
            
            self.panos_commands.extend(commands)
            self.render_panos_commands()
            messagebox.showinfo("Success", f"Generated 2 service commands (TCP and UDP)!")
        else:
            # Create single service
            cmd = 'configure\n'
            cmd += f'set service "{name}" protocol {protocol} port {port}\n'
            if desc:
                cmd += f'set service "{name}" description "{desc}"\n'
            cmd += 'commit'
            
            self.panos_commands.append(cmd)
            self.render_panos_commands()
            messagebox.showinfo("Success", "Service object command generated!")
    
    def add_service_group_member(self):
        """Add member to service group"""
        member = self.panos_service_group_member.get().strip()
        if member and member not in self.panos_service_group_members:
            self.panos_service_group_members.append(member)
            self.render_service_group_members()
            self.panos_service_group_member.delete(0, 'end')
    
    def add_bulk_service_members(self):
        """Add multiple service members from bulk paste"""
        bulk_text = self.panos_service_group_bulk.get("1.0", "end-1c").strip()
        if not bulk_text:
            return
        
        lines = bulk_text.split('\n')
        added_count = 0
        for line in lines:
            member = line.strip()
            if member and member not in self.panos_service_group_members:
                self.panos_service_group_members.append(member)
                added_count += 1
        
        if added_count > 0:
            self.render_service_group_members()
            self.panos_service_group_bulk.delete("1.0", "end")
            messagebox.showinfo("Success", f"Added {added_count} service(s) to the group")
    
    def render_service_group_members(self):
        """Render service group members"""
        for widget in self.panos_service_group_display.winfo_children():
            widget.destroy()
        
        if not self.panos_service_group_members:
            empty_label = ctk.CTkLabel(
                self.panos_service_group_display,
                text="No members added yet",
                text_color=COLORS['text_secondary']
            )
            empty_label.pack(pady=SPACING['md'])
            return
        
        for member in self.panos_service_group_members:
            member_frame = ctk.CTkFrame(self.panos_service_group_display, fg_color="transparent")
            member_frame.pack(fill="x", padx=SPACING['sm'], pady=SPACING['xs'])
            
            member_label = ctk.CTkLabel(
                member_frame,
                text=member,
                font=ctk.CTkFont(size=FONTS['body'])
            )
            member_label.pack(side="left", fill="x", expand=True)
            
            remove_btn = ctk.CTkButton(
                member_frame,
                text="✕",
                command=lambda m=member: self.remove_service_group_member(m),
                width=30,
                height=25,
                fg_color="transparent",
                hover_color=COLORS['danger'],
                text_color=COLORS['danger']
            )
            remove_btn.pack(side="right")
    
    def remove_service_group_member(self, member):
        """Remove member from service group"""
        if member in self.panos_service_group_members:
            self.panos_service_group_members.remove(member)
            self.render_service_group_members()
    
    def generate_service_group(self):
        """Generate service group command"""
        name = self.panos_service_group_name.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter group name")
            return
        
        if not self.panos_service_group_members:
            messagebox.showerror("Error", "Please add at least one service member")
            return
        
        cmd = 'configure\n'
        for member in self.panos_service_group_members:
            cmd += f'set service-group "{name}" members {member}\n'
        cmd += 'commit'
        
        self.panos_commands.append(cmd)
        self.render_panos_commands()
        messagebox.showinfo("Success", f"Service group command generated with {len(self.panos_service_group_members)} members!")
    
    def render_panos_commands(self):
        """Render commands in output panel"""
        # Clear existing
        for widget in self.panos_commands_list.winfo_children():
            widget.destroy()
        
        # Update count
        self.panos_cmd_count.configure(text=f"{len(self.panos_commands)} command{'s' if len(self.panos_commands) != 1 else ''} generated")
        
        if len(self.panos_commands) == 0:
            empty_state = ctk.CTkFrame(self.panos_commands_list, fg_color="transparent")
            empty_state.pack(fill="both", expand=True, pady=SPACING['xl'])
            
            empty_text = ctk.CTkLabel(
                empty_state,
                text="📋\n\nNo commands generated yet\n\nFill out the form to generate CLI commands",
                font=ctk.CTkFont(size=FONTS['body']),
                text_color=COLORS['text_secondary']
            )
            empty_text.pack(expand=True)
            self.panos_action_frame.pack_forget()
            return
        
        self.panos_action_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        for i, cmd in enumerate(self.panos_commands):
            cmd_frame = ctk.CTkFrame(self.panos_commands_list, fg_color=COLORS['bg_card'])
            cmd_frame.pack(fill="x", pady=(0, SPACING['xs']))
            
            cmd_text = ctk.CTkTextbox(
                cmd_frame,
                height=100,
                font=ctk.CTkFont(size=FONTS['small'], family="Consolas"),
                wrap="none"
            )
            cmd_text.pack(fill="both", expand=True, padx=SPACING['sm'], pady=SPACING['sm'])
            cmd_text.insert("1.0", cmd)
            cmd_text.configure(state="disabled")
            
            # Remove button
            remove_btn = StyledButton(
                cmd_frame,
                text="✗",
                command=lambda idx=i: self.remove_panos_command(idx),
                size="small",
                variant="danger"
            )
            remove_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-SPACING['sm'], y=SPACING['sm'])
    
    def remove_panos_command(self, index):
        """Remove a command"""
        if 0 <= index < len(self.panos_commands):
            self.panos_commands.pop(index)
            self.render_panos_commands()
    
    def clear_panos_commands(self):
        """Clear all commands"""
        if self.panos_commands and messagebox.askyesno("Clear Commands", "Clear all generated commands?"):
            self.panos_commands = []
            self.render_panos_commands()
    
    def copy_panos_commands(self):
        """Copy all commands to clipboard"""
        if not self.panos_commands:
            return
        
        text = '\n\n'.join(self.panos_commands)
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Success", "Commands copied to clipboard!")
    
    def download_panos_commands(self):
        """Download commands to file"""
        if not self.panos_commands:
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"panos-commands.txt"
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write('\n\n'.join(self.panos_commands))
                messagebox.showinfo("Success", f"Commands saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
    
