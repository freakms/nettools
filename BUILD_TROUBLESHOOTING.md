# Build Troubleshooting Guide

## Common Build Errors and Solutions

---

### ✅ Error: "No such file or directory: 'version_info.txt'"

**Status:** ✅ FIXED!

**What happened:**
The build script was looking for an optional version info file.

**Solution:**
The build script has been updated to make this file optional. The file now exists, but even if it didn't, the build would still work.

**Action:** Just run the build again:
```batch
python build_exe.py
```

---

### Error: "ModuleNotFoundError: No module named 'customtkinter'"

**Cause:** Dependencies not installed

**Solution:**
```batch
pip install -r requirements.txt
```

**Then retry:**
```batch
python build_exe.py
```

---

### Error: "ModuleNotFoundError: No module named 'PyInstaller'"

**Cause:** PyInstaller not installed

**Solution:**
```batch
pip install pyinstaller
```

**Or install all dependencies:**
```batch
pip install -r requirements.txt
```

---

### Error: "Failed to execute script 'pyi_rth_inspect'"

**Cause:** PyInstaller cache issue or antivirus interference

**Solution 1:** Clear PyInstaller cache
```batch
python -m PyInstaller --clean nettools_app.py
```

**Solution 2:** Check antivirus
- Temporarily disable antivirus
- Or add exception for PyInstaller

**Solution 3:** Reinstall PyInstaller
```batch
pip uninstall pyinstaller
pip install pyinstaller
```

---

### Error: "Permission denied" during build

**Cause:** Insufficient permissions or file in use

**Solution 1:** Run as Administrator
- Right-click Command Prompt
- "Run as administrator"
- Navigate to folder and build

**Solution 2:** Close application if running
- If you tested the app with `python nettools_app.py`
- Close it before building

**Solution 3:** Delete build folders
```batch
rmdir /s /q build
rmdir /s /q dist
rmdir /s /q __pycache__
```

Then rebuild:
```batch
python build_exe.py
```

---

### Error: "UnicodeDecodeError" during build

**Cause:** File encoding issue

**Solution:** Ensure you're using UTF-8 encoding
```batch
chcp 65001
python build_exe.py
```

---

### Error: "RecursionError: maximum recursion depth exceeded"

**Cause:** PyInstaller analyzing deep import chains

**Solution:** Increase recursion limit in build script

Add to `build_exe.py` before PyInstaller.run():
```python
import sys
sys.setrecursionlimit(5000)
```

---

### Warning: "Hidden import 'PIL._tkinter_finder' not found"

**Cause:** Optional import not available

**Status:** This is just a warning, not an error

**Action:** Ignore it - the build will still work

---

### Error: "Icon file not found" or icon-related errors

**Cause:** Icon creation failed

**Solution:** Build without icon
1. Open `build_exe.py`
2. Comment out icon-related lines:
```python
# icon_path = create_icon()
# if icon_path and os.path.exists(icon_path):
#     args.append(f'--icon={icon_path}')
```

Or just remove the icon parameter from args.

---

### Error: Build succeeds but .exe won't start

**Symptom:** Double-click .exe, nothing happens or crashes immediately

**Diagnosis:** Build with console to see errors
```batch
pyinstaller --onefile --console nettools_app.py
```

Run the .exe from Command Prompt:
```batch
cd dist
NetToolsSuite.exe
```

You'll see the error message.

**Common causes:**
1. **Missing DLL:** Install Visual C++ Redistributable
   - Download from Microsoft
   - https://aka.ms/vs/17/release/vc_redist.x64.exe

2. **Import error:** Add to hidden imports in `build_exe.py`

3. **Path issue:** Use absolute paths in code

---

### Build is very slow

**Normal:** First build takes 2-5 minutes

**Too slow (>10 min)?**

**Solution 1:** Exclude unused modules
In `build_exe.py`, add:
```python
args.extend([
    '--exclude-module=matplotlib',
    '--exclude-module=numpy',
    '--exclude-module=scipy',
])
```

**Solution 2:** Use directory mode (faster)
Change in `build_exe.py`:
```python
'--onedir',  # Instead of '--onefile'
```

---

### Antivirus blocks PyInstaller or the .exe

**Symptom:** Build fails with cryptic errors, or .exe is deleted after build

**Solution 1:** Whitelist PyInstaller
Add to antivirus exceptions:
- `C:\Python3X\Scripts\pyinstaller.exe`
- Your project folder

**Solution 2:** Whitelist output
Add to exceptions:
- `dist\NetToolsSuite.exe`

**Solution 3:** Temporarily disable antivirus during build

**Note:** This is a false positive - PyInstaller executables often trigger antivirus

---

### Build succeeds but .exe is huge (>100 MB)

**Normal size:** 30-40 MB for single file

**If larger:**

**Check:** What's included
```batch
pyinstaller --onefile --windowed --log-level=DEBUG nettools_app.py
```

**Solution:** Exclude unnecessary packages
```python
args.extend([
    '--exclude-module=tkinter.test',
    '--exclude-module=test',
])
```

---

### Error: "Can't find version_info.txt"

**Status:** ✅ FIXED in latest version!

**If you still see this:**

**Quick fix:** Create empty file
```batch
echo. > version_info.txt
```

**Proper fix:** Update `build_exe.py` to skip if not exists (already done)

---

## Complete Clean Rebuild Process

If nothing works, try a complete clean rebuild:

```batch
REM 1. Clean everything
rmdir /s /q build
rmdir /s /q dist
del /q *.spec
del /q nettools_icon.ico

REM 2. Reinstall dependencies
pip uninstall -y customtkinter Pillow pythonping pyinstaller
pip install -r requirements.txt

REM 3. Rebuild
python build_exe.py
```

---

## Verification Checklist

Before building, verify:

- [ ] Python 3.8+ installed
- [ ] pip working (`pip --version`)
- [ ] Dependencies installed (`pip list | findstr customtkinter`)
- [ ] No other Python processes running
- [ ] Sufficient disk space (need ~500 MB temp)
- [ ] Antivirus not blocking Python/PyInstaller

---

## Getting Help

If you still have issues:

1. **Check exact error message**
   - Read the full error output
   - Note the last error before it failed

2. **Try clean rebuild** (see above)

3. **Search the error**
   - PyInstaller GitHub issues
   - Stack Overflow

4. **Collect information:**
   - Python version: `python --version`
   - PyInstaller version: `pyinstaller --version`
   - OS version
   - Exact error message
   - Full build output

---

## Quick Reference Commands

```batch
# Install dependencies
pip install -r requirements.txt

# Build (normal)
python build_exe.py

# Build with debug output
pyinstaller --onefile --windowed --log-level=DEBUG nettools_app.py

# Build with console (for debugging)
pyinstaller --onefile --console nettools_app.py

# Clean build
python -m PyInstaller --clean --onefile nettools_app.py

# List installed packages
pip list

# Check for hidden import issues
pyi-makespec nettools_app.py

# Test the app before building
python nettools_app.py
```

---

## Success Indicators

Build is successful when you see:

```
============================================================
✓ Build completed successfully!
============================================================

Your executable is ready at:
  dist/NetToolsSuite.exe
```

And the file exists:
```batch
dir dist\NetToolsSuite.exe
```

You should see a file around 30-40 MB in size.

---

**Most common issue:** Forgetting to install dependencies!

**Always run first:**
```batch
pip install -r requirements.txt
```

Then you're good to go! 🚀
