#!/usr/bin/env python3
"""
VRCPhoto2URL Desktop Executable Builder

This script builds a standalone executable for the VRCPhoto2URL Desktop Client
using PyInstaller. The executable includes all dependencies and can run without
Python being installed on the target system.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not available"""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
        return True
    except ImportError:
        print("📦 Installing PyInstaller...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PyInstaller installed successfully")
            return True
        else:
            print(f"❌ Failed to install PyInstaller: {result.stderr}")
            return False

def create_spec_file():
    """Create PyInstaller spec file with proper configuration"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launch_desktop_client.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
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
    cofile=None,
    icon=None,
    version='version_info.txt'
)
'''
    
    with open('VRCPhoto2URL-Desktop.spec', 'w') as f:
        f.write(spec_content)
    print("✅ Created VRCPhoto2URL-Desktop.spec")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building VRCPhoto2URL Desktop executable (directory mode)...")
    
    result = subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "VRCPhoto2URL-Desktop.spec"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Executable created successfully!")
        
        # Check for directory-based build
        dist_dir = Path("dist/VRCPhoto2URL-Desktop")
        exe_path = dist_dir / "VRCPhoto2URL-Desktop.exe"
        
        if exe_path.exists():
            size_mb = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file()) / (1024 * 1024)
            print(f"📁 Location: {dist_dir.absolute()}")
            print(f"📊 Total Size: {size_mb:.1f} MB")
            print(f"🎯 Executable: {exe_path.absolute()}")
            
            # Copy the entire distribution folder to root
            root_dist = Path("../dist")
            root_dist.mkdir(exist_ok=True)
            dest_dir = root_dist / "VRCPhoto2URL-Desktop"
            
            # Remove existing directory if it exists
            if dest_dir.exists():
                import shutil
                shutil.rmtree(dest_dir)
            
            # Copy the distribution folder
            shutil.copytree(dist_dir, dest_dir)
            print(f"✅ Copied distribution to: {dest_dir.absolute()}")
            print(f"🚀 Run: {dest_dir / 'VRCPhoto2URL-Desktop.exe'}")
        else:
            print("❌ Executable file not found!")
            return False
    else:
        print(f"❌ Build failed!")
        print(f"Error: {result.stderr}")
        return False
    
    return True

def main():
    """Main build process"""
    print("🚀 VRCPhoto2URL Desktop Executable Builder")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("launch_desktop_client.py").exists():
        print("❌ Error: launch_desktop_client.py not found!")
        print("Please run this script from the client directory")
        return False
    
    # Install PyInstaller
    if not install_pyinstaller():
        return False
      # Create spec file
    create_spec_file()
    
    # Build executable
    if not build_executable():
        return False
    
    print("=" * 50)
    print("✅ Build completed successfully!")
    print("\n📋 Next steps:")
    print("1. Test the application: dist/VRCPhoto2URL-Desktop/VRCPhoto2URL-Desktop.exe")
    print("2. Distribute the entire 'VRCPhoto2URL-Desktop' folder to users")
    print("3. Users can run VRCPhoto2URL-Desktop.exe from the distributed folder")
    print("4. No Python installation required on target systems")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
