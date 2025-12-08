# Quick Start - Building on Windows

## ⚡ Fast Track (5 Steps)

### 1️⃣ Transfer Files
Copy entire project folder to Windows machine

### 2️⃣ Install Python
https://www.python.org/downloads/
✅ Check "Add Python to PATH"

### 3️⃣ Install Dependencies
```cmd
cd C:\Projects\NetTools
pip install -r requirements.txt
```

### 4️⃣ Install Inno Setup
https://jrsoftware.org/isdl.php
Use default installation path

### 5️⃣ Build
```cmd
build_installer.bat
```

**Output:** `installer_output\NetTools_Setup_1.0.0.exe` ✅

---

## ⏱️ Time Required

- Setup (first time): ~15 minutes
- Building: ~5 minutes
- **Total: ~20 minutes**

---

## 📋 Quick Checklist

```
□ Windows 10/11 (64-bit)
□ Python installed (with PATH)
□ Dependencies installed (pip install -r requirements.txt)
□ Inno Setup installed
□ Run build_installer.bat
□ Check installer_output\ folder
```

---

## 🎯 Expected Result

```
installer_output\
└── NetTools_Setup_1.0.0.exe  (~25 MB)
```

This is your distributable Windows installer!

---

## 📚 Detailed Guide

See `WINDOWS_BUILD_GUIDE.md` for complete step-by-step instructions.

---

## ❓ Quick Troubleshooting

**Python not found?**
→ Reinstall Python with "Add to PATH" checked

**PyInstaller not found?**
→ Run: `pip install pyinstaller`

**Inno Setup not found?**
→ Install from: https://jrsoftware.org/isdl.php

**Build takes too long?**
→ First build is slow (~10 min), subsequent builds are faster

---

**Ready? Let's build! 🚀**
