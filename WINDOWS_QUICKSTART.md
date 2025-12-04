# Windows Quick Start Guide - PAN-OS Generator

## ✅ Quick Test (No Build Required)

**Just run the application directly:**

```powershell
python panos_generator.py
```

That's it! The GUI should open immediately.

---

## 🔧 Prerequisites

Make sure you have:
- Python 3.11+ installed
- Required packages installed:
  ```powershell
  pip install customtkinter
  ```

---

## 🚀 Running the Application

### Method 1: Direct Run (Recommended for Testing)
```powershell
cd "C:\Users\malte.schad\Downloads\nettools-main (2)\nettools-main"
python panos_generator.py
```

### Method 2: Build Executable (Optional)

**Fast Build (for testing):**
```powershell
python build_panos_fast.py
```
Output: `dist\PAN-OS-Generator-Fast\PAN-OS-Generator-Fast.exe`

**Production Build (single file):**
```powershell
python build_panos_generator.py
```
Output: `dist\PAN-OS-Generator.exe`

---

## ⚠️ Common Windows Issues

### Issue 1: "python3 not found"
**Solution:** On Windows, use `python` not `python3`
```powershell
# ❌ Wrong
python3 panos_generator.py

# ✅ Correct
python panos_generator.py
```

### Issue 2: "SyntaxError: unterminated string literal"
**Cause:** Running the wrong file or file corruption
**Solution:** 
1. Make sure you're in the correct directory
2. Re-download if needed
3. Use `python` (not `python3`)

### Issue 3: "No module named 'customtkinter'"
**Solution:** Install required packages:
```powershell
pip install customtkinter
```

### Issue 4: "Python was not found"
**Solution:** Install Python from:
- Microsoft Store, OR
- https://www.python.org/downloads/
  - ✅ Check "Add Python to PATH" during installation

---

## 📁 File Locations (After Build)

```
nettools-main/
├── panos_generator.py          # Main app (run this)
├── build_panos_generator.py    # Production build script
├── build_panos_fast.py         # Fast build script
│
├── dist/                        # Build outputs
│   ├── PAN-OS-Generator.exe    # Single-file executable
│   └── PAN-OS-Generator-Fast/  # Directory with executable
│       └── PAN-OS-Generator-Fast.exe
│
└── build/                       # Temporary build files (can delete)
```

---

## 🎯 First Test Run

1. **Open PowerShell** in the nettools folder
2. **Run:**
   ```powershell
   python panos_generator.py
   ```
3. **The GUI should open** with two tabs:
   - 🎯 Name Generator
   - 🌐 Address Objects

4. **Try Name Generator:**
   - Enter some server names (one per line)
   - Enter corresponding IPs (one per line)
   - Click "🎯 Generate Object Names"
   - See the preview
   - Click "💻 Generate CLI Commands"
   - Commands appear on the right

5. **Test Copy/Download:**
   - Click "📋 Copy All" to copy commands
   - Click "⬇️ Download" to save to file

---

## 🐛 Still Having Issues?

**Check Python installation:**
```powershell
python --version
```
Should show: `Python 3.11.x` or higher

**Check if customtkinter is installed:**
```powershell
python -c "import customtkinter; print('OK')"
```
Should show: `OK`

**List installed packages:**
```powershell
pip list | findstr customtkinter
```

---

## 💡 Tips

- **Don't need to build** to test - just run the .py file directly
- **Building takes time** - only needed for distribution
- **Fast build** creates a folder with exe (faster to build)
- **Production build** creates a single .exe file (slower to build, easier to distribute)

---

## 🔄 If You Want to Update

If I make changes to the app:
1. Replace `panos_generator.py` with the new version
2. Run `python panos_generator.py` to test
3. Rebuild if needed: `python build_panos_generator.py`

---

## ✅ Success Checklist

- [ ] Python installed and working (`python --version`)
- [ ] customtkinter installed (`pip install customtkinter`)
- [ ] In correct directory (where panos_generator.py is located)
- [ ] Run: `python panos_generator.py`
- [ ] GUI opens without errors
- [ ] Can switch between tabs
- [ ] Can generate commands
- [ ] Can copy/download commands

If all checked ✅ you're ready to use it!

---

**Need help?** Let me know what error you see and I'll help troubleshoot!
