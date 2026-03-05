# -*- mode: python ; coding: utf-8 -*-
"""
MindFlow Markdown — PyInstaller spec file
Build: pyinstaller mindflow.spec

DEBUGGING:
  - For development: Change console=True below to see errors in real-time
  - For final build: Set console=False to hide console
  - Errors are ALWAYS logged to ~/.mindflow/mindflow.log (see main.py logging setup)

Requirements on target machine:
  - Windows 10/11 (for PowerShell COM dialogs)
  - Edge WebView2 (pre-installed on Windows 10/11)
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Bundle the full assets folder (HTML, CSS, JS, vendor scripts)
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'webview',
        'webview.platforms.winforms',
        'subprocess',  # Used for PowerShell dialogs
        'threading',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',  # Removed — using PowerShell instead
    ],
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
    name='MindFlow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True during debugging to see console output
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo.ico',  # Custom icon
)

