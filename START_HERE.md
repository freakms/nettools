# 🚀 NetTools Suite - Quick Start Guide

**Welcome!** Follow these simple steps to build your executable.

---

## ⚡ Super Quick Start (3 Commands)

Open **Command Prompt** or **PowerShell** in this folder and run:

```batch
REM Step 1: Install dependencies
pip install -r requirements.txt

REM Step 2: Test the app (optional)
python nettools_app.py

REM Step 3: Build the .exe
python build_exe.py
```

**Done!** Your executable is at: `dist\NetToolsSuite.exe`

---

## 📋 Detailed Instructions

### Step 1: Install Python (If Not Installed)

1. Download Python from: https://www.python.org/downloads/
2. Run the installer
3. ✅ **IMPORTANT:** Check "Add Python to PATH" during installation
4. Click "Install Now"

### Step 2: Open Command Prompt

**Method 1:** Using File Explorer
1. Open this folder in File Explorer
2. Type `cmd` in the address bar
3. Press Enter

**Method 2:** Using PowerShell
1. Open this folder in File Explorer
2. Hold Shift + Right-click in the folder
3. Select "Open PowerShell window here"

### Step 3: Install Dependencies

In the Command Prompt/PowerShell window, type:

```batch
pip install -r requirements.txt
```

Wait for installation to complete (30-60 seconds).

**If you get "pip is not recognized":**
```batch
python -m pip install -r requirements.txt
```

### Step 4: Build the Executable

**Option A: Automated Build (Easiest)**

Just double-click: `build_windows.bat`

The script will:
- Check Python installation
- Install dependencies
- Build the executable
- Ask if you want to run it

**Option B: Manual Build**

```batch
python build_exe.py
```

### Step 5: Find Your Executable

Location: `dist\NetToolsSuite.exe`

This is a **single file** that you can:
- Run directly (no installation needed)
- Copy to any Windows PC
- Share with others

---

## 🎯 Testing the Application

Before building, you can test it:

```batch
python nettools_app.py
```

The GUI will open. Try:
- **IPv4 Scanner:** Enter `192.168.1.0/30` and click "Start Scan"
- **MAC Formatter:** Enter `AA:BB:CC:DD:EE:FF`
- **Theme:** Switch between Light and Dark

Press `Ctrl+C` in the terminal to close it.

---

## ❓ Troubleshooting

### "pip is not recognized"

**Fix:**
```batch
python -m pip install -r requirements.txt
```

**Or:** Reinstall Python with "Add to PATH" checked

### "Permission denied" during pip install

**Fix:** Run Command Prompt as Administrator
- Right-click Command Prompt
- Select "Run as administrator"
- Navigate to this folder: `cd C:\path\to\folder`
- Run: `pip install -r requirements.txt`

### "ModuleNotFoundError: No module named 'customtkinter'"

**Fix:** You forgot to install dependencies!
```batch
pip install -r requirements.txt
```

### Build fails with PyInstaller error

**Fix 1:** Upgrade PyInstaller
```batch
pip install --upgrade pyinstaller
```

**Fix 2:** Check antivirus
- Some antivirus programs block PyInstaller
- Temporarily disable or add exception

### Windows Defender blocks the .exe

**Fix:** This is a false positive (common with PyInstaller)
1. Click "More info"
2. Click "Run anyway"

**Or:** Add exception in Windows Defender

---

## 📊 What Gets Installed

When you run `pip install -r requirements.txt`, these packages are installed:

| Package | Version | Purpose |
|---------|---------|---------|
| customtkinter | ≥5.2.0 | Modern GUI framework |
| Pillow | ≥10.0.0 | Image processing (icons) |
| pythonping | ≥1.1.4 | Network ping functionality |
| pyinstaller | ≥6.0.0 | Builds the executable |

**Total download size:** ~50-80 MB  
**Installation time:** 30-90 seconds

---

## 🎁 What You Get

After building, you'll have:

```
dist/
└── NetToolsSuite.exe  (~30-40 MB, single file)
```

This executable:
- ✅ Works on any Windows PC (7, 8, 10, 11)
- ✅ No installation required
- ✅ No dependencies needed
- ✅ No admin rights required to run
- ✅ Portable (run from USB, network drive, etc.)

---

## 🔥 Quick Commands Reference

```batch
# Install dependencies
pip install -r requirements.txt

# Test the application
python nettools_app.py

# Build executable (manual)
python build_exe.py

# Build executable (automated)
build_windows.bat

# Upgrade pip first (if issues)
python -m pip install --upgrade pip

# Install individual package
pip install customtkinter
```

---

## 📖 Need More Help?

**For building issues:** Read `BUILD_INSTRUCTIONS.md`  
**For using the app:** Read `USAGE_GUIDE.md`  
**For technical details:** Read `PROJECT_OVERVIEW.md`

---

## ✨ Current Error Fix

You're seeing this error:
```
ModuleNotFoundError: No module named 'customtkinter'
ModuleNotFoundError: No module named 'PyInstaller'
```

**Solution:** Run this ONE command:
```batch
pip install -r requirements.txt
```

Then try running the app or building again!

---

**That's it!** Any questions? Check the documentation files or contact Malte Schad.

🚀 **Happy building!**
