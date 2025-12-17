"""
Settings UI Module
Allows users to customize which tools are visible in the navigation
"""

import customtkinter as ctk
from design_constants import COLORS, SPACING
from ui_components import StyledCard, StyledButton, SectionTitle


class SettingsUI:
    """Settings page for tool visibility and app preferences"""
    
    # All available tools with their info
    ALL_TOOLS = {
        # Dashboard category
        "dashboard": {"name": "Dashboard", "icon": "📊", "category": "Dashboard", "default": True, "required": True},
        
        # Scanning category
        "scanner": {"name": "IPv4 Scanner", "icon": "🔍", "category": "Scanning", "default": True},
        "portscan": {"name": "Port Scanner", "icon": "🔌", "category": "Scanning", "default": True},
        "dns": {"name": "DNS Lookup", "icon": "🌐", "category": "Scanning", "default": True},
        "traceroute": {"name": "Traceroute", "icon": "🔀", "category": "Scanning", "default": True},
        "arp": {"name": "ARP Table", "icon": "📋", "category": "Scanning", "default": True},
        
        # Tools category
        "subnet": {"name": "Subnet Calculator", "icon": "🔢", "category": "Tools", "default": True},
        "mac": {"name": "MAC Formatter", "icon": "🔗", "category": "Tools", "default": True},
        "whois": {"name": "WHOIS Lookup", "icon": "🔎", "category": "Tools", "default": True},
        "ssl": {"name": "SSL Checker", "icon": "🔐", "category": "Tools", "default": True},
        "hash": {"name": "Hash Generator", "icon": "#", "category": "Tools", "default": True},
        "api": {"name": "API Tester", "icon": "📡", "category": "Tools", "default": True},
        "password": {"name": "Password Generator", "icon": "🔑", "category": "Tools", "default": True},
        "speedtest": {"name": "Speed Test", "icon": "⚡", "category": "Tools", "default": True},
        
        # Advanced category
        "compare": {"name": "Scan Comparison", "icon": "⚖️", "category": "Advanced", "default": True},
        "profiles": {"name": "Network Profiles", "icon": "📁", "category": "Advanced", "default": True},
        "bandwidth": {"name": "Bandwidth Monitor", "icon": "📈", "category": "Advanced", "default": True},
        "panos": {"name": "PAN-OS Generator", "icon": "🔒", "category": "Advanced", "default": True},
        "phpipam": {"name": "phpIPAM", "icon": "📊", "category": "Advanced", "default": True},
    }
    
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.checkboxes = {}
        self.create_ui()
    
    def create_ui(self):
        """Create the settings UI"""
        # Main container with scrolling
        main_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="transparent"
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['electric_violet']
        )
        title_label.pack(side="left")
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Customize your NetTools experience",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        subtitle.pack(side="left", padx=(15, 0))
        
        # Tool Visibility Section
        visibility_card = StyledCard(main_frame, variant="elevated")
        visibility_card.pack(fill="x", pady=(0, 15))
        
        vis_header = ctk.CTkFrame(visibility_card, fg_color="transparent")
        vis_header.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            vis_header,
            text="🛠️ Tool Visibility",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        ctk.CTkLabel(
            vis_header,
            text="Enable or disable tools in the navigation menu",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary']
        ).pack(side="left", padx=(15, 0))
        
        # Quick actions
        quick_frame = ctk.CTkFrame(visibility_card, fg_color="transparent")
        quick_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        StyledButton(
            quick_frame,
            text="✓ Enable All",
            command=self._enable_all,
            variant="secondary",
            width=100
        ).pack(side="left", padx=(0, 10))
        
        StyledButton(
            quick_frame,
            text="✗ Disable All",
            command=self._disable_all,
            variant="secondary",
            width=100
        ).pack(side="left", padx=(0, 10))
        
        StyledButton(
            quick_frame,
            text="↺ Reset Defaults",
            command=self._reset_defaults,
            variant="secondary",
            width=120
        ).pack(side="left")
        
        # Get current enabled tools
        enabled_tools = self.app.get_enabled_tools()
        
        # Group tools by category
        categories = {}
        for tool_id, tool_info in self.ALL_TOOLS.items():
            cat = tool_info["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((tool_id, tool_info))
        
        # Create category sections
        for category_name in ["Dashboard", "Scanning", "Tools", "Advanced"]:
            if category_name not in categories:
                continue
            
            tools = categories[category_name]
            
            # Category frame
            cat_frame = ctk.CTkFrame(visibility_card, fg_color=COLORS.get('bg_tertiary', 'gray20'))
            cat_frame.pack(fill="x", padx=15, pady=5)
            
            # Category header
            ctk.CTkLabel(
                cat_frame,
                text=f"  {category_name}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS['neon_cyan']
            ).pack(anchor="w", padx=10, pady=(8, 5))
            
            # Tools grid
            tools_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
            tools_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            # Create checkboxes in a grid (3 columns)
            for idx, (tool_id, tool_info) in enumerate(tools):
                col = idx % 3
                row = idx // 3
                
                is_enabled = tool_id in enabled_tools
                is_required = tool_info.get("required", False)
                
                cb_frame = ctk.CTkFrame(tools_frame, fg_color="transparent", width=200)
                cb_frame.grid(row=row, column=col, sticky="w", padx=5, pady=3)
                
                cb_var = ctk.BooleanVar(value=is_enabled)
                
                cb = ctk.CTkCheckBox(
                    cb_frame,
                    text=f"{tool_info['icon']}  {tool_info['name']}",
                    variable=cb_var,
                    font=ctk.CTkFont(size=12),
                    fg_color=COLORS['electric_violet'],
                    hover_color=COLORS['electric_violet_hover'],
                    command=lambda tid=tool_id: self._on_tool_toggle(tid),
                    state="disabled" if is_required else "normal"
                )
                cb.pack(anchor="w")
                
                if is_required:
                    # Add "(required)" label
                    ctk.CTkLabel(
                        cb_frame,
                        text="(required)",
                        font=ctk.CTkFont(size=9),
                        text_color=COLORS['text_secondary']
                    ).pack(anchor="w", padx=(25, 0))
                
                self.checkboxes[tool_id] = (cb, cb_var)
        
        # Spacer
        ctk.CTkFrame(visibility_card, height=10, fg_color="transparent").pack()
        
        # Apply button
        apply_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        apply_frame.pack(fill="x", pady=(10, 0))
        
        StyledButton(
            apply_frame,
            text="💾 Apply Changes",
            command=self._apply_changes,
            variant="primary",
            width=150
        ).pack(side="left")
        
        self.status_label = ctk.CTkLabel(
            apply_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['success']
        )
        self.status_label.pack(side="left", padx=(15, 0))
        
        # Info section
        info_card = StyledCard(main_frame, variant="default")
        info_card.pack(fill="x", pady=(20, 0))
        
        ctk.CTkLabel(
            info_card,
            text="ℹ️ Note",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            info_card,
            text="• Changes take effect after clicking 'Apply Changes'\n"
                 "• Dashboard is required and cannot be disabled\n"
                 "• Disabled tools are hidden from the navigation menu\n"
                 "• Your preferences are saved automatically",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary'],
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 15))
    
    def _on_tool_toggle(self, tool_id):
        """Handle tool checkbox toggle"""
        pass  # Just update the variable, apply on button click
    
    def _enable_all(self):
        """Enable all tools"""
        for tool_id, (cb, var) in self.checkboxes.items():
            var.set(True)
    
    def _disable_all(self):
        """Disable all optional tools"""
        for tool_id, (cb, var) in self.checkboxes.items():
            tool_info = self.ALL_TOOLS.get(tool_id, {})
            if not tool_info.get("required", False):
                var.set(False)
    
    def _reset_defaults(self):
        """Reset to default tool visibility"""
        for tool_id, (cb, var) in self.checkboxes.items():
            tool_info = self.ALL_TOOLS.get(tool_id, {})
            var.set(tool_info.get("default", True))
    
    def _apply_changes(self):
        """Apply visibility changes"""
        enabled_tools = set()
        for tool_id, (cb, var) in self.checkboxes.items():
            if var.get():
                enabled_tools.add(tool_id)
        
        # Save to app
        self.app.set_enabled_tools(enabled_tools)
        
        # Show status
        self.status_label.configure(text="✓ Changes saved! Restart app to see navigation changes.")
        
        # Clear status after 5 seconds
        self.app.after(5000, lambda: self.status_label.configure(text=""))
