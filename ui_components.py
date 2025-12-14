"""
Reusable UI Components for NetTools Suite
Provides consistent widgets and styling across the application
Professional UI Design System v2.0
"""

import customtkinter as ctk
from design_constants import COLORS, SPACING, RADIUS, FONTS, BUTTON_SIZES, CARD_STYLE, ROW_STYLE, INPUT_STYLE


class StyledCard(ctk.CTkFrame):
    """
    Professional styled card container with subtle depth and clean borders.
    Supports multiple visual styles for different contexts.
    """
    
    def __init__(self, parent, variant="default", hover_effect=True, **kwargs):
        """
        Args:
            variant: "default", "elevated", "outlined", "subtle"
            hover_effect: Enable hover state change
        """
        # Extract custom parameters
        show_border = kwargs.pop('show_border', False)
        
        # Apply card styling based on variant
        kwargs.setdefault('corner_radius', 12)
        
        if variant == "elevated":
            kwargs.setdefault('fg_color', COLORS['dashboard_card'])
            kwargs.setdefault('border_width', 1)
            kwargs.setdefault('border_color', COLORS.get('border', ("#E5E7EB", "#374151")))
        elif variant == "outlined":
            kwargs.setdefault('fg_color', "transparent")
            kwargs.setdefault('border_width', 2)
            kwargs.setdefault('border_color', COLORS['electric_violet'])
        elif variant == "subtle":
            kwargs.setdefault('fg_color', COLORS.get('bg_card', ("gray95", "gray20")))
        else:  # default
            kwargs.setdefault('fg_color', COLORS['dashboard_card'])
        
        super().__init__(parent, **kwargs)
        
        if show_border:
            self.configure(
                border_width=1,
                border_color=COLORS['electric_violet']
            )
        
        # Store original color for hover effect
        self._original_fg = self.cget('fg_color')
        self._hover_enabled = hover_effect and variant in ("default", "elevated")
        
        if self._hover_enabled:
            self.bind('<Enter>', self._on_enter)
            self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, event):
        if self._hover_enabled:
            try:
                self.configure(fg_color=COLORS['dashboard_card_hover'])
            except:
                pass
    
    def _on_leave(self, event):
        if self._hover_enabled:
            try:
                self.configure(fg_color=self._original_fg)
            except:
                pass


class StyledButton(ctk.CTkButton):
    """
    Professional styled button with modern appearance.
    Supports multiple variants: primary, secondary, success, danger, ghost, outline
    """
    
    def __init__(self, parent, size="medium", variant="primary", rounded=False, **kwargs):
        """
        Args:
            size: "small", "medium", "large", "xlarge"
            variant: "primary", "secondary", "success", "danger", "ghost", "outline"
            rounded: Use pill-shaped corners
        """
        # Get size dimensions
        button_size = BUTTON_SIZES.get(size, BUTTON_SIZES["medium"])
        kwargs.setdefault('width', button_size['width'])
        kwargs.setdefault('height', button_size['height'])
        
        # Corner radius
        corner = button_size['height'] // 2 if rounded else 8
        kwargs.setdefault('corner_radius', corner)
        
        # Get variant colors with modern theme
        if variant == "primary":
            kwargs.setdefault('fg_color', COLORS['electric_violet'])
            kwargs.setdefault('hover_color', COLORS['electric_violet_hover'])
            kwargs.setdefault('text_color', "white")
        elif variant == "secondary":
            kwargs.setdefault('fg_color', COLORS.get('bg_card', ("gray90", "gray25")))
            kwargs.setdefault('hover_color', COLORS.get('bg_card_hover', ("gray85", "gray30")))
            kwargs.setdefault('text_color', COLORS['text_primary'])
        elif variant == "success":
            kwargs.setdefault('fg_color', COLORS['success'])
            kwargs.setdefault('hover_color', COLORS['success_hover'])
            kwargs.setdefault('text_color', "white")
        elif variant == "danger":
            kwargs.setdefault('fg_color', COLORS['danger'])
            kwargs.setdefault('hover_color', COLORS['danger_hover'])
            kwargs.setdefault('text_color', "white")
        elif variant == "ghost":
            kwargs.setdefault('fg_color', "transparent")
            kwargs.setdefault('hover_color', COLORS['dashboard_card_hover'])
            kwargs.setdefault('text_color', COLORS['text_primary'])
        elif variant == "outline":
            kwargs.setdefault('fg_color', "transparent")
            kwargs.setdefault('hover_color', COLORS['electric_violet'])
            kwargs.setdefault('text_color', COLORS['electric_violet'])
            kwargs.setdefault('border_width', 2)
            kwargs.setdefault('border_color', COLORS['electric_violet'])
        elif variant == "neutral":
            kwargs.setdefault('fg_color', COLORS['neutral'])
            kwargs.setdefault('hover_color', COLORS['neutral_hover'])
            kwargs.setdefault('text_color', "white")
        
        # Professional font
        kwargs.setdefault('font', ctk.CTkFont(size=FONTS['body'], weight="bold"))
        
        super().__init__(parent, **kwargs)


class StyledEntry(ctk.CTkEntry):
    """
    Professional styled entry field with focus states and clean appearance.
    """
    
    def __init__(self, parent, icon=None, **kwargs):
        kwargs.setdefault('height', INPUT_STYLE['height'])
        kwargs.setdefault('corner_radius', 8)
        kwargs.setdefault('font', ctk.CTkFont(size=FONTS['body']))
        kwargs.setdefault('border_width', 1)
        kwargs.setdefault('border_color', COLORS.get('border', ("#E5E7EB", "#374151")))
        kwargs.setdefault('fg_color', COLORS.get('bg_card', ("white", "#1F2937")))
        
        super().__init__(parent, **kwargs)
        
        # Focus styling
        self.bind('<FocusIn>', self._on_focus_in)
        self.bind('<FocusOut>', self._on_focus_out)
    
    def _on_focus_in(self, event):
        try:
            self.configure(border_color=COLORS['electric_violet'])
        except:
            pass
    
    def _on_focus_out(self, event):
        try:
            self.configure(border_color=COLORS.get('border', ("#E5E7EB", "#374151")))
        except:
            pass


class SectionTitle(ctk.CTkLabel):
    """A styled section title with electric violet theme"""
    
    def __init__(self, parent, text, **kwargs):
        kwargs.setdefault('font', ctk.CTkFont(size=FONTS['heading'], weight="bold"))
        kwargs.setdefault('text_color', COLORS['electric_violet'])
        kwargs.setdefault('text', text)
        
        super().__init__(parent, **kwargs)


class SubTitle(ctk.CTkLabel):
    """A styled subtitle with muted secondary color"""
    
    def __init__(self, parent, text, **kwargs):
        kwargs.setdefault('font', ctk.CTkFont(size=FONTS['body']))
        kwargs.setdefault('text_color', COLORS['text_secondary'])
        kwargs.setdefault('text', text)
        
        super().__init__(parent, **kwargs)


class ResultRow(ctk.CTkFrame):
    """
    Professional styled result row with smooth hover transitions.
    Used for displaying scan results, list items, etc.
    """
    
    def __init__(self, parent, striped=False, interactive=True, **kwargs):
        """
        Args:
            striped: Alternate background for zebra striping
            interactive: Enable hover effects
        """
        # Apply row styling
        kwargs.setdefault('height', ROW_STYLE['height'])
        kwargs.setdefault('corner_radius', 6)
        
        # Determine background color
        if striped:
            kwargs.setdefault('fg_color', ("gray96", "gray18"))
        else:
            kwargs.setdefault('fg_color', COLORS['dashboard_card'])
        
        super().__init__(parent, **kwargs)
        
        # Prevent height collapse
        self.pack_propagate(False)
        
        # Store original color
        self._original_color = self.cget('fg_color')
        self._interactive = interactive
        
        # Add hover effect
        if self._interactive:
            self.bind('<Enter>', self._on_enter)
            self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, event):
        """Handle mouse enter with subtle highlight"""
        if self._interactive:
            try:
                self.configure(fg_color=COLORS['dashboard_card_hover'])
            except (AttributeError, RuntimeError):
                pass
    
    def _on_leave(self, event):
        """Handle mouse leave"""
        if self._interactive:
            try:
                self.configure(fg_color=self._original_color)
            except (AttributeError, RuntimeError):
                pass


class StatusBadge(ctk.CTkFrame):
    """
    Professional status badge/chip with multiple styles.
    Used for showing status indicators, tags, labels.
    """
    
    def __init__(self, parent, text, status="neutral", size="small", **kwargs):
        """
        Args:
            status: "online", "success", "offline", "error", "warning", "info", "neutral"
            size: "small", "medium"
        """
        # Determine colors based on status
        status_colors = {
            "online": (COLORS['success'], "white"),
            "success": (COLORS['success'], "white"),
            "offline": (COLORS['neutral'], "white"),
            "error": (COLORS['danger'], "white"),
            "warning": (COLORS['warning'], "white"),
            "info": (COLORS['electric_violet'], "white"),
            "neutral": (COLORS['neutral'], "white"),
        }
        
        bg_color, text_color = status_colors.get(status, status_colors["neutral"])
        
        kwargs.setdefault('fg_color', bg_color)
        kwargs.setdefault('corner_radius', 12)
        
        super().__init__(parent, **kwargs)
        
        # Font size based on badge size
        font_size = 10 if size == "small" else 12
        pad_x = 8 if size == "small" else 12
        pad_y = 3 if size == "small" else 5
        
        # Add label
        label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=font_size, weight="bold"),
            text_color=text_color
        )
        label.pack(padx=10, pady=4)


class SectionSeparator(ctk.CTkFrame):
    """A visual separator with electric violet theme"""
    
    def __init__(self, parent, **kwargs):
        kwargs.setdefault('height', 2)
        kwargs.setdefault('fg_color', COLORS['electric_violet'])
        
        super().__init__(parent, **kwargs)


class SimpleLoadingIndicator(ctk.CTkLabel):
    """A simple loading indicator with electric violet - static text only"""
    
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
        


class SearchBar(ctk.CTkFrame):
    """
    Search bar with filter functionality.
    Usage: SearchBar(parent, placeholder="Search...", on_search=callback)
    """
    
    def __init__(self, parent, placeholder="Search...", on_search=None, **kwargs):
        kwargs.setdefault('fg_color', 'transparent')
        super().__init__(parent, **kwargs)
        
        self.on_search = on_search
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_text_change)
        
        # Search icon
        self.search_icon = ctk.CTkLabel(
            self,
            text="🔍",
            font=ctk.CTkFont(size=14),
            width=30
        )
        self.search_icon.pack(side="left", padx=(5, 0))
        
        # Search entry
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            textvariable=self.search_var,
            height=36,
            corner_radius=18,
            border_width=1,
            border_color=COLORS['electric_violet']
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Clear button
        self.clear_btn = ctk.CTkButton(
            self,
            text="✕",
            width=30,
            height=30,
            corner_radius=15,
            fg_color="transparent",
            hover_color=COLORS['dashboard_card_hover'],
            command=self.clear
        )
        self.clear_btn.pack(side="right", padx=(0, 5))
        self.clear_btn.pack_forget()  # Hidden initially
    
    def _on_text_change(self, *args):
        """Handle text changes"""
        text = self.search_var.get()
        
        # Show/hide clear button
        if text:
            self.clear_btn.pack(side="right", padx=(0, 5))
        else:
            self.clear_btn.pack_forget()
        
        # Call search callback
        if self.on_search:
            self.on_search(text)
    
    def clear(self):
        """Clear search text"""
        self.search_var.set("")
        self.entry.focus()
    
    def get(self):
        """Get current search text"""
        return self.search_var.get()


class SmartCommandPalette(ctk.CTkFrame):
    """
    Smart command palette / search bar for the sidebar.
    Features:
    - Tool suggestions when typing (e.g., "trace" suggests Traceroute)
    - Ability to search within current tool's content
    - Compact design for sidebar placement
    
    Usage:
        palette = SmartCommandPalette(
            parent, 
            tools=[(id, icon, name), ...],
            on_tool_select=callback,
            on_content_search=callback
        )
    """
    
    def __init__(self, parent, tools=None, on_tool_select=None, on_content_search=None, **kwargs):
        kwargs.setdefault('fg_color', 'transparent')
        super().__init__(parent, **kwargs)
        
        self.tools = tools or []  # List of (tool_id, icon, name, keywords)
        self.on_tool_select = on_tool_select
        self.on_content_search = on_content_search
        self.suggestions_window = None
        self.selected_index = -1
        self.suggestion_buttons = []
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the command palette UI"""
        # Search container
        self.search_container = ctk.CTkFrame(self, fg_color="transparent")
        self.search_container.pack(fill="x", padx=5, pady=5)
        
        # Search entry with icon
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_text_change)
        
        self.entry = ctk.CTkEntry(
            self.search_container,
            placeholder_text="🔍 Search tools...",
            textvariable=self.search_var,
            height=32,
            corner_radius=16,
            border_width=1,
            border_color=COLORS['electric_violet'],
            fg_color=COLORS['bg_card'],
            font=ctk.CTkFont(size=11)
        )
        self.entry.pack(fill="x")
        
        # Bind keyboard events
        self.entry.bind('<Return>', self._on_enter)
        self.entry.bind('<Up>', self._on_arrow_up)
        self.entry.bind('<Down>', self._on_arrow_down)
        self.entry.bind('<Escape>', self._close_suggestions)
        self.entry.bind('<FocusOut>', self._on_focus_out)
    
    def _on_text_change(self, *args):
        """Handle text input changes - show suggestions"""
        text = self.search_var.get().strip().lower()
        
        if not text:
            self._close_suggestions()
            return
        
        # Find matching tools
        matches = self._find_matches(text)
        
        if matches:
            self._show_suggestions(matches)
        else:
            self._close_suggestions()
    
    def _find_matches(self, text):
        """Find tools matching the search text"""
        matches = []
        
        for tool in self.tools:
            tool_id, icon, name = tool[:3]
            keywords = tool[3] if len(tool) > 3 else []
            
            # Check if text matches name or keywords
            name_lower = name.lower()
            if text in name_lower or text in tool_id.lower():
                matches.append(tool)
            elif any(text in kw.lower() for kw in keywords):
                matches.append(tool)
        
        return matches[:6]  # Limit to 6 suggestions
    
    def _show_suggestions(self, matches):
        """Show suggestions dropdown"""
        self._close_suggestions()
        
        if not matches:
            return
        
        # Get position relative to entry
        root = self.winfo_toplevel()
        
        # Create suggestions window
        self.suggestions_window = ctk.CTkToplevel(root)
        self.suggestions_window.withdraw()
        self.suggestions_window.overrideredirect(True)
        self.suggestions_window.attributes('-topmost', True)
        
        try:
            self.suggestions_window.attributes('-toolwindow', True)
        except:
            pass
        
        # Suggestions frame
        suggestions_frame = ctk.CTkFrame(
            self.suggestions_window,
            fg_color=("#2D2D2D", "#1E1B2E"),
            corner_radius=8,
            border_width=1,
            border_color=COLORS['electric_violet']
        )
        suggestions_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Header
        header = ctk.CTkLabel(
            suggestions_frame,
            text="🔍 Tools",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS['neon_cyan'],
            anchor="w"
        )
        header.pack(fill="x", padx=10, pady=(8, 4))
        
        # Suggestion items
        self.suggestion_buttons = []
        self.selected_index = -1
        
        for idx, tool in enumerate(matches):
            tool_id, icon, name = tool[:3]
            
            def make_select(tid=tool_id):
                def select():
                    self._select_tool(tid)
                return select
            
            btn = ctk.CTkButton(
                suggestions_frame,
                text=f" {icon}  {name}",
                command=make_select(),
                fg_color="transparent",
                hover_color=COLORS['electric_violet'],
                text_color="white",
                anchor="w",
                height=32,
                corner_radius=6,
                font=ctk.CTkFont(size=12)
            )
            btn.pack(fill="x", padx=5, pady=2)
            btn.tool_id = tool_id
            self.suggestion_buttons.append(btn)
        
        # Separator
        sep = ctk.CTkFrame(suggestions_frame, height=1, fg_color=COLORS['text_secondary'])
        sep.pack(fill="x", padx=10, pady=6)
        
        # Content search option
        search_text = self.search_var.get().strip()
        search_content_btn = ctk.CTkButton(
            suggestions_frame,
            text=f"🔎 Search \"{search_text}\" in current view",
            command=self._search_content,
            fg_color="transparent",
            hover_color=COLORS['neon_cyan'],
            text_color=COLORS['text_secondary'],
            anchor="w",
            height=30,
            corner_radius=6,
            font=ctk.CTkFont(size=11)
        )
        search_content_btn.pack(fill="x", padx=5, pady=(0, 5))
        
        # Position the suggestions window below the entry
        self.suggestions_window.update_idletasks()
        
        entry_x = self.entry.winfo_rootx()
        entry_y = self.entry.winfo_rooty() + self.entry.winfo_height() + 2
        entry_width = self.entry.winfo_width()
        
        # Ensure minimum width
        width = max(entry_width, 200)
        
        self.suggestions_window.geometry(f"{width}x{self.suggestions_window.winfo_reqheight()}+{entry_x}+{entry_y}")
        self.suggestions_window.deiconify()
        self.suggestions_window.lift()
    
    def _close_suggestions(self, event=None):
        """Close suggestions dropdown"""
        if self.suggestions_window is not None:
            try:
                self.suggestions_window.destroy()
            except:
                pass
            self.suggestions_window = None
            self.suggestion_buttons = []
            self.selected_index = -1
    
    def _on_focus_out(self, event=None):
        """Handle focus out - close suggestions after a delay"""
        self.after(200, self._close_suggestions)
    
    def _on_enter(self, event=None):
        """Handle Enter key - select highlighted suggestion or search content"""
        if self.selected_index >= 0 and self.selected_index < len(self.suggestion_buttons):
            tool_id = self.suggestion_buttons[self.selected_index].tool_id
            self._select_tool(tool_id)
        elif self.suggestion_buttons:
            # Select first suggestion if nothing highlighted
            tool_id = self.suggestion_buttons[0].tool_id
            self._select_tool(tool_id)
        else:
            # No suggestions - do content search
            self._search_content()
        return "break"
    
    def _on_arrow_up(self, event=None):
        """Navigate up in suggestions"""
        if not self.suggestion_buttons:
            return "break"
        
        self._update_selection(self.selected_index - 1)
        return "break"
    
    def _on_arrow_down(self, event=None):
        """Navigate down in suggestions"""
        if not self.suggestion_buttons:
            return "break"
        
        self._update_selection(self.selected_index + 1)
        return "break"
    
    def _update_selection(self, new_index):
        """Update visual selection in suggestions"""
        if new_index < 0:
            new_index = len(self.suggestion_buttons) - 1
        elif new_index >= len(self.suggestion_buttons):
            new_index = 0
        
        # Reset previous selection
        if self.selected_index >= 0 and self.selected_index < len(self.suggestion_buttons):
            self.suggestion_buttons[self.selected_index].configure(fg_color="transparent")
        
        # Highlight new selection
        self.selected_index = new_index
        if self.selected_index >= 0:
            self.suggestion_buttons[self.selected_index].configure(fg_color=COLORS['electric_violet'])
    
    def _select_tool(self, tool_id):
        """Select a tool from suggestions"""
        self._close_suggestions()
        self.search_var.set("")  # Clear search
        
        if self.on_tool_select:
            self.on_tool_select(tool_id)
    
    def _search_content(self):
        """Trigger content search in current view"""
        text = self.search_var.get().strip()
        self._close_suggestions()
        
        if text and self.on_content_search:
            self.on_content_search(text)
    
    def focus(self):
        """Focus the search entry"""
        self.entry.focus()
        self.entry.select_range(0, 'end')
    
    def get(self):
        """Get current search text"""
        return self.search_var.get()
    
    def set_collapsed(self, collapsed):
        """Adjust appearance for collapsed sidebar"""
        if collapsed:
            self.entry.configure(placeholder_text="🔍")
        else:
            self.entry.configure(placeholder_text="🔍 Search tools...")


class SortableTable(ctk.CTkFrame):
    """
    Sortable and filterable table component.
    Usage:
        table = SortableTable(parent, columns=[("IP", 150), ("Status", 100), ("RTT", 80)])
        table.add_row(["192.168.1.1", "Online", "5ms"])
        table.sort_by("IP")
    """
    
    def __init__(self, parent, columns, **kwargs):
        kwargs.setdefault('fg_color', COLORS['dashboard_card'])
        kwargs.setdefault('corner_radius', RADIUS['medium'])
        super().__init__(parent, **kwargs)
        
        self.columns = columns  # List of (name, width) tuples
        self.rows_data = []  # Raw data for sorting/filtering
        self.filtered_data = []  # Filtered data
        self.sort_column = None
        self.sort_ascending = True
        self.row_widgets = []
        
        self._create_header()
        self._create_body()
    
    def _create_header(self):
        """Create sortable header row"""
        self.header_frame = ctk.CTkFrame(self, fg_color=COLORS['electric_violet'], corner_radius=0)
        self.header_frame.pack(fill="x", padx=2, pady=(2, 0))
        
        self.header_buttons = []
        for col_name, col_width in self.columns:
            btn = ctk.CTkButton(
                self.header_frame,
                text=f"{col_name} ↕",
                width=col_width,
                height=35,
                corner_radius=0,
                fg_color="transparent",
                hover_color=COLORS['neon_cyan'],
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w",
                command=lambda c=col_name: self.sort_by(c)
            )
            btn.pack(side="left", padx=1)
            self.header_buttons.append((col_name, btn))
    
    def _create_body(self):
        """Create scrollable body"""
        self.body_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.body_frame.pack(fill="both", expand=True, padx=2, pady=2)
    
    def add_row(self, data, row_id=None):
        """Add a row of data"""
        if row_id is None:
            row_id = len(self.rows_data)
        
        self.rows_data.append({
            'id': row_id,
            'data': data
        })
        self.filtered_data = self.rows_data.copy()
        self._render_rows()
    
    def set_data(self, data_list):
        """Set all data at once (more efficient for large datasets)"""
        self.rows_data = [{'id': i, 'data': d} for i, d in enumerate(data_list)]
        self.filtered_data = self.rows_data.copy()
        self._render_rows()
    
    def clear(self):
        """Clear all data"""
        self.rows_data = []
        self.filtered_data = []
        self._render_rows()
    
    def sort_by(self, column_name):
        """Sort table by column"""
        col_index = None
        for i, (name, _) in enumerate(self.columns):
            if name == column_name:
                col_index = i
                break
        
        if col_index is None:
            return
        
        # Toggle sort direction if same column
        if self.sort_column == column_name:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = column_name
            self.sort_ascending = True
        
        # Sort data
        def sort_key(row):
            value = row['data'][col_index] if col_index < len(row['data']) else ""
            # Try numeric sort
            try:
                return (0, float(str(value).replace('ms', '').replace('%', '')))
            except (ValueError, TypeError):
                return (1, str(value).lower())
        
        self.filtered_data.sort(key=sort_key, reverse=not self.sort_ascending)
        
        # Update header arrows
        for name, btn in self.header_buttons:
            if name == column_name:
                arrow = "↑" if self.sort_ascending else "↓"
                btn.configure(text=f"{name} {arrow}")
            else:
                btn.configure(text=f"{name} ↕")
        
        self._render_rows()
    
    def filter(self, search_text):
        """Filter rows by search text"""
        if not search_text:
            self.filtered_data = self.rows_data.copy()
        else:
            search_lower = search_text.lower()
            self.filtered_data = [
                row for row in self.rows_data
                if any(search_lower in str(cell).lower() for cell in row['data'])
            ]
        self._render_rows()
    
    def _render_rows(self):
        """Render visible rows"""
        # Clear existing widgets
        for widget in self.row_widgets:
            widget.destroy()
        self.row_widgets = []
        
        # Render rows (limit to prevent performance issues)
        max_rows = 500
        for i, row in enumerate(self.filtered_data[:max_rows]):
            row_color = ("gray95", "gray17") if i % 2 == 0 else ("gray90", "gray20")
            
            row_frame = ctk.CTkFrame(self.body_frame, fg_color=row_color, corner_radius=0, height=32)
            row_frame.pack(fill="x", pady=1)
            row_frame.pack_propagate(False)
            
            for j, ((col_name, col_width), cell_data) in enumerate(zip(self.columns, row['data'])):
                cell = ctk.CTkLabel(
                    row_frame,
                    text=str(cell_data),
                    width=col_width,
                    anchor="w",
                    font=ctk.CTkFont(size=11)
                )
                cell.pack(side="left", padx=(5, 1), pady=2)
            
            self.row_widgets.append(row_frame)
        
        # Show count if limited
        if len(self.filtered_data) > max_rows:
            info_label = ctk.CTkLabel(
                self.body_frame,
                text=f"Showing {max_rows} of {len(self.filtered_data)} rows",
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text_secondary']
            )
            info_label.pack(pady=5)
            self.row_widgets.append(info_label)
    
    def get_selected(self):
        """Get selected row data (future: implement row selection)"""
        return None


class SimpleBarChart(ctk.CTkFrame):
    """
    Simple horizontal bar chart using canvas.
    Usage:
        chart = SimpleBarChart(parent, title="Scan Results")
        chart.set_data([("Online", 45, "green"), ("Offline", 200, "red")])
    """
    
    def __init__(self, parent, title="", height=150, **kwargs):
        kwargs.setdefault('fg_color', COLORS['dashboard_card'])
        kwargs.setdefault('corner_radius', RADIUS['medium'])
        super().__init__(parent, **kwargs)
        
        self.title_text = title
        self.chart_height = height
        self.data = []
        
        if title:
            self.title_label = ctk.CTkLabel(
                self,
                text=title,
                font=ctk.CTkFont(size=14, weight="bold")
            )
            self.title_label.pack(pady=(10, 5))
        
        self.canvas = ctk.CTkCanvas(
            self,
            height=height,
            bg=COLORS['bg_dark'],
            highlightthickness=0
        )
        self.canvas.pack(fill="x", padx=15, pady=(5, 15))
        
        self.bind("<Configure>", self._on_resize)
    
    def set_data(self, data):
        """
        Set chart data.
        Args:
            data: List of tuples (label, value, color)
        """
        self.data = data
        self._draw_chart()
    
    def _on_resize(self, event=None):
        """Handle resize"""
        self._draw_chart()
    
    def _draw_chart(self):
        """Draw the bar chart"""
        self.canvas.delete("all")
        
        if not self.data:
            return
        
        width = self.canvas.winfo_width()
        height = self.chart_height
        
        if width < 50:
            return
        
        # Calculate max value
        max_value = max(d[1] for d in self.data) if self.data else 1
        
        # Bar settings
        bar_height = min(30, (height - 20) // len(self.data))
        bar_gap = 8
        label_width = 100
        value_width = 60
        bar_area_width = width - label_width - value_width - 30
        
        y_offset = 10
        
        for label, value, color in self.data:
            # Calculate bar width
            bar_width = (value / max_value) * bar_area_width if max_value > 0 else 0
            
            # Draw label
            self.canvas.create_text(
                10, y_offset + bar_height // 2,
                text=label,
                anchor="w",
                fill=COLORS['text_primary'],
                font=("Segoe UI", 10)
            )
            
            # Draw bar background
            self.canvas.create_rectangle(
                label_width, y_offset,
                label_width + bar_area_width, y_offset + bar_height,
                fill=COLORS['bg_card'],
                outline=""
            )
            
            # Draw bar
            if bar_width > 0:
                self.canvas.create_rectangle(
                    label_width, y_offset,
                    label_width + bar_width, y_offset + bar_height,
                    fill=color,
                    outline=""
                )
            
            # Draw value
            self.canvas.create_text(
                label_width + bar_area_width + 10, y_offset + bar_height // 2,
                text=str(value),
                anchor="w",
                fill=COLORS['text_primary'],
                font=("Segoe UI", 10, "bold")
            )
            
            y_offset += bar_height + bar_gap


class StatCard(ctk.CTkFrame):
    """
    Statistics card showing a metric with icon.
    Usage: StatCard(parent, icon="📡", title="Hosts", value="254", color="green")
    """
    
    def __init__(self, parent, icon="📊", title="Metric", value="0", subtitle="", color=None, **kwargs):
        kwargs.setdefault('fg_color', COLORS['dashboard_card'])
        kwargs.setdefault('corner_radius', RADIUS['medium'])
        kwargs.setdefault('width', 150)
        kwargs.setdefault('height', 100)
        super().__init__(parent, **kwargs)
        
        self.pack_propagate(False)
        
        # Icon
        icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=ctk.CTkFont(size=28)
        )
        icon_label.pack(pady=(15, 5))
        
        # Value
        value_color = color if color else COLORS['text_primary']
        self.value_label = ctk.CTkLabel(
            self,
            text=str(value),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=value_color
        )
        self.value_label.pack()
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary']
        )
        title_label.pack()
        
        # Subtitle (optional)
        if subtitle:
            subtitle_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=ctk.CTkFont(size=9),
                text_color=COLORS['text_secondary']
            )
            subtitle_label.pack()
    
    def update_value(self, value, color=None):
        """Update the displayed value"""
        self.value_label.configure(text=str(value))
        if color:
            self.value_label.configure(text_color=color)


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



class HistoryPanel(ctk.CTkFrame):
    """
    Slide-out history panel showing recent actions and queries.
    """
    
    PANEL_WIDTH = 300
    
    def __init__(self, parent, **kwargs):
        kwargs.setdefault('width', self.PANEL_WIDTH)
        kwargs.setdefault('corner_radius', 0)
        kwargs.setdefault('fg_color', COLORS['dashboard_card'])
        super().__init__(parent, **kwargs)
        
        self.pack_propagate(False)
        self.is_visible = False
        self.history_items = []
        
        self._create_ui()
    
    def _create_ui(self):
        """Create panel UI"""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.pack(fill="x", padx=10, pady=10)
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header,
            text="📜 History",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['electric_violet']
        )
        title.pack(side="left")
        
        close_btn = ctk.CTkButton(
            header,
            text="✕",
            width=30,
            height=30,
            corner_radius=15,
            fg_color="transparent",
            hover_color=COLORS['dashboard_card_hover'],
            command=self.hide
        )
        close_btn.pack(side="right")
        
        # Separator
        sep = ctk.CTkFrame(self, height=2, fg_color=COLORS['electric_violet'])
        sep.pack(fill="x", padx=10, pady=(0, 10))
        
        # History list
        self.history_list = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.history_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Clear button at bottom
        clear_btn = ctk.CTkButton(
            self,
            text="🗑️ Clear History",
            height=35,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS['danger'],
            hover_color=COLORS['danger'],
            command=self.clear_history
        )
        clear_btn.pack(fill="x", padx=10, pady=10)
    
    def add_item(self, action_type, title, subtitle="", data=None, on_click=None):
        """Add an item to history"""
        # Icons for different action types
        icons = {
            "scan": "📡",
            "dns": "🌐",
            "port": "🔌",
            "subnet": "🔢",
            "traceroute": "🛤️",
            "export": "📤",
            "search": "🔍",
        }
        
        icon = icons.get(action_type, "📌")
        
        # Create history item frame
        item_frame = ctk.CTkFrame(
            self.history_list,
            fg_color=COLORS['bg_card'],
            corner_radius=8
        )
        item_frame.pack(fill="x", pady=3)
        
        # Content
        content = ctk.CTkFrame(item_frame, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=8)
        
        # Icon and title row
        title_row = ctk.CTkFrame(content, fg_color="transparent")
        title_row.pack(fill="x")
        
        icon_label = ctk.CTkLabel(
            title_row,
            text=icon,
            font=ctk.CTkFont(size=16)
        )
        icon_label.pack(side="left", padx=(0, 5))
        
        title_label = ctk.CTkLabel(
            title_row,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        title_label.pack(side="left", fill="x", expand=True)
        
        # Timestamp
        from datetime import datetime
        time_label = ctk.CTkLabel(
            title_row,
            text=datetime.now().strftime("%H:%M"),
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_secondary']
        )
        time_label.pack(side="right")
        
        # Subtitle
        if subtitle:
            sub_label = ctk.CTkLabel(
                content,
                text=subtitle,
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text_secondary'],
                anchor="w"
            )
            sub_label.pack(fill="x", pady=(2, 0))
        
        # Make clickable
        if on_click:
            for widget in [item_frame, content, title_row, icon_label, title_label]:
                widget.bind("<Button-1>", lambda e: on_click(data))
                widget.configure(cursor="hand2")
        
        # Store item
        self.history_items.insert(0, {
            'frame': item_frame,
            'type': action_type,
            'title': title,
            'data': data
        })
        
        # Limit history to 50 items
        if len(self.history_items) > 50:
            old_item = self.history_items.pop()
            old_item['frame'].destroy()
    
    def clear_history(self):
        """Clear all history items"""
        for item in self.history_items:
            item['frame'].destroy()
        self.history_items = []
    
    def show(self):
        """Show the panel"""
        if not self.is_visible:
            self.pack(side="right", fill="y", padx=0, pady=0)
            self.is_visible = True
    
    def hide(self):
        """Hide the panel"""
        if self.is_visible:
            self.pack_forget()
            self.is_visible = False
    
    def toggle(self):
        """Toggle panel visibility"""
        if self.is_visible:
            self.hide()
        else:
            self.show()


class TabView(ctk.CTkFrame):
    """
    Tab container for organizing content into tabs.
    """
    
    def __init__(self, parent, tabs=None, **kwargs):
        kwargs.setdefault('fg_color', 'transparent')
        super().__init__(parent, **kwargs)
        
        self.tabs = {}
        self.tab_buttons = {}
        self.active_tab = None
        
        # Tab bar
        self.tab_bar = ctk.CTkFrame(self, fg_color=COLORS['dashboard_card'], height=45)
        self.tab_bar.pack(fill="x")
        self.tab_bar.pack_propagate(False)
        
        # Tab content area
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True)
        
        # Add initial tabs
        if tabs:
            for tab_id, tab_name in tabs:
                self.add_tab(tab_id, tab_name)
    
    def add_tab(self, tab_id, tab_name, content_creator=None):
        """Add a new tab"""
        # Create tab button
        btn = ctk.CTkButton(
            self.tab_bar,
            text=tab_name,
            height=35,
            corner_radius=0,
            fg_color="transparent",
            hover_color=COLORS['dashboard_card_hover'],
            font=ctk.CTkFont(size=12),
            command=lambda: self.select_tab(tab_id)
        )
        btn.pack(side="left", padx=2, pady=5)
        
        # Create content frame
        content_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        # Call content creator if provided
        if content_creator:
            content_creator(content_frame)
        
        self.tabs[tab_id] = content_frame
        self.tab_buttons[tab_id] = btn
        
        # Select first tab
        if len(self.tabs) == 1:
            self.select_tab(tab_id)
        
        return content_frame
    
    def select_tab(self, tab_id):
        """Select a tab"""
        if tab_id not in self.tabs:
            return
        
        # Hide current tab
        if self.active_tab and self.active_tab in self.tabs:
            self.tabs[self.active_tab].pack_forget()
            self.tab_buttons[self.active_tab].configure(fg_color="transparent")
        
        # Show selected tab
        self.tabs[tab_id].pack(fill="both", expand=True)
        self.tab_buttons[tab_id].configure(fg_color=COLORS['electric_violet'])
        self.active_tab = tab_id
    
    def get_tab_content(self, tab_id):
        """Get the content frame for a tab"""
        return self.tabs.get(tab_id)



class ContextMenu:
    """
    Right-click context menu for various UI elements using custom Toplevel window.
    Fixed z-index issue with proper focus management and click-outside handling.
    
    Usage:
        menu = ContextMenu(parent_widget, items=[
            ("Copy", lambda: print("Copied")),
            ("Export", lambda: print("Exported")),
            None,  # Separator
            ("Delete", lambda: print("Deleted"))
        ])
        widget.bind("<Button-3>", menu.show)
    """
    
    # Class-level tracking of active menu
    _active_menu = None
    
    def __init__(self, widget, items):
        """
        Initialize context menu
        
        Args:
            widget: The widget to attach the menu to
            items: List of tuples (label, command) or None for separator
        """
        self.widget = widget
        self.items = items
        self.menu_window = None
        self._click_binding = None
    
    @classmethod
    def close_active_menu(cls):
        """Close any currently active context menu"""
        if cls._active_menu is not None:
            try:
                if cls._active_menu.menu_window is not None:
                    cls._active_menu.menu_window.destroy()
                    cls._active_menu.menu_window = None
            except:
                pass
            cls._active_menu = None
    
    def show(self, event):
        """Show context menu at cursor position using custom Toplevel"""
        import customtkinter as ctk
        
        # Close any existing active menu first
        ContextMenu.close_active_menu()
        
        # Get the root window (main application window)
        root = self.widget.winfo_toplevel()
        
        # Create toplevel window for menu
        self.menu_window = ctk.CTkToplevel(root)
        self.menu_window.withdraw()  # Hide initially while configuring
        
        # Remove window decorations
        self.menu_window.overrideredirect(True)
        
        # Configure for proper layering
        self.menu_window.transient(root)  # Associate with main window
        self.menu_window.attributes('-topmost', True)  # Keep on top
        
        # On Windows, ensure window stays on top
        try:
            self.menu_window.attributes('-toolwindow', True)  # Windows: no taskbar icon
        except:
            pass
        
        # Menu container frame with shadow effect
        menu_frame = ctk.CTkFrame(
            self.menu_window,
            fg_color=("#2D2D2D", "#1E1B2E"),  # Darker background for contrast
            corner_radius=8,
            border_width=2,
            border_color=COLORS['electric_violet']
        )
        menu_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Add menu items
        for item in self.items:
            if item is None:
                # Separator
                sep = ctk.CTkFrame(menu_frame, height=1, fg_color=COLORS['text_secondary'])
                sep.pack(fill="x", padx=10, pady=5)
            else:
                label, command = item
                
                def make_command(cmd):
                    def wrapped():
                        self._close()
                        if cmd:
                            cmd()
                    return wrapped
                
                btn = ctk.CTkButton(
                    menu_frame,
                    text=label,
                    command=make_command(command),
                    fg_color="transparent",
                    hover_color=COLORS['electric_violet'],
                    text_color="white",
                    anchor="w",
                    height=34,
                    corner_radius=6,
                    font=ctk.CTkFont(size=12)
                )
                btn.pack(fill="x", padx=5, pady=2)
        
        # Calculate position - ensure menu stays on screen
        self.menu_window.update_idletasks()
        menu_width = self.menu_window.winfo_reqwidth()
        menu_height = self.menu_window.winfo_reqheight()
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        x = event.x_root
        y = event.y_root
        
        # Adjust if menu would go off-screen
        if x + menu_width > screen_width:
            x = screen_width - menu_width - 10
        if y + menu_height > screen_height:
            y = screen_height - menu_height - 10
        
        self.menu_window.geometry(f"+{x}+{y}")
        
        # Show menu and ensure it's on top
        self.menu_window.deiconify()
        self.menu_window.lift()
        self.menu_window.focus_force()
        
        # Track this as the active menu
        ContextMenu._active_menu = self
        
        # Bind global click to close menu when clicking outside
        def on_global_click(e):
            # Check if click was outside the menu
            if self.menu_window is None:
                return
            try:
                # Get click coordinates relative to screen
                click_x = e.x_root
                click_y = e.y_root
                
                # Get menu bounds
                menu_x = self.menu_window.winfo_rootx()
                menu_y = self.menu_window.winfo_rooty()
                menu_w = self.menu_window.winfo_width()
                menu_h = self.menu_window.winfo_height()
                
                # Close if click is outside menu bounds
                if not (menu_x <= click_x <= menu_x + menu_w and 
                        menu_y <= click_y <= menu_y + menu_h):
                    self._close()
            except:
                self._close()
        
        # Bind to root window for click-outside detection
        self._click_binding = root.bind_all("<Button-1>", on_global_click, add="+")
        
        # Also close on Escape key
        self.menu_window.bind("<Escape>", lambda e: self._close())
        
        # Prevent event propagation
        return "break"
    
    def _close(self):
        """Close this context menu and clean up bindings"""
        if self.menu_window is not None:
            try:
                # Remove global click binding
                if self._click_binding:
                    root = self.widget.winfo_toplevel()
                    try:
                        root.unbind_all("<Button-1>")
                    except:
                        pass
                    self._click_binding = None
                
                self.menu_window.destroy()
                self.menu_window = None
            except:
                pass
        
        if ContextMenu._active_menu == self:
            ContextMenu._active_menu = None




class LoadingSpinner(ctk.CTkFrame):
    """
    Animated loading spinner component
    Usage:
        spinner = LoadingSpinner(parent)
        spinner.pack()
        spinner.start()
        # ... do work ...
        spinner.stop()
    """
    
    def __init__(self, parent, text="Loading...", **kwargs):
        kwargs.setdefault('fg_color', 'transparent')
        super().__init__(parent, **kwargs)
        
        self.text = text
        self.animation_running = False
        self.animation_step = 0
        
        # Spinner characters
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
        # Create label
        self.label = ctk.CTkLabel(
            self,
            text=f"{self.spinner_chars[0]} {self.text}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['electric_violet']
        )
        self.label.pack(pady=20)
    
    def start(self):
        """Start the spinner animation"""
        self.animation_running = True
        self._animate()
    
    def stop(self):
        """Stop the spinner animation"""
        self.animation_running = False
    
    def _animate(self):
        """Animate the spinner"""
        if not self.animation_running:
            return
        
        # Update spinner character
        self.animation_step = (self.animation_step + 1) % len(self.spinner_chars)
        char = self.spinner_chars[self.animation_step]
        self.label.configure(text=f"{char} {self.text}")
        
        # Schedule next frame
        self.after(100, self._animate)
    
    def update_text(self, text):
        """Update the loading text"""
        self.text = text


class ProgressIndicator(ctk.CTkFrame):
    """
    Progress indicator with percentage and bar
    Usage:
        progress = ProgressIndicator(parent, "Scanning...")
        progress.pack()
        progress.update_progress(50, "50/100 hosts scanned")
    """
    
    def __init__(self, parent, title="Progress", **kwargs):
        kwargs.setdefault('fg_color', COLORS['dashboard_card'])
        kwargs.setdefault('corner_radius', 8)
        super().__init__(parent, **kwargs)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.title_label.pack(padx=20, pady=(15, 5))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=300,
            progress_color=COLORS['electric_violet']
        )
        self.progress_bar.pack(padx=20, pady=10)
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="0%",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        self.status_label.pack(padx=20, pady=(0, 15))
    
    def update_progress(self, percentage, status_text=""):
        """Update progress bar and text"""
        # Clamp percentage between 0 and 100
        percentage = max(0, min(100, percentage))
        
        # Update bar
        self.progress_bar.set(percentage / 100)
        
        # Update text
        if status_text:
            self.status_label.configure(text=f"{percentage}% - {status_text}")
        else:
            self.status_label.configure(text=f"{percentage}%")
    
    def reset(self):
        """Reset progress to 0"""
        self.progress_bar.set(0)



class ErrorDialog:
    """
    Enhanced error dialog with suggestions and actions
    Usage:
        ErrorDialog.show(
            parent,
            "Connection Failed",
            "Could not connect to target host",
            suggestions=["Check if host is online", "Verify firewall settings"],
            actions=[("Retry", retry_function), ("Cancel", None)]
        )
    """
    
    @staticmethod
    def show(parent, title, message, suggestions=None, actions=None):
        """Show enhanced error dialog"""
        import tkinter.messagebox as mb
        from tkinter import Toplevel, Frame, Label, Button
        
        dialog = Toplevel(parent)
        dialog.title(title)
        dialog.geometry("500x350")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ctk.CTkFrame(dialog, fg_color=COLORS['bg_primary'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Error icon and title
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))
        
        error_label = ctk.CTkLabel(
            header_frame,
            text=f"❌ {title}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['danger']
        )
        error_label.pack()
        
        # Error message
        message_label = ctk.CTkLabel(
            main_frame,
            text=message,
            font=ctk.CTkFont(size=13),
            wraplength=450,
            justify="left"
        )
        message_label.pack(pady=(0, 15), anchor="w")
        
        # Suggestions
        if suggestions:
            suggestions_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['dashboard_card'], corner_radius=8)
            suggestions_frame.pack(fill="x", pady=(0, 15))
            
            suggest_title = ctk.CTkLabel(
                suggestions_frame,
                text="💡 Suggestions:",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            suggest_title.pack(anchor="w", padx=15, pady=(10, 5))
            
            for suggestion in suggestions:
                suggest_label = ctk.CTkLabel(
                    suggestions_frame,
                    text=f"• {suggestion}",
                    font=ctk.CTkFont(size=11),
                    anchor="w"
                )
                suggest_label.pack(anchor="w", padx=25, pady=2)
            
            ctk.CTkLabel(suggestions_frame, text="").pack(pady=5)  # Spacing
        
        # Action buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))
        
        if actions:
            for action_text, action_func in actions:
                def make_action(func):
                    def wrapped():
                        dialog.destroy()
                        if func:
                            func()
                    return wrapped
                
                btn = StyledButton(
                    button_frame,
                    text=action_text,
                    command=make_action(action_func),
                    size="medium",
                    variant="primary" if action_func else "neutral"
                )
                btn.pack(side="left", padx=5)
        else:
            close_btn = StyledButton(
                button_frame,
                text="Close",
                command=dialog.destroy,
                size="medium"
            )
            close_btn.pack()
        
        dialog.focus_set()




def add_tooltip_to_widget(widget, text):
    """
    Convenience function to add tooltip to any widget
    Usage: add_tooltip_to_widget(my_button, "Click to scan network")
    """
    Tooltip(widget, text)
