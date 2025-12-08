# NetTools Suite - Build Installer Guide

This guide explains how to create a professional Windows installer for NetTools Suite with optional component selection.

---

## Overview

The build process creates:
1. **Standalone Executable** - Bundles Python + all dependencies
2. **Windows Installer** - Professional setup with component selection
3. **Optional Components** - Users choose which tools to install

---

## Prerequisites

### Required Software

1. **Python 3.8+**
   - Download: https://www.python.org/downloads/
   - Make sure "Add to PATH" is checked during installation

2. **PyInstaller**
   ```powershell
   pip install pyinstaller
   ```

3. **Inno Setup 6** (for installer creation)
   - Download: https://jrsoftware.org/isdl.php
   - Install to default location: `C:\Program Files (x86)\Inno Setup 6\`

4. **All Python Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

### Optional (for advanced features)

5. **UPX** (compression tool - reduces exe size)
   - Download: https://upx.github.io/
   - Add to PATH

**Note:** iperf3 is NOT bundled with the installer. Users install it separately.

---

## Build Process

### Method 1: Automated Build (Recommended)

Simply run the build script:

```cmd
build_installer.bat
```

This will:
1. Clean previous builds
2. Build executable with PyInstaller
3. Create installer with Inno Setup
4. Output installer to `installer_output/`

### Method 2: Manual Build

#### Step 1: Build Executable

```powershell
# Clean previous builds
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue

# Build with PyInstaller
pyinstaller nettools.spec
```

**Output:** `dist/NetTools/NetTools.exe`

#### Step 2: Create Installer

```powershell
# Compile Inno Setup script
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" nettools_setup.iss
```

**Output:** `installer_output/NetTools_Setup_1.0.0.exe`

---

## Installer Components

Users can choose which tools to install:

### Installation Types

1. **Full Installation** (All Tools)
   - All features enabled
   - ~60-80 MB

2. **Standard Installation** (Most Common)
   - Core scanning and utility tools
   - Excludes advanced features
   - ~40-50 MB

3. **Minimal Installation** (Core Only)
   - IPv4 Scanner only
   - ~30-40 MB

4. **Custom Installation**
   - User selects specific tools
   - Variable size

### Component Categories

**🔍 Network Scanning Tools:**
- IPv4 Scanner (always included)
- Port Scanner
- Traceroute & Pathping
- Live Ping Monitor
- Bandwidth Testing

**🛠 Network Utilities:**
- DNS Lookup
- Subnet Calculator
- MAC Address Formatter

**📊 Management Tools:**
- Scan Comparison
- Network Profiles

**🛡 Advanced Tools:**
- PAN-OS CLI Generator
- phpIPAM Integration

---

## External Dependencies - iperf3

**Important:** iperf3 is NOT bundled with the installer to keep size small and avoid licensing issues.

### User Installation Process

When users select the "Bandwidth Testing" component during installation:
1. They will see an information page with iperf3 download instructions
2. Users must manually download and install iperf3 from: https://iperf.fr/iperf-download.php
3. Users must add iperf3 to their Windows PATH
4. The application will detect if iperf3 is missing and show setup instructions

### Installation Guide

A comprehensive guide (`IPERF3_INSTALLATION_GUIDE.md`) is included in the installer that covers:
- Step-by-step download instructions
- PATH configuration
- Verification steps
- Troubleshooting

---

## Customization

### Modify Installation Types

Edit `nettools_setup.iss`:

```iss
[Types]
Name: "full"; Description: "Full Installation"
Name: "mytype"; Description: "My Custom Type"
```

### Add/Remove Components

```iss
[Components]
Name: "mycomponent"; Description: "My Tool"; Types: full custom
```

### Change App Icon

1. Create/obtain `network_icon.ico`
2. Place in root directory
3. Rebuild

### Modify App Information

Edit in `nettools_setup.iss`:
```iss
#define MyAppVersion "2.0.0"
#define MyAppPublisher "Your Company Name"
```

---

## Bundle iperf3

To include iperf3 in the installer:

### Step 1: Download iperf3
1. Visit: https://iperf.fr/iperf-download.php
2. Download Windows binary
3. Extract `iperf3.exe`

### Step 2: Place in External Folder
```
/app/external/iperf3.exe
```

### Step 3: Rebuild
The build script will automatically include it.

---

## Troubleshooting

### PyInstaller Issues

**Problem:** Missing modules
```
ModuleNotFoundError: No module named 'xyz'
```

**Solution:** Add to `hiddenimports` in `nettools.spec`:
```python
hiddenimports=[
    'xyz',
    'other_module',
]
```

**Problem:** Large exe size (>200 MB)

**Solutions:**
1. Install UPX and enable compression
2. Exclude unnecessary modules in spec file
3. Use `--exclude-module` for unused packages

### Inno Setup Issues

**Problem:** ISCC.exe not found

**Solution:** 
- Install Inno Setup from https://jrsoftware.org/isdl.php
- Or update path in `build_installer.bat`

**Problem:** Files not found

**Solution:**
- Ensure PyInstaller build completed successfully
- Check `dist/NetTools/` exists
- Verify file paths in `.iss` file

### Runtime Issues

**Problem:** Application crashes on startup

**Solutions:**
1. Test the exe directly: `dist/NetTools/NetTools.exe`
2. Check console output for errors
3. Run from command prompt to see error messages

**Problem:** Missing DLL errors

**Solution:**
- Ensure all dependencies in requirements.txt
- Rebuild with `--hidden-import` for missing modules

---

## Testing the Installer

### Before Distribution

1. **Test on Clean System**
   - Use VM or clean Windows installation
   - Install and test all components
   - Verify uninstall works

2. **Test Component Selection**
   - Try each installation type
   - Verify selected components work
   - Test optional components

3. **Test Shortcuts**
   - Start menu shortcut
   - Desktop icon
   - Quick launch

4. **Test Updates**
   - Install old version
   - Install new version
   - Verify upgrade works

---

## Distribution

### Installer Details

**File:** `NetTools_Setup_1.0.0.exe`
**Size:** ~50-80 MB (depends on components)
**Requirements:** Windows 10 or later (64-bit)
**Installation:** Administrator rights recommended

### What Users Get

✅ **No Python Required** - Everything bundled
✅ **No Dependencies** - All libraries included
✅ **Component Selection** - Choose tools to install
✅ **Start Menu Integration** - Easy access
✅ **Uninstaller** - Clean removal
✅ **Documentation** - Included in install

### System Requirements

- **OS:** Windows 10/11 (64-bit)
- **RAM:** 2 GB minimum, 4 GB recommended
- **Disk:** 100-200 MB (depends on components)
- **Network:** Required for some features

---

## Updating the Application

### Version Updates

1. Edit `nettools_setup.iss`:
   ```iss
   #define MyAppVersion "1.1.0"
   ```

2. Rebuild installer

3. Inno Setup handles upgrades automatically

### Adding New Features

1. Add code to application
2. Test locally
3. Add to components in `.iss` file
4. Rebuild

---

## Advanced Configuration

### Code Signing (Optional)

For trusted distribution:

1. Obtain code signing certificate
2. Add to Inno Setup:
   ```iss
   SignTool=signtool sign /f "cert.pfx" /p "password" $f
   ```

### Silent Installation

Users can install silently:
```cmd
NetTools_Setup_1.0.0.exe /SILENT
NetTools_Setup_1.0.0.exe /VERYSILENT /COMPONENTS="core,scanning"
```

### Custom Installation Path

```cmd
NetTools_Setup_1.0.0.exe /DIR="C:\MyTools\NetTools"
```

---

## Build Checklist

Before releasing:

- [ ] Version number updated
- [ ] All features tested
- [ ] Documentation included
- [ ] Icon looks good
- [ ] Installer tested on clean system
- [ ] All components selectable
- [ ] Shortcuts work
- [ ] Uninstaller works
- [ ] File size acceptable
- [ ] README updated

---

## Quick Reference

### Build Commands

```powershell
# Full automated build
.\build_installer.bat

# Just build exe
pyinstaller nettools.spec

# Just create installer
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" nettools_setup.iss

# Clean everything
Remove-Item -Recurse -Force dist, build, installer_output
```

### File Locations

- **Source:** `nettools_app.py`
- **Spec:** `nettools.spec`
- **Setup Script:** `nettools_setup.iss`
- **Build Script:** `build_installer.bat`
- **Output Exe:** `dist/NetTools/NetTools.exe`
- **Output Installer:** `installer_output/NetTools_Setup_1.0.0.exe`

---

## Support

If you encounter issues:

1. Check this guide
2. Review error messages
3. Test individual components
4. Check PyInstaller docs: https://pyinstaller.org/
5. Check Inno Setup docs: https://jrsoftware.org/ishelp/

---

## Next Steps

After building:

1. **Test thoroughly** on different systems
2. **Create documentation** for end users
3. **Setup distribution** (website, download link)
4. **Plan updates** (versioning strategy)
5. **Consider auto-updates** (for future versions)

---

Happy Building! 🚀
