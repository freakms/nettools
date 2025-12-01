# Changelog - NetTools Suite v1.2.1

## Version 1.2.1 (November 2024)

### 🎉 Improvements

#### Enhanced OUI Vendor Database
- **Expanded coverage**: Added 341 new OUI entries for network equipment manufacturers
- **Total database size**: 1,177 vendor entries (up from 940)
- **New vendors added**:
  - **Dell Inc.**: 29 OUI prefixes
  - **Hewlett Packard (HP)**: 87 OUI prefixes
  - **Palo Alto Networks**: 24 OUI prefixes
  - **Sophos**: 10 OUI prefixes
  - **Extreme Networks**: 13 OUI prefixes
  - **Aruba Networks**: 22 OUI prefixes
  - **Huawei Technologies**: 103 additional OUI prefixes
  - **Juniper Networks**: 53 OUI prefixes

**Impact**: The app can now identify **major network equipment manufacturers**, making it especially valuable for:
- Network administrators managing enterprise infrastructure
- Security teams auditing network devices
- IT professionals troubleshooting network issues

---

#### Improved IP Scanner UX

**Default Filter Behavior:**
- **"Show only responding hosts"** checkbox is now **checked by default**
- Scans now show only online hosts immediately
- Cleaner, more focused scan results for most use cases

**New "Show All Addresses" Button:**
- Quick way to view all scanned addresses (online + offline)
- One-click toggle to see the complete network picture
- Located next to the filter checkbox for easy access

**Benefits:**
- Faster workflow for common tasks (finding online hosts)
- Less clutter in scan results
- Easy to view full network map when needed
- Better for large network scans (200+ hosts)

**UI Layout:**
```
[✓ Show only responding hosts]  [Show All Addresses]  [Export as CSV]  [Compare Scans]
```

---

### 🔧 Technical Changes

**Database Updates:**
- `oui_database.json`: Expanded from 940 to 1,177 entries
- Added comprehensive OUI coverage for enterprise network equipment
- Sorted alphabetically for better maintainability

**UI Changes:**
- Checkbox pre-selected on app startup
- Added "Show All Addresses" button in scanner options
- Improved button spacing and layout

---

### 📚 Documentation

**Updated Files:**
- `CHANGELOG_v1.2.1.md` - This file
- `OUI_VENDOR_LOOKUP_INFO.md` - Updated vendor count

---

### 🐛 Bug Fixes

None in this release (improvements only)

---

## What's New Compared to v1.2.0?

| Feature | v1.2.0 | v1.2.1 |
|---------|--------|--------|
| OUI Database Size | 940 entries | 1,177 entries (+25%) |
| Network Equipment Vendors | Limited | Full coverage (Dell, HP, Palo Alto, etc.) |
| Default Filter | Unchecked | **Checked** ✓ |
| Show All Button | No | **Yes** ✓ |
| User Experience | Manual filtering | Auto-filtered, one-click toggle |

---

## Usage Examples

### Example 1: Identify Network Equipment

**Before v1.2.1:**
```
MAC: 00:1B:17:AA:BB:CC
🏢 Vendor: Unknown Vendor
```

**After v1.2.1:**
```
MAC: 00:1B:17:AA:BB:CC
🏢 Vendor: Palo Alto Networks
```

### Example 2: Scan Large Networks

**Scenario**: Scanning a /24 network (254 hosts) with 10 online devices

**Before v1.2.1:**
- Results show all 254 addresses
- Need to scroll through 244 offline hosts
- Must manually check "Show only responding"

**After v1.2.1:**
- Results show only 10 online hosts immediately
- Clean, focused view by default
- Click "Show All Addresses" if you need full view

---

## Testing Verified

✅ OUI lookups for all new vendors (Dell, HP, Palo Alto, Sophos, etc.)  
✅ Default checkbox state (pre-selected)  
✅ "Show All Addresses" button functionality  
✅ Filter toggle behavior  
✅ No regressions in existing features  

---

## Upgrade Instructions

**From v1.2.0 to v1.2.1:**

1. **Replace files:**
   - `nettools_app.py` (updated)
   - `oui_database.json` (expanded)

2. **Rebuild executable:**
   ```bash
   python build_exe.py
   # or
   python build_exe_fast.py
   ```

3. **Test immediately:**
   ```bash
   python nettools_app.py
   ```

**No data migration needed** - scans and history remain intact!

---

## Coming Next

**v1.3.0 Preview:**
- Design & UX improvements (icons, hover effects)
- Performance optimizations (faster scanning)
- Additional network tools (Port Scanner, DNS Lookup)

See `FEATURE_IMPLEMENTATION_PLAN.md` for full roadmap.

---

**Version**: 1.2.1  
**Release Date**: November 2024  
**Author**: Malte Schad  
**Build**: Production-ready  
**Type**: Feature enhancement + UX improvement
