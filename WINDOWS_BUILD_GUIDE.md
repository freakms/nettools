# NetTools Suite - Windows Build Instructions

## 🎯 Complete Step-by-Step Guide for Building on Windows

Follow these steps to create your Windows installer.

---

## 📋 Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Windows 10 or Windows 11 (64-bit)
- [ ] Administrator access
- [ ] Internet connection (for downloads)
- [ ] ~500 MB free disk space
- [ ] All project files copied to Windows machine

---

## 🚀 Step-by-Step Instructions

### Step 1: Transfer Project Files to Windows

**Copy the entire `/app/` directory to your Windows machine.**

Options:
- **Download as ZIP** from your repository
- **Git clone** if using version control
- **Copy via USB** or network share

**Place files in a convenient location:**
```
C:\Projects\NetTools\
```

---

### Step 2: Install Python on Windows

#### Option A: Download from Python.org (Recommended)

1. **Go to:** https://www.python.org/downloads/
2. **Download:** Python 3.11 or 3.12 (latest stable)
3. **Run installer**
4. **⚠️ IMPORTANT:** Check "Add Python to PATH" ✅
5. Click "Install Now"

#### Option B: Using Chocolatey (if you have it)

```powershell
choco install python
```

#### Verify Installation:

Open **Command Prompt** and run:
```cmd
python --version
```

Expected output: `Python 3.11.x` or similar

---

### Step 3: Install Python Dependencies

Open **Command Prompt** in your project folder:

```cmd
cd C:\Projects\NetTools
```

Install all required packages:
```cmd
pip install -r requirements.txt
```

This installs:
- PyInstaller
- customtkinter
- matplotlib
- pythonping
- And all other dependencies

**Wait for installation to complete** (2-3 minutes)

---

### Step 4: Install Inno Setup

#### Download and Install:

1. **Go to:** https://jrsoftware.org/isdl.php
2. **Download:** Inno Setup 6 (latest version)
3. **Run installer:** `innosetup-6.x.x.exe`
4. **Use default installation path:** `C:\Program Files (x86)\Inno Setup 6\`
5. Complete installation

**Default path is important!** The build script expects Inno Setup at:
```
C:\Program Files (x86)\Inno Setup 6\ISCC.exe
```

---

### Step 5: Build the Installer

#### Simple Method:

1. **Open Command Prompt** in your project folder:
   ```cmd
   cd C:\Projects\NetTools
   ```

2. **Run the build script:**
   ```cmd
   build_installer.bat
   ```

3. **Wait** (3-5 minutes for first build)

#### What You'll See:

```
========================================
NetTools Suite - Build Installer
========================================

Step 1/4: Cleaning previous builds...
Step 2/4: Building executable with PyInstaller...
[PyInstaller output...]
Step 3/4: Checking for Inno Setup...
Step 4/4: Creating installer with Inno Setup...
[Inno Setup output...]

========================================
BUILD COMPLETE!
========================================

Installer created in: installer_output\
Executable available in: dist\NetTools\
```

---

### Step 6: Find Your Installer

**Location:**
```
C:\Projects\NetTools\installer_output\NetTools_Setup_1.0.0.exe
```

**File Size:** ~20-30 MB (compressed)

**This is your distributable installer!** ✅

---

## 🧪 Testing the Build

### Test 1: Test the Executable (Before Installer)

```cmd
cd dist\NetTools
NetTools.exe
```

**Verify:**
- ✅ Application launches
- ✅ No console window appears
- ✅ GUI renders correctly
- ✅ Tools are accessible

### Test 2: Test the Installer

**On the same machine (quick test):**
1. Double-click `installer_output\NetTools_Setup_1.0.0.exe`
2. Follow installation wizard
3. Select some components
4. If you select "Bandwidth Testing", verify iperf3 info page appears
5. Complete installation
6. Launch from Start Menu
7. Verify selected tools work

**On a clean machine (thorough test):**
1. Copy installer to a different Windows PC (or VM)
2. Run installer
3. Test different installation types
4. Verify all features work

---

## 🛠️ Troubleshooting

### Issue: "Python is not installed or not in PATH"

**Solution:**
1. Reinstall Python
2. Make sure "Add Python to PATH" is checked
3. Or manually add Python to PATH:
   - Right-click "This PC" → Properties → Advanced system settings
   - Environment Variables → System variables → Path → Edit
   - Add: `C:\Python311\` and `C:\Python311\Scripts\`

### Issue: "PyInstaller is not installed"

**Solution:**
```cmd
pip install pyinstaller
```

### Issue: "Inno Setup not found"

**Solutions:**
1. Install Inno Setup from https://jrsoftware.org/isdl.php
2. Make sure it's installed to the default location
3. Or edit `build_installer.bat` line 50 to match your install path

### Issue: PyInstaller takes very long (>10 minutes)

**This is normal for first build.** Subsequent builds are faster (~3 minutes).

### Issue: "Module not found" errors

**Solution:**
```cmd
pip install -r requirements.txt --upgrade
```

### Issue: Build succeeds but executable won't run

**Check:**
1. Run from command line to see errors
2. Ensure all dependencies in requirements.txt
3. Check antivirus isn't blocking it

---

## 📦 Build Output Explained

After successful build:

```
C:\Projects\NetTools\
├── build\                    ← Temporary files (can delete)
├── dist\
│   └── NetTools\             ← Standalone application
│       ├── NetTools.exe      ← Main executable
│       └── _internal\        ← Python runtime & libraries
└── installer_output\
    └── NetTools_Setup_1.0.0.exe  ← **YOUR INSTALLER** 🎉
```

**What to distribute:** `NetTools_Setup_1.0.0.exe`

---

## 🚀 Distribution

### File to Distribute:
```
installer_output\NetTools_Setup_1.0.0.exe
```

### User Requirements:
- Windows 10/11 (64-bit)
- 100-200 MB disk space
- Administrator rights (for installation)
- **NO Python needed** ✅

### How Users Install:
1. Download `NetTools_Setup_1.0.0.exe`
2. Run installer
3. Select components
4. If Bandwidth Testing selected → See iperf3 instructions
5. Install
6. Launch from Start Menu

---

## ⚙️ Customization (Optional)

### Change Version Number

Edit `nettools_setup.iss` line 5:
```iss
#define MyAppVersion "1.0.0"  ← Change this
```

### Change Company Name

Edit `nettools_setup.iss` line 6:
```iss
#define MyAppPublisher "Your Company Name"
```

### Add Application Icon

1. Create `nettools.ico` (256x256 recommended)
2. Place in project root
3. Edit `nettools.spec` line 65:
   ```python
   icon='nettools.ico'
   ```
4. Edit `nettools_setup.iss` line 28:
   ```iss
   SetupIconFile=nettools.ico
   ```
5. Rebuild

---

## 📝 Build Checklist

Before distributing:

- [ ] Build completes without errors
- [ ] Executable runs on build machine
- [ ] Installer runs on build machine
- [ ] Tested on clean Windows machine (recommended)
- [ ] Component selection works
- [ ] iperf3 info page shows (when bandwidth testing selected)
- [ ] Start menu shortcuts created
- [ ] Desktop shortcut works (if selected)
- [ ] Uninstaller works correctly
- [ ] Version number is correct
- [ ] Company name is correct

---

## 🎯 Quick Reference

### Full Build Command:
```cmd
cd C:\Projects\NetTools
build_installer.bat
```

### Output:
```
installer_output\NetTools_Setup_1.0.0.exe
```

### Time Required:
- First build: 5-10 minutes
- Subsequent builds: 3-5 minutes

### Final Size:
- Installer: ~25 MB
- Installed: ~60-100 MB (depends on components)

---

## ✅ Success Criteria

**You'll know it worked when:**
1. ✅ Build script completes without errors
2. ✅ File exists: `installer_output\NetTools_Setup_1.0.0.exe`
3. ✅ Installer runs and shows component selection
4. ✅ iperf3 information page appears (if bandwidth testing selected)
5. ✅ Application installs and launches successfully

---

## 📞 Support

**If you encounter issues:**

1. Check error messages carefully
2. Verify all prerequisites installed
3. Check `build\nettools\warn-nettools.txt` for warnings
4. Ensure antivirus isn't blocking
5. Try running Command Prompt as Administrator

**Common files to check:**
- `build\nettools\warn-nettools.txt` - PyInstaller warnings
- Build script output - Error messages

---

## 🎉 You're Ready!

Everything is configured correctly. Just follow the steps above on your Windows machine and you'll have a professional installer ready to distribute!

**Good luck! 🚀**
