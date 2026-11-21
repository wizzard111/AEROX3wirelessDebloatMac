# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for the macOS build: dist/Aerox Lite.app

VERSION = '5.0.0'

a = Analysis(
    ['aerox_lite.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['rclick', 'smartbattery', 'helpers', 'osinput', 'osplatform', 'hid',
                   'PIL._tkinter_finder', 'pystray._darwin',
                   'pynput.keyboard._darwin', 'pynput.mouse._darwin'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Aerox Lite',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Aerox Lite',
)
app = BUNDLE(
    coll,
    name='Aerox Lite.app',
    icon=None,
    bundle_identifier='io.github.aeroxlite',
    version=VERSION,
    info_plist={
        'CFBundleShortVersionString': VERSION,
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '11.0',
        'NSHumanReadableCopyright': 'MIT License',
    },
)
