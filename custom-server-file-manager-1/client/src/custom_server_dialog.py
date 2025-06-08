from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QMessageBox, QTextEdit,
                              QCheckBox, QProgressBar)
from PySide6.QtCore import Qt, QThread, QTimer, Signal
import requests
import json

class ConnectionTestThread(QThread):
    """Thread for testing server connection without blocking UI"""
    connection_tested = Signal(bool, str)
    
    def __init__(self, server_url, api_key):
        super().__init__()
        self.server_url = server_url
        self.api_key = api_key
        
    def run(self):
        try:
            # Test connection to health endpoint
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            response = requests.get(f"{self.server_url}/health", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.connection_tested.emit(True, f"Connected successfully! Server status: {data.get('status', 'unknown')}")
            else:
                self.connection_tested.emit(False, f"Connection failed: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.connection_tested.emit(False, f"Connection error: {str(e)}")

class ServerConnectionDialog(QDialog):
    def __init__(self, parent=None, existing_config=None):
        super().__init__(parent)
        self.setWindowTitle("Connect to Custom Server")
        self.setFixedSize(500, 400)
        self.existing_config = existing_config or {}
        self.connection_thread = None
        self.setup_ui()
        self.load_existing_config()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Custom File Server Connection")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Server URL
        self.server_url_label = QLabel("Server URL:")
        self.server_url_input = QLineEdit()
        self.server_url_input.setPlaceholderText("https://your-server.railway.app")
        layout.addWidget(self.server_url_label)
        layout.addWidget(self.server_url_input)

        # API Key
        self.api_key_label = QLabel("API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Your server API key")
        layout.addWidget(self.api_key_label)
        layout.addWidget(self.api_key_input)

        # Show/Hide API key
        self.show_api_key_checkbox = QCheckBox("Show API key")
        self.show_api_key_checkbox.toggled.connect(self.toggle_api_key_visibility)
        layout.addWidget(self.show_api_key_checkbox)

        # Connection test progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Buttons
        button_layout = QHBoxLayout()
        
        self.test_button = QPushButton("Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_button)
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_server)
        self.connect_button.setEnabled(False)
        button_layout.addWidget(self.connect_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)

        # Status message
        self.status_message = QTextEdit()
        self.status_message.setMaximumHeight(100)
        self.status_message.setReadOnly(True)
        self.status_message.setPlaceholderText("Connection status will appear here...")
        layout.addWidget(self.status_message)

    def load_existing_config(self):
        """Load existing configuration if available"""
        if self.existing_config:
            self.server_url_input.setText(self.existing_config.get('server_url', ''))
            self.api_key_input.setText(self.existing_config.get('api_key', ''))

    def toggle_api_key_visibility(self, checked):
        """Toggle API key visibility"""
        if checked:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)

    def test_connection(self):
        """Test connection to server"""
        server_url = self.server_url_input.text().strip()
        api_key = self.api_key_input.text().strip()
        
        if not server_url:
            QMessageBox.warning(self, "Input Error", "Please enter a server URL.")
            return
        
        # Ensure URL has protocol
        if not server_url.startswith(('http://', 'https://')):
            server_url = 'https://' + server_url
            self.server_url_input.setText(server_url)
        
        self.test_button.setEnabled(False)
        self.connect_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_message.setText("Testing connection...")
        
        # Start connection test in separate thread
        self.connection_thread = ConnectionTestThread(server_url, api_key)
        self.connection_thread.connection_tested.connect(self.on_connection_tested)
        self.connection_thread.start()

    def on_connection_tested(self, success, message):
        """Handle connection test result"""
        self.test_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_message.setText(message)
        
        if success:
            self.connect_button.setEnabled(True)
            self.status_message.setStyleSheet("color: green;")
        else:
            self.connect_button.setEnabled(False)
            self.status_message.setStyleSheet("color: red;")

    def connect_to_server(self):
        """Connect to server and close dialog"""
        server_url = self.server_url_input.text().strip()
        api_key = self.api_key_input.text().strip()
        
        if not server_url:
            QMessageBox.warning(self, "Input Error", "Please enter a server URL.")
            return
            
        # Store connection details
        self.connection_config = {
            'server_url': server_url,
            'api_key': api_key
        }
        
        self.accept()

    def get_connection_config(self):
        """Get the connection configuration"""
        return getattr(self, 'connection_config', None)