# NetTools Suite - Version 1.8.0 Changelog

**Release Date:** 2025  
**Focus:** Feature Polish & Completion

---

## 🐛 Bug Fixes

### Status Bar Overlap (Critical UI Bug)
- **Fixed:** Status bar overlapping with main content area
- **Impact:** Improved visual consistency and readability
- **Technical:** Reordered UI component creation sequence

---

## ✨ New Features

### 1. Port Scanner Export Functionality
**NEW:** Export port scan results in multiple formats

- **Formats Supported:**
  - CSV (Comma-Separated Values)
  - JSON (with metadata)
  - XML (hierarchical structure)
  - TXT (human-readable report)

- **Features:**
  - Smart format detection from file extension
  - Includes scan metadata (target, timestamp, port count)
  - Professional formatted output
  - Desktop as default save location
  - Timestamped filenames

### 2. Enhanced IPv4 Scanner Export
**IMPROVED:** Multi-format export for network scans

- **Previous:** CSV only
- **Now:** CSV, JSON, XML, and TXT formats
- **Added:**
  - Comprehensive scan statistics in exports
  - Structured metadata (CIDR, online/offline counts)
  - Professional report formatting

### 3. Network Profile Manager - Complete Implementation
**COMPLETED:** Full save and restore functionality

#### Profile Creation:
- Capture current configuration of all network interfaces
- Save DHCP/Static settings
- Preserve IP addresses, gateways, DNS servers
- Visual interface preview before saving
- Named profiles for easy identification

#### Profile Application:
- One-click restore of saved configurations
- Administrator privilege checking
- Background processing (non-blocking UI)
- Detailed success/failure reporting
- Handles multiple interfaces simultaneously
- Graceful error handling for missing interfaces

---

## 🔧 Technical Improvements

### Export System:
- Unified export architecture across tools
- Format-specific rendering methods
- Consistent file naming conventions
- XML support added to application

### Network Management:
- Threaded profile application
- Robust error handling
- Interface validation before changes
- Detailed operation logging

### Code Quality:
- Improved method organization
- Enhanced inline documentation
- Better error messages
- Consistent naming patterns

---

## 💡 User Experience Enhancements

- **Export Dialogs:** Clear format selection with file type filters
- **Feedback:** Detailed success/error messages for all operations
- **Performance:** Non-blocking network operations
- **Safety:** Confirmation dialogs before major changes
- **Flexibility:** Multiple export formats for different use cases

---

## 📦 Data Formats

### Port Scanner Exports:
```
CSV:  target,port,state,service
JSON: {scan_info: {...}, results: [...]}
XML:  <portscan><scan_info>...</scan_info><results>...</results></portscan>
TXT:  Formatted report with headers and columns
```

### Network Scanner Exports:
```
CSV:  ip,status,rtt
JSON: {scan_info: {...}, results: [...]}
XML:  <ipscan><scan_info>...</scan_info><results>...</results></ipscan>
TXT:  Formatted report with statistics
```

### Network Profiles:
```
JSON: {id, name, interfaces: [{name, config: {...}}], created}
```

---

## 🔄 Backward Compatibility

- ✅ All existing features maintained
- ✅ No breaking changes to data formats
- ✅ Keyboard shortcuts still functional (Ctrl+E)
- ✅ Previous profiles remain compatible

---

## 📋 Known Limitations

- Network Profile Manager requires Windows
- Administrator privileges needed for network changes
- Profile application requires interfaces to exist
- DNS configuration limited to first few servers

---

## 🚀 Performance

- Export operations complete in < 1 second for typical datasets
- Profile application runs in background thread
- No UI freezing during network operations
- Efficient file I/O operations

---

## 🔜 Coming in Phase 2

- Custom icons for each tool
- Enhanced button hover effects
- Improved color scheme consistency
- Additional UI polish
- phpIPAM integration (optional)

---

## 📝 Upgrade Notes

**From v1.7.0 to v1.8.0:**
1. No configuration changes required
2. Existing scans and profiles remain compatible
3. New export formats available immediately
4. Network Profile Manager now fully functional

---

## 🙏 Acknowledgments

Thanks to all users who reported the status bar overlap issue and requested the enhanced export functionality!

---

**Full Feature List:**
- ✅ IPv4 Network Scanner (with multi-format export)
- ✅ MAC Address Formatter & OUI Vendor Lookup
- ✅ Network Scan Comparison & Export
- ✅ Network Profile Manager (save/load complete)
- ✅ Port Scanner (with multi-format export)
- ✅ DNS Lookup Tool
- ✅ Subnet Calculator

**Version:** 1.8.0  
**Status:** Production Ready  
**Platform:** Windows  
**License:** Proprietary  
**Author:** freakms
