# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller spec file for VRCPhoto2URL Desktop Client
Creates a standalone executable with all dependencies
"""

import sys
from pathlib import Path

# Get paths
client_dir = Path(SPECPATH)
src_dir = client_dir / "src"
project_root = client_dir.parent

block_cipher = None

a = Analysis(
    ['launch_desktop_client.py'],
    pathex=[str(client_dir), str(src_dir)],
    binaries=[],
    datas=[
        # Include config example
        ('client_config.json.example', '.'),
        # Include any other data files if needed
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'PySide6.QtNetwork',
        'requests',
        'watchdog',
        'watchdog.observers',
        'watchdog.events',
        'PIL',
        'PIL.Image',
        'PIL.ImageQt',
        'src.modern_client',
        'src.server_client',
        'src.ui_components',
        'src.settings_dialog',
        'src.connection_dialog',
        'src.workers.upload_worker',
        'src.workers.monitor_worker',
        'src.workers.delete_worker',
        'src.utils.file_utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'jupyter',
        'IPython',
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
    name='VRCPhoto2URL-Desktop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for windowed application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file path here if you have one
    version='version_info.txt'  # Will create this separately
)
