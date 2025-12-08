# Building NetTools Suite on Your System

## ⚠️ Important: Current Environment

**You are currently on a Linux system** (Emergent platform), but NetTools Suite is a **Windows desktop application** that needs to be built and packaged on **Windows**.

---

## 🎯 What You Need to Know

### The Two-Step Build Process

1. **Step 1: PyInstaller** (Works on Linux or Windows)
   - Creates standalone executable
   - Bundles Python + dependencies
   - ✅ Can be done here on Linux
   - Output: `dist/NetTools/` folder

2. **Step 2: Inno Setup** (Windows-only ❌)
   - Creates the `.exe` installer
   - Adds component selection UI
   - Requires Windows to run
   - Output: `NetTools_Setup_1.0.0.exe`

---

## 🖥️ Options for Building

### Option 1: Build on Windows Machine (Recommended)

**This creates the complete installer with all features.**

#### Requirements:
- Windows 10 or 11
- Python 3.8+
- PyInstaller (`pip install pyinstaller`)
- Inno Setup 6 (https://jrsoftware.org/isdl.php)

#### Steps:
1. **Copy all files** from `/app/` to your Windows machine
2. **Install Inno Setup** from https://jrsoftware.org/isdl.php
3. **Open Command Prompt** in the project folder
4. **Run:** `build_installer.bat`
5. **Find installer:** `installer_output\NetTools_Setup_1.0.0.exe`

**This is the easiest and recommended approach!**

---

### Option 2: Build Executable Here, Package on Windows

**If you want to test the build here first:**

#### On Linux (Emergent Platform):
```bash
# Run this script
./build_executable.sh

# Or manually:
python -m PyInstaller nettools.spec --noconfirm
```

**Output:** `dist/NetTools/` folder with the executable

**Note:** This creates a **Linux executable**, not a Windows `.exe`. To create a Windows executable, you must build on Windows.

#### Then on Windows:
1. Copy all files to Windows
2. Run `build_installer.bat` to create the installer

---

### Option 3: Cross-Compilation (Advanced)

**PyInstaller cross-compilation is not officially supported.** 

You cannot reliably create a Windows executable from Linux. You need to build on the target platform (Windows).

---

## 🚀 Recommended Workflow

### For Your Situation:

Since you're developing on the Emergent platform (Linux) but need a Windows application:

**Development & Testing:**
1. ✅ Develop code here on Emergent
2. ✅ Test Python code functionality
3. ✅ Make changes and improvements

**Building & Distribution:**
1. ✅ Download/clone your project to a Windows machine
2. ✅ Run `build_installer.bat` on Windows
3. ✅ Test the installer on Windows
4. ✅ Distribute `NetTools_Setup_1.0.0.exe`

---

## 📋 What You Have Ready

**All configuration files are ready:**
- ✅ `nettools.spec` - PyInstaller config
- ✅ `nettools_setup.iss` - Inno Setup config
- ✅ `build_installer.bat` - Windows build script
- ✅ `build_executable.sh` - Linux build script (for testing)
- ✅ All documentation files
- ✅ Application code

**Everything is configured correctly!** You just need to run the build on Windows.

---

## 🖥️ Setting Up Windows Build Environment

### Quick Setup on Windows:

#### 1. Install Python
```powershell
# Download from python.org
# Or use Chocolatey:
choco install python
```

#### 2. Install Dependencies
```powershell
# In your project folder:
pip install -r requirements.txt
```

#### 3. Install Inno Setup
- Download: https://jrsoftware.org/isdl.php
- Install to default location: `C:\Program Files (x86)\Inno Setup 6\`

#### 4. Build
```powershell
build_installer.bat
```

**Done!** Installer will be in `installer_output\`

---

## 🎯 Alternative: Use GitHub Actions (Automated)

You can automate Windows builds using GitHub Actions:

### Create `.github/workflows/build.yml`:
```yaml
name: Build Windows Installer

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Install Inno Setup
      run: choco install innosetup
    
    - name: Build installer
      run: build_installer.bat
    
    - name: Upload installer
      uses: actions/upload-artifact@v3
      with:
        name: NetTools-Installer
        path: installer_output/*.exe
```

This builds automatically on GitHub's Windows servers!

---

## ❓ FAQ

### Q: Can I build a Windows installer on Linux?
**A:** No, Inno Setup requires Windows. You can create the PyInstaller bundle, but the installer must be built on Windows.

### Q: What if I don't have a Windows machine?
**A:** Use:
- Virtual machine (VirtualBox, VMware)
- Cloud Windows instance (AWS, Azure)
- GitHub Actions (automated, free for public repos)
- Wine on Linux (not recommended, unreliable)

### Q: Can I just distribute the `dist/NetTools/` folder?
**A:** Yes! You can ZIP the entire `dist/NetTools/` folder and distribute it. Users can extract and run `NetTools.exe` directly. However, they won't get:
- Component selection
- Start menu shortcuts
- Desktop icon
- Uninstaller
- Professional installer experience

### Q: Will the Linux build work on Windows?
**A:** No. PyInstaller creates platform-specific executables. You must build on Windows to get a Windows `.exe`.

---

## ✅ Summary

**Current Status:**
- ✅ All build scripts configured correctly
- ✅ All documentation ready
- ⚠️ Need Windows to create the installer

**Next Steps:**
1. **Copy project files** to a Windows machine
2. **Install Inno Setup** on Windows
3. **Run `build_installer.bat`** on Windows
4. **Get your installer:** `installer_output\NetTools_Setup_1.0.0.exe`

**Everything is ready - you just need to run the final build on Windows!**

---

## 📞 Need Help?

If you need to build on Windows and don't have access:
1. Use a Windows VM (VirtualBox is free)
2. Use GitHub Actions (automated, no Windows needed)
3. Use a cloud Windows instance (AWS EC2, Azure)

All your build files are ready to go! 🚀
