# Testing Guide - NetTools Suite v1.2

## Overview

This document provides step-by-step testing procedures for the new features in version 1.2.

---

## Quick Start Testing

### Prerequisites
```bash
cd /app
python nettools_app.py
```

---

## Test Suite 1: OUI Vendor Lookup (v1.1 Feature)

### Test 1.1: Basic Vendor Lookup
1. Open MAC Formatter tab
2. Enter: `00:0C:29:12:34:56`
3. **Expected**: See "🏢 Vendor: VMware, Inc." below input field
4. ✅ **Pass** if vendor shown correctly

### Test 1.2: Different MAC Formats
1. Test colon format: `3C:22:FB:12:34:56`
   - **Expected**: "🏢 Vendor: Apple, Inc."
2. Test dash format: `3C-22-FB-12-34-56`
   - **Expected**: "🏢 Vendor: Apple, Inc."
3. Test plain format: `3C22FB123456`
   - **Expected**: "🏢 Vendor: Apple, Inc."
4. Test Cisco format: `3C22.FB12.3456`
   - **Expected**: "🏢 Vendor: Apple, Inc."
5. ✅ **Pass** if all formats work

### Test 1.3: Unknown Vendor
1. Enter: `AA:BB:CC:DD:EE:FF`
2. **Expected**: "🏢 Vendor: Unknown"
3. ✅ **Pass** if "Unknown" shown

### Test 1.4: Invalid MAC
1. Enter: `invalid`
2. **Expected**: Warning message, no vendor shown
3. ✅ **Pass** if handled gracefully

---

## Test Suite 2: History Feature (v1.1 Feature)

### Test 2.1: CIDR History
1. Go to IPv4 Scanner tab
2. Scan `192.168.1.0/24` (or any valid CIDR)
3. Click ⏱ (clock) button
4. **Expected**: Popup showing recent scans
5. Click on a CIDR from history
6. **Expected**: CIDR filled in input field
7. ✅ **Pass** if history works

### Test 2.2: MAC History
1. Go to MAC Formatter tab
2. Enter a few different MAC addresses
3. Click ⏱ (clock) button
4. **Expected**: Popup showing recent MACs
5. Click on a MAC from history
6. **Expected**: MAC filled in input field, formats updated
7. ✅ **Pass** if history works

---

## Test Suite 3: Scan Storage (v1.2 Feature)

### Test 3.1: Automatic Save
1. Go to IPv4 Scanner tab
2. Run a scan (any network)
3. Wait for completion
4. **Expected**: Status shows "Scan complete (Saved as [ID])"
5. **Expected**: "Compare Scans" button becomes enabled
6. ✅ **Pass** if scan saved and button enabled

### Test 3.2: Multiple Scans
1. Run scan of `192.168.1.0/24`
2. Run scan of `10.0.0.0/24`
3. Run scan of `172.16.0.0/24`
4. Click "Compare Scans"
5. **Expected**: Dropdown shows all 3 scans with format:
   ```
   [ID] - [CIDR] ([online]/[total] online)
   ```
6. ✅ **Pass** if all scans appear in dropdown

### Test 3.3: Persistent Storage
1. Run a scan
2. Close the application
3. Reopen the application
4. Run another scan
5. Click "Compare Scans"
6. **Expected**: Previous scan still available in dropdown
7. ✅ **Pass** if scans persist across restarts

---

## Test Suite 4: Scan Comparison (v1.2 Feature)

### Test 4.1: Basic Comparison
1. Run a scan of any network
2. Wait a few seconds
3. Run the same scan again
4. Click "Compare Scans" button
5. Select first scan in "Scan 1" dropdown
6. Select second scan in "Scan 2" dropdown
7. Click "Compare" button
8. **Expected**: Results showing change summary and details
9. **Expected**: Summary like "✅ Unchanged: X | 🆕 New: Y | ❌ Missing: Z | 🔄 Changed: W"
10. ✅ **Pass** if comparison shown

### Test 4.2: Change Detection - New Hosts
**Setup**: This test requires two scans where a device appears

1. Scan network when a device is offline
2. Turn device online
3. Scan again
4. Compare scans
5. **Expected**: Device shown with 🆕 icon
6. **Expected**: "Scan 1 Status: N/A", "Scan 2 Status: Online"
7. ✅ **Pass** if new host detected

### Test 4.3: Change Detection - Missing Hosts
**Setup**: This test requires two scans where a device disappears

1. Scan network when a device is online
2. Turn device offline
3. Scan again
4. Compare scans
5. **Expected**: Device shown with ❌ icon
6. **Expected**: "Scan 1 Status: Online", "Scan 2 Status: N/A"
7. ✅ **Pass** if missing host detected

### Test 4.4: Change Detection - Changed Status
**Setup**: This test requires a host that changes status

1. Scan network with all hosts in consistent state
2. Change some hosts' status
3. Scan again
4. Compare scans
5. **Expected**: Changed hosts shown with 🔄 icon
6. ✅ **Pass** if changed hosts detected

### Test 4.5: Unchanged Hosts
1. Run same scan twice with no network changes
2. Compare scans
3. **Expected**: All hosts shown with ✅ icon
4. **Expected**: "Unchanged: [total count]"
5. ✅ **Pass** if all hosts marked unchanged

### Test 4.6: Same Scan Warning
1. Open "Compare Scans"
2. Select same scan in both dropdowns
3. Click "Compare"
4. **Expected**: Warning: "Please select two different scans to compare."
5. ✅ **Pass** if warning shown

### Test 4.7: Insufficient Scans
1. Fresh install or clear scan history
2. Run only 1 scan
3. Click "Compare Scans"
4. **Expected**: Info message: "You need at least 2 saved scans to compare..."
5. ✅ **Pass** if info shown

---

## Test Suite 5: Export Functionality (v1.2 Feature)

### Test 5.1: Export Comparison
1. Perform a comparison (see Test 4.1)
2. Click "Export Comparison" button
3. Choose save location
4. **Expected**: File save dialog appears
5. **Expected**: Default filename: `comparison_[scan1]_vs_[scan2].csv`
6. Save file
7. **Expected**: Success message
8. ✅ **Pass** if file saved

### Test 5.2: Verify CSV Contents
1. Export a comparison (see Test 5.1)
2. Open CSV file in Excel or text editor
3. **Expected**: Headers: `Change,IP Address,Scan 1 Status,Scan 2 Status,Scan 1 RTT,Scan 2 RTT`
4. **Expected**: Data rows with proper format
5. **Expected**: Change types: `new`, `missing`, `changed`, `unchanged`
6. ✅ **Pass** if CSV format correct

### Test 5.3: Export Before Comparison
1. Open "Compare Scans"
2. Select two scans but DON'T click "Compare"
3. Click "Export Comparison" directly
4. **Expected**: Comparison performed and then exported
5. ✅ **Pass** if export works

---

## Test Suite 6: UI/UX Testing (v1.2 Features)

### Test 6.1: Button States
1. Fresh app start (no scans)
2. **Expected**: "Compare Scans" button is **disabled**
3. Run a scan
4. **Expected**: "Compare Scans" button becomes **enabled**
5. ✅ **Pass** if button states correct

### Test 6.2: Window Behavior
1. Click "Compare Scans"
2. **Expected**: Modal window opens (900x700)
3. **Expected**: Main window is blocked (can't interact)
4. Click "Close" in comparison window
5. **Expected**: Main window is interactive again
6. ✅ **Pass** if window behavior correct

### Test 6.3: Color Coding
1. Perform a comparison with mixed results
2. **Expected**: Colors match change types:
   - ✅ Green for unchanged
   - 🆕 Blue for new
   - ❌ Red for missing
   - 🔄 Orange for changed
3. ✅ **Pass** if colors correct

### Test 6.4: Scrolling
1. Perform comparison of large network (200+ hosts)
2. **Expected**: Results area is scrollable
3. **Expected**: All results visible via scrolling
4. ✅ **Pass** if scrolling works

---

## Test Suite 7: Edge Cases & Error Handling

### Test 7.1: Empty Scans
1. Run a scan on a network with no responding hosts
2. Run another similar scan
3. Compare scans
4. **Expected**: Comparison shows "No differences" or empty results
5. ✅ **Pass** if handled gracefully

### Test 7.2: Large Networks
1. Scan a /20 network (4000+ hosts)
2. Compare with another scan
3. **Expected**: UI remains responsive
4. **Expected**: Results display correctly (may limit unchanged items)
5. ✅ **Pass** if handles large scans

### Test 7.3: File System Errors
**Manual test**: Make `~/.nettools/` directory read-only
1. Run a scan
2. **Expected**: App continues to work (may show error in console)
3. **Expected**: No crash
4. ✅ **Pass** if app doesn't crash

### Test 7.4: Corrupted Scan Data
**Manual test**: Edit `~/.nettools/scans.json` to be invalid JSON
1. Restart app
2. Run a scan
3. **Expected**: App initializes with empty scan list
4. **Expected**: New scan saved correctly
5. ✅ **Pass** if recovers from corruption

---

## Test Suite 8: Integration Testing

### Test 8.1: Complete Workflow
1. Fresh app start
2. Run scan #1 of `192.168.1.0/24`
3. Use history to re-scan same network
4. Compare both scans
5. Export comparison
6. Format a MAC address found in scan
7. Check vendor for that MAC
8. **Expected**: All features work together smoothly
9. ✅ **Pass** if complete workflow succeeds

### Test 8.2: Multi-Network Workflow
1. Scan network A (e.g., `192.168.1.0/24`)
2. Scan network B (e.g., `10.0.0.0/24`)
3. Scan network A again
4. Compare: Select both scans of network A
5. **Expected**: Comparison makes sense (same CIDR)
6. ✅ **Pass** if multi-network handled

---

## Test Suite 9: Performance Testing

### Test 9.1: Scan Storage Speed
1. Run 20 consecutive scans
2. **Expected**: Each scan saves instantly (< 1 second)
3. **Expected**: Oldest scans are removed automatically
4. ✅ **Pass** if storage is fast

### Test 9.2: Comparison Speed
1. Run two large scans (200+ hosts)
2. Perform comparison
3. **Expected**: Comparison completes in < 1 second
4. **Expected**: UI doesn't freeze
5. ✅ **Pass** if comparison is fast

### Test 9.3: Memory Usage
1. Run 20 scans
2. Open comparison window
3. Perform multiple comparisons
4. **Expected**: No memory leaks
5. **Expected**: App remains responsive
6. ✅ **Pass** if memory stable

---

## Regression Testing (Existing Features)

### Test R.1: IPv4 Scanning
1. Scan a network
2. **Expected**: Results display correctly
3. **Expected**: All original features still work
4. ✅ **Pass** if no regression

### Test R.2: MAC Formatting
1. Format a MAC address
2. **Expected**: All 4 formats shown
3. **Expected**: Switch commands generated
4. ✅ **Pass** if no regression

### Test R.3: CSV Export
1. Run a scan
2. Click "Export as CSV"
3. **Expected**: CSV file saved correctly
4. ✅ **Pass** if no regression

### Test R.4: Theme Switching
1. Switch between Dark and Light themes
2. **Expected**: All UI elements update correctly
3. **Expected**: New comparison window respects theme
4. ✅ **Pass** if no regression

---

## Test Results Template

Copy and fill out:

```
=== Test Results for v1.2.0 ===

Date: __________
Tested by: __________
Environment: [ ] Python Script  [ ] Windows EXE  [ ] Linux

Test Suite 1: OUI Vendor Lookup
  1.1 Basic Lookup:       [ ] Pass  [ ] Fail
  1.2 Different Formats:  [ ] Pass  [ ] Fail
  1.3 Unknown Vendor:     [ ] Pass  [ ] Fail
  1.4 Invalid MAC:        [ ] Pass  [ ] Fail

Test Suite 2: History Feature
  2.1 CIDR History:       [ ] Pass  [ ] Fail
  2.2 MAC History:        [ ] Pass  [ ] Fail

Test Suite 3: Scan Storage
  3.1 Automatic Save:     [ ] Pass  [ ] Fail
  3.2 Multiple Scans:     [ ] Pass  [ ] Fail
  3.3 Persistent Storage: [ ] Pass  [ ] Fail

Test Suite 4: Scan Comparison
  4.1 Basic Comparison:   [ ] Pass  [ ] Fail
  4.2 New Hosts:          [ ] Pass  [ ] Fail  [ ] Skip (requires setup)
  4.3 Missing Hosts:      [ ] Pass  [ ] Fail  [ ] Skip (requires setup)
  4.4 Changed Status:     [ ] Pass  [ ] Fail  [ ] Skip (requires setup)
  4.5 Unchanged Hosts:    [ ] Pass  [ ] Fail
  4.6 Same Scan Warning:  [ ] Pass  [ ] Fail
  4.7 Insufficient Scans: [ ] Pass  [ ] Fail

Test Suite 5: Export Functionality
  5.1 Export Comparison:  [ ] Pass  [ ] Fail
  5.2 Verify CSV:         [ ] Pass  [ ] Fail
  5.3 Export Before Comp: [ ] Pass  [ ] Fail

Test Suite 6: UI/UX
  6.1 Button States:      [ ] Pass  [ ] Fail
  6.2 Window Behavior:    [ ] Pass  [ ] Fail
  6.3 Color Coding:       [ ] Pass  [ ] Fail
  6.4 Scrolling:          [ ] Pass  [ ] Fail

Test Suite 7: Edge Cases
  7.1 Empty Scans:        [ ] Pass  [ ] Fail
  7.2 Large Networks:     [ ] Pass  [ ] Fail
  7.3 File System Errors: [ ] Pass  [ ] Fail  [ ] Skip
  7.4 Corrupted Data:     [ ] Pass  [ ] Fail  [ ] Skip

Test Suite 8: Integration
  8.1 Complete Workflow:  [ ] Pass  [ ] Fail
  8.2 Multi-Network:      [ ] Pass  [ ] Fail

Test Suite 9: Performance
  9.1 Storage Speed:      [ ] Pass  [ ] Fail
  9.2 Comparison Speed:   [ ] Pass  [ ] Fail
  9.3 Memory Usage:       [ ] Pass  [ ] Fail

Regression Tests
  R.1 IPv4 Scanning:      [ ] Pass  [ ] Fail
  R.2 MAC Formatting:     [ ] Pass  [ ] Fail
  R.3 CSV Export:         [ ] Pass  [ ] Fail
  R.4 Theme Switching:    [ ] Pass  [ ] Fail

Overall: [ ] All Pass  [ ] Some Failures

Notes:
__________________________________________
__________________________________________
```

---

## Critical Path Testing (Minimum Required)

If time is limited, test these critical paths:

1. ✅ Run 2 scans and compare them (Test 4.1)
2. ✅ Export a comparison (Test 5.1)
3. ✅ Check OUI vendor lookup works (Test 1.1)
4. ✅ Verify history buttons work (Tests 2.1, 2.2)
5. ✅ Ensure no crashes or errors

---

## Known Issues to Watch For

1. **Tkinter/GUI not available** in headless environments
   - Expected: Can't run GUI in this environment
   - Test with Windows desktop instead

2. **Large scans may be slow**
   - Expected for /16 networks or larger
   - Should still complete without crash

3. **JSON file corruption**
   - App should recover automatically
   - Creates new empty history if needed

---

## Success Criteria

✅ **Release Ready** if:
- All critical path tests pass
- No crashes or data loss
- Features work as documented
- UI is responsive and intuitive

---

**Testing completed by: __________**  
**Date: __________**  
**Version tested: 1.2.0**  
**Status: [ ] Approved for Release  [ ] Needs Fixes**
