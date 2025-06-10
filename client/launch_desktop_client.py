#!/usr/bin/env python3
"""
Desktop Client Launcher
Properly configures the module path and launches the modern desktop client
"""

import sys
import os
from pathlib import Path

def setup_module_path():
    """Setup module paths for both development and PyInstaller environments"""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running in PyInstaller bundle
        bundle_dir = Path(sys._MEIPASS)
        sys.path.insert(0, str(bundle_dir))
    else:
        # Running in development
        client_dir = Path(__file__).parent
        src_dir = client_dir / "src"
        sys.path.insert(0, str(src_dir))

# Setup module paths
setup_module_path()

if __name__ == "__main__":
    try:
        from PySide6.QtWidgets import QApplication
        
        # Try to import the main client module with multiple fallbacks
        ModernCustomClient = None
        
        try:
            from src.modern_client import ModernCustomClient
            print("✅ Imported from src.modern_client")
        except ImportError:
            try:
                import sys
                import os
                # Add current directory to path for PyInstaller
                if hasattr(sys, '_MEIPASS'):
                    sys.path.insert(0, sys._MEIPASS)
                else:
                    sys.path.insert(0, os.path.dirname(__file__))
                    
                from modern_client import ModernCustomClient
                print("✅ Imported from modern_client")
            except ImportError:
                try:
                    from client.src.modern_client import ModernCustomClient
                    print("✅ Imported from client.src.modern_client")
                except ImportError as e:
                    print(f"❌ Failed to import ModernCustomClient: {e}")
                    print("Available modules:")
                    import sys
                    for module in sorted(sys.modules.keys()):
                        if 'modern' in module.lower() or 'client' in module.lower():
                            print(f"  - {module}")
                    raise
        
        # Create Qt application
        app = QApplication(sys.argv)
        
        # Create and show the client
        client = ModernCustomClient()
        client.show()
        
        print("🚀 Desktop Client started successfully!")
        print("📁 Monitor VRChat screenshot folders automatically")
        print("🔗 Connect to your server to start uploading")
        
        # Run the application
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("📦 Please install required dependencies:")
        print("   pip install PySide6 watchdog requests")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start client: {e}")
        sys.exit(1)
