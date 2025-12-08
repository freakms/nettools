# NetTools Suite - Installer

Welcome to NetTools Suite! This installer allows you to choose which network tools you want to install on your system.

---

## Installation Options

### Installation Types

1. **Full Installation**
   - All network tools and features
   - Professional-grade advanced tools
   - Recommended for network administrators

2. **Standard Installation**
   - Most commonly used tools
   - Excludes advanced professional features
   - Good for general network management

3. **Minimal Installation**
   - Core IPv4 scanning only
   - Smallest installation footprint
   - Good for basic network discovery

4. **Custom Installation**
   - Choose specific tools you need
   - Flexible component selection
   - Optimize for your use case

---

## Available Components

### Network Scanning Tools
- **IPv4 Scanner** - Discover devices on your network (always included)
- **Port Scanner** - Scan ports on network devices
- **Traceroute & Pathping** - Trace network routes
- **Live Ping Monitor** - Real-time ping monitoring with graphs
- **Bandwidth Testing** - Network speed testing ⚠️ *Requires manual iperf3 installation*

### Network Utilities
- **DNS Lookup** - Query DNS records
- **Subnet Calculator** - Calculate subnet information
- **MAC Address Formatter** - Format and validate MAC addresses

### Management Tools
- **Scan Comparison** - Compare network scans
- **Network Profiles** - Save and manage network configurations

### Advanced Professional Tools
- **PAN-OS CLI Generator** - Generate Palo Alto firewall configurations
- **phpIPAM Integration** - Connect to phpIPAM servers

---

## System Requirements

- **Operating System**: Windows 10 or later (64-bit)
- **Memory**: 2 GB RAM minimum, 4 GB recommended
- **Disk Space**: 100-200 MB (depends on selected components)
- **Python**: NOT REQUIRED - Application is standalone
- **Privileges**: Administrator rights recommended for installation

---

## External Dependencies

### ⚠️ iperf3 for Bandwidth Testing

The **Bandwidth Testing** tool requires **iperf3** to be installed separately on your system.

**If you select Bandwidth Testing:**
- You will see an information page during installation with detailed instructions
- Download link: https://iperf.fr/iperf-download.php
- Complete installation guide included in documentation folder
- The application will guide you if iperf3 is not found

**Why separate?**
- Keeps installer size small
- You may already have iperf3 installed
- Allows you to use your preferred iperf3 version

**The application works without iperf3** - only the Bandwidth Testing feature requires it.

---

## Getting Started

### After Installation

1. **Launch the Application**
   - Use the Start Menu shortcut: "NetTools Suite"
   - Or use the Desktop icon (if you selected this option)

2. **First Time Setup**
   - No additional configuration needed for core features
   - All selected tools are ready to use immediately
   - Python is NOT required on your system

3. **If You Selected Bandwidth Testing**
   - Follow the iperf3 installation guide in the docs folder
   - The application will show instructions if iperf3 is missing
   - All other tools work independently

---

## Documentation

Documentation is installed to:
```
C:\Program Files\NetTools Suite\docs\
```

Available guides:
- **USAGE_GUIDE.md** - How to use each tool
- **IPERF3_INSTALLATION_GUIDE.md** - Complete iperf3 setup guide
- **PROJECT_OVERVIEW.md** - Feature descriptions
- **START_HERE.md** - Quick start guide

---

## Uninstallation

To remove NetTools Suite:

**Method 1:**
1. Open Windows Settings
2. Go to Apps & Features
3. Find "NetTools Suite"
4. Click Uninstall

**Method 2:**
- Use "Uninstall NetTools Suite" from the Start Menu

All application files and shortcuts will be removed.

---

## Support & Updates

### Getting Help
- Check the included documentation in the `docs` folder
- Review the built-in tooltips in the application
- Each tool has contextual help text

### Version Information
This installer contains **NetTools Suite v1.0.0**

---

## Privacy & Data

- ✅ **No data collection** - This application does not send any data externally
- ✅ **Local operation** - All processing happens on your machine
- ✅ **Network access** - Only used for network tools (scanning, testing, etc.)
- ✅ **No telemetry** - No usage tracking or analytics
- ✅ **No registration** - No accounts or sign-up required

Your network scans and data stay on your computer.

---

## What's Included

This is a **standalone application**:
- ✅ Python runtime bundled
- ✅ All dependencies included
- ✅ No external installations needed (except iperf3 for bandwidth testing)
- ✅ Works offline (for local network tools)
- ✅ No subscription or license key required

---

## License

See LICENSE.txt in the installation folder for complete license information.

---

## Troubleshooting

### Application won't start
- Try running as Administrator
- Check Windows Event Viewer for errors
- Reinstall with "Full Installation" option

### Bandwidth Testing not working
- Install iperf3 following the guide in docs folder
- Verify iperf3 is in your Windows PATH
- Restart the application after installing iperf3

### Tools not showing up
- Check which installation type you selected
- Reinstall with "Custom" and select specific components
- "Minimal" installation only includes IPv4 Scanner

---

Thank you for choosing NetTools Suite! 🚀