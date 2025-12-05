# Color System Reference

## Issue Fixed
The Live Ping Monitor was using color keys that don't exist in the COLORS dictionary.

## Available Color Keys in design_constants.py

### Primary Colors
- `COLORS['primary']` - Blue (tuple: light, dark)
- `COLORS['primary_hover']` - Blue hover state

### Semantic Colors
- `COLORS['success']` - Green
- `COLORS['warning']` - Orange
- `COLORS['danger']` - Red
- `COLORS['neutral']` - Gray

### Status Colors
- `COLORS['online']` - Green (#4CAF50)
- `COLORS['offline']` - Gray (#757575)
- `COLORS['scanning']` - Blue (#2196F3)

### Background & Text (Tuples for light/dark mode)
- `COLORS['bg_card']` - (gray90, gray17)
- `COLORS['bg_card_hover']` - (gray85, gray20)
- `COLORS['text_primary']` - (gray10, gray90)
- `COLORS['text_secondary']` - (gray60, gray40)

## What Was Changed

### Before (Incorrect)
```python
header = ctk.CTkFrame(self, fg_color=COLORS['bg_secondary'])  # ❌ Key doesn't exist
self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS['bg_primary'])  # ❌ Key doesn't exist
bg=COLORS['bg_card']  # ❌ Tuple, not string
color=COLORS['text']  # ❌ Key doesn't exist
```

### After (Fixed)
```python
header = ctk.CTkFrame(self, fg_color=COLORS['bg_card'])  # ✅ Uses existing key
self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")  # ✅ Uses string
bg="gray85"  # ✅ Direct color string
color='#333333'  # ✅ Direct hex color
```

## Best Practices

### For Frames
```python
# Use existing color keys or transparent
fg_color=COLORS['bg_card']  # For styled cards
fg_color="transparent"      # For invisible containers
```

### For Canvas (matplotlib, tkinter)
```python
# Use direct color strings, not tuple keys
bg="gray85"           # Light gray
facecolor='#f0f0f0'  # Light background
color='#333333'      # Dark text
```

### For Text Colors
```python
# Use text color keys (tuples are OK for CTk widgets)
text_color=COLORS['text_primary']    # Main text
text_color=COLORS['text_secondary']  # Secondary text
```

## Adding New Colors

If you need colors that don't exist, add them to `/app/design_constants.py`:

```python
COLORS = {
    # ... existing colors ...
    
    # Add new colors here
    "bg_primary": "gray95",
    "bg_secondary": "gray90",
    "text": "gray10",
}
```

## Current Live Monitor Colors

The Live Ping Monitor now uses:
- **Header background**: `COLORS['bg_card']`
- **Scroll area**: `"transparent"`
- **Status canvas**: `"gray85"`
- **Graph background**: `'#f0f0f0'`
- **Graph axes**: `'#ffffff'`
- **Graph text**: `'#333333'`
- **Status indicators**: Direct hex colors (`#00ff00`, `#ffff00`, `#ff0000`)
