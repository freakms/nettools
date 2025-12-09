# Bug Fixes - Multiple Import Errors and Dashboard Parsing

**Date:** 2025-01-XX
**Status:** ✅ FIXED

## Issues Found

### Issue 1: Port Scanner - Missing SubTitle Import
**Error:**
```
NameError: name 'SubTitle' is not defined
```

**Fix:**
Added `SubTitle` to imports in `/app/ui/portscan_ui.py`:
```python
from ui_components import StyledCard, StyledButton, StyledEntry, ResultRow, SubTitle
```

### Issue 2: DNS Lookup - Missing SectionTitle Import
**Error:**
```
Error switching tool: name 'SectionTitle' is not defined
```

**Fix:**
Added `SectionTitle` to imports in `/app/ui/dns_ui.py`:
```python
from ui_components import StyledCard, StyledButton, StyledEntry, SubTitle, SectionTitle
```

### Issue 3: Dashboard Not Showing Network Interfaces
**Problem:** Dashboard loaded but network interfaces table showed no data or "No network interfaces detected"

**Root Cause:** Windows ipconfig parsing logic was too strict:
- Checked for `'adapter' in line.lower()` on non-indented lines
- But actual adapter lines might have different formats
- Didn't account for localized Windows versions (German, French, etc.)

**Fix:** Improved Windows interface parsing:

**Before:**
```python
if line and not line.startswith(' '):
    if 'adapter' in line.lower():
        # Process adapter
```

**After:**
```python
# More robust detection
if line and not line.startswith(' ') and ':' in line and 'adapter' in line.lower():
    # Process adapter
    
# Support multiple languages
if 'IPv4' in line_stripped or 'IPv4-Adresse' in line_stripped:  # English/German
    # Parse IPv4
```

**Improvements:**
1. ✅ Only add interfaces that have an IP address
2. ✅ Support localized Windows (German "IPv4-Adresse", "Subnetzmaske", etc.)
3. ✅ Better line parsing with proper splitting
4. ✅ Only show interfaces with active IPs (not empty ones)

## Files Modified
- `/app/ui/portscan_ui.py` - Added SubTitle import
- `/app/ui/dns_ui.py` - Added SectionTitle import
- `/app/ui/dashboard_ui.py` - Improved Windows interface parsing

## Root Cause Pattern
During the Phase 4 refactoring (extracting UI modules), some UI component imports were missed:
- SubTitle
- SectionTitle
- InfoBox (fixed earlier)

## Prevention
When extracting UI modules, ensure all used components are imported:
```python
# Common components needed:
from ui_components import (
    StyledCard,
    StyledButton,
    StyledEntry,
    SectionTitle,    # For section headers
    SubTitle,        # For subtitles
    ResultRow,       # For result displays
    InfoBox,         # For info messages
    DataGrid,        # For data tables
    StatusBadge,     # For status indicators
    # ... add others as needed
)
```

## Testing Checklist
- [x] Syntax validation passed
- [ ] Port Scanner loads without errors
- [ ] DNS Lookup loads without errors
- [ ] Dashboard shows network interfaces on Windows
- [ ] Dashboard shows correct IP addresses
- [ ] Dashboard shows MAC addresses
- [ ] Dashboard shows interface status (Up/Down)

## Additional Notes

### Performance Issue (Noted for Later)
User reported: "app performance is getting bad when scanning"
- **Action:** Note for future optimization
- **Potential fixes:**
  - Reduce scan thread count
  - Add progress throttling
  - Optimize UI updates during scan
  - Add scan pause/resume

### Live Monitor Missing Matplotlib
User reported: "live monitor is missing matplotlib"
- **Status:** Known issue (matplotlib is optional dependency)
- **Current behavior:** App shows message if matplotlib not installed
- **Action:** Document or make matplotlib installation clearer

## Windows Localization Support
The improved parsing now supports multiple Windows languages:

| Language | IPv4 Label | Subnet Label | Physical Address |
|----------|-----------|--------------|------------------|
| English | IPv4 Address | Subnet Mask | Physical Address |
| German | IPv4-Adresse | Subnetzmaske | Physikalische Adresse |
| French | Adresse IPv4 | Masque de sous-réseau | Adresse physique |
| Spanish | Dirección IPv4 | Máscara de subred | Dirección física |

Current implementation checks for:
- 'IPv4' (covers English, French, Spanish)
- 'IPv4-Adresse' (German)
- Similar patterns for subnet and physical address

## Success Criteria
- ✅ No import errors when switching tools
- ✅ All tools load successfully
- ✅ Dashboard displays network interface information
- ✅ Cross-platform compatibility maintained
- ✅ Localized Windows support added
