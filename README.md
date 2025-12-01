Pre-Word:
I am not a developer, but I made this App to optimize and pimp my daily business.
So i do not want to get this Commercial, but it would be glad to get some back for emergent coins ;)

This App was developed also with emergent.sh

https://www.paypal.com/donate/?hosted_button_id=PBAARPBKPNG86

# NetTools Suite

**Version:** 1.0.0  
**Author:** freakms  
**Description:** Modern desktop application for network utilities - IPv4 Scanner & MAC Formatter

---

## Features

### 🔍 IPv4 Scanner
- **CIDR Network Scanning**: Supports any valid CIDR notation (e.g., `192.168.1.0/24`, `10.0.0.0/8`)
- **Adjustable Speed**: Choose between Gentle (600ms timeout), Medium (300ms), or Aggressive (150ms)
- **Parallel Scanning**: High-performance multi-threaded scanning (32-128 concurrent threads)
- **Real-time Results**: Live progress updates with visual status indicators
- **Filtering**: Option to show only responding hosts
- **CSV Export**: Export scan results to desktop
- **Smart Warnings**: Alerts for large network scans

### 🔧 MAC Formatter
- **Flexible Input**: Accept MAC addresses in any format
- **Multiple Outputs**: Generate 4 standard formats:
  - Plain: `AABBCCDDEEFF`
  - Colon: `AA:BB:CC:DD:EE:FF`
  - Dash-4: `AABB-CCDD-EEFF`
  - Dash-2: `AA-BB-CC-DD-EE-FF`
- **Vendor Commands**: Auto-generate switch commands for:
  - EXTREME CLI
  - Huawei CLI
  - Huawei Access-User CLI
  - Dell CLI
- **Quick Copy**: One-click copy for all outputs

### 🎨 Modern UI
- **Light/Dark Theme**: Toggle between themes
- **Custom Icon**: Network topology visualization
- **Responsive Design**: Resizable interface with minimum 980x680
- **Keyboard Shortcuts**:
  - `Enter`: Start scan or copy first MAC format
  - `Ctrl+E`: Export CSV

---

## Installation & Setup

### Prerequisites
- **Python 3.8 or higher**
- **Windows, macOS, or Linux**

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the Application

```bash
python nettools_app.py
```

---

## Building Standalone Executable

### Build Single-File .exe (Windows)

```bash
python build_exe.py
```

**Output**: `dist/NetToolsSuite.exe`

### Manual Build (Alternative)

If you prefer to use PyInstaller directly:

```bash
# Windows (single file)
pyinstaller --onefile --windowed --name=NetToolsSuite --icon=nettools_icon.ico nettools_app.py

# macOS (app bundle)
pyinstaller --onefile --windowed --name=NetToolsSuite nettools_app.py

# Linux (single file)
pyinstaller --onefile --name=NetToolsSuite nettools_app.py
```

---

## Usage Guide

### IPv4 Scanner

1. **Enter CIDR**: Type network range (e.g., `192.168.1.0/24`)
2. **Select Aggressiveness**: Choose scan speed
3. **Click "Start Scan"**: Begin scanning
4. **View Results**: Real-time updates with status indicators
   - 🟢 Green dot = Host is online
   - ⚫ Gray dot = No response
5. **Filter Results**: Check "Show only responding hosts" to filter
6. **Export**: Click "Export as CSV" or press `Ctrl+E`

**Tips:**
- Smaller networks (/24-/32) scan quickly
- Large networks (/16-/20) will show a warning
- Use "Aggressive" mode for faster scans on reliable networks
- Use "Gentle" mode for slower/unreliable networks

### MAC Formatter

1. **Enter MAC Address**: Type in any format
   - Valid: `AA:BB:CC:DD:EE:FF`, `AABBCCDDEEFF`, `AA-BB-CC-DD-EE-FF`
2. **View Formats**: All 4 standard formats appear instantly
3. **Copy**: Click any "Copy" button to copy to clipboard
4. **Switch Commands**: View vendor-specific commands (toggle with button)
5. **Quick Copy**: Press `Enter` to copy Format 1

---

## Technical Details

### Architecture
- **GUI Framework**: CustomTkinter (modern themed Tkinter)
- **Network Library**: pythonping (ICMP without admin rights)
- **Threading**: ThreadPoolExecutor for parallel operations
- **IP Calculations**: ipaddress module (built-in Python)

### Performance
- **Scan Speed**: 32-128 concurrent threads
- **Timeout Range**: 150-600ms per host
- **Memory Usage**: ~50-80MB (running)
- **Executable Size**: ~25-40MB (single file)

### Platform Support
- ✅ **Windows**: Full support, no admin rights needed
- ✅ **macOS**: Full support, may require network permissions
- ✅ **Linux**: Full support, may require capabilities for ICMP

---

## Troubleshooting

### "Ping failed" or "Permission denied"
- **Windows**: Should work without admin rights
- **Linux**: Run `sudo setcap cap_net_raw+ep $(which python3)` or run as sudo
- **macOS**: Grant network permissions when prompted

### Build fails with "Module not found"
```bash
pip install --upgrade -r requirements.txt
```

### Executable won't start
- Check antivirus (may block unsigned executables)
- Run from command line to see error messages
- Rebuild with `--debug=all` flag for detailed logs

### Dark theme not applying
- Restart the application
- Check system theme settings

---

## Development

### Project Structure
```
/app/
├── nettools_app.py      # Main application
├── build_exe.py         # Build script
├── requirements.txt     # Dependencies
└── README.md           # This file
```

### Extending Features

**Add new network tool:**
1. Create new tab in `create_tabs()`
2. Implement tool logic
3. Add UI elements

**Customize theme:**
1. Modify colors in `ctk.set_default_color_theme()`
2. Adjust `change_theme()` method

---

## License & Credits

**Created by:** freakms  
**Framework:** CustomTkinter by Tom Schimansky  
**Ping Library:** pythonping by Alessandro Maggio  

---

## Version History

### v1.0.0 (2025)
- Initial release
- IPv4 Scanner with CIDR support
- MAC Formatter with vendor commands
- Light/Dark theme
- Single-file executable build

---

## Support

For issues or feature requests, please contact the developer or check the documentation.

**Enjoy using NetTools Suite! 🚀**
