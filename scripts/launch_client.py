#!/usr/bin/env python3
"""
VRCPhoto2URL Client Launcher
Launches the desktop client with proper error handling and auto-connection
"""
import sys
import os
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import PySide6
        import requests
        import watchdog
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("\n💡 To install requirements, run:")
        print("   pip install -r requirements.txt")
        return False

def check_config():
    """Check if client configuration exists"""
    script_dir = Path(__file__).parent.parent  # Go up to VRCPhoto2URL root
    client_dir = script_dir / "client"
    config_file = client_dir / "client_config.json"
    if config_file.exists():
        print("✅ Client configuration found")
        return True
    else:
        print("❌ Client configuration not found")
        print(f"\n💡 Expected file: {config_file}")
        print("   This file should contain server URL and API key")
        return False

def launch_client():
    """Launch the desktop client"""
    print("🚀 Launching VRCPhoto2URL Desktop Client...")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return 1
    
    # Check configuration
    if not check_config():
        return 1
      # Change to correct directory
    script_dir = Path(__file__).parent.parent  # Go up to VRCPhoto2URL root
    client_dir = script_dir / "client"
    os.chdir(client_dir)
    
    # Launch client
    try:
        print("\n🖥️ Starting GUI client...")
        print("🔗 Auto-connection will be attempted in 1 second")
        print("📁 Ready to monitor VRChat Screenshots folder")
        print("\n💡 Close the window to exit")
        print("-" * 50)
          # Add src to Python path and launch
        sys.path.insert(0, str(client_dir / "src"))
        from modern_client import ModernCustomClient
        from PySide6.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        client = ModernCustomClient()
        client.show()
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Error launching client: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("🎮 VRCPhoto2URL - VRChat Screenshot Auto-Uploader")
    print("🌐 Server: Railway.app Production")
    print()
    
    exit_code = launch_client()
    
    if exit_code == 0:
        print("\n👋 Client closed successfully")
    else:
        print(f"\n💥 Client exited with error code: {exit_code}")
        input("Press Enter to continue...")
    
    sys.exit(exit_code)
