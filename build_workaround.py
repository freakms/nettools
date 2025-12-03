#!/usr/bin/env python3
"""
Build script with workaround for locked files
Renames dist folder instead of deleting it
"""

import PyInstaller.__main__
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime


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


def handle_locked_dirs():
    """Rename locked directories instead of deleting them"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Handle dist folder
    if os.path.exists("dist"):
        backup_name = f"dist_old_{timestamp}"
        try:
            print(f"Renaming dist to {backup_name}...")
            os.rename("dist", backup_name)
            print(f"✓ Old dist renamed to {backup_name}")
        except Exception as e:
            print(f"✗ Could not rename dist: {e}")
            print("\nManual steps needed:")
            print("1. Close ALL NetToolsSuite windows")
            print("2. Open Task Manager (Ctrl+Shift+Esc)")
            print("3. End all 'NetToolsSuite.exe' processes")
            print("4. Close any File Explorer windows showing dist folder")
            print("5. Try again")
            return False
    
    # Handle build folder
    if os.path.exists("build"):
        try:
            shutil.rmtree("build")
            print("✓ Build folder cleaned")
        except:
            backup_name = f"build_old_{timestamp}"
            try:
                os.rename("build", backup_name)
                print(f"✓ Build renamed to {backup_name}")
            except Exception as e:
                print(f"! Warning: Could not clean build: {e}")
    
    return True


def build_executable():
    """Build directory-based executable (FAST)"""
    print("\n" + "="*60)
    print("NetTools Suite - Build with Workaround")
    print("="*60 + "\n")
    
    # Handle locked directories
    if not handle_locked_dirs():
        return
    
    # Create icon
    icon_path = create_icon()
    
    # PyInstaller arguments
    args = [
        'nettools_app.py',
        '--onedir',                      # Directory mode (FAST)
        '--windowed',
        '--name=NetToolsSuite',
        '--add-data=oui_database.json;.',
        '--add-data=tools;tools',        # Include tools package
    ]
    
    # Add icon if available
    if icon_path and os.path.exists(icon_path):
        args.append(f'--icon={icon_path}')
    
    # Add version info
    if sys.platform == 'win32':
        version_file = 'version_info.txt'
        if os.path.exists(version_file):
            args.append(f'--version-file={version_file}')
    
    # Hidden imports
    hidden_imports = [
        'PIL._tkinter_finder',
        'customtkinter',
        'pythonping',
    ]
    
    for imp in hidden_imports:
        args.append(f'--hidden-import={imp}')
    
    print("Building executable...\n")
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
        print("  dist/NetToolsSuite/NetToolsSuite.exe")
        print("\nDistribute the entire 'dist/NetToolsSuite' folder\n")
    except Exception as e:
        print("\n" + "="*60)
        print(f"✗ Build failed: {e}")
        print("="*60 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    build_executable()
