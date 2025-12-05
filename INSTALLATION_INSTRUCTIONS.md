# NetTools Installation Instructions

## Required Dependencies

The NetTools application requires several Python packages to run. After downloading the application, you need to install these dependencies.

## Installation Steps

### Option 1: Install from requirements.txt (Recommended)

1. Open Command Prompt or PowerShell in the application directory
2. Run the following command:

```bash
pip install -r requirements.txt
```

### Option 2: Install Individual Packages

If you don't have a requirements.txt file or prefer manual installation:

```bash
pip install customtkinter
pip install pythonping
pip install pillow
pip install matplotlib
```

## Verify Installation

After installation, verify all packages are installed:

```bash
pip list | findstr "customtkinter pythonping pillow matplotlib"
```

You should see output showing all four packages.

## Common Issues

### Issue: "pip is not recognized"
**Solution:** Make sure Python is added to your PATH, or use:
```bash
python -m pip install -r requirements.txt
```

### Issue: Permission Denied
**Solution:** Run Command Prompt as Administrator, or use:
```bash
pip install --user -r requirements.txt
```

### Issue: Multiple Python Versions
**Solution:** Specify the Python version:
```bash
python3 -m pip install -r requirements.txt
# or
py -3 -m pip install -r requirements.txt
```

## Running the Application

After installing dependencies, run:

```bash
python nettools_app.py
```

Or double-click `nettools_app.py` if Python is associated with .py files.

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows 10/11, Linux, macOS
- **RAM**: Minimum 512 MB (1 GB recommended)
- **Display**: 1280x720 minimum resolution

## Package Purposes

- **customtkinter**: Modern UI framework
- **pythonping**: ICMP ping functionality
- **pillow**: Image processing for icons
- **matplotlib**: Real-time graph rendering for Live Ping Monitor
