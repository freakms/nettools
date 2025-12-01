# Changelog - NetTools Suite v1.2

## Version 1.2.0 (November 2024)

### 🎉 Major New Features

#### Scan Comparison & Export
- **Automatic scan storage**: All scan results are automatically saved for comparison
- **Compare any two scans**: Select from up to 20 recent scans per network
- **Visual diff display**: Instantly see what changed between scans
- **Four change types**: New (🆕), Missing (❌), Changed (🔄), Unchanged (✅)
- **Summary statistics**: Quick overview of changes
- **Export comparisons**: Save comparison reports as CSV files
- **Persistent storage**: Scans saved in `~/.nettools/scans.json`

**Use Cases:**
- Security monitoring (detect unauthorized devices)
- Troubleshooting (find hosts that went offline)
- Change documentation (before/after maintenance)
- Network auditing (track topology changes)

**UI Changes:**
- Added "Compare Scans" button in IPv4 Scanner tab
- New comparison window with dual-select interface
- Color-coded change indicators for easy identification
- Export functionality built into comparison window

---

### 📊 Feature Details

#### Scan Storage System
- **Automatic**: Every completed scan is saved
- **Capacity**: Stores up to 20 scans per application
- **Data stored**:
  - Scan ID (timestamp-based)
  - CIDR network scanned
  - Complete results (IP, status, RTT)
  - Summary (total/online/offline counts)
  - Timestamp

#### Comparison Engine
- **Smart IP matching**: Handles scans of the same network
- **Change detection**: Identifies new, missing, changed, and unchanged hosts
- **Performance optimized**: Handles large scans (1000+ hosts) efficiently
- **Detailed reporting**: Shows status and RTT for both scans

#### Export Options
- **CSV format**: Compatible with Excel, Google Sheets
- **Comprehensive data**: Includes all change types and metrics
- **Auto-naming**: Files named `comparison_[scan1]_vs_[scan2].csv`
- **Custom save location**: Choose where to save

---

## Version 1.1.0 (November 2024)

### 🎉 New Features

#### OUI Vendor Lookup
- Automatic manufacturer identification from MAC addresses
- Database with 940+ vendor entries
- Real-time lookup as you type
- Visual indicator with 🏢 icon

#### History & Recent Items
- CIDR History with ⏱ clock icon
- MAC History with quick access
- Stores up to 10 most recent items
- Persistent across sessions

---

## Version 1.0.0 (Initial Release)

### Core Features
- IPv4 Network Scanner with CIDR support
- MAC Address Formatter
- Switch command generation
- Dark/Light themes
- CSV export
- Scalable UI

---

## 🚀 What's Next?

Planned for v1.3 and beyond:

### Phase C: Design & UX Improvements
- Custom icons for tabs and buttons
- Better layouts and spacing
- Hover effects and visual polish
- Animated status indicators

### Phase D: Performance Boost
- Async/multi-threaded ping operations
- Faster scanning for large networks
- Result caching

### Phase E: Additional Tools
- Port Scanner
- Wake-on-LAN (WOL)
- DNS Lookup
- Subnet Calculator

### Phase F: Network Profile Manager
- Save network configuration profiles
- One-click profile switching
- DHCP and static IP support
- Essential for network admins

### Phase G: phpIPAM Integration
- Two-way sync with phpIPAM
- Browse IPAM subnets
- Auto-update on scan
- Enterprise-level integration

---

## 📚 Documentation

New documentation added in v1.2:
- `SCAN_COMPARISON_GUIDE.md` - Complete guide to scan comparison feature
- Updated `CHANGELOG_v1.2.md` - This file
- Updated `FEATURE_IMPLEMENTATION_PLAN.md` - Roadmap updates

---

## 🐛 Bug Fixes

None in this release (new features only)

---

## 🔧 Technical Improvements

- Added `ScanManager` class for scan storage and comparison
- Enhanced scan completion handler to auto-save results
- Improved UI with dynamic button states
- Better error handling in comparison logic
- Optimized JSON storage for scan data

---

## 📝 Notes for Users

### Rebuilding Required
To use the new features, you must **rebuild the application**:

```bash
python build_exe.py
# or
python build_exe_fast.py
# or
build_fast_simple.bat
```

### Testing Without Rebuilding
You can test immediately by running:
```bash
python nettools_app.py
```

### Storage Location
Scans are stored at:
- **Windows**: `C:\Users\<YourName>\.nettools\scans.json`
- **Linux**: `~/.nettools/scans.json`

You can backup this file to preserve scan history.

---

**Version**: 1.2.0  
**Release Date**: November 2024  
**Author**: freakms  
**Build**: Production-ready
