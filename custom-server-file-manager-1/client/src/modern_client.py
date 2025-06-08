#!/usr/bin/env python3
"""
Custom Server File Manager - Modern Desktop Client
Beautiful modern desktop client for the Custom Server File Manager
"""

import sys
import os
import threading
import time
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# File monitoring
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

# GUI imports
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QFileDialog, QMessageBox,
    QTabWidget, QListWidget, QFrame, QDialog, QCheckBox, QSpinBox,
    QComboBox, QGroupBox, QFormLayout, QProgressBar, QScrollArea,
    QSplitter, QLineEdit, QGridLayout, QStackedWidget
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QDragEnterEvent, QDropEvent, QColor, QPalette, QPixmap, QIcon

# Local imports
from ui_components import ModernCard, ActionButton, StatusIndicator, FileDropZone, ModernProgressBar, NotificationCard
from server_client import ServerManager
from settings_dialog import SettingsDialog

class FileMonitorHandler(FileSystemEventHandler):
    """Enhanced file monitor for automatic uploads"""
    
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.photo_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif', 
                                 '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.m4v',
                                 '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma',
                                 '.pdf', '.txt', '.doc', '.docx', '.zip', '.rar', '.7z'}
        self.pending_uploads = {}  # Track files pending upload to avoid duplicates
        
    def on_created(self, event):
        """Handle new file creation"""
        if not event.is_directory:
            filepath = event.src_path
            filename = os.path.basename(filepath)
            
            # Check if it's an allowed file type
            if any(filename.lower().endswith(ext) for ext in self.allowed_extensions):
                # Use smart delay for large files (especially VRChat screenshots)
                # VRChat screenshots are typically 3840x2160 and can be 5-10MB
                # Need more time for large files to be fully written
                delay = 5.0 if any(filename.lower().endswith(ext) for ext in self.photo_extensions) else 2.0
                
                # Track this file to avoid duplicate uploads
                self.pending_uploads[filepath] = time.time()
                
                threading.Timer(delay, lambda: self._process_file(filepath)).start()
    
    def on_moved(self, event):
        """Handle file move/rename events (important for VRCX which renames VRChat screenshots)"""
        if not event.is_directory:
            src_path = event.src_path
            dest_path = event.dest_path
            filename = os.path.basename(dest_path)
            
            # Check if destination is an allowed file type
            if any(filename.lower().endswith(ext) for ext in self.allowed_extensions):
                # Remove old path from pending uploads if it exists
                if src_path in self.pending_uploads:
                    del self.pending_uploads[src_path]
                
                # Use shorter delay for moved files since they should already be complete
                delay = 2.0 if any(filename.lower().endswith(ext) for ext in self.photo_extensions) else 1.0
                
                # Track the new path
                self.pending_uploads[dest_path] = time.time()
                
                threading.Timer(delay, lambda: self._process_file(dest_path)).start()
    
    def _process_file(self, filepath):
        """Process file for upload with duplicate checking"""
        try:
            # Check if this file is still pending (not already processed)
            if filepath in self.pending_uploads:
                del self.pending_uploads[filepath]
                
                # Double-check file still exists
                if os.path.exists(filepath):
                    self.callback(filepath)
                    
        except Exception as e:
            print(f"Error processing file {filepath}: {e}")
            # Clean up pending uploads entry
            if filepath in self.pending_uploads:
                del self.pending_uploads[filepath]

class UploadWorker(QThread):
    """Enhanced upload worker with queue management"""
    upload_complete = Signal(str, str, str, int)  # filename, service, url, size
    upload_failed = Signal(str, str)  # filename, error
    upload_progress = Signal(str, int)  # status, percentage
    
    def __init__(self, server_manager):
        super().__init__()
        self.server_manager = server_manager
        self.upload_queue = []
        self.running = False
        
    def add_upload(self, filepath: str):
        """Add file to upload queue"""
        if filepath not in [item['filepath'] for item in self.upload_queue]:
            self.upload_queue.append({
                'filepath': filepath,
                'timestamp': time.time(),
                'filename': os.path.basename(filepath)
            })
    
    def run(self):
        """Process upload queue"""
        self.running = True
        
        while self.running and self.upload_queue:
            try:
                upload_item = self.upload_queue.pop(0)
                filepath = upload_item['filepath']
                filename = upload_item['filename']
                
                self.upload_progress.emit(f"Preparing {filename}", 10)
                
                # Wait for file to be ready
                if not self._wait_for_file_ready(filepath, filename):
                    continue
                
                self.upload_progress.emit(f"Uploading {filename}", 50)
                  # Upload file
                file_size = os.path.getsize(filepath)
                result = self.server_manager.upload_file(filepath)
                
                if result and 'url' in result:
                    self.upload_progress.emit(f"Completed {filename}", 100)
                    self.upload_complete.emit(filename, "Custom Server", result['url'], file_size)
                else:
                    self.upload_failed.emit(filename, "Upload failed - no response")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                self.upload_failed.emit(filename, f"Upload error: {str(e)}")
        
        self.running = False
    
    def _wait_for_file_ready(self, filepath: str, filename: str) -> bool:
        """Wait for file to be ready for upload with enhanced stability checking"""
        max_retries = 15  # Increased retries for large VRChat screenshots
        last_size = 0
        stable_count = 0
        required_stable_checks = 3  # File size must be stable for 3 consecutive checks
        
        for retry in range(max_retries):
            try:
                if not os.path.exists(filepath):
                    self.upload_failed.emit(filename, "File not found")
                    return False
                
                # Get current file size
                current_size = os.path.getsize(filepath)
                
                # Test file access
                with open(filepath, 'rb') as test_file:
                    # Try to read first byte
                    test_file.read(1)
                    # For large files, also check if we can seek to end
                    if current_size > 1024 * 1024:  # For files > 1MB
                        test_file.seek(-1, 2)  # Seek to last byte
                        test_file.read(1)
                
                # Check if file size is stable (not growing)
                if current_size == last_size and current_size > 0:
                    stable_count += 1
                    if stable_count >= required_stable_checks:
                        return True
                else:
                    stable_count = 0
                    last_size = current_size
                
                # Dynamic wait time based on file size and retry count
                if current_size > 5 * 1024 * 1024:  # > 5MB (like VRChat screenshots)
                    wait_time = min(3 + retry * 0.5, 8)  # 3-8 seconds for large files
                else:
                    wait_time = min(1 + retry * 0.2, 3)  # 1-3 seconds for smaller files
                
                if retry < max_retries - 1:
                    progress = 20 + retry * 4
                    size_mb = current_size / (1024 * 1024)
                    self.upload_progress.emit(
                        f"Waiting for {filename} to be ready ({size_mb:.1f}MB, {stable_count}/{required_stable_checks} stable)", 
                        min(progress, 95)
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    return stable_count >= required_stable_checks
                
            except PermissionError:
                if retry < max_retries - 1:
                    wait_time = min(2 + retry * 0.5, 5)  # Longer wait for permission issues
                    self.upload_progress.emit(f"File {filename} is locked, waiting...", 20 + retry * 3)
                    time.sleep(wait_time)
                    continue
                else:
                    self.upload_failed.emit(filename, "File is locked or in use by another application")
                    return False
            except Exception as e:
                self.upload_failed.emit(filename, f"File access error: {str(e)}")
                return False
        
        return False
    
    def stop(self):
        """Stop the upload worker gracefully"""
        self.running = False

class ModernCustomClient(QMainWindow):
    """Modern Custom Server File Manager Client"""
    
    def __init__(self):
        super().__init__()
        
        # Core components
        self.server_manager = ServerManager()
        
        # Application state
        self.connected = False
        self.monitoring = False
        self.monitored_directories = []
        self.upload_stats = {
            'total_uploads': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'total_size': 0
        }
        
        # File observer
        self.observer = None
        
        # Upload worker
        self.upload_worker = UploadWorker(self.server_manager)
        self.setup_worker_connections()
        
        # UI setup
        self.setup_modern_ui()
        self.load_settings()
        
        # Welcome
        self.show_welcome_message()
        
    def setup_worker_connections(self):
        """Connect upload worker signals"""
        self.upload_worker.upload_complete.connect(self.on_upload_success)
        self.upload_worker.upload_failed.connect(self.on_upload_failed)
        self.upload_worker.upload_progress.connect(self.on_upload_progress)
    
    def setup_modern_ui(self):
        """Setup beautiful modern user interface"""
        self.setWindowTitle("🏠 Custom Server File Manager - Client v2.0")
        self.setMinimumSize(1300, 900)
        self.resize(1400, 950)
        
        # Apply modern theme
        self.apply_modern_theme()
        
        # Central widget with modern layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create modern header
        self.create_modern_header(main_layout)
        
        # Create main content area
        self.create_main_content(main_layout)
        
        # Create status bar
        self.create_status_bar()
        
    def apply_modern_theme(self):
        """Apply modern dark theme"""
        palette = QPalette()
        
        # Colors
        dark_bg = QColor(26, 26, 26)  # #1a1a1a
        medium_bg = QColor(45, 45, 45)  # #2d2d2d
        light_bg = QColor(64, 64, 64)  # #404040
        primary_color = QColor(76, 175, 80)  # #4CAF50
        text_color = QColor(255, 255, 255)  # White
        disabled_color = QColor(128, 128, 128)  # Gray
        
        # Set palette colors
        palette.setColor(QPalette.Window, dark_bg)
        palette.setColor(QPalette.WindowText, text_color)
        palette.setColor(QPalette.Base, medium_bg)
        palette.setColor(QPalette.AlternateBase, light_bg)
        palette.setColor(QPalette.ToolTipBase, text_color)
        palette.setColor(QPalette.ToolTipText, text_color)
        palette.setColor(QPalette.Text, text_color)
        palette.setColor(QPalette.Button, medium_bg)
        palette.setColor(QPalette.ButtonText, text_color)
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, primary_color)
        palette.setColor(QPalette.Highlight, primary_color)
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        palette.setColor(QPalette.Disabled, QPalette.Text, disabled_color)
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled_color)
        
        self.setPalette(palette)
        
        # Set global stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QWidget {
                background-color: transparent;
                color: #ffffff;
            }
            QFrame {
                border: none;
            }
        """)
    
    def create_modern_header(self, parent_layout):
        """Create beautiful header with gradient and controls"""
        header_frame = QFrame()
        header_frame.setMinimumHeight(120)
        header_frame.setMaximumHeight(120)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4CAF50, stop:0.5 #2E7D32, stop:1 #1B5E20);
                border-bottom: 3px solid #2E7D32;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 20, 30, 20)
        
        # Title section
        title_layout = QVBoxLayout()
        
        title_label = QLabel("🏠 Custom Server File Manager")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title_label.setStyleSheet("color: white; background: transparent;")
        
        subtitle_label = QLabel("Upload files to your server • Auto-upload photos • Auto-resize • Share anywhere")
        subtitle_label.setFont(QFont("Segoe UI", 11))
        subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); background: transparent;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.addStretch()
        
        # Status section
        status_layout = QVBoxLayout()
        
        # Connection status
        self.connection_status = StatusIndicator("❌ Not Connected", "error")
        status_layout.addWidget(self.connection_status)
        
        # Monitoring status
        self.monitoring_status = StatusIndicator("📁 Not Monitoring", "info")
        status_layout.addWidget(self.monitoring_status)
        
        status_layout.addStretch()
        
        # Controls section
        controls_layout = QHBoxLayout()
        
        self.connect_btn = ActionButton("🔗 Connect", "primary")
        self.connect_btn.clicked.connect(self.toggle_connection)
        
        self.monitor_btn = ActionButton("🔍 Monitor", "secondary")
        self.monitor_btn.clicked.connect(self.toggle_monitoring)
        self.monitor_btn.setEnabled(False)
        
        self.settings_btn = ActionButton("⚙️ Settings", "secondary")
        self.settings_btn.clicked.connect(self.show_settings)
        
        controls_layout.addWidget(self.connect_btn)
        controls_layout.addWidget(self.monitor_btn)
        controls_layout.addWidget(self.settings_btn)
        
        # Add to header
        header_layout.addLayout(title_layout, 3)
        header_layout.addLayout(status_layout, 1)
        header_layout.addLayout(controls_layout, 2)
        
        parent_layout.addWidget(header_frame)
    
    def create_main_content(self, parent_layout):
        """Create main content area with upload and activity panels"""
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setChildrenCollapsible(False)
        
        # Left panel - Upload
        self.create_upload_panel(content_splitter)
        
        # Right panel - Activity
        self.create_activity_panel(content_splitter)
        
        # Set splitter proportions
        content_splitter.setSizes([600, 700])
        
        parent_layout.addWidget(content_splitter)
    
    def create_upload_panel(self, parent):
        """Create upload panel with drag-drop and controls"""
        upload_widget = QWidget()
        upload_layout = QVBoxLayout(upload_widget)
        upload_layout.setContentsMargins(20, 20, 20, 20)
        upload_layout.setSpacing(20)
        
        # Upload card
        upload_card = ModernCard("📤 Upload Files", "")
        
        # Drop zone
        self.drop_zone = FileDropZone()
        self.drop_zone.files_dropped.connect(self.handle_files_dropped)
        upload_card.add_content(self.drop_zone)
        
        # Upload controls
        controls_layout = QHBoxLayout()
        
        browse_btn = ActionButton("📁 Browse Files", "primary")
        browse_btn.clicked.connect(self.browse_files)
        
        add_folder_btn = ActionButton("📂 Add Folder to Monitor", "secondary")
        add_folder_btn.clicked.connect(self.add_folder_to_monitor)
        self.add_folder_btn = add_folder_btn
        add_folder_btn.setEnabled(False)
        
        controls_layout.addWidget(browse_btn)
        controls_layout.addWidget(add_folder_btn)
        controls_layout.addStretch()
        
        upload_card.add_content(controls_layout)
        
        # Progress section
        self.progress_card = ModernCard("⏳ Upload Progress", "")
        self.progress_bar = ModernProgressBar()
        self.progress_card.add_content(self.progress_bar)
        self.progress_card.hide()
        
        upload_layout.addWidget(upload_card)
        upload_layout.addWidget(self.progress_card)
        upload_layout.addStretch()
        
        parent.addWidget(upload_widget)
    
    def create_activity_panel(self, parent):
        """Create activity panel with tabs"""
        activity_widget = QWidget()
        activity_layout = QVBoxLayout(activity_widget)
        activity_layout.setContentsMargins(20, 20, 20, 20)
        activity_layout.setSpacing(20)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #404040;
                border-radius: 8px;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #505050;
            }
        """)
        
        # Activity log tab
        self.create_activity_tab()
        
        # Files tab
        self.create_files_tab()
        
        # Statistics tab
        self.create_statistics_tab()
        
        activity_layout.addWidget(self.tab_widget)
        
        parent.addWidget(activity_widget)
    
    def create_activity_tab(self):
        """Create activity log tab"""
        activity_widget = QWidget()
        activity_layout = QVBoxLayout(activity_widget)
        activity_layout.setContentsMargins(20, 20, 20, 20)
        
        self.activity_log = QTextEdit()
        self.activity_log.setReadOnly(True)
        self.activity_log.setFont(QFont("Consolas", 10))
        self.activity_log.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 10px;
                color: #ffffff;
            }
        """)
        
        activity_layout.addWidget(self.activity_log)
        
        self.tab_widget.addTab(activity_widget, "📋 Activity")
    
    def create_files_tab(self):
        """Create recent files tab"""
        files_widget = QWidget()
        files_layout = QVBoxLayout(files_widget)
        files_layout.setContentsMargins(20, 20, 20, 20)
        
        self.files_list = QListWidget()
        self.files_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1a;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 10px;
                color: #ffffff;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
            }
        """)
        
        files_layout.addWidget(self.files_list)
        
        self.tab_widget.addTab(files_widget, "📁 Files")
    
    def create_statistics_tab(self):
        """Create statistics tab"""
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setContentsMargins(20, 20, 20, 20)
        stats_layout.setSpacing(20)
        
        # Stats grid
        stats_grid = QGridLayout()
        
        # Create stat cards
        self.total_uploads_card = ModernCard("📤 Total Uploads", "")
        self.total_uploads_card.set_value("0")
        
        self.total_size_card = ModernCard("💾 Total Size", "")
        self.total_size_card.set_value("0 B")
        
        self.success_rate_card = ModernCard("✅ Success Rate", "")
        self.success_rate_card.set_value("100%")
        
        self.avg_speed_card = ModernCard("⚡ Avg Speed", "")
        self.avg_speed_card.set_value("0 MB/s")
        
        stats_grid.addWidget(self.total_uploads_card, 0, 0)
        stats_grid.addWidget(self.total_size_card, 0, 1)
        stats_grid.addWidget(self.success_rate_card, 1, 0)
        stats_grid.addWidget(self.avg_speed_card, 1, 1)
        
        stats_layout.addLayout(stats_grid)
        stats_layout.addStretch()
        
        self.tab_widget.addTab(stats_widget, "📊 Statistics")
    
    def create_status_bar(self):
        """Create modern status bar"""
        status_bar = self.statusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #2d2d2d;
                border-top: 1px solid #404040;
                color: #ffffff;
                font-size: 11px;
                padding: 5px;
            }
        """)
        
        status_bar.showMessage("Ready • Click Connect to get started")
    
    # Event handlers and methods
    def toggle_connection(self):
        """Toggle server connection"""
        if not self.connected:
            self.connect_to_server()
        else:
            self.disconnect_from_server()
    
    def connect_to_server(self):
        """Connect to the server"""
        try:
            # Try to connect with default settings
            server_url = self.get_setting('server_url', 'http://localhost:8000')
            api_key = self.get_setting('api_key', '')
            
            if self.server_manager.connect(server_url, api_key):
                self.connected = True
                self.connection_status.update_status("✅ Connected", "success")
                self.connect_btn.setText("🔌 Disconnect")
                self.connect_btn.setStyleType("danger")
                self.monitor_btn.setEnabled(True)
                self.add_folder_btn.setEnabled(True)
                
                self.log_activity("✅ Connected to server successfully")
                self.statusBar().showMessage(f"Connected to {server_url}")
            else:
                self.show_connection_dialog()
                
        except Exception as e:
            self.log_activity(f"❌ Connection failed: {str(e)}")
            self.show_connection_dialog()
    
    def disconnect_from_server(self):
        """Disconnect from server"""
        self.connected = False
        self.server_manager.disconnect()
        
        # Update UI
        self.connection_status.update_status("❌ Not Connected", "error")
        self.connect_btn.setText("🔗 Connect")
        self.connect_btn.setStyleType("primary")
        self.monitor_btn.setEnabled(False)
        self.add_folder_btn.setEnabled(False)
        
        # Stop monitoring if active
        if self.monitoring:
            self.toggle_monitoring()
        
        self.log_activity("🔌 Disconnected from server")
        self.statusBar().showMessage("Disconnected")
    
    def show_connection_dialog(self):
        """Show connection configuration dialog"""
        from .connection_dialog import ConnectionDialog
        
        dialog = ConnectionDialog(self)
        if dialog.exec() == QDialog.Accepted:
            settings = dialog.get_settings()
            self.save_setting('server_url', settings['server_url'])
            self.save_setting('api_key', settings.get('api_key', ''))
            
            # Try connecting with new settings
            if self.server_manager.connect(settings['server_url'], settings.get('api_key', '')):
                self.connected = True
                self.connection_status.update_status("✅ Connected", "success")
                self.connect_btn.setText("🔌 Disconnect")
                self.connect_btn.setStyleType("danger")
                self.monitor_btn.setEnabled(True)
                self.add_folder_btn.setEnabled(True)
                
                self.log_activity("✅ Connected to server successfully")
                self.statusBar().showMessage(f"Connected to {settings['server_url']}")
            else:
                self.log_activity("❌ Connection failed with provided settings")
    
    def toggle_monitoring(self):
        """Toggle folder monitoring"""
        if not self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start folder monitoring"""
        if not WATCHDOG_AVAILABLE:
            QMessageBox.warning(self, "Monitoring Unavailable", 
                              "File monitoring requires the 'watchdog' package.\n"
                              "Install it with: pip install watchdog")
            return
        
        if not self.monitored_directories:
            QMessageBox.information(self, "No Folders", 
                                  "Please add folders to monitor first.")
            return
        
        try:
            self.observer = Observer()
            event_handler = FileMonitorHandler(self.handle_auto_upload)
            
            for directory in self.monitored_directories:
                self.observer.schedule(event_handler, directory, recursive=True)
            
            self.observer.start()
            self.monitoring = True
            
            self.monitoring_status.update_status("🔍 Monitoring Active", "success")
            self.monitor_btn.setText("⏹️ Stop Monitor")
            
            self.log_activity(f"🔍 Started monitoring {len(self.monitored_directories)} folders")
            
        except Exception as e:
            self.log_activity(f"❌ Failed to start monitoring: {str(e)}")
    
    def stop_monitoring(self):
        """Stop folder monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        
        self.monitoring = False
        self.monitoring_status.update_status("📁 Not Monitoring", "info")
        self.monitor_btn.setText("🔍 Monitor")
        
        self.log_activity("⏹️ Stopped folder monitoring")
    
    def add_folder_to_monitor(self):
        """Add folder to monitoring list"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Monitor")
        
        if folder and folder not in self.monitored_directories:
            self.monitored_directories.append(folder)
            self.log_activity(f"📂 Added folder to monitor: {folder}")
            
            # Restart monitoring if active
            if self.monitoring:
                self.stop_monitoring()
                self.start_monitoring()
    
    def browse_files(self):
        """Browse and select files to upload"""
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Select Files to Upload",
            "",
            "All Files (*.*);;"
            "Images (*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff *.tif);;"
            "Videos (*.mp4 *.avi *.mov *.wmv *.flv *.mkv *.m4v);;"
            "Audio (*.mp3 *.wav *.flac *.aac *.ogg *.wma);;"
            "Documents (*.pdf *.txt *.doc *.docx);;"
            "Archives (*.zip *.rar *.7z)"
        )
        
        if files:
            self.handle_files_dropped(files)
    
    def handle_files_dropped(self, files):
        """Handle dropped files"""
        if not self.connected:
            QMessageBox.warning(self, "Not Connected", 
                              "Please connect to server first.")
            return
        
        self.log_activity(f"📤 Queuing {len(files)} files for upload")
        
        for filepath in files:
            self.upload_worker.add_upload(filepath)
        
        if not self.upload_worker.isRunning():
            self.upload_worker.start()
        
        self.progress_card.show()
    
    def handle_auto_upload(self, filepath):
        """Handle automatic upload from monitoring"""
        if self.connected and self.get_setting('auto_upload_enabled', True):
            self.log_activity(f"🔍 Auto-uploading: {os.path.basename(filepath)}")
            self.upload_worker.add_upload(filepath)
            
            if not self.upload_worker.isRunning():
                self.upload_worker.start()
            
            self.progress_card.show()
    
    def on_upload_success(self, filename, service, url, size):
        """Handle successful upload"""
        self.upload_stats['total_uploads'] += 1
        self.upload_stats['successful_uploads'] += 1
        self.upload_stats['total_size'] += size
        
        # Update statistics
        self.update_statistics()
        
        # Add to files list
        self.files_list.addItem(f"✅ {filename} - {url}")
        
        # Log activity
        self.log_activity(f"✅ Uploaded: {filename} -> {url}")
        
        # Auto-copy to clipboard if enabled
        if self.get_setting('auto_clipboard', True):
            QApplication.clipboard().setText(url)
            self.log_activity(f"📋 URL copied to clipboard")
        
        # Show notification
        NotificationCard.show_success(self, f"Uploaded {filename}")
    
    def on_upload_failed(self, filename, error):
        """Handle failed upload"""
        self.upload_stats['total_uploads'] += 1
        self.upload_stats['failed_uploads'] += 1
        
        # Update statistics
        self.update_statistics()
        
        # Log activity
        self.log_activity(f"❌ Failed: {filename} - {error}")
        
        # Show notification
        NotificationCard.show_error(self, f"Failed to upload {filename}")
    
    def on_upload_progress(self, status, percentage):
        """Handle upload progress"""
        self.progress_bar.update_progress(percentage, status)
        
        if percentage == 100:
            QTimer.singleShot(2000, self.progress_card.hide)
    
    def update_statistics(self):
        """Update statistics display"""
        total = self.upload_stats['total_uploads']
        successful = self.upload_stats['successful_uploads']
        size = self.upload_stats['total_size']
        
        self.total_uploads_card.set_value(str(total))
        self.total_size_card.set_value(self.format_file_size(size))
        
        if total > 0:
            success_rate = (successful / total) * 100
            self.success_rate_card.set_value(f"{success_rate:.1f}%")
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def show_settings(self):
        """Show settings dialog"""
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec()
    
    def log_activity(self, message):
        """Log activity with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activity_log.append(f"[{timestamp}] {message}")
    
    def show_welcome_message(self):
        """Show welcome message"""
        self.log_activity("🌟 Custom Server File Manager Client started")
        self.log_activity("🔗 Click 'Connect' to connect to your server")
    
    def get_setting(self, key, default=None):
        """Get setting value"""
        # In a real app, this would load from a config file
        settings = getattr(self, '_settings', {})
        return settings.get(key, default)
    
    def save_setting(self, key, value):
        """Save setting value"""
        if not hasattr(self, '_settings'):
            self._settings = {}
        self._settings[key] = value
        # In a real app, this would save to a config file
    
    def load_settings(self):
        """Load settings from file"""
        try:
            config_file = Path.home() / ".custom_server_client" / "config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    self._settings = json.load(f)
            else:
                self._settings = {}
        except Exception:
            self._settings = {}
    
    def save_settings(self):
        """Save settings to file"""
        try:
            config_dir = Path.home() / ".custom_server_client"
            config_dir.mkdir(exist_ok=True)
            
            config_file = config_dir / "config.json"
            with open(config_file, 'w') as f:
                json.dump(self._settings, f, indent=2)
        except Exception:
            pass
    
    def closeEvent(self, event):
        """Handle application close"""
        if self.monitoring:
            self.stop_monitoring()
        
        if self.upload_worker.isRunning():
            self.upload_worker.stop()
            self.upload_worker.wait()
        
        self.save_settings()
        event.accept()

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Custom Server File Manager")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Custom Server")
    
    window = ModernCustomClient()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
