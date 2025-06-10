#!/usr/bin/env python3
"""
Build VRCPhoto2URL Desktop Executable
Creates a standalone .exe file for distribution
"""

import subprocess
import sys
import os
from pathlib import Path
import shutil

def install_pyinstaller():
    """Install PyInstaller if not available"""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
        return True
    except ImportError:
        print("📦 Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False

def create_spec_file():
    """Create PyInstaller spec file for VRCPhoto2URL"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launch_desktop_client.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('client_config.json.example', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtWidgets', 
        'PySide6.QtGui',
        'requests',
        'json',
        'pathlib',
        'threading',
        'queue',
        'time',
        'datetime',
        'uuid',
        'os',
        'sys'
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
    name='VRCPhoto2URL-Desktop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version='version_info.txt'
)
'''
    
    with open('VRCPhoto2URL-Desktop.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created VRCPhoto2URL-Desktop.spec")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building VRCPhoto2URL Desktop executable...")
    
    try:
        # Run PyInstaller
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "VRCPhoto2URL-Desktop.spec"]
        subprocess.check_call(cmd)
        
        # Check if executable was created
        exe_path = Path("dist/VRCPhoto2URL-Desktop.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"✅ Executable created successfully!")
            print(f"📁 Location: {exe_path.absolute()}")
            print(f"📊 Size: {size_mb:.1f} MB")
            return True
        else:
            print("❌ Executable not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def copy_to_root():
    """Copy the executable to the root directory"""
    exe_path = Path("dist/VRCPhoto2URL-Desktop.exe")
    root_dist = Path("../dist")
    
    if not root_dist.exists():
        root_dist.mkdir()
    
    if exe_path.exists():
        dest_path = root_dist / "VRCPhoto2URL-Desktop.exe"
        shutil.copy2(exe_path, dest_path)
        print(f"✅ Copied executable to: {dest_path.absolute()}")
        return True
    return False

def main():
    """Main build process"""
    print("🚀 VRCPhoto2URL Desktop Executable Builder")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("launch_desktop_client.py").exists():
        print("❌ Error: launch_desktop_client.py not found")
        print("   Please run this script from the client/ directory")
        return False
    
    # Install PyInstaller
    if not install_pyinstaller():
        return False
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if not build_executable():
        return False
    
    # Copy to root
    copy_to_root()
    
    print("\n" + "=" * 50)
    print("✅ Build completed successfully!")
    print("📁 Executable location: ../dist/VRCPhoto2URL-Desktop.exe")
    print("🎯 Ready for distribution!")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
