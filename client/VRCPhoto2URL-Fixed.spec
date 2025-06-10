# -*- mode: python ; coding: utf-8 -*-

"""
Fixed PyInstaller spec file for VRCPhoto2URL Desktop Client
Properly includes all local modules and dependencies
"""

import sys
import os
from pathlib import Path

# Get paths
client_dir = Path(SPECPATH)
src_dir = client_dir / "src"

block_cipher = None

# Add src directory to Python path
sys.path.insert(0, str(src_dir))

a = Analysis(
    ['launch_desktop_client.py'],
    pathex=[str(client_dir), str(src_dir)],
    binaries=[],
    datas=[
        # Include config example
        ('client_config.json.example', '.'),
        # Include any static files if needed
    ],
    hiddenimports=[
        # PySide6 modules
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'PySide6.QtNetwork',
          # Standard library modules
        'json',
        'pathlib',
        'threading',
        'queue',
        'datetime',
        'uuid',
        'base64',
        'urllib.parse',
        'urllib.request',
        'email',
        'email.message',
        'collections.abc',
        'calendar',
        
        # Third-party modules
        'requests',
        'requests.adapters',
        'requests.auth',
        'requests.exceptions',
        'PIL',
        'PIL.Image',
        'PIL.ImageQt',
        'watchdog',
        'watchdog.observers',
        'watchdog.events',
        
        # Local application modules - CRITICAL!
        'src',
        'src.modern_client',
        'src.server_client', 
        'src.ui_components',
        'src.settings_dialog',
        'src.connection_dialog',
        'src.workers',
        'src.workers.upload_worker',
        'src.workers.monitor_worker',
        'src.workers.delete_worker',
        'src.utils',
        'src.utils.file_utils',
        'src.ui',
        'src.ui.ui_components',
        'src.ui.settings_dialog',
        'src.ui.connection_dialog',
        'src.ui.main_window',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'jupyter',
        'IPython',
        'test',
        'unittest',
        'doctest',
        'xmlrpc',
        'pydoc',
        'wsgiref',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filter out some problematic modules
a.binaries = [x for x in a.binaries if not x[0].startswith('api-ms-win-')]

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
    console=True,  # Enable console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version='version_info.txt'
)
