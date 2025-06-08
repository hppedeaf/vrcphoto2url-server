import os
import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QLabel, QPushButton, QMenuBar, QFileDialog, 
                              QMessageBox, QListWidget, QListWidgetItem, QTextEdit,
                              QSplitter, QGroupBox, QProgressBar, QStatusBar, QDialog)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QPixmap, QIcon, QAction

# Add the parent directory to sys.path to import custom modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from custom_server_client import CustomServerClient
from custom_server_dialog import ServerConnectionDialog

class FileUploadThread(QThread):
    """Thread for uploading files without blocking UI"""
    upload_progress = Signal(int)
    upload_finished = Signal(bool, str, dict)
    
    def __init__(self, client, file_path):
        super().__init__()
        self.client = client
        self.file_path = file_path
        
    def run(self):
        try:
            result = self.client.upload_file(self.file_path)
            if result and result.get('success'):
                self.upload_finished.emit(True, "File uploaded successfully!", result)
            else:
                self.upload_finished.emit(False, result.get('error', 'Unknown error'), {})
        except Exception as e:
            self.upload_finished.emit(False, str(e), {})

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom File Server Client")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize server client
        self.server_client = None
        self.upload_thread = None
        
        self.setup_ui()
        self.create_menu()
        
        # Auto-refresh timer for file list
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_file_list)
        
    def setup_ui(self):
        """Setup the main UI"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(self.central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Controls
        self.setup_control_panel(splitter)
        
        # Right panel - File list and preview
        self.setup_file_panel(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Not connected to server")
        
    def setup_control_panel(self, splitter):
        """Setup the left control panel"""
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        
        # Connection group
        connection_group = QGroupBox("Server Connection")
        connection_layout = QVBoxLayout(connection_group)
        
        self.connection_status = QLabel("Status: Not Connected")
        self.connection_status.setStyleSheet("color: red; font-weight: bold;")
        connection_layout.addWidget(self.connection_status)
        
        self.connect_button = QPushButton("Connect to Server")
        self.connect_button.clicked.connect(self.show_connection_dialog)
        connection_layout.addWidget(self.connect_button)
        
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self.disconnect_from_server)
        self.disconnect_button.setEnabled(False)
        connection_layout.addWidget(self.disconnect_button)
        
        control_layout.addWidget(connection_group)
        
        # File operations group
        file_ops_group = QGroupBox("File Operations")
        file_ops_layout = QVBoxLayout(file_ops_group)
        
        self.upload_button = QPushButton("Upload File")
        self.upload_button.clicked.connect(self.upload_file)
        self.upload_button.setEnabled(False)
        file_ops_layout.addWidget(self.upload_button)
        
        self.refresh_button = QPushButton("Refresh File List")
        self.refresh_button.clicked.connect(self.refresh_file_list)
        self.refresh_button.setEnabled(False)
        file_ops_layout.addWidget(self.refresh_button)
        
        # Upload progress
        self.upload_progress = QProgressBar()
        self.upload_progress.setVisible(False)
        file_ops_layout.addWidget(self.upload_progress)
        
        control_layout.addWidget(file_ops_group)
        
        # Server info
        self.server_info = QTextEdit()
        self.server_info.setMaximumHeight(150)
        self.server_info.setReadOnly(True)
        self.server_info.setPlaceholderText("Server information will appear here...")
        control_layout.addWidget(QLabel("Server Info:"))
        control_layout.addWidget(self.server_info)
        
        control_layout.addStretch()
        
        splitter.addWidget(control_widget)
        
    def setup_file_panel(self, splitter):
        """Setup the right file panel"""
        file_widget = QWidget()
        file_layout = QVBoxLayout(file_widget)
        
        # File list
        file_layout.addWidget(QLabel("Uploaded Files:"))
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.on_file_selected)
        self.file_list.itemDoubleClicked.connect(self.download_selected_file)
        file_layout.addWidget(self.file_list)
        
        # File actions
        file_actions_layout = QHBoxLayout()
        
        self.download_button = QPushButton("Download Selected")
        self.download_button.clicked.connect(self.download_selected_file)
        self.download_button.setEnabled(False)
        file_actions_layout.addWidget(self.download_button)
        
        self.copy_url_button = QPushButton("Copy URL")
        self.copy_url_button.clicked.connect(self.copy_selected_url)
        self.copy_url_button.setEnabled(False)
        file_actions_layout.addWidget(self.copy_url_button)
        
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected_file)
        self.delete_button.setEnabled(False)
        file_actions_layout.addWidget(self.delete_button)
        
        file_layout.addLayout(file_actions_layout)
        
        splitter.addWidget(file_widget)
        
    def create_menu(self):
        """Create the menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        connect_action = QAction("Connect to Server", self)
        connect_action.triggered.connect(self.show_connection_dialog)
        file_menu.addAction(connect_action)
        
        file_menu.addSeparator()
        
        upload_action = QAction("Upload File", self)
        upload_action.triggered.connect(self.upload_file)
        file_menu.addAction(upload_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def show_connection_dialog(self):
        """Show the server connection dialog"""
        existing_config = None
        if self.server_client:
            existing_config = {
                'server_url': self.server_client.server_url,
                'api_key': self.server_client.api_key
            }
            
        dialog = ServerConnectionDialog(self, existing_config)
        if dialog.exec() == QDialog.Accepted:
            config = dialog.get_connection_config()
            if config:
                self.connect_to_server(config)
                
    def connect_to_server(self, config):
        """Connect to the server with given configuration"""
        try:
            self.server_client = CustomServerClient(
                server_url=config['server_url'],
                api_key=config.get('api_key', '')
            )
            
            # Test connection
            if self.server_client.test_connection():
                self.connection_status.setText("Status: Connected")
                self.connection_status.setStyleSheet("color: green; font-weight: bold;")
                self.status_bar.showMessage(f"Connected to {config['server_url']}")
                
                # Enable controls
                self.upload_button.setEnabled(True)
                self.refresh_button.setEnabled(True)
                self.disconnect_button.setEnabled(True)
                self.connect_button.setText("Reconnect")
                
                # Get server info
                self.update_server_info()
                
                # Load file list
                self.refresh_file_list()
                
                # Start auto-refresh timer
                self.refresh_timer.start(30000)  # Refresh every 30 seconds
                
            else:
                raise Exception("Connection test failed")
                
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to server:\n{str(e)}")
            self.server_client = None
            
    def disconnect_from_server(self):
        """Disconnect from the server"""
        self.server_client = None
        self.refresh_timer.stop()
        
        self.connection_status.setText("Status: Not Connected")
        self.connection_status.setStyleSheet("color: red; font-weight: bold;")
        self.status_bar.showMessage("Disconnected from server")
        
        # Disable controls
        self.upload_button.setEnabled(False)
        self.refresh_button.setEnabled(False)
        self.download_button.setEnabled(False)
        self.copy_url_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.disconnect_button.setEnabled(False)
        self.connect_button.setText("Connect to Server")
        
        # Clear data
        self.file_list.clear()
        self.server_info.clear()
        
    def update_server_info(self):
        """Update server information display"""
        if not self.server_client:
            return
            
        try:
            stats = self.server_client.get_server_stats()
            if stats and stats.get('success'):
                data = stats['data']
                info_text = f"""Server Statistics:
• Total Files: {data.get('total_files', 'Unknown')}
• Total Size: {data.get('total_size_mb', 'Unknown')} MB
• Available Space: {data.get('available_space_mb', 'Unknown')} MB
• Server Version: {data.get('version', 'Unknown')}
• Uptime: {data.get('uptime_seconds', 'Unknown')} seconds"""
                self.server_info.setText(info_text)
        except Exception as e:
            self.server_info.setText(f"Error getting server info: {str(e)}")
            
    def upload_file(self):
        """Upload a file to the server"""
        if not self.server_client:
            QMessageBox.warning(self, "Not Connected", "Please connect to a server first.")
            return
            
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Upload", "", 
            "All Files (*);;Image Files (*.png;*.jpg;*.jpeg;*.gif;*.bmp);;Text Files (*.txt;*.log)",
            options=options
        )
        
        if file_path:
            self.upload_progress.setVisible(True)
            self.upload_progress.setRange(0, 0)  # Indeterminate
            self.upload_button.setEnabled(False)
            
            # Start upload in separate thread
            self.upload_thread = FileUploadThread(self.server_client, file_path)
            self.upload_thread.upload_finished.connect(self.on_upload_finished)
            self.upload_thread.start()
            
    def on_upload_finished(self, success, message, result_data):
        """Handle upload completion"""
        self.upload_progress.setVisible(False)
        self.upload_button.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Upload Success", message)
            self.refresh_file_list()
            self.update_server_info()
        else:
            QMessageBox.critical(self, "Upload Failed", f"Upload failed:\n{message}")
            
    def refresh_file_list(self):
        """Refresh the file list from server"""
        if not self.server_client:
            return
            
        try:
            files_data = self.server_client.list_files()
            if files_data and files_data.get('success'):
                self.file_list.clear()
                files = files_data.get('data', [])
                
                for file_info in files:
                    item_text = f"{file_info['filename']} ({file_info.get('size_mb', 0):.2f} MB)"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, file_info)  # Store file info
                    self.file_list.addItem(item)
                    
                self.status_bar.showMessage(f"Loaded {len(files)} files")
        except Exception as e:
            QMessageBox.warning(self, "Refresh Error", f"Failed to refresh file list:\n{str(e)}")
            
    def on_file_selected(self, item):
        """Handle file selection"""
        if item:
            self.download_button.setEnabled(True)
            self.copy_url_button.setEnabled(True)
            self.delete_button.setEnabled(True)
        else:
            self.download_button.setEnabled(False)
            self.copy_url_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            
    def download_selected_file(self):
        """Download the selected file"""
        current_item = self.file_list.currentItem()
        if not current_item or not self.server_client:
            return
            
        file_info = current_item.data(Qt.UserRole)
        if not file_info:
            return
            
        # Ask user where to save
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save File As", file_info['filename'], 
            "All Files (*)", options=options
        )
        
        if save_path:
            try:
                result = self.server_client.download_file(file_info['id'], save_path)
                if result and result.get('success'):
                    QMessageBox.information(self, "Download Success", f"File saved to:\n{save_path}")
                else:
                    QMessageBox.critical(self, "Download Failed", result.get('error', 'Unknown error'))
            except Exception as e:
                QMessageBox.critical(self, "Download Error", f"Download failed:\n{str(e)}")
                
    def copy_selected_url(self):
        """Copy the selected file's URL to clipboard"""
        current_item = self.file_list.currentItem()
        if not current_item or not self.server_client:
            return
            
        file_info = current_item.data(Qt.UserRole)
        if not file_info:
            return
            
        url = f"{self.server_client.server_url}/files/{file_info['id']}"
        
        try:
            import pyperclip
            pyperclip.copy(url)
            QMessageBox.information(self, "URL Copied", f"File URL copied to clipboard:\n{url}")
        except ImportError:
            QMessageBox.information(self, "URL", f"File URL:\n{url}")
            
    def delete_selected_file(self):
        """Delete the selected file"""
        current_item = self.file_list.currentItem()
        if not current_item or not self.server_client:
            return
            
        file_info = current_item.data(Qt.UserRole)
        if not file_info:
            return
            
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion", 
            f"Are you sure you want to delete '{file_info['filename']}'?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                result = self.server_client.delete_file(file_info['id'])
                if result and result.get('success'):
                    QMessageBox.information(self, "Delete Success", "File deleted successfully!")
                    self.refresh_file_list()
                    self.update_server_info()
                else:
                    QMessageBox.critical(self, "Delete Failed", result.get('error', 'Unknown error'))
            except Exception as e:
                QMessageBox.critical(self, "Delete Error", f"Delete failed:\n{str(e)}")
                
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About", 
                         "Custom File Server Client\n\n"
                         "A desktop client for connecting to custom file servers.\n"
                         "Upload, download, and manage your files remotely.")
                         
    def closeEvent(self, event):
        """Handle application close"""
        if self.refresh_timer.isActive():
            self.refresh_timer.stop()
        event.accept()