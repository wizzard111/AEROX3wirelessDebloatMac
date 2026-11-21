# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for the macOS build ("Aerox Lite.app"). Run from the repository root:
#   python -m PyInstaller --distpath build/dist --workpath build/work packaging/macos/AeroxLite.spec
import os

SRC = os.path.abspath(os.path.join(SPECPATH, '..', '..', 'src'))
# Standard-library parts the app never uses (smaller download, faster start, less memory).
EXCLUDES = ['unittest', 'pydoc', 'doctest', 'pdb', 'test', 'tkinter.test', 'idlelib', 'lib2to3',
            'distutils', 'setuptools', 'pip', 'ensurepip', 'venv', 'xmlrpc', 'sqlite3', 'curses',
            'turtle', 'turtledemo', 'PIL.ImageQt', 'numpy',
            # image formats / colour management the app never uses (the AVIF codec alone is ~7.5 MB)
            'PIL._avif', 'PIL.AvifImagePlugin', 'PIL._webp', 'PIL.WebPImagePlugin', 'PIL._imagingcms', 'PIL.ImageCms',
            # no network access: drops OpenSSL (~6 MB); hashlib falls back to its built-in hashes
            'ssl', '_ssl', '_hashlib']


def trim_datas(datas):
    """Tcl's time-zone database is only used by Tcl's own clock command, which the app does not use."""
    return [d for d in datas if '_tcl_data/tzdata' not in d[0].replace('\\', '/')]

VERSION = '5.0.1'

a = Analysis(
    [os.path.join(SRC, 'aerox_lite.py')],
    pathex=[SRC],
    binaries=[],
    datas=[],
    hiddenimports=['generic', 'generic_ui', 'model_art', 'rivalcfg', 'rclick', 'smartbattery', 'helpers', 'osinput', 'osplatform', 'hid',
                   'PIL._tkinter_finder', 'pystray._darwin',
                   'pynput.keyboard._darwin', 'pynput.mouse._darwin', 'ApplicationServices'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDES,
    noarchive=False,
    optimize=2,
)
a.datas = trim_datas(a.datas)
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
