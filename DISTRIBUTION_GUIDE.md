# NetTools Suite - Distribution Guide

This guide covers how to build, test, and distribute the NetTools Suite Windows installer.

---

## Overview

The NetTools Suite uses a two-step build process:
1. **PyInstaller** → Creates standalone executable (no Python needed)
2. **Inno Setup** → Packages into professional Windows installer

---

## Build Requirements

### On the Build Machine

✅ **Python 3.8+** (only for building, not for end users)
✅ **PyInstaller 6.0+** (`pip install pyinstaller`)
✅ **Inno Setup 6** (https://jrsoftware.org/isdl.php)
✅ **All Python dependencies** (`pip install -r requirements.txt`)

### Build Environment
- Windows 10/11 (64-bit) recommended for building Windows installers
- 4+ GB RAM
- 1+ GB free disk space
- Administrator privileges

---

## Quick Build

### One-Command Build

```batch
build_installer.bat
```

This automatically:
1. ✅ Cleans previous builds
2. ✅ Bundles app with PyInstaller  
3. ✅ Creates installer with Inno Setup
4. ✅ Outputs to `installer_output/`

**Output:** `installer_output/NetTools_Setup_1.0.0.exe`

---

## Manual Build (Step-by-Step)

### Step 1: Clean Previous Builds

```batch
rmdir /s /q dist build installer_output
mkdir installer_output
```

### Step 2: Build Standalone Executable

```batch
python -m PyInstaller nettools.spec --noconfirm
```

**Verification:**
```batch
cd dist\NetTools
NetTools.exe
```

The application should launch. Test core features.

### Step 3: Create Installer

```batch
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" nettools_setup.iss
```

**Output:** `installer_output\NetTools_Setup_1.0.0.exe`

---

## What Gets Built

### Standalone Executable (`dist/NetTools/`)
- **NetTools.exe** - Main application (8-15 MB)
- **_internal/** - Python runtime & libraries
- **Total size:** ~50-70 MB uncompressed

### Windows Installer (`installer_output/`)
- **NetTools_Setup_1.0.0.exe** - Installer package
- **Compressed size:** ~20-30 MB
- **Installed size:** 60-100 MB (depending on components)

---

## Installer Features

### Component Selection

Users can choose from **4 installation types**:

1. **Full** - All tools (~80 MB)
2. **Standard** - Common tools (~50 MB)
3. **Minimal** - Core only (~40 MB)
4. **Custom** - User selects individual tools

### Selectable Components

**Always Installed:**
- Core application
- IPv4 Scanner

**Optional:**
- Port Scanner
- Traceroute
- Live Ping Monitor
- Bandwidth Testing (requires manual iperf3 install)
- DNS Lookup
- Subnet Calculator
- MAC Formatter
- Scan Comparison
- Network Profiles
- PAN-OS Generator
- phpIPAM Integration

### External Dependencies

**iperf3 for Bandwidth Testing:**
- NOT bundled with installer
- User installs separately
- Clear instructions shown during installation
- Complete guide included in docs folder

---

## Testing the Build

### Pre-Distribution Testing Checklist

#### Test the Executable (Before Packaging)

```batch
cd dist\NetTools
NetTools.exe
```

- [ ] Application launches without errors
- [ ] GUI renders correctly
- [ ] Sidebar navigation works
- [ ] Tools load properly
- [ ] No console window appears

#### Test the Installer

**On a Clean Windows Machine (VM recommended):**

1. **Installation Tests**
   - [ ] Installer launches and shows wizard
   - [ ] Component selection works
   - [ ] All installation types complete successfully
   - [ ] iperf3 information page shows (if bandwidth testing selected)
   - [ ] Desktop shortcut created (if selected)
   - [ ] Start menu entries created

2. **Application Tests**
   - [ ] Launch from Start Menu
   - [ ] Launch from Desktop shortcut
   - [ ] IPv4 Scanner works
   - [ ] Each selected tool loads
   - [ ] Bandwidth test shows iperf3 instructions if not installed

3. **Uninstallation Tests**
   - [ ] Uninstaller runs successfully
   - [ ] All files removed
   - [ ] Start menu entries removed
   - [ ] Desktop shortcut removed (if was created)

---

## Distribution

### What to Distribute

**Installer File:**
```
NetTools_Setup_1.0.0.exe
```

**Minimum User Requirements:**
- Windows 10 or 11 (64-bit)
- 100-200 MB disk space
- Administrator rights (for installation)
- NO Python required

### Distribution Channels

**Direct Download:**
- Host on your website
- Provide download link
- Include SHA-256 checksum for verification

**Example:**
```
File: NetTools_Setup_1.0.0.exe
Size: ~25 MB
SHA256: [generate with certUtil -hashfile filename SHA256]
```

**Enterprise Deployment:**
- Silent install supported: `/SILENT` or `/VERYSILENT`
- Component selection: `/COMPONENTS="core,scanning,utilities"`
- Custom path: `/DIR="C:\MyPath\NetTools"`

---

## User Instructions

### For End Users

**Installation:**
1. Download `NetTools_Setup_1.0.0.exe`
2. Right-click → Run as Administrator
3. Follow installation wizard
4. Select desired components
5. Launch from Start Menu

**If Bandwidth Testing Selected:**
1. Read iperf3 installation instructions during setup
2. Download iperf3 from: https://iperf.fr/iperf-download.php
3. Follow guide in: `C:\Program Files\NetTools Suite\docs\IPERF3_INSTALLATION_GUIDE.md`
4. Restart NetTools application

---

## Customization for Distribution

### Update Version Number

Edit `nettools_setup.iss`:
```iss
#define MyAppVersion "1.0.0"  ← Change this
```

### Update Company Information

Edit `nettools_setup.iss`:
```iss
#define MyAppPublisher "Your Company Name"
#define MyAppURL "https://yourwebsite.com"
```

### Add Application Icon

1. Create or obtain `nettools.ico` (256x256 recommended)
2. Place in `/app/` directory
3. Edit `nettools.spec`:
   ```python
   icon='nettools.ico'
   ```
4. Edit `nettools_setup.iss`:
   ```iss
   SetupIconFile=nettools.ico
   ```
5. Rebuild

### Code Signing (Recommended for Distribution)

For trusted distribution, sign your executable:

1. Obtain a code signing certificate
2. Sign the installer:
   ```batch
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com NetTools_Setup_1.0.0.exe
   ```

Benefits:
- ✅ No "Unknown Publisher" warning
- ✅ Builds trust with users
- ✅ Prevents tampering

---

## Troubleshooting Build Issues

### PyInstaller Fails

**Error: Module not found**
- Add to `hiddenimports` in `nettools.spec`
- Verify module is in `requirements.txt`

**Error: Import failed**
- Check Python version compatibility
- Ensure all dependencies installed

### Inno Setup Fails

**Error: ISCC.exe not found**
- Install Inno Setup from official website
- Update path in `build_installer.bat` line 50

**Error: Source file not found**
- Ensure PyInstaller build succeeded
- Check `dist/NetTools/` exists
- Verify paths in `.iss` file

### Large Executable Size

If exe is >100 MB:
1. Exclude unnecessary modules in `nettools.spec`:
   ```python
   excludes=['pandas', 'scipy', 'torch']
   ```
2. Install UPX for better compression
3. Remove test/debug files

### Runtime Errors in Built Executable

**Application won't start:**
1. Run from command line to see errors
2. Check all dependencies bundled
3. Verify `_internal` folder present

**Missing features:**
1. Check data files in `nettools.spec` `datas` section
2. Ensure `tools/` folder copied

---

## Advanced Build Options

### Debug Build

For troubleshooting:
```python
# In nettools.spec
console=True  # Shows console window with debug output
debug=True    # Additional debug info
```

### Optimize Build Size

```python
# In nettools.spec
excludes=[
    'torch', 'tensorflow',  # ML libraries not needed
    'numpy.testing',        # Test utilities
    'pytest', 'unittest',   # Testing frameworks
]
```

### Multiple Architecture Support

Currently builds for x64 only. To support x86:
```iss
; In nettools_setup.iss
ArchitecturesAllowed=x64 x86
```

---

## Versioning Strategy

### Recommended Versioning: Semantic Versioning

**Format:** MAJOR.MINOR.PATCH (e.g., 1.0.0)

- **MAJOR**: Breaking changes, major new features
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, small improvements

**Examples:**
- 1.0.0 → Initial release
- 1.0.1 → Bug fixes
- 1.1.0 → New features (Live Ping Monitor)
- 2.0.0 → Major redesign

### Update Process

1. Update version in `nettools_setup.iss`
2. Update version in `nettools_app.py` (if displayed)
3. Create changelog
4. Rebuild
5. Test thoroughly
6. Distribute

---

## Support Documentation for Users

Include in distribution:
- ✅ `README_INSTALLER.md` - User installation guide
- ✅ `IPERF3_INSTALLATION_GUIDE.md` - iperf3 setup instructions
- ✅ `LICENSE.txt` - License information
- ✅ `USAGE_GUIDE.md` - How to use the tools

These are automatically included in the installer in the `docs/` folder.

---

## Build Checklist

Before distributing a new version:

- [ ] Version number updated in `.iss` file
- [ ] All features tested in development
- [ ] Linting/code quality checks passed
- [ ] `requirements.txt` up to date
- [ ] Build completes without errors
- [ ] Executable tested on development machine
- [ ] Installer tested on clean Windows VM
- [ ] All installation types tested
- [ ] Component selection verified
- [ ] iperf3 instructions display correctly
- [ ] Shortcuts created properly
- [ ] Documentation files included
- [ ] Uninstaller works correctly
- [ ] Changelog updated
- [ ] No hardcoded paths or credentials
- [ ] (Optional) Executable is code-signed

---

## Maintenance

### Regular Updates
- Keep dependencies updated (`pip list --outdated`)
- Update PyInstaller to latest stable version
- Test on new Windows versions
- Monitor for security vulnerabilities

### User Feedback
- Collect bug reports
- Track feature requests
- Monitor common issues
- Improve documentation based on questions

---

## Summary

**Build Process:**
1. Run `build_installer.bat` on Windows
2. Test `dist/NetTools/NetTools.exe`
3. Test `installer_output/NetTools_Setup_1.0.0.exe` on clean system
4. Distribute installer file

**User Experience:**
1. User downloads installer (~25 MB)
2. User runs installer and selects components
3. If bandwidth testing selected, user sees iperf3 instructions
4. User launches NetTools from Start Menu
5. Application works without Python installed

**External Dependencies:**
- iperf3 for Bandwidth Testing (user installs separately)
- All other functionality works out-of-the-box

---

**Happy Building and Distributing! 🚀**
