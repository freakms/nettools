#!/bin/bash
################################################################################
# NetTools Suite - Linux Build Script
################################################################################
#
# This script automates the build process for Linux users.
# Run: chmod +x build_linux.sh && ./build_linux.sh
#
# Requirements:
#   - Python 3.8 or higher
#   - pip package manager
#
# Output:
#   - dist/NetToolsSuite (executable binary)
#
################################################################################

set -e  # Exit on error

echo ""
echo "============================================================"
echo "NetTools Suite - Linux Build Script"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed!"
    echo ""
    echo "Please install Python 3.8 or higher:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo "  Arch: sudo pacman -S python python-pip"
    echo ""
    exit 1
fi

echo "[1/5] Python found:"
python3 --version
echo ""

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "[ERROR] pip3 is not installed!"
    echo ""
    echo "Please install pip:"
    echo "  Ubuntu/Debian: sudo apt install python3-pip"
    echo "  Fedora: sudo dnf install python3-pip"
    echo ""
    exit 1
fi

echo "[2/5] pip found:"
pip3 --version
echo ""

# Install dependencies
echo "[3/5] Installing dependencies..."
echo ""
pip3 install --user -r requirements.txt || {
    echo ""
    echo "[ERROR] Failed to install dependencies!"
    echo ""
    exit 1
}

echo ""
echo "[4/5] Building executable..."
echo ""
python3 build_exe.py || {
    echo ""
    echo "[ERROR] Build failed!"
    echo ""
    exit 1
}

echo ""
echo "[5/5] Setting executable permissions..."
chmod +x dist/NetToolsSuite

echo ""
echo "============================================================"
echo "Build completed successfully!"
echo "============================================================"
echo ""
echo "Your executable is ready at:"
echo "  dist/NetToolsSuite"
echo ""
echo "To run:"
echo "  ./dist/NetToolsSuite"
echo ""
echo "For ping to work without sudo, run:"
echo "  sudo setcap cap_net_raw+ep \$(which python3)"
echo ""
echo "Or run with sudo:"
echo "  sudo ./dist/NetToolsSuite"
echo ""

# Ask if user wants to grant capabilities
read -p "Grant network capabilities to Python now? (requires sudo) [Y/n]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo "Granting capabilities..."
    sudo setcap cap_net_raw+ep $(which python3) && \
        echo "✓ Capabilities granted! You can now run without sudo." || \
        echo "✗ Failed to grant capabilities. Run with sudo instead."
fi

echo ""
echo "Build script completed!"
