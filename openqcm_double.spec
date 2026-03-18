# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for openQCM Dual — one-directory build.

Usage:
    pyinstaller openqcm_double.spec

Output:
    dist/openQCM_Dual/openQCM_Dual.exe
"""

import os

block_cipher = None
ROOT = os.path.abspath(".")
ICON = os.path.join(ROOT, "openqcm", "gui", "assets", "openqcm.ico")

a = Analysis(
    ["run.py"],
    pathex=[ROOT],
    binaries=[],
    datas=[
        (os.path.join("openqcm", "gui", "assets", "openqcm.ico"), os.path.join("openqcm", "gui", "assets")),
    ],
    hiddenimports=[
        "pyqtgraph",
        "numpy",
        "serial",
        "serial.tools",
        "serial.tools.list_ports",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "scipy", "PIL", "pandas"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="openQCM_Dual",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON if os.path.exists(ICON) else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="openQCM_Dual",
)
