# Bug Fix: IPv4 Scanner Type Error

## Issue
When starting an IPv4 scan, the application displayed an error at the bottom:
```
Error: unsupported operand type(s) for -: 'str' and 'int'
```

## Root Cause
**Variable Name Collision**: The application was using `self.current_page` for TWO different purposes:

1. **Navigation** (string): To track which tool is currently displayed (e.g., "scanner", "mac", "panos")
2. **Pagination** (integer): To track which page of scan results is displayed

When the navigation system set `self.current_page = "scanner"`, the pagination code tried to calculate:
```python
current_page_start = (self.current_page - 1) * self.results_per_page
# This became: ("scanner" - 1) * 100  → Type Error!
```

## Initial Fix Attempt
First, we added explicit `int()` conversions in `/app/tools/scanner.py` for `timeout_ms` and `max_workers`, but this didn't solve the root issue.

## Solution
**Renamed pagination variables** to avoid collision with navigation variables:

### Changes Made

**File: `/app/nettools_app.py`**

Renamed all pagination-related variables from:
- `self.current_page` → `self.scan_current_page`
- `self.total_pages` → `self.scan_total_pages`

**Affected Lines:**
- Line 126: Variable initialization
- Line 5232: Reset on scan start
- Lines 5394-5395: Page range calculation during scan
- Lines 5549-5560: Page navigation methods
- Lines 5570-5601: Page rendering and UI updates
- Line 889: "Last page" button command

**File: `/app/tools/scanner.py`** (Defensive improvement)

Added explicit `int()` conversions for robustness:
1. Lines 145, 207: `timeout_ms = int(timeout_map.get(aggression, 300))`
2. Lines 154, 216: `max_workers = int(worker_map.get(aggression, 64))`

## Testing
- ✓ Syntax check: Passed
- ✓ Variable naming: No more collisions between navigation and pagination
- ✓ Type safety: All pagination calculations use integers
- ⏳ User testing: Pending

## Impact
- **Navigation** (`self.current_page`) can now safely use strings for tool names
- **Pagination** (`self.scan_current_page`) uses integers for page numbers
- IPv4 scanner will work reliably with all aggression settings (Gentle, Medium, Aggressive)
- Scan results pagination will function correctly across all pages

## Prevention
This type of bug can be prevented by:
1. Using more specific variable names that indicate their purpose
2. Avoiding generic names like `current_page` that could have multiple meanings
3. Adding type hints to make variable types explicit

## Date
December 2025
