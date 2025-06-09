#!/usr/bin/env python3
"""
VRCPhoto2URL Executable Builder
Creates a standalone executable for easy distribution
"""

import subprocess
import sys
import os
from pathlib import Path

def build_executable():
    """Build the VRCPhoto2URL executable"""
    print("🚀 Building VRCPhoto2URL Executable...")
    print("=" * 50)
    
    # Get the project root
    project_root = Path(__file__).parent
    
    # Build command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=VRCPhoto2URL",
        "--add-data=client/client_config.json;client/",
        "--add-data=client/src;client/src/",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtWidgets", 
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=requests",
        "--hidden-import=watchdog",
        "--hidden-import=watchdog.observers",
        "--hidden-import=watchdog.events",
        "scripts/launch_client.py"
    ]
    
    print(f"📦 Command: {' '.join(cmd)}")
    print("🔄 Building... This may take a few minutes...")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build successful!")
        print("\n📂 Executable created at: dist/VRCPhoto2URL.exe")
        print("\n🎯 You can now distribute this single .exe file!")
        print("💡 Users just need to run VRCPhoto2URL.exe - no Python required!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error:")
        print(f"   {e}")
        print(f"\n📝 Error output:")
        print(f"   {e.stderr}")
        return False
        
    return True

if __name__ == "__main__":
    success = build_executable()
    if success:
        print("\n🎉 VRCPhoto2URL executable is ready!")
    else:
        print("\n🔧 Build failed. Please check the errors above.")
        sys.exit(1)
