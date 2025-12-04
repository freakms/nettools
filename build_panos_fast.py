"""
Fast build script for PAN-OS Generator (no optimization)
Faster build times for testing

Usage:
    python build_panos_fast.py
"""

import PyInstaller.__main__
import os

# Get the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the build parameters (optimized for speed)
PyInstaller.__main__.run([
    'panos_generator.py',                    # Main script
    '--name=PAN-OS-Generator-Fast',          # Executable name
    '--onedir',                              # Directory bundle (faster)
    '--windowed',                            # No console window
    '--icon=NONE',                           # No icon
    '--add-data=design_constants.py;.',      # Include design constants
    '--add-data=ui_components.py;.',         # Include UI components
    '--noconfirm',                           # Overwrite without asking
    '--debug=imports',                       # Debug import issues
    f'--distpath={script_dir}/dist',         # Output directory
    f'--workpath={script_dir}/build',        # Build directory
    f'--specpath={script_dir}',              # Spec file location
])

print("\n" + "="*70)
print("Fast Build Complete!")
print("="*70)
print(f"\nExecutable location: {script_dir}/dist/PAN-OS-Generator-Fast/")
print("\nNote: This is a directory bundle (faster to build but larger)")
print("For production, use build_panos_generator.py for a single-file executable")
print("="*70 + "\n")
