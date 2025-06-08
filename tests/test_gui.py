#!/usr/bin/env python3
"""
Test if the GUI can start properly
"""
import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox

def test_gui():
    """Test if GUI frameworks work"""
    print("🖥️ Testing GUI Framework...")
    
    # Create application
    app = QApplication(sys.argv)
    
    # Show a simple message box
    msgBox = QMessageBox()
    msgBox.setWindowTitle("VRCPhoto2URL Test")
    msgBox.setText("✅ PySide6 is working!\n\nClick OK to test the client.")
    msgBox.setStandardButtons(QMessageBox.Ok)
    
    # Show message box and wait for response
    if msgBox.exec() == QMessageBox.Ok:
        print("✅ Message box test successful")
        
        # Try to import and start the client
        try:
            print("🚀 Attempting to start client...")
            sys.path.insert(0, 'src')
            from modern_client import ModernCustomClient
            
            # Create client window
            client = ModernCustomClient()
            client.show()
            
            print("✅ Client window created successfully")
            print("🔗 Auto-connection should happen in 1 second...")
            print("💡 Close the window to exit")
            
            # Run app
            return app.exec()
            
        except Exception as e:
            print(f"❌ Error starting client: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    return 0

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    exit_code = test_gui()
    sys.exit(exit_code)
