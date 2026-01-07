#!/usr/bin/env python3
"""
NetTools Minimal - Fast Build Script
Creates standalone executable using PyInstaller
"""

import PyInstaller.__main__
import os
import shutil

def build():
    # Clean previous build
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    PyInstaller.__main__.run([
        'nettools_minimal.py',
        '--name=NetTools_Minimal',
        '--onefile',
        '--windowed',
        '--icon=../nettools.ico' if os.path.exists('../nettools.ico') else '',
        '--add-data=ui;ui',
        '--add-data=tools;tools',
        '--add-data=design_constants.py;.',
        '--add-data=ui_components.py;.',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=customtkinter',
        '--exclude-module=speedtest',
        '--exclude-module=phpipam_client',
        '--exclude-module=phpipam_config',
        '--clean',
        '--noconfirm',
    ])
    
    print("\n✅ Build complete: dist/NetTools_Minimal.exe")

if __name__ == "__main__":
    build()
