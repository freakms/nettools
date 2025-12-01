"""
Design System Constants for NetTools Suite
Centralizes all design tokens for consistency
"""

# Color Palette - Consistent Design System
COLORS = {
    # Primary Colors
    "primary": ("#2196F3", "#1976D2"),       # Blue (light, dark)
    "primary_hover": ("#42A5F5", "#2196F3"), # Blue hover
    
    # Semantic Colors
    "success": ("#4CAF50", "#388E3C"),       # Green
    "success_hover": ("#66BB6A", "#4CAF50"),
    "warning": ("#FFC107", "#FF6F00"),       # Orange
    "warning_hover": ("#FFD54F", "#FFC107"),
    "danger": ("#F44336", "#D32F2F"),        # Red
    "danger_hover": ("#EF5350", "#F44336"),
    
    # Neutral Colors
    "neutral": ("#757575", "#616161"),       # Gray
    "neutral_hover": ("#9E9E9E", "#757575"),
    
    # Status Colors
    "online": "#4CAF50",
    "offline": "#757575",
    "scanning": "#2196F3",
    
    # Background & Text
    "bg_card": ("gray90", "gray17"),
    "bg_card_hover": ("gray85", "gray20"),
    "text_primary": ("gray10", "gray90"),
    "text_secondary": ("gray60", "gray40"),
}

# Spacing System (8px base unit)
SPACING = {
    "xs": 5,
    "sm": 10,
    "md": 15,
    "lg": 20,
    "xl": 25,
    "xxl": 30,
}

# Border Radius
RADIUS = {
    "small": 4,
    "medium": 6,
    "large": 8,
    "xlarge": 10,
}

# Font Sizes
FONTS = {
    "title": 24,
    "heading": 18,
    "subheading": 14,
    "body": 12,
    "small": 11,
    "tiny": 10,
}

# Button Sizes
BUTTON_SIZES = {
    "small": {"width": 100, "height": 32},
    "medium": {"width": 140, "height": 38},
    "large": {"width": 180, "height": 42},
    "xlarge": {"width": 200, "height": 48},
}

# Card Styling
CARD_STYLE = {
    "padding": SPACING["lg"],
    "radius": RADIUS["large"],
    "border_width": 1,
}

# Results Row Styling
ROW_STYLE = {
    "height": 40,
    "padding_x": 12,
    "padding_y": 8,
    "radius": RADIUS["medium"],
    "spacing": 3,
}

# Input Field Styling
INPUT_STYLE = {
    "height": 38,
    "padding": 15,
    "radius": RADIUS["medium"],
}
