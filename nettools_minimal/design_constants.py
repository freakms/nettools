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
    "success": ("#22C55E", "#16A34A"),       # Green (updated)
    "success_hover": ("#4ADE80", "#22C55E"),
    "warning": ("#F59E0B", "#D97706"),       # Orange/Amber
    "warning_hover": ("#FBBF24", "#F59E0B"),
    "danger": ("#EF4444", "#DC2626"),        # Red
    "danger_hover": ("#F87171", "#EF4444"),
    
    # Neutral Colors
    "neutral": ("#6B7280", "#4B5563"),       # Gray (updated)
    "neutral_hover": ("#9CA3AF", "#6B7280"),
    
    # Status Colors
    "online": "#22C55E",
    "offline": "#6B7280",
    "scanning": "#3B82F6",
    
    # Background & Text
    "bg_primary": ("#F9FAFB", "#111827"),     # Main background
    "bg_card": ("#FFFFFF", "#1F2937"),        # Card background
    "bg_card_hover": ("#F3F4F6", "#374151"),  # Card hover
    "bg_dark": "#0F172A",                      # Dark background
    "text_primary": ("#111827", "#F9FAFB"),
    "text_secondary": ("#6B7280", "#9CA3AF"),
    
    # Dashboard Electric Violet Theme
    "dashboard_bg": ("#F5F3FF", "#0F0D1B"),           # Deep purple-black
    "dashboard_card": ("#FFFFFF", "#1E1B2E"),         # Dark violet cards
    "dashboard_card_hover": ("#F9F7FF", "#2A2640"),   # Lighter on hover
    "electric_violet": ("#8B5CF6", "#A78BFA"),        # Primary electric violet
    "electric_violet_hover": ("#A78BFA", "#C4B5FD"),  # Violet hover
    "neon_cyan": ("#06B6D4", "#22D3EE"),              # Accent neon cyan
    "neon_cyan_hover": ("#22D3EE", "#67E8F9"),        # Cyan hover
    "glow_purple": "#9333EA",                         # Glow effect color
    "glow_cyan": "#0891B2",                           # Cyan glow
    
    # Additional UI Colors
    "border": ("#E5E7EB", "#374151"),                 # Border color
    "focus_ring": "#8B5CF6",                          # Focus ring color
    "selection": ("#EDE9FE", "#312E81"),              # Selection background
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

# Button Sizes - Updated for professional appearance
BUTTON_SIZES = {
    "tiny": {"width": 60, "height": 26},
    "small": {"width": 100, "height": 32},
    "medium": {"width": 140, "height": 38},
    "large": {"width": 180, "height": 42},
    "xlarge": {"width": 220, "height": 48},
}

# Card Styling
CARD_STYLE = {
    "padding": SPACING["lg"],
    "radius": 12,
    "border_width": 1,
}

# Results Row Styling
ROW_STYLE = {
    "height": 44,
    "padding_x": 16,
    "padding_y": 10,
    "radius": 6,
    "spacing": 4,
}

# Input Field Styling
INPUT_STYLE = {
    "height": 40,
    "padding": 16,
    "radius": 8,
}

# Additional Professional Styling
ICON_SIZES = {
    "small": 14,
    "medium": 18,
    "large": 24,
    "xlarge": 32,
}

# Shadow/Depth simulation colors (for layered UI)
SHADOWS = {
    "light": ("gray80", "gray10"),
    "medium": ("gray70", "gray8"),
    "strong": ("gray60", "gray5"),
}

# Animation timing (in milliseconds)
ANIMATION = {
    "fast": 100,
    "normal": 200,
    "slow": 350,
}
