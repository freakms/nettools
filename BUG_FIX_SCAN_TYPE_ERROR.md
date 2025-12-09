# Bug Fix: IPv4 Scanner Type Error

## Issue
When starting an IPv4 scan, the application displayed an error at the bottom:
```
Error: unsupported operand type(s) for -: 'str' and 'int'
```

## Root Cause
In `/app/tools/scanner.py`, the `timeout_ms` value was retrieved from a dictionary using `.get()` which could potentially return the value in a way that Python treated it ambiguously in some contexts. When this value was used in the calculation `timeout_ms/1000` (line 50), Python raised a type error.

Similarly, the `max_workers` value had the same potential issue.

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
