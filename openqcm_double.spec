# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for openQCM Dual — one-file build.

Usage:
    pyinstaller openqcm_double.spec

Output:
    dist/openQCM_Dual.exe
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
        "numpy.core._multiarray_tests",
        "serial",
        "serial.tools",
        "serial.tools.list_ports",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Unused GUI / science libraries
        "tkinter", "matplotlib", "scipy", "PIL", "pandas",
        # Unused PyQt5 modules (we only need QtCore, QtGui, QtWidgets)
        "PyQt5.QtWebEngine", "PyQt5.QtWebEngineCore", "PyQt5.QtWebEngineWidgets",
        "PyQt5.QtWebChannel", "PyQt5.QtWebSockets",
        "PyQt5.QtMultimedia", "PyQt5.QtMultimediaWidgets",
        "PyQt5.QtBluetooth", "PyQt5.QtNfc",
        "PyQt5.QtNetwork", "PyQt5.QtNetworkAuth",
        "PyQt5.QtSql", "PyQt5.QtXml", "PyQt5.QtXmlPatterns",
        "PyQt5.QtDBus", "PyQt5.QtDesigner", "PyQt5.QtHelp",
        "PyQt5.QtLocation", "PyQt5.QtPositioning", "PyQt5.QtSensors",
        "PyQt5.QtSerialPort", "PyQt5.QtSvg",
        "PyQt5.QtTest", "PyQt5.QtTextToSpeech",
        "PyQt5.Qt3DCore", "PyQt5.Qt3DExtras", "PyQt5.Qt3DInput",
        "PyQt5.Qt3DLogic", "PyQt5.Qt3DRender", "PyQt5.Qt3DAnimation",
        "PyQt5.QtQuick", "PyQt5.QtQuickWidgets", "PyQt5.QtQml",
        "PyQt5.QtRemoteObjects", "PyQt5.QtChart",
        # Unused pyqtgraph backends
        "OpenGL", "PyOpenGL",
        # Unused numpy extras
        "numpy.f2py", "numpy.distutils",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Strip unused Qt plugins and DLLs that survive the excludes list
_QT_PLUGIN_KEEP = {"platforms", "styles", "imageformats"}
a.binaries = [
    (name, path, typ) for name, path, typ in a.binaries
    if not any(skip in name.lower() for skip in [
        "qtwebengine", "qt5web", "qt5multimedia", "qt5network",
        "qt5sql", "qt5svg", "qt5xml", "qt5bluetooth", "qt5nfc",
        "qt5location", "qt5sensors", "qt5serialport", "qt5quick",
        "qt5qml", "qt5remoteobjects", "qt5dbus", "qt5designer",
        "qt5help", "qt5test", "qt53d", "qt5chart",
        "opengl32sw",
        "d3dcompiler",
    ])
]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="openQCM_Dual",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON if os.path.exists(ICON) else None,
)
