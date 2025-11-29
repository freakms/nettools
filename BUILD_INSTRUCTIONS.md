# NetTools Suite - Build Instructions

## Quick Start (Windows)

If you're on Windows and want to build the .exe quickly:

```batch
REM 1. Open Command Prompt or PowerShell
REM 2. Navigate to the app directory
cd C:\path\to\app

REM 3. Install dependencies
pip install -r requirements.txt

REM 4. Build the executable
python build_exe.py

REM 5. Find your executable in:
REM    dist\NetToolsSuite.exe
```

---

## Detailed Build Process

### Prerequisites

1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **Required packages** (installed via requirements.txt):
   - customtkinter (GUI framework)
   - Pillow (image processing)
   - pythonping (network ping)
   - pyinstaller (executable builder)

### Step-by-Step Build

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Troubleshooting:**
- If pip is not found: `python -m pip install -r requirements.txt`
- If permission denied (Linux/Mac): `pip install --user -r requirements.txt`

#### 2. Test the Application (Optional)

Before building, test that everything works:

```bash
python nettools_app.py
```

The GUI should open. Test:
- ✓ IPv4 Scanner with a small network (e.g., 192.168.1.0/30)
- ✓ MAC Formatter with a test MAC (e.g., AA:BB:CC:DD:EE:FF)
- ✓ Theme switching (Light/Dark)

#### 3. Build the Executable

**Option A: Using the build script (Recommended)**

```bash
python build_exe.py
```

This will:
- Create the application icon
- Configure PyInstaller
- Build a single-file executable
- Place output in `dist/NetToolsSuite.exe`

**Option B: Manual PyInstaller command**

```bash
pyinstaller --onefile --windowed --name=NetToolsSuite --icon=nettools_icon.ico nettools_app.py
```

#### 4. Test the Executable

```bash
# Windows
dist\NetToolsSuite.exe

# Linux/Mac
./dist/NetToolsSuite
```

---

## Platform-Specific Notes

### Windows

**✓ Recommended Platform**
- No admin rights needed for building
- No admin rights needed for running (pythonping works without elevation)
- Executable size: ~25-40 MB

**Build command:**
```batch
python build_exe.py
```

**Antivirus Warning:**
Windows Defender or other antivirus may flag the .exe as suspicious (false positive). This is common with PyInstaller executables. To fix:
1. Add exception in antivirus
2. Or code-sign the executable (requires certificate)

### macOS

**Builds as .app bundle**

```bash
python build_exe.py
```

Output: `dist/NetToolsSuite.app`

**Network Permissions:**
- First run will ask for network access permission
- Grant permission in System Preferences > Security & Privacy

**Gatekeeper Warning:**
- Right-click > Open (first time)
- Or disable Gatekeeper: `sudo spctl --master-disable`

### Linux

**Build command:**
```bash
python build_exe.py
```

Output: `dist/NetToolsSuite`

**ICMP Capabilities:**
For ping to work without sudo:

```bash
# Grant raw socket capability to Python
sudo setcap cap_net_raw+ep $(which python3)

# Or run the executable with sudo
sudo ./dist/NetToolsSuite
```

---

## Build Configuration

### Customizing the Build

Edit `build_exe.py` to customize:

```python
args = [
    'nettools_app.py',
    '--onefile',          # Single file (change to --onedir for folder)
    '--windowed',         # No console (remove for debug console)
    '--name=NetToolsSuite',  # Change executable name
    '--icon=nettools_icon.ico',  # Custom icon path
]
```

### Build Variants

**Single File (Default):**
- Pros: Easy distribution, one file
- Cons: Slower startup (~2-3 seconds)
- Flag: `--onefile`

**Directory Mode:**
- Pros: Faster startup
- Cons: Multiple files to distribute
- Flag: `--onedir`

**Debug Console:**
- Shows error messages in console
- Remove `--windowed` flag
- Useful for troubleshooting

---

## Advanced Options

### Reducing Executable Size

1. **Use UPX compression:**
```bash
pip install upx
pyinstaller --onefile --windowed --upx-dir=/path/to/upx nettools_app.py
```

2. **Exclude unused modules:**
```python
args.extend([
    '--exclude-module=matplotlib',
    '--exclude-module=scipy',
    # Add other unused modules
])
```

### Adding Version Info (Windows)

Create `version_info.txt`:

```
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Malte Schad'),
        StringStruct(u'FileDescription', u'NetTools Suite'),
        StringStruct(u'FileVersion', u'1.0.0'),
        StringStruct(u'InternalName', u'NetToolsSuite'),
        StringStruct(u'LegalCopyright', u'© Malte Schad'),
        StringStruct(u'OriginalFilename', u'NetToolsSuite.exe'),
        StringStruct(u'ProductName', u'NetTools Suite'),
        StringStruct(u'ProductVersion', u'1.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
```

Then add to build:
```bash
pyinstaller --onefile --windowed --version-file=version_info.txt nettools_app.py
```

---

## Troubleshooting Build Issues

### Issue: "Module not found" during build

**Solution:**
```bash
pip install --upgrade -r requirements.txt
```

### Issue: "Failed to execute script"

**Solution:**
Build with console to see errors:
```bash
pyinstaller --onefile --console nettools_app.py
```

### Issue: Executable won't start

**Check:**
1. Antivirus is not blocking it
2. All dependencies are installed during build
3. Try building without `--windowed` to see errors

### Issue: Import errors in built executable

**Solution:**
Add hidden imports:
```python
args.append('--hidden-import=problematic_module')
```

### Issue: Icon not showing

**Solution:**
1. Ensure icon file exists: `nettools_icon.ico`
2. Use absolute path: `--icon=C:\full\path\to\icon.ico`
3. Try without icon to test if that's the issue

---

## Distribution

### What to Distribute

**Single File Build:**
- Only distribute: `dist/NetToolsSuite.exe`
- No other files needed!

**Directory Build:**
- Zip the entire `dist/NetToolsSuite/` folder
- Users must extract all files together

### Code Signing (Optional)

For professional distribution without antivirus warnings:

1. **Windows:** Use `signtool.exe` with code signing certificate
2. **macOS:** Use `codesign` with Apple Developer certificate
3. **Linux:** Use GPG signatures

**Simple signing (Windows):**
```batch
signtool sign /f certificate.pfx /p password /tr http://timestamp.digicert.com dist\NetToolsSuite.exe
```

---

## Testing Checklist

Before distributing, test the executable:

- [ ] Application starts without errors
- [ ] Theme switching works (Light/Dark)
- [ ] IPv4 Scanner:
  - [ ] CIDR parsing (test /24, /30, /32, /31)
  - [ ] Scan starts and completes
  - [ ] Results display correctly
  - [ ] Progress bar updates
  - [ ] Cancel button works
  - [ ] Filter "only responding" works
  - [ ] CSV export works
- [ ] MAC Formatter:
  - [ ] Input validation works
  - [ ] All 4 formats display
  - [ ] Switch commands generate correctly
  - [ ] Copy buttons work
  - [ ] Toggle commands button works
- [ ] Keyboard shortcuts:
  - [ ] Enter starts scan / copies MAC
  - [ ] Ctrl+E exports CSV
- [ ] Window resizing works
- [ ] Status bar updates correctly

---

## Performance Tuning

### Startup Time

**Single file:** 2-3 seconds (extracts to temp)
**Directory mode:** <1 second (runs directly)

**To improve single-file startup:**
- Use `--onedir` instead
- Or accept the startup delay

### Scan Performance

**Default settings:**
- Medium: 64 concurrent threads, 300ms timeout
- Aggressive: 128 threads, 150ms timeout
- Gentle: 32 threads, 600ms timeout

**For faster scans:**
- Use Aggressive mode
- Or increase thread count in code

---

## Continuous Integration (CI/CD)

### GitHub Actions Example

```yaml
name: Build NetTools

on: [push, pull_request]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Build executable
        run: python build_exe.py
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: NetToolsSuite
          path: dist/NetToolsSuite.exe
```

---

## Support

For build issues:
1. Check this guide first
2. Try building with `--console` to see errors
3. Check PyInstaller documentation: https://pyinstaller.org/
4. Review CustomTkinter issues: https://github.com/TomSchimansky/CustomTkinter/issues

---

**Build script created by:** Malte Schad  
**Last updated:** 2025  
**Python version:** 3.8+  
**Supported OS:** Windows, macOS, Linux
