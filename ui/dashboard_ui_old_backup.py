"""
Dashboard UI Module
Contains the home page dashboard with stats and quick actions
"""

import customtkinter as ctk
from design_constants import COLORS, SPACING, RADIUS, FONTS
from ui_components import StyledButton


class DashboardUI:
    """Dashboard page UI implementation"""
    
    def __init__(self, app):
        """
        Initialize Dashboard UI
        
        Args:
            app: Reference to main NetToolsApp instance
        """
        self.app = app
    
    def create_content(self, parent):
        """Create Dashboard home page with electric violet theme"""
        # Main dashboard container with dark violet background
        dashboard = ctk.CTkScrollableFrame(
            parent,
            fg_color=COLORS['dashboard_bg'],
            corner_radius=0
        )
        dashboard.pack(fill="both", expand=True)
        
        # Header section
        header_frame = ctk.CTkFrame(dashboard, fg_color="transparent")
        header_frame.pack(fill="x", padx=SPACING['xxl'], pady=(SPACING['xxl'], SPACING['lg']))
        
        title = ctk.CTkLabel(
            header_frame,
            text="⚡ Network Command Center",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS['electric_violet']
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Professional network management at your fingertips",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary']
        )
        subtitle.pack(anchor="w", pady=(5, 0))
        
        # Stats cards row (4 cards)
        stats_frame = ctk.CTkFrame(dashboard, fg_color="transparent")
        stats_frame.pack(fill="x", padx=SPACING['xxl'], pady=SPACING['md'])
        
        # Configure grid
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        stats_frame.grid_columnconfigure(3, weight=1)
        
        # Card 1: Quick Scan
        self._create_stat_card(
            stats_frame, 
            "🔍", 
            "Quick Scan", 
            "Start IPv4 Scan",
            COLORS['electric_violet'],
            lambda: self.app.show_page("scanner"),
            0, 0
        )
        
        # Card 2: Favorites
        fav_count = len(self.app.favorite_tools)
        self._create_stat_card(
            stats_frame,
            "⭐",
            "Favorites",
            f"{fav_count} Starred Tools",
            COLORS['neon_cyan'],
            None,
            0, 1
        )
        
        # Card 3: Recent Activity
        recent_scans = len(self.app.scanner.results) if hasattr(self.app, 'scanner') else 0
        self._create_stat_card(
            stats_frame,
            "📊",
            "Recent Activity",
            f"{recent_scans} Results",
            ("#22C55E", "#16A34A"),
            None,
            0, 2
        )
        
        # Card 4: Tools Available
        total_tools = 10  # Total number of tools
        self._create_stat_card(
            stats_frame,
            "🛠️",
            "Tools",
            f"{total_tools} Available",
            ("#F59E0B", "#D97706"),
            None,
            0, 3
        )
        
        # Main content area (2 columns)
        content_frame = ctk.CTkFrame(dashboard, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=SPACING['xxl'], pady=SPACING['md'])
        
        content_frame.grid_columnconfigure(0, weight=3)
        content_frame.grid_columnconfigure(1, weight=2)
        
        # Left column
        left_col = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING['md']))
        
        # Quick Actions section
        self._create_quick_actions_section(left_col)
        
        # Recent Scans section
        self._create_recent_scans_section(left_col)
        
        # Right column
        right_col = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew")
        
        # Favorite Tools section
        self._create_favorite_tools_section(right_col)
        
        # Tips & Shortcuts section
        self._create_tips_section(right_col)
    
    def _create_stat_card(self, parent, icon, title, subtitle, color, command, row, col):
        """Create a stat card with electric glow effect"""
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS['dashboard_card'],
            corner_radius=RADIUS['large'],
            border_width=2,
            border_color=color
        )
        card.grid(row=row, column=col, padx=SPACING['sm'], pady=SPACING['sm'], sticky="nsew")
        
        # Make card clickable if command provided
        if command:
            card.configure(cursor="hand2")
            card.bind("<Button-1>", lambda e: command())
            # Hover effects
            card.bind("<Enter>", lambda e: card.configure(border_color=COLORS['glow_purple']))
            card.bind("<Leave>", lambda e: card.configure(border_color=color))
        
        # Icon
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=40),
            text_color=color
        )
        icon_label.pack(pady=(SPACING['lg'], SPACING['sm']))
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary']
        )
        title_label.pack()
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            card,
            text=subtitle,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        subtitle_label.pack(pady=(SPACING['xs'], SPACING['lg']))
    
    def _create_quick_actions_section(self, parent):
        """Create quick actions section"""
        section = ctk.CTkFrame(
            parent,
            fg_color=COLORS['dashboard_card'],
            corner_radius=RADIUS['large']
        )
        section.pack(fill="x", pady=SPACING['md'])
        
        # Section header
        header = ctk.CTkLabel(
            section,
            text="🎯 Quick Actions",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['electric_violet'],
            anchor="w"
        )
        header.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['md']))
        
        # Action buttons
        actions = [
            ("🔍 IPv4 Scanner", "Scan network for active hosts", lambda: self.app.show_page("scanner")),
            ("🔌 Port Scanner", "Check open ports on hosts", lambda: self.app.show_page("portscan")),
            ("🗺️ Traceroute", "Trace network path", lambda: self.app.show_page("traceroute")),
            ("🌐 DNS Lookup", "Resolve hostnames", lambda: self.app.show_page("dns")),
        ]
        
        for text, desc, cmd in actions:
            btn_frame = ctk.CTkFrame(section, fg_color="transparent")
            btn_frame.pack(fill="x", padx=SPACING['lg'], pady=SPACING['xs'])
            
            btn = StyledButton(
                btn_frame,
                text=text,
                command=cmd,
                size="large",
                variant="primary"
            )
            btn.pack(side="left", fill="x", expand=True)
            
            desc_label = ctk.CTkLabel(
                btn_frame,
                text=desc,
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text_secondary']
            )
            desc_label.pack(side="left", padx=SPACING['md'])
        
        # Add spacing at bottom
        ctk.CTkLabel(section, text="", height=SPACING['md']).pack()
    
    def _create_recent_scans_section(self, parent):
        """Create recent scans section"""
        section = ctk.CTkFrame(
            parent,
            fg_color=COLORS['dashboard_card'],
            corner_radius=RADIUS['large']
        )
        section.pack(fill="both", expand=True, pady=SPACING['md'])
        
        # Section header
        header = ctk.CTkLabel(
            section,
            text="📈 Recent Scans",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['electric_violet'],
            anchor="w"
        )
        header.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['md']))
        
        # Check if there are any scans
        if hasattr(self.app, 'scanner') and len(self.app.scanner.results) > 0:
            results_preview = self.app.scanner.results[:5]  # Show last 5
            
            for result in results_preview:
                item_frame = ctk.CTkFrame(
                    section,
                    fg_color=("gray85", "gray20"),
                    corner_radius=RADIUS['medium']
                )
                item_frame.pack(fill="x", padx=SPACING['lg'], pady=SPACING['xs'])
                
                # IP
                ip_label = ctk.CTkLabel(
                    item_frame,
                    text=result.get('ip', 'N/A'),
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLORS['text_primary']
                )
                ip_label.pack(side="left", padx=SPACING['md'], pady=SPACING['sm'])
                
                # Status
                status = result.get('status', 'Unknown')
                status_color = COLORS['online'] if status == 'Online' else COLORS['offline']
                status_label = ctk.CTkLabel(
                    item_frame,
                    text=f"● {status}",
                    font=ctk.CTkFont(size=11),
                    text_color=status_color
                )
                status_label.pack(side="left", padx=SPACING['sm'])
                
                # RTT
                if result.get('rtt'):
                    rtt_label = ctk.CTkLabel(
                        item_frame,
                        text=f"{result.get('rtt')} ms",
                        font=ctk.CTkFont(size=11),
                        text_color=COLORS['text_secondary']
                    )
                    rtt_label.pack(side="right", padx=SPACING['md'])
        else:
            # Empty state
            empty_label = ctk.CTkLabel(
                section,
                text="No recent scans yet\nStart your first scan to see results here",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_secondary'],
                justify="center"
            )
            empty_label.pack(pady=SPACING['xxl'])
        
        # Add spacing at bottom
        ctk.CTkLabel(section, text="", height=SPACING['md']).pack()
    
    def _create_favorite_tools_section(self, parent):
        """Create favorite tools section"""
        section = ctk.CTkFrame(
            parent,
            fg_color=COLORS['dashboard_card'],
            corner_radius=RADIUS['large']
        )
        section.pack(fill="x", pady=SPACING['md'])
        
        # Section header
        header = ctk.CTkLabel(
            section,
            text="⭐ Favorite Tools",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['neon_cyan'],
            anchor="w"
        )
        header.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['md']))
        
        # Tool mapping for display names
        tool_names = {
            "scanner": "IPv4 Scanner",
            "portscan": "Port Scanner",
            "traceroute": "Traceroute",
            "bandwidth": "Bandwidth Test",
            "dns": "DNS Lookup",
            "subnet": "Subnet Calculator",
            "mac": "MAC Formatter",
            "compare": "Scan Comparison",
            "profiles": "Network Profiles",
            "panos": "PAN-OS Generator",
            "phpipam": "phpIPAM"
        }
        
        if self.app.favorite_tools:
            for tool_id in self.app.favorite_tools:
                tool_name = tool_names.get(tool_id, tool_id.title())
                
                btn_frame = ctk.CTkFrame(
                    section,
                    fg_color=("gray85", "gray20"),
                    corner_radius=RADIUS['medium']
                )
                btn_frame.pack(fill="x", padx=SPACING['lg'], pady=SPACING['xs'])
                btn_frame.configure(cursor="hand2")
                btn_frame.bind("<Button-1>", lambda e, tid=tool_id: self.app.show_page(tid))
                
                star_label = ctk.CTkLabel(
                    btn_frame,
                    text="⭐",
                    font=ctk.CTkFont(size=14)
                )
                star_label.pack(side="left", padx=SPACING['sm'], pady=SPACING['sm'])
                
                name_label = ctk.CTkLabel(
                    btn_frame,
                    text=tool_name,
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS['text_primary']
                )
                name_label.pack(side="left", padx=SPACING['xs'])
        else:
            # Empty state
            empty_label = ctk.CTkLabel(
                section,
                text="No favorites yet\nStar your favorite tools for quick access",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_secondary'],
                justify="center"
            )
            empty_label.pack(pady=SPACING['lg'])
        
        # Add spacing at bottom
        ctk.CTkLabel(section, text="", height=SPACING['md']).pack()
    
    def _create_tips_section(self, parent):
        """Create tips and shortcuts section"""
        section = ctk.CTkFrame(
            parent,
            fg_color=COLORS['dashboard_card'],
            corner_radius=RADIUS['large']
        )
        section.pack(fill="both", expand=True, pady=SPACING['md'])
        
        # Section header
        header = ctk.CTkLabel(
            section,
            text="💡 Tips & Shortcuts",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['neon_cyan'],
            anchor="w"
        )
        header.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['md']))
        
        # Tips list
        tips = [
            ("Ctrl+K", "Quick tool switcher"),
            ("⭐ Click", "Star/unstar tools in sidebar"),
            ("Import List", "Scan multiple IPs at once"),
            ("Save Profile", "Save scan configurations"),
            ("Compare Scans", "Track network changes over time"),
        ]
        
        for shortcut, description in tips:
            tip_frame = ctk.CTkFrame(
                section,
                fg_color=("gray85", "gray20"),
                corner_radius=RADIUS['medium']
            )
            tip_frame.pack(fill="x", padx=SPACING['lg'], pady=SPACING['xs'])
            
            shortcut_label = ctk.CTkLabel(
                tip_frame,
                text=shortcut,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS['electric_violet']
            )
            shortcut_label.pack(side="left", padx=SPACING['md'], pady=SPACING['sm'])
            
            desc_label = ctk.CTkLabel(
                tip_frame,
                text=description,
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_secondary']
            )
            desc_label.pack(side="left", padx=SPACING['xs'])
        
        # Add spacing at bottom
        ctk.CTkLabel(section, text="", height=SPACING['md']).pack()
