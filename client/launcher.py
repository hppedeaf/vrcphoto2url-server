#!/usr/bin/env python3
"""
Desktop Client Launcher
Simple launcher script for the Custom Server File Manager Desktop Client
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Launch the desktop client with proper error handling"""
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    client_dir = script_dir
    
    print("🚀 Custom Server File Manager - Desktop Client Launcher")
    print("=" * 60)
    print(f"📁 Client Directory: {client_dir}")
    
    # Check if we're in the right directory
    if not (client_dir / "src" / "modern_client.py").exists():
        print("❌ Error: modern_client.py not found!")
        print("📍 Please run this script from the client directory")
        input("Press Enter to exit...")
        return 1
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Error: Python {python_version.major}.{python_version.minor} detected")
        print("🐍 Python 3.8 or higher is required")
        input("Press Enter to exit...")
        return 1
    
    print(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if dependencies are installed
    try:
        import PySide6
        print("✓ PySide6 available")
    except ImportError:
        print("❌ PySide6 not found - installing dependencies...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True, cwd=client_dir)
            print("✓ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            print("🔧 Please manually run: pip install -r requirements.txt")
            input("Press Enter to exit...")
            return 1
    
    # Test import of the modern client
    try:
        sys.path.insert(0, str(client_dir / "src"))
        from modern_client import ModernCustomClient
        print("✓ Modern client ready")
    except ImportError as e:
        print(f"❌ Failed to import modern client: {e}")
        print("🔧 Please check the installation")
        input("Press Enter to exit...")
        return 1
    
    # Launch the client
    print("\n🎯 Launching desktop client...")
    print("💡 Tip: Use Ctrl+C in this window to stop the client")
    print("=" * 60)
    
    try:
        # Run the main client
        os.chdir(client_dir)
        subprocess.run([sys.executable, "run_client.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Client exited with error: {e}")
        input("Press Enter to exit...")
        return 1
    except KeyboardInterrupt:
        print("\n⚡ Client stopped by user")
        return 0
    
    print("\n✅ Client closed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
