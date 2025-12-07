# Quick Build Guide - NetTools Suite

## Step-by-Step: From Source to Installer

---

## Phase 1: Test the Application (15-30 minutes)

### 1. Run the Application
```cmd
cd C:\path\to\nettools
python nettools_app.py
```

### 2. Quick Test Checklist
- [ ] Application starts
- [ ] Open Live Ping Monitor (test with 8.8.8.8)
- [ ] Try IPv4 Scanner
- [ ] Open PAN-OS Generator → test one tab
- [ ] Navigate between different tools
- [ ] No crashes

✅ **If all works:** Proceed to Phase 2
❌ **If issues:** Fix them first, then retest

---

## Phase 2: Install Build Tools (10-15 minutes)

### 1. Install PyInstaller
```cmd
pip install pyinstaller
```

Verify:
```cmd
pyinstaller --version
```
Should show: `6.x.x` or similar

### 2. Install Inno Setup
1. Download: https://jrsoftware.org/isdl.php
2. Run installer
3. Install to default location: `C:\Program Files (x86)\Inno Setup 6\`

Verify:
```cmd
dir "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
```
Should show the file exists

### 3. Verify All Dependencies
```cmd
pip install -r requirements.txt
```

---

## Phase 3: Build the Installer (5-10 minutes)

### Option A: Automated Build (Recommended)

```cmd
cd C:\path\to\nettools
build_installer.bat
```

**What it does:**
1. Cleans old builds
2. Runs PyInstaller
3. Runs Inno Setup
4. Creates installer

**Output:**
- `installer_output\NetTools_Setup_1.0.0.exe`

### Option B: Manual Build

If automated build fails:

**Step 1: Build Executable**
```cmd
pyinstaller nettools.spec
```

Check: `dist\NetTools\NetTools.exe` should exist

**Step 2: Test Executable**
```cmd
cd dist\NetTools
NetTools.exe
```

Test the app - does it work?

**Step 3: Create Installer**
```cmd
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" nettools_setup.iss
```

Check: `installer_output\NetTools_Setup_1.0.0.exe` should exist

---

## Phase 4: Test the Installer (10-15 minutes)

### Quick Test (On Your System)

1. **Run the installer:**
   ```cmd
   installer_output\NetTools_Setup_1.0.0.exe
   ```

2. **Choose "Custom Installation"**
   - Select some components
   - Complete installation

3. **Test the installed app:**
   - Find in Start Menu
   - Launch
   - Test a few features

4. **Uninstall:**
   - Control Panel → Programs
   - Uninstall NetTools Suite
   - Verify files removed

### Thorough Test (Clean System - Recommended)

Use a Windows VM or clean test PC:

1. **Install:**
   - Try "Full Installation"
   - Note installation size
   - Check Start Menu / Desktop

2. **Launch & Test:**
   - All features work?
   - No missing DLLs?
   - Performance good?

3. **Uninstall:**
   - Clean removal?
   - No leftover files?

---

## Common Issues & Solutions

### Issue: "PyInstaller not found"
```cmd
pip install pyinstaller
```

### Issue: "Module not found" during build
Add to `nettools.spec` in `hiddenimports`:
```python
hiddenimports=[
    'missing_module_name',
]
```
Then rebuild.

### Issue: "ISCC.exe not found"
- Install Inno Setup
- Or update path in `build_installer.bat`

### Issue: Installer very large (>200 MB)
- Normal for first build
- Includes Python + all libraries
- Can optimize later with UPX

### Issue: Executable won't run
- Test from command line to see errors:
  ```cmd
  cd dist\NetTools
  NetTools.exe
  ```
- Check for missing dependencies

### Issue: Missing features in compiled version
- Check component selection in installer
- Verify files in `dist\NetTools\`

---

## Build Time Estimates

| Task | Time | Output |
|------|------|--------|
| PyInstaller build | 2-5 min | dist\NetTools\NetTools.exe |
| Inno Setup compile | 1-2 min | installer_output\NetTools_Setup_1.0.0.exe |
| **Total** | **3-7 min** | Ready to distribute! |

---

## File Sizes (Approximate)

- **Standalone exe:** 150-180 MB
- **Installer:** 60-80 MB (compressed)
- **Installed (Full):** 150-200 MB
- **Installed (Minimal):** 80-100 MB

---

## Success Criteria

✅ **Ready to distribute when:**
- [ ] Application runs from source
- [ ] PyInstaller build succeeds
- [ ] Executable runs standalone
- [ ] Installer creates successfully
- [ ] Installer runs and installs
- [ ] Installed app works correctly
- [ ] Uninstaller removes cleanly
- [ ] Tested on clean system

---

## Next Steps After Building

1. **Test thoroughly** (use TESTING_CHECKLIST.md)
2. **Fix any issues** found
3. **Rebuild** if needed
4. **Create distribution package:**
   - Installer file
   - README for users
   - Version notes
5. **Distribute:**
   - Website
   - Download link
   - Share with users

---

## Quick Commands Reference

```cmd
# Install build tools
pip install pyinstaller
pip install -r requirements.txt

# Build everything (automated)
build_installer.bat

# Or build manually
pyinstaller nettools.spec
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" nettools_setup.iss

# Clean builds
rmdir /s /q dist build installer_output

# Test executable
cd dist\NetTools
NetTools.exe

# Run installer
installer_output\NetTools_Setup_1.0.0.exe
```

---

## Getting Help

- **Build Guide:** BUILD_INSTALLER_GUIDE.md (detailed)
- **Testing:** TESTING_CHECKLIST.md (comprehensive)
- **PyInstaller Docs:** https://pyinstaller.org/
- **Inno Setup Docs:** https://jrsoftware.org/ishelp/

---

## Ready to Build?

1. ✅ Application tested
2. ✅ Build tools installed
3. ✅ Ready to run `build_installer.bat`

**Let's go!** 🚀
