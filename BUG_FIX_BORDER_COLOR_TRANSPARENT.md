# Bug Fix: CustomTkinter Border Color Transparency Error

## Issue
Application crashed on startup with the following error:
```
ValueError: transparency is not allowed for this attribute
```

**Error Location:** `nettools_app.py`, line 551 in `create_sidebar()` method

## Root Cause
CustomTkinter's `CTkButton` widget does **not accept** "transparent" as a valid value for the `border_color` parameter. 

The code was attempting to:
```python
btn = ctk.CTkButton(
    ...
    border_width=1,
    border_color="transparent"  # ❌ Invalid value
)
```

And later in `switch_page()`:
```python
btn.configure(
    fg_color="transparent",
    border_color="transparent"  # ❌ Invalid value
)
```

## Solution
Instead of using "transparent" for border_color, set `border_width=0` to hide the border completely.

### Fix 1: Button Creation (Line 550)
**Before:**
```python
border_width=1,
border_color="transparent"
```

**After:**
```python
border_width=0
```

### Fix 2: Active Button State (Line 605)
**Before:**
```python
btn.configure(
    fg_color=COLORS['dashboard_card_hover'],
    border_color=COLORS['electric_violet']
)
```

**After:**
```python
btn.configure(
    fg_color=COLORS['dashboard_card_hover'],
    border_width=2,
    border_color=COLORS['electric_violet']
)
```

### Fix 3: Inactive Button State (Line 610)
**Before:**
```python
btn.configure(
    fg_color="transparent",
    border_color="transparent"
)
```

**After:**
```python
btn.configure(
    fg_color="transparent",
    border_width=0
)
```

## Technical Details

### CustomTkinter Border Behavior:
- `border_width=0` → No border visible (correct way to hide border)
- `border_color="transparent"` → ValueError (not supported)
- When border_width=0, border_color is ignored

### Design Impact:
- Inactive buttons: No border (clean look)
- Active buttons: 2px electric violet border (clear indicator)
- Same visual result as intended

## Changes Summary

### Files Modified:
- `/app/nettools_app.py`

### Lines Changed:
- **Line 550**: Removed border_color, set border_width=0
- **Line 605**: Added border_width=2 for active state
- **Line 610**: Removed border_color, set border_width=0

## Testing
- ✓ Syntax check: Passed
- ⏳ Application starts without errors
- ⏳ Navigation buttons display correctly
- ⏳ Active page shows violet border
- ⏳ Inactive pages have no border

## Prevention
- Always check CustomTkinter documentation for valid parameter values
- Use `border_width=0` instead of `border_color="transparent"`
- Test on actual CustomTkinter version being used

## Date
December 2025
