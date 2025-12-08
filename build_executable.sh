#!/bin/bash
# NetTools Suite - Build Executable Script (Linux)
# This creates the standalone executable that can be packaged later

echo "========================================"
echo "NetTools Suite - Build Executable"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    exit 1
fi

# Check if PyInstaller is installed
if ! python -m pip show pyinstaller &> /dev/null; then
    echo ""
    echo "ERROR: PyInstaller is not installed"
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

echo ""
echo "Step 1/2: Cleaning previous builds..."
rm -rf dist build
mkdir -p installer_output

echo ""
echo "Step 2/2: Building executable with PyInstaller..."
python -m PyInstaller nettools.spec --noconfirm

if [ $? -ne 0 ]; then
    echo "ERROR: PyInstaller build failed"
    exit 1
fi

echo ""
echo "========================================"
echo "BUILD COMPLETE!"
echo "========================================"
echo ""
echo "Executable created in: dist/NetTools/"
echo ""
echo "⚠️  IMPORTANT:"
echo "The Windows installer (.exe) can only be created on Windows"
echo "using Inno Setup. The standalone executable is ready in dist/"
echo ""
echo "To create the installer:"
echo "1. Copy all files to a Windows machine"
echo "2. Install Inno Setup: https://jrsoftware.org/isdl.php"
echo "3. Run: build_installer.bat"
echo ""
