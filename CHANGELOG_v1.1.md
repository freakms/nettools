# Changelog - NetTools Suite v1.1

## Version 1.1.0 (November 2024)

### 🎉 New Features

#### 1. OUI Vendor Lookup
- **Automatic manufacturer identification** from MAC addresses
- Database with **940+ vendor entries** including:
  - Network equipment manufacturers (Cisco, Huawei, Dell, HP, Juniper)
  - Computer manufacturers (Apple, Microsoft, Intel, AMD)
  - Mobile device manufacturers (Samsung, Xiaomi)
  - IoT and smart device manufacturers
- Real-time lookup as you type MAC addresses
- Supports all MAC address formats (colon, dash, plain, Cisco)
- Visual indicator with 🏢 icon and green color
- Shows "Unknown Vendor" for unrecognized OUIs

#### 2. History & Recent Items (v1.0.1)
- **CIDR History**: Quick access to recently scanned networks
- **MAC History**: Quick access to recently formatted MAC addresses
- Clock icon (⏱) buttons next to input fields
- Stores up to 10 most recent items per category
- Persistent storage across app sessions
- Timestamps for each history item
- One-click to reuse previous inputs

### 🔧 Technical Improvements
- Added `oui_database.json` with comprehensive manufacturer database
- Enhanced MAC formatter with real-time vendor lookup
- Improved user feedback with color-coded vendor display
- Optimized database loading on startup

### 📚 Documentation
- Added `OUI_VENDOR_LOOKUP_INFO.md` - Complete feature documentation
- Updated `REBUILD_INSTRUCTIONS.txt` - Build guide for new features
- Updated `FEATURE_IMPLEMENTATION_PLAN.md` - Roadmap updates

### 🐛 Bug Fixes
- None in this release (new features only)

---

## Version 1.0.1 (November 2024)

### 🎉 New Features
- History & Recent Items feature
- Persistent history storage

---

## Version 1.0.0 (Initial Release)

### Features
- IPv4 Network Scanner with CIDR support
- MAC Address Formatter with multiple output formats
- Switch command generation (EXTREME, Huawei, Dell)
- Dark/Light theme support
- Modern customtkinter UI
- CSV export functionality
- Scalable interface
- Two build options (single-file and directory-based)

---

## Upcoming Features

See `FEATURE_IMPLEMENTATION_PLAN.md` for the complete roadmap:
- ✅ Phase A: History & OUI Vendor Lookup (DONE)
- 🔄 Phase B: Scan Comparison & Export
- 📋 Phase C: Design & UX Improvements
- 📋 Phase D: Performance Boost
- 📋 Phase E: Additional Tools (Port Scanner, WOL, DNS Lookup)
- 📋 Phase F: Network Profile Changer
- 📋 Phase G: phpIPAM Integration
