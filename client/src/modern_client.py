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
import subprocess
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
                delay = 5.0 if any(filename.lower().endswith(ext) for ext in self.photo_extensions) else 2.0
                self.pending_uploads[filepath] = time.time()
                threading.Timer(delay, lambda: self._process_file(filepath)).start()
    
    def on_moved(self, event):
        """Handle file move/rename events (important for VRCX which renames VRChat screenshots)"""
        if not event.is_directory:
            src_path = event.src_path
            dest_path = event.dest_path
            filename = os.path.basename(dest_path)
            
            if any(filename.lower().endswith(ext) for ext in self.allowed_extensions):
                if src_path in self.pending_uploads:
                    del self.pending_uploads[src_path]
                
                delay = 2.0 if any(filename.lower().endswith(ext) for ext in self.photo_extensions) else 1.0
                self.pending_uploads[dest_path] = time.time()
                threading.Timer(delay, lambda: self._process_file(dest_path)).start()
    
    def _process_file(self, filepath):
        """Process file for upload with duplicate checking"""
        try:
            if filepath in self.pending_uploads:
                del self.pending_uploads[filepath]
                if os.path.exists(filepath):
                    self.callback(filepath)
        except Exception as e:
            print(f"Error processing file {filepath}: {e}")
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
        """Add file to upload queue and start worker if not running"""
        if filepath not in [item['filepath'] for item in self.upload_queue]:
            self.upload_queue.append({
                'filepath': filepath,
                'timestamp': time.time(),
                'filename': os.path.basename(filepath)
            })
            
            # Start the worker if it's not already running
            if not self.isRunning():                self.start()
    
    def run(self):
        """Process upload queue"""
        self.running = True
        
        while self.running and self.upload_queue:
            upload_item = None
            try:
                upload_item = self.upload_queue.pop(0)
                filepath = upload_item['filepath']
                filename = upload_item['filename']
                
                self.upload_progress.emit(f"Preparing {filename}", 10)
                
                if not self._wait_for_file_ready(filepath, filename):
                    continue
                
                self.upload_progress.emit(f"Uploading {filename}", 50)
                file_size = os.path.getsize(filepath)
                
                # Try to upload the file
                result = self.server_manager.upload_file(filepath)
                
                # Check if upload was successful                if result and 'url' in result:
                    self.upload_progress.emit(f"Completed {filename}", 100)
                    self.upload_complete.emit(filename, "Custom Server", result['url'], file_size)
                else:
                    self.upload_failed.emit(filename, "Upload failed - no URL in response")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                # Import ServerError to handle server-specific errors
                try:
                    from .server_client import ServerError
                except ImportError:
                    from server_client import ServerError
                
                if upload_item:
                    filename = upload_item['filename']
                else:
                    filename = "unknown file"
                
                if isinstance(e, ServerError):
                    self.upload_failed.emit(filename, str(e))
                else:
                    self.upload_failed.emit(filename, f"Upload error: {str(e)}")
        
        self.running = False
    
    def _wait_for_file_ready(self, filepath: str, filename: str) -> bool:
        """Wait for file to be ready for upload with enhanced stability checking"""
        max_retries = 15
        last_size = 0
        stable_count = 0
        required_stable_checks = 3
        
        for retry in range(max_retries):
            try:
                if not os.path.exists(filepath):
                    self.upload_failed.emit(filename, "File not found")
                    return False
                
                current_size = os.path.getsize(filepath)
                
                with open(filepath, 'rb') as test_file:
                    test_file.read(1)
                    if current_size > 1024 * 1024:
                        test_file.seek(-1, 2)
                        test_file.read(1)
                
                if current_size == last_size and current_size > 0:
                    stable_count += 1
                    if stable_count >= required_stable_checks:
                        return True
                else:
                    stable_count = 0
                    last_size = current_size
                
                if current_size > 5 * 1024 * 1024:
                    wait_time = min(3 + retry * 0.5, 8)
                else:
                    wait_time = min(1 + retry * 0.2, 3)
                
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
                    wait_time = min(2 + retry * 0.5, 5)
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
          # Try auto-connection after everything is set up
        QTimer.singleShot(1000, self.try_auto_connection)  # 1 second delay
        
        # Try auto-monitoring after connection if enabled
        QTimer.singleShot(2000, self.try_auto_monitoring)  # 2 second delay
        
    def setup_worker_connections(self):
        """Connect upload worker signals"""
        self.upload_worker.upload_complete.connect(self.on_upload_success)
        self.upload_worker.upload_failed.connect(self.on_upload_failed)
        self.upload_worker.upload_progress.connect(self.on_upload_progress)
    
    def setup_modern_ui(self):
        """Setup beautiful modern user interface with proper scaling"""
        self.setWindowTitle("🏠 VRCPhoto2URL - Desktop Client v2.0")
        self.setMinimumSize(1400, 1000)
        self.resize(1600, 1100)
        
        # Enable high DPI scaling
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # Apply modern theme with proper scaling
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
        
    def apply_modern_theme(self, custom_primary_color=None, custom_accent_color=None):
        """Apply modern dark theme matching web interface with optional custom colors"""
        palette = QPalette()
        
        # Colors matching the web admin interface
        primary_bg = QColor(15, 15, 35)      # --bg-primary: #0f0f23
        secondary_bg = QColor(26, 26, 46)    # --bg-secondary: #1a1a2e  
        surface_bg = QColor(30, 41, 59)      # --bg-surface: #1e293b
        hover_bg = QColor(51, 65, 85)        # --bg-hover: #334155
          # Use custom primary color if provided, otherwise default
        if custom_primary_color:
            if isinstance(custom_primary_color, str):
                primary_color = QColor(custom_primary_color)
            else:
                primary_color = custom_primary_color
        else:
            primary_color = QColor(244, 67, 54) # Red theme default: #F44336
        text_primary = QColor(255, 255, 255)  # --text-primary: #ffffff
        text_secondary = QColor(203, 213, 225) # --text-secondary: #cbd5e1
        text_muted = QColor(148, 163, 184)    # --text-muted: #94a3b8
        border_color = QColor(51, 65, 85)     # --border-color: #334155
        success_color = QColor(16, 185, 129)  # --success: #10b981
        
        # Set palette colors
        palette.setColor(QPalette.Window, primary_bg)
        palette.setColor(QPalette.WindowText, text_primary)
        palette.setColor(QPalette.Base, secondary_bg)
        palette.setColor(QPalette.AlternateBase, surface_bg)
        palette.setColor(QPalette.ToolTipBase, surface_bg)
        palette.setColor(QPalette.ToolTipText, text_primary)
        palette.setColor(QPalette.Text, text_primary)
        palette.setColor(QPalette.Button, surface_bg)
        palette.setColor(QPalette.ButtonText, text_primary)
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, primary_color)
        palette.setColor(QPalette.Highlight, primary_color)
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        palette.setColor(QPalette.Disabled, QPalette.Text, text_muted)
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, text_muted)
        
        self.setPalette(palette)
        
        # Set global stylesheet matching web design
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgb(15, 15, 35), stop:1 rgb(26, 26, 46));
                color: rgb(255, 255, 255);
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }}
            QWidget {{
                background-color: transparent;
                color: rgb(255, 255, 255);
                font-size: 14px;
            }}
            QFrame {{
                border: none;
            }}
            QLabel {{
                font-size: 14px;
                color: rgb(255, 255, 255);
            }}
            QTextEdit, QListWidget {{
                font-size: 13px;
                line-height: 1.5;            }}
        """)
      def apply_saved_theme_colors(self, primary_color=None, accent_color=None):
        """Apply saved theme colors to the application"""
        if primary_color or accent_color:
            try:
                try:
                    from .ui_components import apply_custom_theme
                except ImportError:
                    from ui_components import apply_custom_theme
                apply_custom_theme(self, primary_color=primary_color or "#667eea", accent_color=accent_color or "#764ba2")
                self.log_activity(f"🎨 Applied saved theme colors: Primary={primary_color}, Accent={accent_color}")
            except Exception as e:
                self.log_activity(f"⚠️ Failed to apply saved theme colors: {str(e)}")

    def refresh_theme(self):
        """Refresh theme with current settings"""
        # Load saved colors from settings
        primary_color = self.get_setting('primary_color')
        accent_color = self.get_setting('accent_color')
        
        # Apply theme with saved colors
        self.apply_modern_theme(primary_color, accent_color)
        
        # Update header gradient if we have custom colors
        if primary_color or accent_color:
            self.update_header_gradient(primary_color, accent_color)
    
    def update_header_gradient(self, primary_color=None, accent_color=None):
        """Update header gradient with custom colors"""
        primary = primary_color or "rgb(102, 126, 234)"
        accent = accent_color or "rgb(118, 75, 162)"
        
        # Find header frame and update its gradient
        header_frame = self.findChild(QFrame)
        if header_frame and header_frame.minimumHeight() == 140:  # Our header frame
            header_frame.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 {primary}, stop:0.5 {accent}, stop:1 {primary});
                    border-bottom: 2px solid rgb(51, 65, 85);
                    border-radius: 0px;
                }}
            """)
    
    def create_modern_header(self, parent_layout):
        """Create modern header matching web interface design"""
        header_frame = QFrame()
        header_frame.setMinimumHeight(140)
        header_frame.setMaximumHeight(140)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #F44336, stop:0.5 #D32F2F, stop:1 #F44336);
                border-bottom: 2px solid rgb(51, 65, 85);
                border-radius: 0px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(40, 25, 40, 25)
        header_layout.setSpacing(30)
        
        # Title section with proper typography
        title_layout = QVBoxLayout()
        
        title_label = QLabel("🚀 VRCPhoto2URL")
        title_label.setFont(QFont("Inter", 28, QFont.Bold))
        title_label.setStyleSheet("""
            color: white; 
            background: transparent;
            font-weight: 700;
            letter-spacing: -0.5px;
        """)
        
        subtitle_label = QLabel("Desktop Client • Auto-upload VRChat screenshots • Share instantly")
        subtitle_label.setFont(QFont("Inter", 13))
        subtitle_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9); 
            background: transparent;
            font-weight: 400;
            line-height: 1.5;
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.addStretch()
        
        # Status section with cards
        status_layout = QVBoxLayout()
        status_layout.setSpacing(12)
        
        # Connection status
        self.connection_status = StatusIndicator("❌ Not Connected", "error")
        status_layout.addWidget(self.connection_status)
        
        # Monitoring status
        self.monitoring_status = StatusIndicator("📁 Not Monitoring", "info")
        status_layout.addWidget(self.monitoring_status)
        
        status_layout.addStretch()
        
        # Controls section with modern buttons
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(15)
        
        self.connect_btn = ActionButton("🔗 Connect", "primary")
        self.connect_btn.clicked.connect(self.toggle_connection)
        
        self.monitor_btn = ActionButton("🔍 Monitor", "secondary")
        self.monitor_btn.clicked.connect(self.toggle_monitoring)
        self.monitor_btn.setEnabled(False)
        
        self.settings_btn = ActionButton("⚙️ Settings", "outline")
        self.settings_btn.clicked.connect(self.show_settings)
        
        controls_layout.addWidget(self.connect_btn)
        controls_layout.addWidget(self.monitor_btn)
        controls_layout.addWidget(self.settings_btn)
        
        # Add to header with proper proportions
        header_layout.addLayout(title_layout, 4)
        header_layout.addLayout(status_layout, 2)
        header_layout.addLayout(controls_layout, 3)
        
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
        """Create upload panel with drag-drop and controls with scroll area"""
        upload_widget = QWidget()
        upload_layout = QVBoxLayout(upload_widget)
        upload_layout.setContentsMargins(20, 20, 20, 20)
        upload_layout.setSpacing(20)
        
        # Create scroll area for upload content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(51, 65, 85, 0.3);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(102, 126, 234, 0.6);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(102, 126, 234, 0.8);
            }
        """)
        
        # Content widget for scroll area
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        
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
        
        controls_layout.addWidget(browse_btn)
        controls_layout.addStretch()
        
        upload_card.add_content(controls_layout)
        
        # Add folder management section to upload card
        folder_management = QHBoxLayout()
        
        add_folder_btn = ActionButton("📂 Add Folder to Monitor", "secondary")
        add_folder_btn.clicked.connect(self.add_folder_to_monitor)
        self.add_folder_btn = add_folder_btn
        add_folder_btn.setEnabled(False)
        
        manage_folders_btn = ActionButton("📋 Manage Folders", "outline")
        manage_folders_btn.clicked.connect(self.show_folder_manager)
        self.manage_folders_btn = manage_folders_btn
        manage_folders_btn.setEnabled(False)
        
        folder_management.addWidget(add_folder_btn)
        folder_management.addWidget(manage_folders_btn)
        folder_management.addStretch()
        
        upload_card.add_content(folder_management)
          # Monitored folders display
        self.monitored_folders_card = ModernCard("📁 Monitored Folders", "")
        self.monitored_folders_list = QLabel("No folders monitored")
        self.monitored_folders_list.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(15, 15, 35, 0.8), stop:1 rgba(26, 26, 46, 0.8));
                border: 1px solid rgb(51, 65, 85);
                border-radius: 12px;
                padding: 20px;
                color: rgba(203, 213, 225, 0.9);
                font-family: 'Inter', sans-serif;
                font-size: 13px;
                line-height: 1.6;
                font-weight: 400;
            }
        """)
        self.monitored_folders_card.add_content(self.monitored_folders_list)
        
        # Progress card for uploads
        self.progress_card = ModernCard("📈 Upload Progress", "")
        self.progress_bar = ModernProgressBar()
        self.progress_card.add_content(self.progress_bar)
        self.progress_card.hide()  # Hidden by default
        
        scroll_layout.addWidget(upload_card)
        scroll_layout.addWidget(self.monitored_folders_card)
        scroll_layout.addWidget(self.progress_card)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        upload_layout.addWidget(scroll_area)
        
        parent.addWidget(upload_widget)
    
    def create_activity_panel(self, parent):
        """Create activity panel with tabs"""
        activity_widget = QWidget()
        activity_layout = QVBoxLayout(activity_widget)
        activity_layout.setContentsMargins(20, 20, 20, 20)
        activity_layout.setSpacing(20)        # Create tab widget with web-matching styling
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid rgb(51, 65, 85);
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(15, 15, 35, 0.8), stop:1 rgba(26, 26, 46, 0.8));
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(51, 65, 85, 0.8), stop:1 rgba(30, 41, 59, 0.8));
                color: rgba(203, 213, 225, 0.9);
                padding: 16px 24px;
                margin-right: 4px;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                font-family: 'Inter', sans-serif;
                font-weight: 500;
                font-size: 14px;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgb(102, 126, 234), stop:1 rgb(118, 75, 162));
                color: white;
                font-weight: 600;
            }
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(71, 85, 105, 0.9), stop:1 rgba(45, 55, 72, 0.9));
                color: white;
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
        """Create activity log tab with scroll area"""
        activity_widget = QWidget()
        activity_layout = QVBoxLayout(activity_widget)
        activity_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create scroll area for activity log
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        self.activity_log = QTextEdit()
        self.activity_log.setReadOnly(True)
        self.activity_log.setFont(QFont("Inter", 12))
        self.activity_log.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(15, 15, 35, 0.9), stop:1 rgba(26, 26, 46, 0.9));
                border: 1px solid rgb(51, 65, 85);
                border-radius: 12px;
                padding: 20px;
                color: rgb(255, 255, 255);
                font-family: 'Inter', sans-serif;
                font-size: 13px;
                line-height: 1.6;
            }
            QScrollBar:vertical {
                background: rgba(51, 65, 85, 0.3);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(102, 126, 234, 0.6);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
        background: rgba(102, 126, 234, 0.8);
            }        """)
        
        scroll_area.setWidget(self.activity_log)
        activity_layout.addWidget(scroll_area)
        self.tab_widget.addTab(activity_widget, "📋 Activity")
    
    def create_files_tab(self):
        """Create recent files tab with scroll area"""
        files_widget = QWidget()
        files_layout = QVBoxLayout(files_widget)
        files_layout.setContentsMargins(20, 20, 20, 20)
          # Create scroll area for files list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        self.files_list = QListWidget()
        self.files_list.setStyleSheet("""
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(15, 15, 35, 0.9), stop:1 rgba(26, 26, 46, 0.9));
                border: 1px solid rgb(51, 65, 85);
                border-radius: 12px;
                padding: 15px;
                color: rgb(255, 255, 255);
                font-family: 'Inter', sans-serif;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 12px 16px;
                border-bottom: 1px solid rgba(51, 65, 85, 0.3);
                border-radius: 8px;
                margin-bottom: 4px;
                background: rgba(51, 65, 85, 0.1);
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(244, 67, 54, 0.3), stop:1 rgba(211, 47, 47, 0.3));
                border: 1px solid rgba(244, 67, 54, 0.5);
            }
            QListWidget::item:hover {
                background: rgba(51, 65, 85, 0.2);
                border-bottom: 1px solid rgba(244, 67, 54, 0.4);
                cursor: pointer;
            }
            QScrollBar:vertical {
                background: rgba(51, 65, 85, 0.3);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(244, 67, 54, 0.6);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(244, 67, 54, 0.8);
            }
        """)
        
        # Connect double-click to copy URL
        self.files_list.itemDoubleClicked.connect(self.copy_file_url)
        
        scroll_area.setWidget(self.files_list)
        files_layout.addWidget(scroll_area)
        self.tab_widget.addTab(files_widget, "📁 Files")
    
    def create_statistics_tab(self):
        """Create statistics tab with scroll area"""
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setContentsMargins(20, 20, 20, 20)
        stats_layout.setSpacing(20)
        
        # Create scroll area for statistics
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Content widget for scroll area
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        
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
        
        scroll_layout.addLayout(stats_grid)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        stats_layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(stats_widget, "📊 Statistics")
    
    def create_status_bar(self):
        """Create modern status bar matching web interface"""
        status_bar = self.statusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(51, 65, 85, 0.9), stop:1 rgba(30, 41, 59, 0.9));
                border-top: 1px solid rgb(51, 65, 85);
                color: rgba(203, 213, 225, 0.9);
                font-family: 'Inter', sans-serif;
                font-size: 12px;
                font-weight: 500;
                padding: 8px 20px;
                height: 32px;
            }            QStatusBar::item {
                border: none;
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
                self.manage_folders_btn.setEnabled(bool(self.monitored_directories))
                
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
        self.manage_folders_btn.setEnabled(False)
        
        # Stop monitoring if active
        if self.monitoring:
            self.toggle_monitoring()
        
        self.log_activity("🔌 Disconnected from server")
        self.statusBar().showMessage("Disconnected")
      def show_connection_dialog(self):
        """Show connection configuration dialog"""
        try:
            from .connection_dialog import ConnectionDialog
        except ImportError:
            from connection_dialog import ConnectionDialog
        
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
                self.manage_folders_btn.setEnabled(bool(self.monitored_directories))
                
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
        """Add folder to monitoring list with VRChat auto-detection"""
        # First try to auto-detect VRChat folder
        vrchat_folder = self.detect_vrchat_folder()
        if vrchat_folder and vrchat_folder not in self.monitored_directories:
            reply = QMessageBox.question(
                self, 
                "VRChat Folder Detected", 
                f"🎮 VRChat Screenshots folder detected:\n\n{vrchat_folder}\n\nWould you like to monitor this folder for automatic uploads?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Yes:
                self.monitored_directories.append(vrchat_folder)
                self.save_setting('monitored_directories', self.monitored_directories)
                self.log_activity(f"📸 Added VRChat folder to monitor: {vrchat_folder}")
                
                # Restart monitoring if active
                if self.monitoring:
                    self.stop_monitoring()
                    self.start_monitoring()
                return
            elif reply == QMessageBox.Cancel:
                return
        
        # Manual folder selection
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Select Folder to Monitor",
            str(Path.home() / "Pictures"),  # Default to Pictures folder
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder and folder not in self.monitored_directories:
            self.monitored_directories.append(folder)
            self.save_setting('monitored_directories', self.monitored_directories)
            self.log_activity(f"📂 Added folder to monitor: {folder}")
            
            # Check if this looks like a VRChat folder
            if self.is_vrchat_screenshots_folder(Path(folder)):
                self.log_activity("🎮 This folder appears to contain VRChat screenshots!")
              # Restart monitoring if active
            if self.monitoring:
                self.stop_monitoring()
                self.start_monitoring()
        elif folder in self.monitored_directories:
            QMessageBox.information(self, "Already Monitoring", f"Folder is already being monitored:\n{folder}")
        
        # Update the monitored folders display
        self.update_monitored_folders_display()
    
    def show_folder_manager(self):
        """Show folder manager dialog for removing/managing monitored folders"""
        if not self.monitored_directories:
            QMessageBox.information(self, "No Folders", "No folders are currently being monitored.")
            return
        
        # Create folder manager dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("📁 Manage Monitored Folders")
        dialog.setFixedSize(500, 400)
        dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgb(15, 15, 35), stop:1 rgb(26, 26, 46));
                color: rgb(255, 255, 255);
                font-family: 'Inter', sans-serif;
            }
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(15, 15, 35, 0.9), stop:1 rgba(26, 26, 46, 0.9));
                border: 1px solid rgb(51, 65, 85);
                border-radius: 12px;
                padding: 12px;
                font-family: 'Inter', sans-serif;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid rgba(51, 65, 85, 0.3);
                border-radius: 8px;
                margin-bottom: 4px;
                background: rgba(51, 65, 85, 0.1);
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(102, 126, 234, 0.3), stop:1 rgba(118, 75, 162, 0.3));
                border: 1px solid rgba(102, 126, 234, 0.5);
                color: white;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(51, 65, 85, 0.8), stop:1 rgba(30, 41, 59, 0.8));
                border: 1px solid rgb(51, 65, 85);
                border-radius: 8px;
                padding: 12px 20px;
                font-family: 'Inter', sans-serif;
                font-weight: 500;
                font-size: 13px;
                color: rgba(203, 213, 225, 0.9);
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(71, 85, 105, 0.9), stop:1 rgba(45, 55, 72, 0.9));
                color: white;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 41, 59, 0.9), stop:1 rgba(15, 23, 42, 0.9));
            }
            QPushButton.danger {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(220, 53, 69, 0.8), stop:1 rgba(200, 35, 51, 0.8));
                border-color: rgba(220, 53, 69, 0.6);
                color: white;
            }
            QPushButton.danger:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(200, 35, 51, 0.9), stop:1 rgba(164, 29, 42, 0.9));
            }
            QLabel {
                font-family: 'Inter', sans-serif;
                font-size: 16px;
                font-weight: 600;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(dialog)
          # Title
        title_label = QLabel("📁 Monitored Folders")
        title_label.setStyleSheet("""
            font-family: 'Inter', sans-serif;
            font-size: 18px; 
            font-weight: 700; 
            color: white; 
            margin-bottom: 15px;
            letter-spacing: -0.3px;
        """)
        layout.addWidget(title_label)
        
        # Folders list
        folders_list = QListWidget()
        for folder in self.monitored_directories:
            folders_list.addItem(folder)
        layout.addWidget(folders_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        remove_btn = QPushButton("🗑️ Remove Selected")
        remove_btn.setProperty("class", "danger")
        remove_btn.setStyleSheet("QPushButton { background-color: #dc3545; border-color: #dc3545; }")
        
        open_btn = QPushButton("📂 Open Folder")
        refresh_btn = QPushButton("🔄 Refresh")
        close_btn = QPushButton("✅ Close")
        
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(open_btn)
        button_layout.addWidget(refresh_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Button connections
        def remove_selected():
            current_item = folders_list.currentItem()
            if current_item:
                folder_path = current_item.text()
                reply = QMessageBox.question(
                    dialog,
                    "Remove Folder",
                    f"Stop monitoring this folder?\n\n{folder_path}",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.monitored_directories.remove(folder_path)
                    self.save_setting('monitored_directories', self.monitored_directories)
                    folders_list.takeItem(folders_list.currentRow())
                    self.log_activity(f"🗑️ Removed folder from monitoring: {folder_path}")
                    
                    # Restart monitoring if active
                    if self.monitoring:
                        self.stop_monitoring()
                        if self.monitored_directories:  # Only restart if there are folders left
                            self.start_monitoring()
                    
                    # Update display
                    self.update_monitored_folders_display()
                      # Close dialog if no folders left
                    if not self.monitored_directories:
                        QMessageBox.information(dialog, "All Folders Removed", "No folders are being monitored anymore.")
                        dialog.accept()
            else:
                QMessageBox.information(dialog, "No Selection", "Please select a folder to remove.")
        
        def open_selected():
            current_item = folders_list.currentItem()
            if current_item:
                folder_path = current_item.text()
                if Path(folder_path).exists():
                    import subprocess
                    subprocess.Popen(f'explorer "{folder_path}"')
                else:
                    QMessageBox.warning(dialog, "Folder Not Found", f"Folder no longer exists:\n{folder_path}")
            else:
                QMessageBox.information(dialog, "No Selection", "Please select a folder to open.")
        
        def refresh_list():
            # Remove non-existent folders
            existing_folders = [f for f in self.monitored_directories if Path(f).exists()]
            if len(existing_folders) != len(self.monitored_directories):
                removed_count = len(self.monitored_directories) - len(existing_folders)
                self.monitored_directories = existing_folders
                self.save_setting('monitored_directories', self.monitored_directories)
                
                # Refresh the list widget
                folders_list.clear()
                for folder in self.monitored_directories:
                    folders_list.addItem(folder)
                
                self.update_monitored_folders_display()
                QMessageBox.information(dialog, "Folders Refreshed", f"Removed {removed_count} non-existent folders.")
                
                if not self.monitored_directories:
                    dialog.accept()
            else:
                QMessageBox.information(dialog, "All Good", "All monitored folders still exist.")
        
        remove_btn.clicked.connect(remove_selected)
        open_btn.clicked.connect(open_selected)
        refresh_btn.clicked.connect(refresh_list)
        close_btn.clicked.connect(dialog.accept)
        
        dialog.exec()
    
    def update_monitored_folders_display(self):
        """Update the monitored folders display in the UI"""
        if not self.monitored_directories:
            self.monitored_folders_list.setText("No folders monitored")
        else:
            # Create a nicely formatted list
            folder_text = ""
            for i, folder in enumerate(self.monitored_directories):
                folder_name = Path(folder).name
                if len(folder) > 50:
                    # Truncate long paths
                    display_path = f"...{folder[-45:]}"
                else:
                    display_path = folder
                
                folder_text += f"<b>{i+1}. {folder_name}</b><br>{display_path}<br><br>"            
            self.monitored_folders_list.setText(f"<html>{folder_text}</html>")
        
        # Update manage folders button state
        self.manage_folders_btn.setEnabled(bool(self.monitored_directories) and self.connected)
    
    def log_activity(self, message: str):
        """Log activity message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"<font color='#4CAF50'>[{timestamp}] {message}</font>"
        
        # Append to activity log
        self.activity_log.append(formatted_message)
        
        # Auto-scroll to bottom
        self.activity_log.verticalScrollBar().setValue(self.activity_log.verticalScrollBar().maximum())
    
    def browse_files(self):
        """Open file dialog to select files for upload"""
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Select Files to Upload",
            str(Path.home()),
            "All Files (*);;Images (*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff *.tif);;Videos (*.mp4 *.avi *.mov *.wmv *.flv *.mkv *.m4v);;Audio (*.mp3 *.wav *.flac *.aac *.ogg *.wma);;Documents (*.pdf *.txt *.doc *.docx);;Archives (*.zip *.rar *.7z)"
        )
        
        if files:
            for file in files:
                self.upload_worker.add_upload(file)
            
            self.log_activity(f"📤 Added {len(files)} files to upload queue")
    
    def handle_files_dropped(self, files: List[str]):
        """Handle files dropped onto the application window"""
        if not files:
            return
        
        # Add to upload worker
        for file in files:
            self.upload_worker.add_upload(file)
        
        self.log_activity(f"📥 Added {len(files)} files to upload queue from drop")
    
    def handle_auto_upload(self, filepath: str):
        """Handle automatic upload of newly created/moved files"""
        if not self.connected:
            self.log_activity("❌ Cannot upload, not connected to server")
            return
          # Add to upload worker
        self.upload_worker.add_upload(filepath)
        self.log_activity(f"📤 Auto-uploading file: {filepath}")
    
    def detect_vrchat_folder(self) -> Optional[str]:
        """Auto-detect VRChat screenshots folder"""
        possible_paths = [
            Path.home() / "Pictures" / "VRChat",
            Path.home() / "Documents" / "VRChat",
            Path("C:/Users") / os.getlogin() / "Pictures" / "VRChat",
            Path("D:/VRChat/Screenshots"),
            Path("E:/VRChat/Screenshots")
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_dir():
                # Check if it looks like a VRChat screenshots folder
                if self.is_vrchat_screenshots_folder(path):
                    return str(path)
        
        return None
    
    def is_vrchat_screenshots_folder(self, path: Path) -> bool:
        """Check if a folder looks like a VRChat screenshots folder"""
        try:
            if not path.exists() or not path.is_dir():
                return False
            
            # Check for VRChat in folder name
            if "vrchat" in path.name.lower():
                return True
            
            # Check for VRChat screenshot filename patterns
            files = list(path.glob("*.png"))
            vrchat_files = [f for f in files if "VRChat_" in f.name or "vrchat" in f.name.lower()]
            
            # If folder has VRChat-pattern files, consider it a VRChat folder
            if vrchat_files:
                return True
                
            # Check if folder has recent PNG files (potential screenshots)
            return len(files) > 0
            
        except Exception:
            return False
    
    def load_settings(self):
        """Load settings from file with VRChat auto-detection and monitored directories restoration"""
        try:
            # Load from user's home directory
            config_file = Path.home() / ".custom_server_client" / "config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    self._settings = json.load(f)
            else:
                self._settings = {}
            
            # Restore monitored directories from settings
            saved_directories = self._settings.get('monitored_directories', [])
            if saved_directories:
                # Verify directories still exist
                valid_directories = []
                for directory in saved_directories:
                    if Path(directory).exists():
                        valid_directories.append(directory)
                    else:
                        self.log_activity(f"📂 Removed non-existent folder: {directory}")
                
                self.monitored_directories = valid_directories
                
                # Update settings if directories were removed
                if len(valid_directories) != len(saved_directories):
                    self.save_setting('monitored_directories', valid_directories)
                
                self.log_activity(f"📂 Restored {len(valid_directories)} monitored folders from settings")
            else:
                # First launch or no saved directories - try auto-detecting VRChat folder
                vrchat_folder = self.detect_vrchat_folder()
                if vrchat_folder:
                    self.monitored_directories = [vrchat_folder]
                    self.save_setting('monitored_directories', self.monitored_directories)
                    self.log_activity(f"🎮 Auto-detected and added VRChat folder: {vrchat_folder}")
                else:
                    self.monitored_directories = []            # Update the folders display
            QTimer.singleShot(500, self.update_monitored_folders_display)
            
            # Apply saved theme colors if available
            primary_color = self._settings.get('primary_color')
            accent_color = self._settings.get('accent_color')
            if primary_color or accent_color:
                # Use QTimer to ensure UI is fully initialized before applying theme
                QTimer.singleShot(1000, lambda: self.apply_saved_theme_colors(primary_color, accent_color))
            
        except Exception as e:
            self.log_activity(f"⚠️ Failed to load settings: {str(e)}")
            self._settings = {}
            self.monitored_directories = []
            
            # Try VRChat auto-detection as fallback
            try:
                vrchat_folder = self.detect_vrchat_folder()
                if vrchat_folder:
                    self.monitored_directories = [vrchat_folder]
                    self.save_setting('monitored_directories', self.monitored_directories)
                    self.log_activity(f"🎮 Auto-detected VRChat folder on fallback: {vrchat_folder}")
                QTimer.singleShot(500, self.update_monitored_folders_display)
            except Exception:
                pass
    
    def try_auto_connection(self):
        """Try auto-connection after UI is set up"""
        server_url = self.get_setting('server_url', '')
        if server_url and not self.connected:
            self.log_activity(f"🔄 Attempting auto-connection to {server_url}")
            self.connect_to_server()
    
    def try_auto_monitoring(self):
        """Try auto-monitoring if enabled in settings and connected"""
        start_monitoring = self.get_setting('start_monitoring', False)
        if start_monitoring and self.connected and self.monitored_directories and not self.monitoring:
            self.log_activity("🔄 Auto-starting folder monitoring...")
            self.start_monitoring()
    
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
        # Stop monitoring if active
        if self.monitoring:
            self.stop_monitoring()
          # Stop upload worker if running
        if self.upload_worker.isRunning():
            self.upload_worker.stop()
            self.upload_worker.wait()
        
        # Save settings
        self.save_settings()
        event.accept()

    def get_setting(self, key, default=None):
        """Get setting value"""
        return getattr(self, '_settings', {}).get(key, default)
    
    def save_setting(self, key, value):
        """Save setting value"""
        if not hasattr(self, '_settings'):
            self._settings = {}
        self._settings[key] = value
        self.save_settings()
    
    def show_welcome_message(self):
        """Show welcome message in activity log"""
        self.log_activity("🏠 Welcome to Custom Server File Manager!")
        self.log_activity("📁 Connect to your server to start uploading files")
        self.log_activity("🔍 Add folders to monitor for automatic uploads")
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self)
        
        # Connect to settings changed signal to refresh theme immediately
        if hasattr(dialog, 'settings_changed'):
            dialog.settings_changed.connect(self.on_settings_changed)
        
        if dialog.exec() == QDialog.Accepted:
            settings = dialog.get_settings()
            for key, value in settings.items():
                self.save_setting(key, value)
            self.log_activity("⚙️ Settings updated")
            
            # Apply theme changes if color settings were modified
            if 'primary_color' in settings or 'accent_color' in settings:
                self.apply_saved_theme_colors(                settings.get('primary_color'), 
                    settings.get('accent_color')
                )
    
    def on_settings_changed(self):
        """Handle settings changes from dialog"""
        # Reload and apply settings immediately
        primary_color = self.get_setting('primary_color')
        accent_color = self.get_setting('accent_color')
        
        if primary_color or accent_color:
            self.apply_saved_theme_colors(primary_color, accent_color)

    def on_upload_success(self, filename, service, url, size):
        """Handle successful upload"""
        self.upload_stats['total_uploads'] += 1
        self.upload_stats['successful_uploads'] += 1
        self.upload_stats['total_size'] += size
        
        # Update statistics
        self.update_statistics()
          # Add to files list with stored URL data
        item_text = f"✅ {filename} - Click to copy URL"
        self.files_list.addItem(item_text)
        # Store URL data in the item for easy access
        item = self.files_list.item(self.files_list.count() - 1)
        item.setData(Qt.UserRole, url)
        
        # Log activity
        self.log_activity(f"✅ Uploaded: {filename} -> {url}")
        
        # Auto-copy to clipboard if enabled
        if self.get_setting('auto_clipboard', True):
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText(url)
            self.log_activity(f"📋 URL copied to clipboard")
        
        # Show notification
        NotificationCard.show_success(self, f"Uploaded {filename}")
    
    def copy_file_url(self, item):
        """Copy file URL to clipboard when item is double-clicked"""
        if item:
            url = item.data(Qt.UserRole)
            if url:
                from PySide6.QtWidgets import QApplication, QMessageBox
                QApplication.clipboard().setText(url)
                self.log_activity(f"📋 Copied URL to clipboard: {url}")
                
                # Show a brief notification
                msg = QMessageBox(self)
                msg.setWindowTitle("URL Copied")
                msg.setText(f"URL copied to clipboard!\n\n{url}")
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
    
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
        failed = self.upload_stats['failed_uploads']
        size = self.upload_stats['total_size']
        
        # Format file size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"
          # Update status
        self.total_uploads_card.set_value(str(total))
        self.total_size_card.set_value(size_str)
        
        # Calculate success rate
        success_rate = 100 if total == 0 else (successful / total) * 100
        self.success_rate_card.set_value(f"{success_rate:.1f}%")
