"""
Build script for PAN-OS Generator executable
Creates a standalone executable using PyInstaller

Usage:
    python build_panos_generator.py
"""

import PyInstaller.__main__
import os

# Get the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the build parameters
PyInstaller.__main__.run([
    'panos_generator.py',                    # Main script
    '--name=PAN-OS-Generator',               # Executable name
    '--onefile',                             # Single executable file
    '--windowed',                            # No console window (GUI app)
    '--icon=NONE',                           # No icon (add if you have one)
    '--add-data=design_constants.py;.',      # Include design constants
    '--add-data=ui_components.py;.',         # Include UI components
    '--clean',                               # Clean PyInstaller cache
    '--noconfirm',                           # Overwrite without asking
    f'--distpath={script_dir}/dist',         # Output directory
    f'--workpath={script_dir}/build',        # Build directory
    f'--specpath={script_dir}',              # Spec file location
])

print("\n" + "="*70)
print("Build Complete!")
print("="*70)
print(f"\nExecutable location: {script_dir}/dist/PAN-OS-Generator.exe")
print("\nYou can now run the standalone executable without Python installed!")
print("="*70 + "\n")
