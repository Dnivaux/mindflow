# -*- mode: python ; coding: utf-8 -*-
"""
MindFlow Markdown — PyInstaller spec file
Build: pyinstaller mindflow.spec

Requirements on target machine:
  - Node.js (for npx markmap-cli)
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
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    console=False,           # No console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo.ico',         # Custom icon
)
