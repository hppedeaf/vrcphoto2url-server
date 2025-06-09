#!/usr/bin/env python3
"""
VRCPhoto2URL Client Launcher - Robust Version
Launches the desktop client with proper error handling and stdin management
"""
import sys
import os
import subprocess
from pathlib import Path
import time

def is_console_available():
    """Check if we have a proper console available"""
    try:
        return sys.stdin and sys.stdin.isatty()
    except (AttributeError, OSError):
        return False

def safe_input(prompt="Press Enter to continue...", timeout=10):
    """Safe input that won't crash if stdin is unavailable"""
    try:
        if is_console_available():
            return input(prompt)
        else:
            print(f"No console available. Waiting {timeout} seconds...")
            time.sleep(timeout)
            return ""
    except (EOFError, KeyboardInterrupt, OSError):
        print(f"Input interrupted. Waiting {timeout} seconds...")
        time.sleep(timeout)
        return ""

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
        print("   pip install -r client/requirements.txt")
        return False

def check_config():
    """Check if client configuration exists"""
    script_dir = Path(__file__).parent.parent  # Go up to VRCPhoto2URL root
    client_dir = script_dir / "client"
    config_file = client_dir / "client_config.json"
    
    if config_file.exists():
        print("✅ Client configuration found")
        # Check if it's properly configured
        try:
            import json
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            if config.get('server_url') == 'https://your-app.railway.app':
                print("⚠️  Configuration uses template values")
                print("   Please update client_config.json with your Railway URL")
                return False
            elif config.get('api_key') == 'your-api-key-here':
                print("⚠️  Configuration uses template API key")
                print("   Please update client_config.json with your API key")
                return False
            else:
                print(f"   Server: {config.get('server_url')}")
                return True
        except Exception as e:
            print(f"❌ Error reading configuration: {e}")
            return False
    else:
        print("❌ Client configuration not found")
        print(f"   Expected: {config_file}")
        print("   Please create client_config.json from the example file")
        return False

def launch_client():
    """Launch the VRCPhoto2URL desktop client"""
    try:
        # Get the project root directory
        script_dir = Path(__file__).parent.parent  # Go up to VRCPhoto2URL root
        client_dir = script_dir / "client"
        
        print("🔍 Checking requirements...")
        if not check_requirements():
            return 1
        
        print("🔍 Checking configuration...")
        if not check_config():
            return 1
        
        print("\n🚀 Launching VRCPhoto2URL Client...")
        print("📁 Ready to monitor VRChat Screenshots folder")
        print("\n💡 Close the window to exit")
        print("-" * 50)
        
        # Add src to Python path and launch
        sys.path.insert(0, str(client_dir / "src"))
        
        # Import and run the client
        try:
            from modern_client import ModernCustomClient
            from PySide6.QtWidgets import QApplication
            
            app = QApplication(sys.argv)
            client = ModernCustomClient()
            client.show()
            
            return app.exec()
        except ImportError as e:
            print(f"❌ Error importing client modules: {e}")
            print("   Make sure all dependencies are installed")
            return 1
        
    except Exception as e:
        print(f"❌ Error launching client: {e}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    """Main entry point"""
    print("🎮 VRCPhoto2URL - VRChat Screenshot Auto-Uploader")
    print("🌐 Server: Railway.app Production")
    print("=" * 60)
    
    try:
        exit_code = launch_client()
        
        if exit_code == 0:
            print("\n👋 Client closed successfully")
        else:
            print(f"\n💥 Client exited with error code: {exit_code}")
            print("\n🔧 Troubleshooting:")
            print("   1. Make sure all requirements are installed: pip install -r client/requirements.txt")
            print("   2. Check that client_config.json has correct server URL and API key")
            print("   3. Verify internet connection to Railway server")
            
            # Safe input that won't crash
            safe_input("\nPress Enter to exit...", timeout=10)
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\n\n🛑 Launch cancelled by user")
        return 130
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        safe_input("Press Enter to exit...", timeout=10)
        return 1

if __name__ == "__main__":
    sys.exit(main())
