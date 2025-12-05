# NetTools Suite - Installation Guide

## Welcome to NetTools Suite!

A comprehensive network utility toolkit for Windows with professional-grade tools for network administrators, IT professionals, and power users.

---

## System Requirements

- **Operating System:** Windows 10 or Windows 11 (64-bit)
- **RAM:** 2 GB minimum, 4 GB recommended
- **Disk Space:** 100-200 MB (depends on selected components)
- **Administrator Rights:** Recommended for full functionality

---

## Installation

### Quick Start

1. **Download** the installer: `NetTools_Setup_x.x.x.exe`
2. **Run** the installer (right-click → Run as Administrator recommended)
3. **Select Components** - Choose which tools you need
4. **Install** - Follow the wizard
5. **Launch** - Find NetTools in your Start Menu

### Installation Types

**Full Installation (Recommended)**
- All tools and features
- Best for network administrators
- ~80 MB

**Standard Installation**
- Most commonly used tools
- Good for general use
- ~50 MB

**Minimal Installation**
- Core scanning tools only
- Smallest footprint
- ~40 MB

**Custom Installation**
- Pick exactly what you need
- Variable size

---

## What's Included

### 🔍 Network Scanning Tools

**IPv4 Scanner** (Core - Always Included)
- Scan networks for active hosts
- Hostname resolution
- Quick CIDR scanning
- Export results

**Port Scanner**
- Scan for open ports
- Service detection
- Multiple port ranges
- Fast scanning

**Traceroute**
- Trace network path
- Hop-by-hop analysis
- Latency tracking

**Live Ping Monitor** 
- Real-time ping monitoring
- Multiple hosts simultaneously
- Visual graphs
- Color-coded status
- Export data

**Bandwidth Testing**
- Upload/download speed tests
- Uses iperf3
- Detailed statistics
- Requires iperf3 installation

### 🛠 Network Utilities

**DNS Lookup**
- Forward and reverse DNS
- Multiple record types
- Batch lookups

**Subnet Calculator**
- CIDR calculations
- IP range planning
- Network info

**MAC Address Formatter**
- Format MAC addresses
- Vendor lookup (OUI database)
- Multiple formats

### 📊 Management Tools

**Scan Comparison**
- Compare scan results
- Track changes over time
- Network monitoring

**Network Profiles**
- Save network configurations
- Quick profile switching
- Manage settings

### 🛡 Advanced Professional Tools

**PAN-OS CLI Generator**
- Generate firewall configs
- Address objects
- NAT rules
- Security policies
- Schedule objects
- Application filters
- URL categories
- 8 different generators

**phpIPAM Integration**
- IP address management
- IPAM integration
- Network documentation

---

## Component Selection During Installation

### What to Choose?

**For Basic Network Troubleshooting:**
- ✅ IPv4 Scanner
- ✅ Port Scanner
- ✅ DNS Lookup
- ✅ Traceroute

**For Network Monitoring:**
- ✅ IPv4 Scanner
- ✅ Live Ping Monitor
- ✅ Bandwidth Testing (+ iperf3)
- ✅ Scan Comparison

**For Network Administration:**
- ✅ All Network Scanning
- ✅ All Network Utilities
- ✅ Network Profiles

**For Firewall Management:**
- ✅ IPv4 Scanner
- ✅ PAN-OS CLI Generator
- ✅ Subnet Calculator

**For Maximum Capability:**
- ✅ Full Installation (everything)

---

## First Launch

After installation:

1. **Find NetTools** in Start Menu or Desktop
2. **Launch** the application
3. **Explore** the categorized tools in the sidebar
4. **Start** with IPv4 Scanner for a quick test

---

## Optional: iperf3 Installation

For **Bandwidth Testing** feature:

### Option 1: Install During Setup
- Check "Install iperf3" during component selection
- Automatically added to system PATH

### Option 2: Install Later
The app will show installation instructions if iperf3 is not found.

**Quick Install (Chocolatey):**
```powershell
choco install iperf3
```

**Or download manually:**
https://iperf.fr/iperf-download.php

---

## Navigation

The application uses a **category-based sidebar**:

📊 **Quick Access**
- Live Ping Monitor (one-click)

🔍 **Network Scanning**
- IPv4 Scanner
- Port Scanner
- Traceroute
- Bandwidth Test

🛠 **Network Tools**
- DNS Lookup
- Subnet Calculator
- MAC Formatter

📊 **Management**
- Scan Comparison
- Network Profiles

🛡 **Advanced**
- PAN-OS Generator
- phpIPAM

---

## Features Highlight

### Live Ping Monitor
- Monitor multiple hosts in real-time
- Table view with inline graphs
- Color-coded status (Green/Yellow/Red)
- Export results
- Pause/Resume monitoring

### PAN-OS Generator
- 8 different CLI generators
- Copy to clipboard
- Save commands
- Bulk operations
- Professional firewall configs

### IPv4 Scanner
- Fast network scanning
- Hostname resolution
- Export to CSV/JSON
- Scan history
- Profile management

---

## Shortcuts

After installation, you'll find:

- **Start Menu:** NetTools Suite
- **Desktop:** NetTools icon (if selected)
- **Quick Launch:** Quick access (if selected)
- **Documentation:** In install folder\docs\

---

## Updating

To update to a newer version:

1. Download new installer
2. Run installer (automatically detects existing installation)
3. Choose "Update" or "Reinstall"
4. Your settings are preserved

---

## Uninstalling

### Via Control Panel
1. Open **Settings** → **Apps**
2. Find **NetTools Suite**
3. Click **Uninstall**

### Via Installer
1. Run installer again
2. Choose **Remove**

### Via Start Menu
1. Find **NetTools Suite** folder
2. Click **Uninstall**

---

## Troubleshooting

### Application Won't Start

**Solution:**
- Right-click → Run as Administrator
- Check Windows Event Viewer for errors
- Reinstall application

### Missing Features

**Solution:**
- Run installer again
- Choose "Modify"
- Select missing components

### iperf3 Not Working

**Solution:**
- Install iperf3 separately
- Check PATH environment variable
- See Bandwidth Test page for instructions

### Firewall Blocking

**Solution:**
- Add NetTools to Windows Firewall exceptions
- Allow network scanning features

---

## Getting Help

### Documentation
- **Installation Guide:** This file
- **Feature Guides:** In install folder\docs\
- **Online Help:** [Your Website]

### Support
- Email: support@yourcompany.com
- Website: https://yourwebsite.com
- Issues: [GitHub/Support Page]

---

## Privacy & Security

- **No Telemetry:** NetTools doesn't send usage data
- **No Internet Required:** Most features work offline
- **No Account Needed:** Use immediately after install
- **Local Data:** All data stays on your computer

---

## License

NetTools Suite is provided under the MIT License.
See LICENSE.txt for full terms.

---

## Credits

**Developed by:** Your Company
**Version:** 1.0.0
**Website:** https://yourwebsite.com

**Third-Party Components:**
- Python & libraries
- customtkinter (UI framework)
- pythonping (network utilities)
- matplotlib (graphing)
- iperf3 (bandwidth testing - optional)

---

## System Integration

After installation, NetTools integrates with Windows:

- ✅ Start Menu entry
- ✅ Optional Desktop shortcut
- ✅ Optional Quick Launch
- ✅ File associations (for config files)
- ✅ PATH integration (for iperf3 if selected)

---

## Tips for Best Experience

1. **Run as Administrator** for full functionality
2. **Install iperf3** if you need bandwidth testing
3. **Try Live Monitor** for real-time network monitoring
4. **Use Profiles** to save your network configurations
5. **Explore PAN-OS Generator** if you manage firewalls

---

## What's New in Version 1.0.0

🎉 **Initial Release**
- Complete network toolkit
- 10+ professional tools
- Modern category-based UI
- Live ping monitoring
- PAN-OS configuration generator
- Bandwidth testing support
- Component-based installation

---

## Thank You!

Thank you for choosing NetTools Suite for your network administration needs.

Happy Networking! 🚀

---

**NetTools Suite** - Professional Network Utilities for Windows
