# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launch_desktop_client.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('client_config.json.example', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'requests',
        'pathlib',
        'json',
        'datetime',
        'threading',
        'time',
        'os',
        'sys',
        'subprocess',
        'watchdog',
        'watchdog.observers',
        'watchdog.events',
        'modern_client',
        'connection_dialog',
        'settings_dialog',
        'server_client',
        'ui_components',
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
    name='VRCPhoto2URL-Desktop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon=None,
    version='version_info.txt'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VRCPhoto2URL-Desktop'
)
