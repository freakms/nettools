#!/usr/bin/env python3
"""
Quick version checker for NetTools Suite
Run this to verify which version you have
"""

import sys
from pathlib import Path

def check_version():
    print("=" * 70)
    print("NetTools Suite - Version Checker")
    print("=" * 70)
    print()
    
    # Check if running from source or exe
    if getattr(sys, 'frozen', False):
        print("✓ Running from: EXECUTABLE (.exe)")
        print(f"  Location: {sys.executable}")
    else:
        print("✓ Running from: PYTHON SCRIPT")
        print(f"  Location: {__file__}")
    
    print()
    
    # Try to read version from nettools_app.py
    try:
        app_file = Path(__file__).parent / "nettools_app.py"
        if app_file.exists():
            with open(app_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find version
            for line in content.split('\n'):
                if 'APP_VERSION' in line and '=' in line:
                    version = line.split('=')[1].strip().strip('"').strip("'")
                    print(f"✓ Source code version: {version}")
                    break
        else:
            print("⚠ nettools_app.py not found (may be running from .exe)")
    except Exception as e:
        print(f"⚠ Could not read version from source: {e}")
    
    print()
    
    # Check for sidebar vs tabs
    print("=" * 70)
    print("Expected in v1.3.0 (Modern UI):")
    print("=" * 70)
    print("  ✓ Sidebar on the LEFT side")
    print("  ✓ 'NetTools' branding at top")
    print("  ✓ 'Professional Suite' subtitle")
    print("  ✓ Navigation buttons: 🔍 IPv4 Scanner, 🏷️ MAC Formatter, 📊 Scan Comparison")
    print("  ✓ Theme selector at BOTTOM of sidebar")
    print("  ✓ NO tabs at the top")
    print()
    
    print("If you see in v1.2.1 (Old UI):")
    print("=" * 70)
    print("  ✗ Tabs at the TOP")
    print("  ✗ Header bar with 'NetTools Suite'")
    print("  ✗ 'IPv4 Scanner & MAC Formatter' subtitle")
    print("  ✗ Theme selector in TOP-RIGHT corner")
    print()
    
    print("=" * 70)
    print("How to fix if you see OLD UI:")
    print("=" * 70)
    print("  1. Close ALL instances of NetTools app")
    print("  2. Delete build, dist folders and *.spec files")
    print("  3. Run: rebuild_clean.bat")
    print("  4. Run the NEW .exe from: dist\\NetToolsSuite\\NetToolsSuite.exe")
    print()
    
    print("=" * 70)
    print("Quick commands:")
    print("=" * 70)
    print("  Clean rebuild: rebuild_clean.bat")
    print("  Fast rebuild:  python build_exe_fast.py")
    print("  Test source:   python nettools_app.py")
    print()

if __name__ == "__main__":
    check_version()
    input("\nPress Enter to exit...")
