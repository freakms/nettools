#!/usr/bin/env python3
"""
Build script for NetTools Suite executable
Creates a single-file Windows executable using PyInstaller
"""

import PyInstaller.__main__
import sys
import os
from pathlib import Path


def create_icon():
    """Create application icon"""
    try:
        from nettools_app import NetworkIcon
        icon = NetworkIcon.create_icon(256)
        icon_path = Path("nettools_icon.ico")
        
        # Save as ICO for Windows
        icon.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        print(f"✓ Icon created: {icon_path}")
        return str(icon_path)
    except Exception as e:
        print(f"! Warning: Could not create icon: {e}")
        return None


def build_executable():
    """Build single-file executable"""
    print("\n" + "="*60)
    print("NetTools Suite - Build Script")
    print("="*60 + "\n")
    
    # Create icon
    icon_path = create_icon()
    
    # PyInstaller arguments
    args = [
        'nettools_app.py',              # Main script
        '--onefile',                     # Single file executable
        '--windowed',                    # No console window (Windows)
        '--name=NetToolsSuite',          # Executable name
        '--clean',                       # Clean build
    ]
    
    # Add icon if available
    if icon_path and os.path.exists(icon_path):
        args.append(f'--icon={icon_path}')
    
    # Add version info for Windows (only if file exists)
    if sys.platform == 'win32':
        version_file = 'version_info.txt'
        if os.path.exists(version_file):
            args.append(f'--version-file={version_file}')
    
    # Hidden imports that might be needed
    hidden_imports = [
        'PIL._tkinter_finder',
        'customtkinter',
        'pythonping',
    ]
    
    for imp in hidden_imports:
        args.append(f'--hidden-import={imp}')
    
    print("Building executable with PyInstaller...\n")
    print("Arguments:")
    for arg in args:
        print(f"  {arg}")
    print()
    
    # Run PyInstaller
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "="*60)
        print("✓ Build completed successfully!")
        print("="*60)
        print("\nExecutable location:")
        print("  dist/NetToolsSuite.exe")
        print("\nYou can now distribute this single file!\n")
    except Exception as e:
        print("\n" + "="*60)
        print(f"✗ Build failed: {e}")
        print("="*60 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    build_executable()
