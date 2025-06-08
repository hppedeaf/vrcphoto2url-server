#!/usr/bin/env python3
"""
Connection Dialog for Custom Server File Manager Client
Modern dialog for configuring server connection
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox,
    QFrame, QProgressBar, QTabWidget, QWidget, QTextEdit,
    QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QPixmap

from .server_client import ServerManager, ServerError

class ConnectionTestWorker(QThread):
    """Worker thread for testing connection"""
    
    test_complete = Signal(bool, str)  # success, message
    
    def __init__(self, server_url, api_key):
        super().__init__()
        self.server_url = server_url
        self.api_key = api_key
        
    def run(self):
        """Test connection in background"""
        try:
            manager = ServerManager()
            if manager.connect(self.server_url, self.api_key):
                info = manager.test_connection()
                manager.disconnect()
                self.test_complete.emit(True, "Connection successful!")
            else:
                self.test_complete.emit(False, "Connection failed")
        except ServerError as e:
            self.test_complete.emit(False, str(e))
        except Exception as e:
            self.test_complete.emit(False, f"Unexpected error: {str(e)}")

class ConnectionDialog(QDialog):
    """Modern connection configuration dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.test_worker = None
        self.setup_ui()
        self.load_saved_settings()
        
    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("🔗 Connect to Server")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        # Apply modern styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 10px;
                background-color: #2d2d2d;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #4CAF50;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #404040;
                border-radius: 6px;
                background-color: #2d2d2d;
                color: #ffffff;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton[class="primary"] {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton[class="primary"]:hover {
                background-color: #45a049;
            }
            QPushButton[class="secondary"] {
                background-color: #404040;
                color: white;
            }
            QPushButton[class="secondary"]:hover {
                background-color: #505050;
            }
            QCheckBox {
                color: #ffffff;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #404040;
                border-radius: 3px;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border-color: #4CAF50;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        self.create_header(main_layout)
        
        # Connection settings
        self.create_connection_section(main_layout)
        
        # Test section
        self.create_test_section(main_layout)
        
        # Buttons
        self.create_buttons(main_layout)
        
    def create_header(self, parent_layout):
        """Create dialog header"""
        header_layout = QVBoxLayout()
        
        title_label = QLabel("🔗 Server Connection")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #4CAF50; margin-bottom: 5px;")
        
        subtitle_label = QLabel("Configure connection to your Custom Server File Manager")
        subtitle_label.setFont(QFont("Segoe UI", 10))
        subtitle_label.setStyleSheet("color: #aaaaaa;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        parent_layout.addLayout(header_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #404040; max-height: 1px;")
        parent_layout.addWidget(separator)
    
    def create_connection_section(self, parent_layout):
        """Create connection settings section"""
        connection_group = QGroupBox("Connection Settings")
        connection_layout = QFormLayout(connection_group)
        connection_layout.setSpacing(15)
        
        # Server URL
        self.server_url_input = QLineEdit()
        self.server_url_input.setPlaceholderText("http://localhost:8000")
        self.server_url_input.setText("http://localhost:8000")
        connection_layout.addRow("Server URL:", self.server_url_input)
        
        # API Key (optional)
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Enter API key if required")
        connection_layout.addRow("API Key (Optional):", self.api_key_input)
        
        # Remember connection
        self.remember_checkbox = QCheckBox("Remember connection settings")
        self.remember_checkbox.setChecked(True)
        connection_layout.addRow("", self.remember_checkbox)
        
        parent_layout.addWidget(connection_group)
    
    def create_test_section(self, parent_layout):
        """Create connection test section"""
        test_group = QGroupBox("Connection Test")
        test_layout = QVBoxLayout(test_group)
        test_layout.setSpacing(10)
        
        # Test button
        self.test_button = QPushButton("🔍 Test Connection")
        self.test_button.setProperty("class", "secondary")
        self.test_button.clicked.connect(self.test_connection)
        
        # Test progress
        self.test_progress = QProgressBar()
        self.test_progress.setVisible(False)
        self.test_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #404040;
                border-radius: 6px;
                background-color: #1a1a1a;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 4px;
            }
        """)
        
        # Test result
        self.test_result_label = QLabel("")
        self.test_result_label.setWordWrap(True)
        self.test_result_label.setVisible(False)
        
        test_layout.addWidget(self.test_button)
        test_layout.addWidget(self.test_progress)
        test_layout.addWidget(self.test_result_label)
        
        parent_layout.addWidget(test_group)
    
    def create_buttons(self, parent_layout):
        """Create dialog buttons"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setProperty("class", "secondary")
        cancel_button.clicked.connect(self.reject)
        
        # Connect button
        self.connect_button = QPushButton("🔗 Connect")
        self.connect_button.setProperty("class", "primary")
        self.connect_button.clicked.connect(self.accept_connection)
        self.connect_button.setDefault(True)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.connect_button)
        
        parent_layout.addLayout(button_layout)
    
    def test_connection(self):
        """Test connection to server"""
        server_url = self.server_url_input.text().strip()
        api_key = self.api_key_input.text().strip()
        
        if not server_url:
            QMessageBox.warning(self, "Input Error", "Please enter a server URL.")
            return
        
        # Start test
        self.test_button.setEnabled(False)
        self.test_progress.setVisible(True)
        self.test_progress.setRange(0, 0)  # Indeterminate progress
        self.test_result_label.setVisible(False)
        
        # Start worker thread
        self.test_worker = ConnectionTestWorker(server_url, api_key)
        self.test_worker.test_complete.connect(self.on_test_complete)
        self.test_worker.start()
    
    def on_test_complete(self, success, message):
        """Handle test completion"""
        self.test_button.setEnabled(True)
        self.test_progress.setVisible(False)
        self.test_result_label.setVisible(True)
        
        if success:
            self.test_result_label.setText(f"✅ {message}")
            self.test_result_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self.test_result_label.setText(f"❌ {message}")
            self.test_result_label.setStyleSheet("color: #f44336; font-weight: bold;")
        
        # Clean up worker
        if self.test_worker:
            self.test_worker.deleteLater()
            self.test_worker = None
    
    def accept_connection(self):
        """Accept connection with validation"""
        server_url = self.server_url_input.text().strip()
        
        if not server_url:
            QMessageBox.warning(self, "Input Error", "Please enter a server URL.")
            return
        
        # Save settings if requested
        if self.remember_checkbox.isChecked():
            self.save_settings()
        
        self.accept()
    
    def get_settings(self):
        """Get connection settings"""
        return {
            'server_url': self.server_url_input.text().strip(),
            'api_key': self.api_key_input.text().strip(),
            'remember': self.remember_checkbox.isChecked()
        }
    
    def load_saved_settings(self):
        """Load saved connection settings"""
        # In a real application, load from config file
        # For now, just set defaults
        pass
    
    def save_settings(self):
        """Save connection settings"""
        # In a real application, save to config file
        # For now, just pass
        pass
    
    def closeEvent(self, event):
        """Handle dialog close"""
        if self.test_worker and self.test_worker.isRunning():
            self.test_worker.terminate()
            self.test_worker.wait()
        event.accept()

def show_connection_dialog(parent=None):
    """Show connection dialog and return settings if accepted"""
    dialog = ConnectionDialog(parent)
    if dialog.exec() == QDialog.Accepted:
        return dialog.get_settings()
    return None
