#!/usr/bin/env python3
"""
Custom File Server Client - Main Entry Point
Run this script to start the modern desktop client application.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
current_dir = Path(__file__).parent.absolute()
src_dir = current_dir / "src"
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(src_dir))

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from src.modern_client import ModernCustomClient
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure you have installed the required dependencies:")
    print("pip install -r requirements.txt")
    print("\nTo install dependencies, run:")
    print("pip install PySide6 requests watchdog Pillow pyperclip")
    sys.exit(1)

def main():
    """Main application entry point"""
    # Create QApplication
    app = QApplication(sys.argv)
      # Set application properties
    app.setApplicationName("Custom Server File Manager")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Custom File Manager")
    
    # High DPI scaling is handled automatically in Qt 6+
    
    # Create and show main window
    window = ModernCustomClient()
    window.show()
    
    # Start the event loop
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
