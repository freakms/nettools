"""
Reusable UI Components for NetTools Suite
Provides consistent widgets and styling across the application
"""

import customtkinter as ctk
from design_constants import COLORS, SPACING, RADIUS, FONTS, BUTTON_SIZES, CARD_STYLE, ROW_STYLE, INPUT_STYLE


class StyledCard(ctk.CTkFrame):
    """A styled card container with electric violet theme"""
    
    def __init__(self, parent, **kwargs):
        # Extract custom parameters
        show_border = kwargs.pop('show_border', False)
        
        # Apply electric violet card styling
        kwargs.setdefault('corner_radius', CARD_STYLE['radius'])
        kwargs.setdefault('fg_color', COLORS['dashboard_card'])
        
        super().__init__(parent, **kwargs)
        
        if show_border:
            self.configure(
                border_width=CARD_STYLE['border_width'],
                border_color=COLORS['electric_violet']
            )


class StyledButton(ctk.CTkButton):
    """A styled button with electric violet theme"""
    
    def __init__(self, parent, size="medium", variant="primary", **kwargs):
        # Get size dimensions
        button_size = BUTTON_SIZES.get(size, BUTTON_SIZES["medium"])
        kwargs.setdefault('width', button_size['width'])
        kwargs.setdefault('height', button_size['height'])
        
        # Get variant colors with electric violet theme
        if variant == "primary":
            kwargs.setdefault('fg_color', COLORS['electric_violet'])
            kwargs.setdefault('hover_color', COLORS['electric_violet_hover'])
        elif variant == "success":
            kwargs.setdefault('fg_color', COLORS['success'])
            kwargs.setdefault('hover_color', COLORS['success_hover'])
        elif variant == "danger":
            kwargs.setdefault('fg_color', COLORS['danger'])
            kwargs.setdefault('hover_color', COLORS['danger_hover'])
        elif variant == "neutral":
            kwargs.setdefault('fg_color', COLORS['neutral'])
            kwargs.setdefault('hover_color', COLORS['neutral_hover'])
        
        # Default font
        kwargs.setdefault('font', ctk.CTkFont(size=FONTS['body'], weight="bold"))
        
        super().__init__(parent, **kwargs)


class StyledEntry(ctk.CTkEntry):
    """A styled entry field with consistent appearance"""
    
    def __init__(self, parent, **kwargs):
        kwargs.setdefault('height', INPUT_STYLE['height'])
        kwargs.setdefault('corner_radius', INPUT_STYLE['radius'])
        kwargs.setdefault('font', ctk.CTkFont(size=FONTS['body']))
        
        super().__init__(parent, **kwargs)


class SectionTitle(ctk.CTkLabel):
    """A styled section title with electric violet theme"""
    
    def __init__(self, parent, text, **kwargs):
        kwargs.setdefault('font', ctk.CTkFont(size=FONTS['heading'], weight="bold"))
        kwargs.setdefault('text_color', COLORS['electric_violet'])
        kwargs.setdefault('text', text)
        
        super().__init__(parent, **kwargs)


class SubTitle(ctk.CTkLabel):
    """A styled subtitle with neon cyan accent"""
    
    def __init__(self, parent, text, **kwargs):
        kwargs.setdefault('font', ctk.CTkFont(size=FONTS['body']))
        kwargs.setdefault('text_color', COLORS['neon_cyan'])
        kwargs.setdefault('text', text)
        
        super().__init__(parent, **kwargs)


class ResultRow(ctk.CTkFrame):
    """A styled result row with electric violet hover effect"""
    
    def __init__(self, parent, **kwargs):
        # Apply electric violet row styling
        kwargs.setdefault('height', ROW_STYLE['height'])
        kwargs.setdefault('corner_radius', ROW_STYLE['radius'])
        kwargs.setdefault('fg_color', COLORS['dashboard_card'])
        
        super().__init__(parent, **kwargs)
        
        # Prevent height collapse
        self.pack_propagate(False)
        
        # Add hover effect
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        
        # Store original color
        self._original_color = kwargs.get('fg_color', COLORS['dashboard_card'])
    
    def _on_enter(self, event):
        """Handle mouse enter with violet glow"""
        try:
            self.configure(fg_color=COLORS['dashboard_card_hover'])
        except (AttributeError, RuntimeError):
            # Child widgets may not be fully initialized yet
            pass
    
    def _on_leave(self, event):
        """Handle mouse leave"""
        try:
            self.configure(fg_color=self._original_color)
        except (AttributeError, RuntimeError):
            # Child widgets may not be fully initialized yet
            pass


class StatusBadge(ctk.CTkFrame):
    """A styled status badge/chip"""
    
    def __init__(self, parent, text, status="neutral", **kwargs):
        # Determine color based on status
        if status == "online" or status == "success":
            bg_color = COLORS['success']
        elif status == "offline" or status == "error":
            bg_color = COLORS['neutral']
        elif status == "warning":
            bg_color = COLORS['warning']
        else:
            bg_color = COLORS['neutral']
        
        kwargs.setdefault('fg_color', bg_color)
        kwargs.setdefault('corner_radius', 12)
        
        super().__init__(parent, **kwargs)
        
        # Add label
        label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=FONTS['small'], weight="bold"),
            text_color="white"
        )
        label.pack(padx=10, pady=4)


class SectionSeparator(ctk.CTkFrame):
    """A visual separator with electric violet theme"""
    
    def __init__(self, parent, **kwargs):
        kwargs.setdefault('height', 2)
        kwargs.setdefault('fg_color', COLORS['electric_violet'])
        
        super().__init__(parent, **kwargs)


class LoadingSpinner(ctk.CTkLabel):
    """A simple loading indicator with electric violet"""
    
    def __init__(self, parent, text="Loading...", **kwargs):
        kwargs.setdefault('text', f"⏳ {text}")
        kwargs.setdefault('font', ctk.CTkFont(size=FONTS['subheading']))
        kwargs.setdefault('text_color', COLORS['electric_violet'])
        
        super().__init__(parent, **kwargs)


class InfoBox(ctk.CTkFrame):
    """An information/alert box with electric violet theme"""
    
    def __init__(self, parent, message, box_type="info", **kwargs):
        # Determine color based on type with violet theme
        if box_type == "success":
            bg_color = COLORS['success']
        elif box_type == "warning":
            bg_color = COLORS['warning']
        elif box_type == "error":
            bg_color = COLORS['danger']
        else:
            bg_color = COLORS['electric_violet']
        
        kwargs.setdefault('fg_color', bg_color)
        kwargs.setdefault('corner_radius', RADIUS['medium'])
        
        super().__init__(parent, **kwargs)
        
        # Add message label
        label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=FONTS['body']),
            text_color="white",
            wraplength=400
        )
        label.pack(padx=SPACING['md'], pady=SPACING['sm'])


class DataGrid(ctk.CTkFrame):
    """A grid layout for displaying data in columns"""
    
    def __init__(self, parent, columns, **kwargs):
        kwargs.setdefault('fg_color', 'transparent')
        super().__init__(parent, **kwargs)
        
        self.columns = columns
        self.row_count = 0
        
        # Create header
        self._create_header()
    
    def _create_header(self):
        """Create the header row with electric violet theme"""
        header_frame = ctk.CTkFrame(
            self,
            corner_radius=RADIUS['medium'],
            fg_color=COLORS['electric_violet']
        )
        header_frame.pack(fill="x", pady=(0, SPACING['xs']))
        
        for i, column in enumerate(self.columns):
            label = ctk.CTkLabel(
                header_frame,
                text=column['title'],
                font=ctk.CTkFont(size=FONTS['body'], weight="bold"),
                text_color="white",
                width=column.get('width', 150),
                anchor="w"
            )
            label.pack(side="left", padx=SPACING['sm'], pady=SPACING['sm'])
    
    def add_row(self, data, alternate=False):
        """Add a data row to the grid"""
        row_frame = ResultRow(
            self,
            fg_color=("gray92", "gray15") if alternate else COLORS['dashboard_card']
        )
        row_frame.pack(fill="x", pady=ROW_STYLE['spacing'])
        row_frame._original_color = ("gray92", "gray15") if alternate else COLORS['dashboard_card']
        
        for i, column in enumerate(self.columns):
            value = data.get(column['key'], '')
            label = ctk.CTkLabel(
                row_frame,
                text=str(value),
                font=ctk.CTkFont(size=FONTS['body']),
                width=column.get('width', 150),
                anchor="w"
            )
            label.pack(side="left", padx=SPACING['sm'], pady=ROW_STYLE['padding_y'])
        
        self.row_count += 1
        return row_frame
    
    def clear_rows(self):
        """Clear all data rows"""
        for widget in self.winfo_children()[1:]:  # Skip header
            widget.destroy()
        self.row_count = 0



class Tooltip:
    """
    Modern tooltip that appears on hover with smooth positioning.
    Attach to any widget using: Tooltip(widget, "Tooltip text")
    """
    
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.scheduled_id = None
        
        widget.bind('<Enter>', self._on_enter)
        widget.bind('<Leave>', self._on_leave)
        widget.bind('<Button-1>', self._on_leave)
    
    def _on_enter(self, event=None):
        """Schedule tooltip display"""
        self._cancel_scheduled()
        self.scheduled_id = self.widget.after(self.delay, self._show_tooltip)
    
    def _on_leave(self, event=None):
        """Hide tooltip"""
        self._cancel_scheduled()
        self._hide_tooltip()
    
    def _cancel_scheduled(self):
        """Cancel scheduled tooltip"""
        if self.scheduled_id:
            self.widget.after_cancel(self.scheduled_id)
            self.scheduled_id = None
    
    def _show_tooltip(self):
        """Display the tooltip"""
        if self.tooltip_window:
            return
        
        # Get widget position
        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Create tooltip window
        self.tooltip_window = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes('-topmost', True)
        
        # Tooltip content
        frame = ctk.CTkFrame(
            tw,
            fg_color=("#2D2D2D", "#2D2D2D"),
            corner_radius=6,
            border_width=1,
            border_color=COLORS['electric_violet']
        )
        frame.pack()
        
        label = ctk.CTkLabel(
            frame,
            text=self.text,
            font=ctk.CTkFont(size=11),
            text_color="white",
            wraplength=250
        )
        label.pack(padx=10, pady=6)
    
    def _hide_tooltip(self):
        """Destroy tooltip window"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class ToastNotification:
    """
    Modern toast notification that slides in from the bottom-right.
    Usage: ToastNotification(parent, "Message", toast_type="success")
    """
    
    _active_toasts = []
    
    def __init__(self, parent, message, toast_type="info", duration=3000):
        self.parent = parent
        self.message = message
        self.toast_type = toast_type
        self.duration = duration
        self.toast_window = None
        
        self._show_toast()
    
    def _show_toast(self):
        """Display the toast notification"""
        # Get icon and color based on type
        icons = {
            "success": "✅",
            "error": "❌", 
            "warning": "⚠️",
            "info": "ℹ️"
        }
        colors = {
            "success": ("#22C55E", "#16A34A"),
            "error": ("#EF4444", "#DC2626"),
            "warning": ("#F59E0B", "#D97706"),
            "info": COLORS['electric_violet']
        }
        
        icon = icons.get(self.toast_type, "ℹ️")
        bg_color = colors.get(self.toast_type, COLORS['electric_violet'])
        
        # Calculate position (stack toasts)
        offset_y = len(ToastNotification._active_toasts) * 70
        
        # Get screen position
        try:
            screen_width = self.parent.winfo_screenwidth()
            screen_height = self.parent.winfo_screenheight()
        except Exception:
            screen_width = 1920
            screen_height = 1080
        
        x = screen_width - 350
        y = screen_height - 120 - offset_y
        
        # Create toast window
        self.toast_window = tw = ctk.CTkToplevel(self.parent)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"320x60+{x}+{y}")
        tw.attributes('-topmost', True)
        tw.attributes('-alpha', 0.95)
        
        # Track active toast
        ToastNotification._active_toasts.append(self)
        
        # Toast content
        frame = ctk.CTkFrame(
            tw,
            fg_color=bg_color,
            corner_radius=10
        )
        frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Icon
        icon_label = ctk.CTkLabel(
            frame,
            text=icon,
            font=ctk.CTkFont(size=20),
            width=40
        )
        icon_label.pack(side="left", padx=(10, 5))
        
        # Message
        msg_label = ctk.CTkLabel(
            frame,
            text=self.message,
            font=ctk.CTkFont(size=12),
            text_color="white",
            anchor="w",
            wraplength=220
        )
        msg_label.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Close button
        close_btn = ctk.CTkButton(
            frame,
            text="✕",
            width=30,
            height=30,
            corner_radius=15,
            fg_color="transparent",
            hover_color=("gray70", "gray40"),
            command=self._close
        )
        close_btn.pack(side="right", padx=5)
        
        # Auto-close after duration
        self.parent.after(self.duration, self._close)
    
    def _close(self):
        """Close the toast"""
        if self.toast_window:
            try:
                self.toast_window.destroy()
            except Exception:
                pass
            self.toast_window = None
        
        if self in ToastNotification._active_toasts:
            ToastNotification._active_toasts.remove(self)


class CollapsibleSidebar(ctk.CTkFrame):
    """
    Collapsible sidebar with icons and smooth animation.
    """
    
    COLLAPSED_WIDTH = 60
    EXPANDED_WIDTH = 250
    
    def __init__(self, parent, **kwargs):
        kwargs.setdefault('width', self.EXPANDED_WIDTH)
        kwargs.setdefault('corner_radius', 0)
        kwargs.setdefault('fg_color', COLORS['dashboard_card'])
        
        super().__init__(parent, **kwargs)
        self.pack_propagate(False)
        
        self.is_collapsed = False
        self.nav_items = []
        self.nav_buttons = {}
        self.category_labels = []
        
        self._create_header()
        
        # Nav container
        self.nav_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.nav_scroll.pack(fill="both", expand=True, padx=0, pady=0)
    
    def _create_header(self):
        """Create sidebar header with logo and collapse button"""
        self.header = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color="transparent")
        self.header.pack(fill="x", padx=0, pady=0)
        self.header.pack_propagate(False)
        
        # Logo section
        self.logo_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.logo_frame.pack(fill="x", padx=10, pady=(15, 5))
        
        self.logo_icon = ctk.CTkLabel(
            self.logo_frame,
            text="⚡",
            font=ctk.CTkFont(size=28)
        )
        self.logo_icon.pack(side="left")
        
        self.logo_text = ctk.CTkLabel(
            self.logo_frame,
            text=" NetTools",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS['electric_violet']
        )
        self.logo_text.pack(side="left")
        
        # Collapse button
        self.collapse_btn = ctk.CTkButton(
            self.header,
            text="◀",
            width=30,
            height=30,
            corner_radius=15,
            fg_color="transparent",
            hover_color=COLORS['dashboard_card_hover'],
            command=self.toggle_collapse,
            font=ctk.CTkFont(size=14)
        )
        self.collapse_btn.place(relx=1.0, x=-40, y=20)
        
        # Separator
        self.separator = ctk.CTkFrame(self, height=2, fg_color=COLORS['electric_violet'])
        self.separator.pack(fill="x", padx=10, pady=5)
    
    def add_category(self, name, icon=""):
        """Add a category header"""
        label = ctk.CTkLabel(
            self.nav_scroll,
            text=f"{icon} {name}" if icon else name,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS['neon_cyan'],
            anchor="w"
        )
        label.pack(fill="x", padx=15, pady=(15, 5))
        self.category_labels.append((label, icon, name))
        return label
    
    def add_nav_item(self, page_id, icon, text, tooltip="", command=None):
        """Add a navigation item with icon"""
        btn_frame = ctk.CTkFrame(self.nav_scroll, fg_color="transparent")
        btn_frame.pack(fill="x", padx=8, pady=2)
        
        btn = ctk.CTkButton(
            btn_frame,
            text=f" {icon}  {text}",
            command=command,
            height=40,
            corner_radius=6,
            anchor="w",
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            text_color=COLORS['text_primary'],
            hover_color=COLORS['dashboard_card_hover']
        )
        btn.pack(fill="x")
        
        # Store info for collapse/expand
        self.nav_items.append({
            'frame': btn_frame,
            'button': btn,
            'icon': icon,
            'text': text,
            'page_id': page_id
        })
        self.nav_buttons[page_id] = btn
        
        # Add tooltip
        if tooltip:
            Tooltip(btn, tooltip)
        
        return btn
    
    def toggle_collapse(self):
        """Toggle sidebar collapsed state"""
        self.is_collapsed = not self.is_collapsed
        
        if self.is_collapsed:
            self._collapse()
        else:
            self._expand()
    
    def _collapse(self):
        """Collapse sidebar to show only icons"""
        self.configure(width=self.COLLAPSED_WIDTH)
        self.collapse_btn.configure(text="▶")
        self.logo_text.pack_forget()
        
        # Update nav items to show only icons
        for item in self.nav_items:
            item['button'].configure(text=f" {item['icon']}")
        
        # Hide category labels
        for label, icon, name in self.category_labels:
            label.configure(text=icon if icon else "•")
    
    def _expand(self):
        """Expand sidebar to full width"""
        self.configure(width=self.EXPANDED_WIDTH)
        self.collapse_btn.configure(text="◀")
        self.logo_text.pack(side="left")
        
        # Update nav items to show icons + text
        for item in self.nav_items:
            item['button'].configure(text=f" {item['icon']}  {item['text']}")
        
        # Show category labels
        for label, icon, name in self.category_labels:
            label.configure(text=f"{icon} {name}" if icon else name)
    
    def set_active(self, page_id):
        """Set the active navigation item"""
        for pid, btn in self.nav_buttons.items():
            if pid == page_id:
                btn.configure(fg_color=COLORS['electric_violet'])
            else:
                btn.configure(fg_color="transparent")


# Icon mapping for navigation items
NAV_ICONS = {
    "dashboard": "🏠",
    "scanner": "📡",
    "portscan": "🔌",
    "traceroute": "🛤️",
    "bandwidth": "📶",
    "dns": "🌐",
    "subnet": "🔢",
    "mac": "🔗",
    "compare": "⚖️",
    "profiles": "📁",
    "panos": "🛡️",
    "phpipam": "📊",
}
