# filepath: custom-server-file-manager/client/src/custom_main.py
"""
Custom Client Application - Entry Point
This file initializes the GUI and connects to the server.
"""

import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()