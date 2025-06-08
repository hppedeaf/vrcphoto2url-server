# File: /custom-server-file-manager/client/main.py

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.modern_client import ModernCustomClient

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Custom Server File Manager")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Custom File Manager")
    
    # High DPI scaling is handled automatically in Qt 6+
    
    # Create and show the main window
    window = ModernCustomClient()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()