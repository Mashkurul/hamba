# =============================================================
# hamba.spec - PyInstaller build spec for HAMBA
# =============================================================
# Build command:  pyinstaller hamba.spec
# Output:         dist/HAMBA/HAMBA.exe
# =============================================================

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect customtkinter assets (themes, images)
ctk_datas = collect_data_files("customtkinter", include_py_files=True)

a = Analysis(
    ["app.py"],
    pathex=["."],
    binaries=[],
    datas=ctk_datas + [
        # Include the database folder (will be empty on first run – that's fine)
        ("database",  "database"),
        ("models",    "models"),
        ("modules",   "modules"),
        ("gui",       "gui"),
        ("assets",    "assets"),
        ("config.py", "."),
        ("database.py", "."),
    ],
    hiddenimports=[
        "customtkinter",
        "darkdetect",
        "PIL",
        "PIL._tkinter_finder",
        "tkinter",
        "tkinter.ttk",
        "sqlite3",
        "hashlib",
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
    [],
    exclude_binaries=True,
    name="HAMBA",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,      # No black terminal window – GUI only
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/hamba.ico",   # HAMBA cow icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="HAMBA",
)
