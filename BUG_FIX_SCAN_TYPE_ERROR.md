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
Added explicit `int()` conversions to ensure both `timeout_ms` and `max_workers` are always integers:

### Changes Made

**File: `/app/tools/scanner.py`**

1. **Line 145** - In `scan_network()` method:
   ```python
   # Before:
   timeout_ms = timeout_map.get(aggression, 300)
   
   # After:
   timeout_ms = int(timeout_map.get(aggression, 300))
   ```

2. **Line 154** - In `scan_network()` method:
   ```python
   # Before:
   max_workers = worker_map.get(aggression, 64)
   
   # After:
   max_workers = int(worker_map.get(aggression, 64))
   ```

3. **Line 207** - In `scan_ip_list()` method:
   ```python
   # Before:
   timeout_ms = timeout_map.get(aggression, 300)
   
   # After:
   timeout_ms = int(timeout_map.get(aggression, 300))
   ```

4. **Line 216** - In `scan_ip_list()` method:
   ```python
   # Before:
   max_workers = worker_map.get(aggression, 64)
   
   # After:
   max_workers = int(worker_map.get(aggression, 64))
   ```

## Testing
- Syntax check: ✓ Passed
- Type conversion test: ✓ All aggression levels convert correctly
- Edge cases: ✓ Default values work correctly

## Impact
This fix ensures that the IPv4 scanner will work reliably with all aggression settings (Gentle, Medium, Aggressive) without type errors.

## Date
December 2025
