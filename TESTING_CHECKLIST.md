# NetTools Suite - Testing Checklist

## Pre-Build Testing (Test the Python Application)

Before building the installer, test all features to ensure everything works:

### 🔍 Network Scanning Tools

#### IPv4 Scanner
- [ ] Scan a network (e.g., 192.168.1.0/24)
- [ ] Scan with hostname (e.g., google.com)
- [ ] Export results to CSV
- [ ] Save to scan history
- [ ] Import IP list
- [ ] Profile management works

#### Port Scanner
- [ ] Scan common ports
- [ ] Scan custom port range
- [ ] Multiple hosts scan
- [ ] Results display correctly

#### Traceroute
- [ ] Trace to external host (e.g., 8.8.8.8)
- [ ] View hop details
- [ ] Latency information shown

#### Live Ping Monitor
- [ ] Open Live Monitor window
- [ ] Add multiple hosts (e.g., 8.8.8.8, google.com, 1.1.1.1)
- [ ] Start monitoring
- [ ] Check color-coded status bars
- [ ] Verify graphs update in real-time
- [ ] Pause/Resume works
- [ ] Export data
- [ ] Stop monitoring

#### Bandwidth Testing
- [ ] Page loads (shows iperf3 install instructions if not installed)
- [ ] If iperf3 installed: Run upload test
- [ ] If iperf3 installed: Run download test
- [ ] Results display correctly

### 🛠 Network Utilities

#### DNS Lookup
- [ ] Forward lookup (hostname → IP)
- [ ] Reverse lookup (IP → hostname)
- [ ] Multiple record types (A, AAAA, MX, etc.)

#### Subnet Calculator
- [ ] Calculate subnet info
- [ ] CIDR notation works
- [ ] Results accurate

#### MAC Formatter
- [ ] Format MAC addresses
- [ ] OUI lookup works
- [ ] Multiple format outputs

### 📊 Management Tools

#### Scan Comparison
- [ ] Compare two scans
- [ ] Show differences
- [ ] Export comparison

#### Network Profiles
- [ ] Create new profile
- [ ] Save profile
- [ ] Load profile
- [ ] Delete profile

### 🛡 Advanced Tools

#### PAN-OS Generator
Test all tabs:
- [ ] Name Generator: Generate names
- [ ] Address Objects: Create address objects
- [ ] Groups: Create address groups (test "shared" vsys)
- [ ] NAT Rules: Generate NAT rule
- [ ] Security Policies: Generate policy rule
- [ ] Schedule Objects: Create schedule
- [ ] App Filter: Create application filter
- [ ] URL Category: Create URL category
- [ ] Commands appear in output panel
- [ ] Copy commands works
- [ ] Clear commands works

#### phpIPAM
- [ ] Connection settings page loads
- [ ] (If configured) API connection works

### 📊 Quick Access & Navigation

- [ ] Live Ping Monitor button in sidebar works
- [ ] All category sections visible
- [ ] Navigation between pages smooth
- [ ] No crashes when switching pages

### 🎨 UI/UX

- [ ] Application starts without errors
- [ ] All fonts render correctly
- [ ] Color scheme consistent
- [ ] Buttons respond to clicks
- [ ] Tooltips work (if any)
- [ ] Window resizes properly
- [ ] Theme toggle works (if implemented)

---

## Issues Found During Testing

Document any issues here:

| Issue | Location | Severity | Status |
|-------|----------|----------|--------|
|       |          |          |        |

---

## Build Process Testing

### Prerequisites Check
- [ ] Python 3.8+ installed
- [ ] PyInstaller installed (`pip show pyinstaller`)
- [ ] All requirements installed (`pip install -r requirements.txt`)
- [ ] Inno Setup installed (if creating installer)

### Build the Executable

1. **Clean previous builds:**
   ```cmd
   rmdir /s /q dist
   rmdir /s /q build
   ```

2. **Build with PyInstaller:**
   ```cmd
   pyinstaller nettools.spec
   ```

3. **Test the executable:**
   - Navigate to `dist\NetTools\`
   - Run `NetTools.exe`
   - Test all features again
   - Check for errors

### Build Issues

- [ ] PyInstaller completes without errors
- [ ] Executable file created
- [ ] Executable runs without errors
- [ ] All features work in compiled version
- [ ] No missing DLL errors
- [ ] File size reasonable (<200 MB)

---

## Installer Testing

### Build the Installer

1. **Ensure executable is built**
2. **Run build script:**
   ```cmd
   build_installer.bat
   ```
3. **Check output:**
   - Installer created in `installer_output/`
   - File size reasonable

### Installation Testing (Use a VM or Clean System)

#### First-Time Installation

- [ ] Installer runs
- [ ] Welcome screen appears
- [ ] License agreement shown
- [ ] Component selection screen works
- [ ] Installation types visible
- [ ] Progress bar shows
- [ ] Installation completes
- [ ] Finish screen offers "Launch"

#### Component Selection Testing

Test each installation type:

**Full Installation:**
- [ ] All components selected by default
- [ ] Installation completes
- [ ] All tools accessible in app

**Standard Installation:**
- [ ] Correct components selected
- [ ] Installation completes
- [ ] Only selected tools available

**Minimal Installation:**
- [ ] Only core components selected
- [ ] Installation completes
- [ ] Only IPv4 Scanner available

**Custom Installation:**
- [ ] Can select/deselect individual components
- [ ] Selections respected
- [ ] Only selected tools available

#### Post-Installation Checks

- [ ] Start Menu shortcut works
- [ ] Desktop icon works (if selected)
- [ ] Application launches
- [ ] All selected features work
- [ ] Documentation accessible
- [ ] iperf3 in PATH (if selected)

#### Update Installation

- [ ] Install old version first
- [ ] Run new installer
- [ ] Update option appears
- [ ] Update completes
- [ ] Settings preserved
- [ ] New features available

#### Uninstallation

- [ ] Uninstaller accessible from Control Panel
- [ ] Uninstaller runs
- [ ] All files removed
- [ ] Start Menu entry removed
- [ ] Desktop icon removed (if created)
- [ ] No leftover files in Program Files

---

## Compatibility Testing

Test on different Windows versions:

- [ ] Windows 10 (64-bit)
- [ ] Windows 11 (64-bit)

---

## Final Checks Before Distribution

- [ ] Version number correct
- [ ] All features tested
- [ ] No critical bugs
- [ ] Installer tested on clean system
- [ ] Documentation up to date
- [ ] File sizes acceptable
- [ ] Uninstaller works

---

## Sign-Off

**Tested by:** ___________________
**Date:** ___________________
**Version:** ___________________
**Status:** [ ] Approved for Release  [ ] Needs Work

**Notes:**
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________
