# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller specification file for Video Downloader."""

import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_data_files

block_cipher = None
project_root = Path(SPECPATH).parent.resolve()

# Collect CustomTkinter assets
ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all('customtkinter')

# Application assets (icons, images)
datas = [
    (str(project_root / 'assets'), 'assets'),
    (str(project_root / 'app' / 'database' / 'schema.sql'), 'app/database'),
] + ctk_datas

binaries = list(ctk_binaries)

hiddenimports = [
    'sqlite3',
    'platformdirs',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'yt_dlp',
] + ctk_hiddenimports

icon_path = str(project_root / 'assets' / 'icons' / 'app_icon.ico')

a = Analysis(
    [str(project_root / 'main.py')],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'ruff', 'tkinter.test'],
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
    name='VideoDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path if os.path.exists(icon_path) else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VideoDownloader',
)
