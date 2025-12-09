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
        self.configure(fg_color=COLORS['dashboard_card_hover'])
    
    def _on_leave(self, event):
        """Handle mouse leave"""
        self.configure(fg_color=self._original_color)


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
    """A simple loading indicator"""
    
    def __init__(self, parent, text="Loading...", **kwargs):
        kwargs.setdefault('text', f"⏳ {text}")
        kwargs.setdefault('font', ctk.CTkFont(size=FONTS['subheading']))
        kwargs.setdefault('text_color', COLORS['primary'])
        
        super().__init__(parent, **kwargs)


class InfoBox(ctk.CTkFrame):
    """An information/alert box"""
    
    def __init__(self, parent, message, box_type="info", **kwargs):
        # Determine color based on type
        if box_type == "success":
            bg_color = COLORS['success']
        elif box_type == "warning":
            bg_color = COLORS['warning']
        elif box_type == "error":
            bg_color = COLORS['danger']
        else:
            bg_color = COLORS['primary']
        
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
