# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for NetTools Suite
Creates a standalone Windows executable with all dependencies
"""

block_cipher = None

# Analysis: Collect all files and dependencies
a = Analysis(
    ['nettools_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('design_constants.py', '.'),
        ('ui_components.py', '.'),
        ('tools/*.py', 'tools'),
        ('oui.txt', '.'),  # MAC address vendor database
    ],
    hiddenimports=[
        'pythonping',
        'customtkinter',
        'PIL',
        'PIL._imagingtk',
        'PIL._tkinter_finder',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch',
        'tensorflow',
        'numpy.testing',
        'pytest',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove unnecessary files to reduce size
a.datas = [x for x in a.datas if not x[0].startswith('matplotlib/mpl-data/sample_data')]
a.datas = [x for x in a.datas if not x[0].startswith('matplotlib/tests')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='NetTools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='network_icon.ico' if os.path.exists('network_icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NetTools',
)
