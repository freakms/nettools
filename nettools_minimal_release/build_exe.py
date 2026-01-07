#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════╗
║           NetTools Minimal - EXE Build Script                 ║
║                                                               ║
║  Erstellt eine standalone Windows-Executable mit PyInstaller  ║
╚═══════════════════════════════════════════════════════════════╝

Verwendung:
    python build_exe.py              # Standard-Build
    python build_exe.py --onefile    # Single-File EXE
    python build_exe.py --debug      # Mit Konsole für Debugging
"""

import PyInstaller.__main__
import os
import sys
import shutil
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# KONFIGURATION
# ═══════════════════════════════════════════════════════════════

APP_NAME = "NetTools_Minimal"
MAIN_SCRIPT = "nettools_minimal.py"
VERSION = "1.0.0"

# Icon-Pfad (optional)
ICON_PATH = "nettools.ico"

# Zu inkludierende Dateien/Ordner
DATA_FILES = [
    ("ui", "ui"),
    ("tools", "tools"),
    ("design_constants.py", "."),
    ("ui_components.py", "."),
]

# Hidden Imports (Module die PyInstaller nicht automatisch findet)
HIDDEN_IMPORTS = [
    "PIL._tkinter_finder",
    "customtkinter",
    "tkinter",
    "tkinter.ttk",
    "dns.resolver",
    "dns.reversename",
]

# Auszuschließende Module (für kleinere EXE)
EXCLUDES = [
    "speedtest",
    "phpipam_client",
    "phpipam_config",
    "matplotlib",  # Nur wenn nicht benötigt
    "numpy",       # Nur wenn nicht benötigt
]

# ═══════════════════════════════════════════════════════════════
# BUILD-FUNKTIONEN
# ═══════════════════════════════════════════════════════════════

def clean_build():
    """Entfernt alte Build-Artefakte"""
    print("🧹 Cleaning old build files...")
    
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = [f'{APP_NAME}.spec']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed: {dir_name}/")
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"   Removed: {file_name}")

def build_exe(onefile=True, debug=False, console=False):
    """
    Erstellt die EXE-Datei
    
    Args:
        onefile: True = einzelne EXE, False = Ordner mit DLLs
        debug: True = zusätzliche Debug-Infos
        console: True = Konsole sichtbar (für Debugging)
    """
    
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║           NetTools Minimal - Build Starting                   ║
╠═══════════════════════════════════════════════════════════════╣
║  App Name:    {APP_NAME:<46} ║
║  Version:     {VERSION:<46} ║
║  Mode:        {'Single File' if onefile else 'Directory':<46} ║
║  Console:     {'Yes' if console else 'No (Windowed)':<46} ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    # PyInstaller-Argumente zusammenstellen
    args = [
        MAIN_SCRIPT,
        f'--name={APP_NAME}',
        '--clean',
        '--noconfirm',
    ]
    
    # Single-File oder Directory
    if onefile:
        args.append('--onefile')
    else:
        args.append('--onedir')
    
    # Fenster-Modus
    if console:
        args.append('--console')
    else:
        args.append('--windowed')
    
    # Icon (falls vorhanden)
    if os.path.exists(ICON_PATH):
        args.append(f'--icon={ICON_PATH}')
        print(f"✓ Using icon: {ICON_PATH}")
    
    # Daten-Dateien hinzufügen
    for src, dst in DATA_FILES:
        if os.path.exists(src):
            # Windows verwendet ; als Separator
            separator = ';' if sys.platform == 'win32' else ':'
            args.append(f'--add-data={src}{separator}{dst}')
            print(f"✓ Including: {src} → {dst}")
    
    # Hidden Imports
    for module in HIDDEN_IMPORTS:
        args.append(f'--hidden-import={module}')
    
    # Excludes (für kleinere EXE)
    for module in EXCLUDES:
        args.append(f'--exclude-module={module}')
    
    # Debug-Modus
    if debug:
        args.append('--debug=all')
    
    print("\n🔨 Building executable...\n")
    print(f"   Command: pyinstaller {' '.join(args)}\n")
    
    # PyInstaller ausführen
    try:
        PyInstaller.__main__.run(args)
        
        # Erfolgsmeldung
        if onefile:
            exe_path = f"dist/{APP_NAME}.exe"
        else:
            exe_path = f"dist/{APP_NAME}/{APP_NAME}.exe"
        
        if os.path.exists(exe_path.replace('/', os.sep)):
            size_mb = os.path.getsize(exe_path.replace('/', os.sep)) / (1024 * 1024)
            print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                    ✅ BUILD SUCCESSFUL                        ║
╠═══════════════════════════════════════════════════════════════╣
║  Output:      {exe_path:<46} ║
║  Size:        {f'{size_mb:.1f} MB':<46} ║
╚═══════════════════════════════════════════════════════════════╝

Zum Ausführen:
    {exe_path}
""")
        else:
            print(f"\n⚠️  Build completed but EXE not found at expected path")
            
    except Exception as e:
        print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                    ❌ BUILD FAILED                            ║
╠═══════════════════════════════════════════════════════════════╣
║  Error: {str(e)[:54]:<54} ║
╚═══════════════════════════════════════════════════════════════╝
""")
        sys.exit(1)

def create_spec_file():
    """Erstellt eine .spec-Datei für erweiterte Konfiguration"""
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# NetTools Minimal - PyInstaller Spec File

block_cipher = None

a = Analysis(
    ['{MAIN_SCRIPT}'],
    pathex=[],
    binaries=[],
    datas=[
        ('ui', 'ui'),
        ('tools', 'tools'),
        ('design_constants.py', '.'),
        ('ui_components.py', '.'),
    ],
    hiddenimports={HIDDEN_IMPORTS},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes={EXCLUDES},
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{ICON_PATH}' if os.path.exists('{ICON_PATH}') else None,
)
'''
    
    spec_file = f"{APP_NAME}.spec"
    with open(spec_file, 'w') as f:
        f.write(spec_content)
    
    print(f"✓ Created: {spec_file}")
    print(f"  Build with: pyinstaller {spec_file}")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    """Hauptfunktion - verarbeitet Kommandozeilen-Argumente"""
    
    # Argumente parsen
    onefile = '--onefile' in sys.argv or '-f' in sys.argv
    debug = '--debug' in sys.argv or '-d' in sys.argv
    console = '--console' in sys.argv or '-c' in sys.argv
    create_spec = '--spec' in sys.argv
    no_clean = '--no-clean' in sys.argv
    
    # Hilfe anzeigen
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        print("""
Optionen:
    --onefile, -f    Single-File EXE (Standard)
    --onedir         Directory mit DLLs (schnellerer Start)
    --console, -c    Konsole anzeigen (für Debugging)
    --debug, -d      Debug-Informationen
    --spec           Nur .spec-Datei erstellen
    --no-clean       Alte Build-Dateien behalten
    --help, -h       Diese Hilfe anzeigen
""")
        sys.exit(0)
    
    # Nur .spec-Datei erstellen
    if create_spec:
        create_spec_file()
        sys.exit(0)
    
    # Build durchführen
    if not no_clean:
        clean_build()
    
    # Standard: onefile wenn nicht anders angegeben
    if '--onedir' in sys.argv:
        onefile = False
    else:
        onefile = True
    
    build_exe(onefile=onefile, debug=debug, console=console)

if __name__ == "__main__":
    main()
