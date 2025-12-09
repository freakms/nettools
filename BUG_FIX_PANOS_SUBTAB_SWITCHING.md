# Bug Fix - PAN-OS Generator Subtab Switching Issue

**Date:** 2025-01-XX
**Status:** ✅ FIXED

## Issue
When clicking in input data boxes in the Name Generator tab of the PAN-OS Generator, the view would unexpectedly switch to showing Single Address or Address Groups tabs.

## Root Cause
The initialization code had a logic error where it tried to directly pack `self.panos_name_gen_tab` at the module level:

```python
# Show name generator by default
self.panos_current_tab = "name"
self.panos_name_gen_tab.pack(fill="both", expand=True)
```

This created a conflict because:
1. The `panos_name_gen_tab` is already a child of `panos_addresses_tab`
2. The `panos_addresses_tab` itself wasn't being packed
3. This caused the widget hierarchy to be incorrect
4. Focus events and other interactions were triggering unexpected tab switching behavior

## Fix Applied
Changed the initialization to properly pack the parent addresses tab instead of trying to pack the subtab directly:

**Before:**
```python
# Show name generator by default
self.panos_current_tab = "name"
self.panos_name_gen_tab.pack(fill="both", expand=True)
```

**After:**
```python
# Show addresses tab by default (which shows name generator)
self.panos_current_tab = "addresses"
self.panos_addresses_tab.pack(fill="both", expand=True)
```

## Why This Works
The proper widget hierarchy is:
```
panos_tab_content (main container)
└── panos_addresses_tab (scrollable frame)
    ├── subtab_frame (buttons for Name Generator, Single Address, Groups)
    └── panos_name_gen_tab (content - shown by default)
        └── card with input fields
```

By packing the `panos_addresses_tab`, we ensure:
1. The correct parent-child relationship is maintained
2. The Name Generator content is shown by default (since it's not `pack_forget()` in the initialization)
3. Focus events stay within the correct widget hierarchy
4. Subtab switching works as intended

## Files Modified
- `/app/ui/panos_ui.py` - Fixed tab initialization logic

## Testing
- ✅ Python syntax validation passed
- ⏳ User testing required:
  1. Navigate to PAN-OS Generator
  2. Verify Name Generator tab is shown by default
  3. Click in the Base Names input box
  4. Verify it doesn't switch to other subtabs
  5. Click in the IP Addresses input box
  6. Verify it doesn't switch to other subtabs
  7. Manually click the Single Address and Address Groups buttons
  8. Verify subtab switching works correctly

## Prevention
When creating nested tab structures:
- Always pack the parent tab/frame, not the child content
- Ensure widget hierarchy is maintained correctly
- The child content visibility is controlled within its parent context
- Don't bypass the parent-child relationship by packing children directly
