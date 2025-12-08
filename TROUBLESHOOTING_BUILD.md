# Troubleshooting: No Installer File Created

## 🔍 Most Common Issue: Inno Setup Not Installed

If `build_installer.bat` finishes without error but `installer_output` is empty, **Inno Setup is probably not installed**.

---

## ✅ Quick Diagnosis

### Run This Diagnostic Script:

```cmd
diagnose_build.bat
```

This will check:
1. Python installed ✓
2. PyInstaller installed ✓
3. Executable created ✓
4. **Inno Setup installed** ← Most likely issue
5. Output folders exist ✓
6. Config files exist ✓

---

## 🔧 Solution: Install Inno Setup

### Step 1: Download Inno Setup

**URL:** https://jrsoftware.org/isdl.php

**What to download:** "Inno Setup 6.x.x" (latest stable version)

**File name:** Something like `innosetup-6.2.2.exe`

### Step 2: Install Inno Setup

1. **Run the installer** you just downloaded
2. **Accept all defaults** - especially the installation path!
3. **Default path MUST be:** `C:\Program Files (x86)\Inno Setup 6\`
4. Complete installation

### Step 3: Verify Installation

Open Command Prompt and run:
```cmd
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /?
```

**If successful:** You'll see Inno Setup help text  
**If error:** Inno Setup is not installed correctly

### Step 4: Rebuild

```cmd
build_installer.bat
```

Now you should get: `installer_output\NetTools_Setup_1.0.0.exe` ✅

---

## 📋 Other Possible Issues

### Issue 1: Inno Setup in Different Location

**Symptom:** Inno Setup is installed but not at default path

**Check your installation path:**
- `C:\Program Files (x86)\Inno Setup 6\ISCC.exe` ← Default
- `C:\Program Files\Inno Setup 6\ISCC.exe` ← Alternative
- `C:\InnoSetup\ISCC.exe` ← Custom

**Solution:** Edit `build_installer.bat` line 50:
```batch
set "INNO_PATH=C:\Your\Custom\Path\ISCC.exe"
```

---

### Issue 2: PyInstaller Failed

**Symptom:** `dist\NetTools\NetTools.exe` doesn't exist

**Check:**
```cmd
dir dist\NetTools\NetTools.exe
```

**If file doesn't exist:**
```cmd
pip install -r requirements.txt
python -m PyInstaller nettools.spec --noconfirm
```

---

### Issue 3: Missing .iss File

**Symptom:** `nettools_setup.iss` not in project folder

**Check:**
```cmd
dir nettools_setup.iss
```

**Solution:** Make sure you copied ALL files from the project

---

### Issue 4: Permissions Error

**Symptom:** "Access denied" or permission errors

**Solution:** Run Command Prompt as Administrator
1. Right-click Command Prompt
2. "Run as Administrator"
3. Navigate to project folder
4. Run `build_installer.bat`

---

## 🔍 Manual Step-by-Step Check

### Check 1: Python Works
```cmd
python --version
```
Expected: `Python 3.11.x` or similar

### Check 2: PyInstaller Installed
```cmd
python -m pip show pyinstaller
```
Expected: Shows version info

### Check 3: Executable Exists
```cmd
dir dist\NetTools\NetTools.exe
```
Expected: File exists with size ~8-15 MB

### Check 4: Inno Setup Installed
```cmd
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /?
```
Expected: Shows Inno Setup help text

### Check 5: Config File Exists
```cmd
dir nettools_setup.iss
```
Expected: File exists

### Check 6: Output Folder Exists
```cmd
dir installer_output
```
Expected: Folder exists (may be empty before build)

---

## 🎯 Most Likely Solution

**90% of the time, the issue is:**

```
Inno Setup is not installed or not at the default path
```

**Fix:**
1. Install from: https://jrsoftware.org/isdl.php
2. Use default installation path
3. Run `build_installer.bat` again

---

## 📝 What to Look For in Build Output

When you run `build_installer.bat`, you should see:

```
========================================
NetTools Suite - Build Installer
========================================

Step 1/4: Cleaning previous builds...
[OK]

Step 2/4: Building executable with PyInstaller...
[... lots of PyInstaller output ...]
[Should end with "Building COLLECT completed successfully"]

Step 3/4: Checking for Inno Setup...
[Should NOT see "WARNING: Inno Setup not found"]

Step 4/4: Creating installer with Inno Setup...
[... Inno Setup output ...]
[Should end with "Successful compile"]

========================================
BUILD COMPLETE!
========================================

Installer created in: installer_output\
```

**If you see:** "WARNING: Inno Setup not found"  
**Then:** Install Inno Setup and try again

---

## 🆘 Still Not Working?

### Provide This Information:

1. **Run diagnostic:**
   ```cmd
   diagnose_build.bat > diagnosis.txt
   ```

2. **Run build with full output:**
   ```cmd
   build_installer.bat > build_log.txt 2>&1
   ```

3. **Check these:**
   - Does `dist\NetTools\NetTools.exe` exist?
   - Does Inno Setup show up in Windows Programs list?
   - What's the full path to Inno Setup?

4. **Send:**
   - diagnosis.txt
   - build_log.txt
   - Screenshot of `dir "C:\Program Files (x86)\Inno Setup 6\"`

---

## ✅ Expected Final Result

After successful build:

```
YourProject\
├── dist\
│   └── NetTools\
│       └── NetTools.exe            ✅ (~8-15 MB)
└── installer_output\
    └── NetTools_Setup_1.0.0.exe   ✅ (~20-30 MB) ← THIS IS YOUR INSTALLER
```

---

## 💡 Quick Checklist

- [ ] Python installed and in PATH
- [ ] PyInstaller installed (`pip install pyinstaller`)
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] **Inno Setup installed at default path** ← Check this!
- [ ] All project files copied from `/app/`
- [ ] Running from correct directory
- [ ] No antivirus blocking

**Most common missing item:** Inno Setup installation

---

**Next Step:** Run `diagnose_build.bat` to find the exact issue!
