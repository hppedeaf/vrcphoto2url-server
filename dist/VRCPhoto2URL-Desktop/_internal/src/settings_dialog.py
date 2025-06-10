#!/usr/bin/env python3
"""
Settings Dialog for Custom Server File Manager Client
Modern settings interface with theme customization
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QSpinBox,
    QFrame, QTabWidget, QWidget, QGroupBox, QComboBox,
    QGridLayout, QSlider, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor

class SettingsDialog(QDialog):
    """Modern settings dialog with multiple categories"""
    
    settings_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        
        # Initialize color variables
        self.current_primary_color = 'rgb(244, 67, 54)'  # Red theme default
        self.current_accent_color = 'rgb(211, 47, 47)'   # Red theme secondary
        
        # Settings management
        self.settings_file = Path.home() / ".custom_server_client" / "settings.json"
        self.backup_dir = Path.home() / ".custom_server_client" / "backups"
        self.auto_save_enabled = True
        self.settings_dirty = False
        
        self.setup_ui()
        self.load_settings()
        self.setup_auto_save()
        
    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("⚙️ Settings")
        self.setMinimumSize(700, 550)
        self.resize(800, 650)
        self.setModal(True)
        
        # Apply enhanced red gradient styling
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgb(15, 15, 35), stop:0.3 rgb(20, 20, 40), 
                    stop:0.7 rgb(22, 22, 42), stop:1 rgb(26, 26, 46));
                color: #ffffff;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                font-weight: 400;
            }
            
            QTabWidget::pane {
                border: none;
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(45, 55, 72, 0.4), stop:1 rgba(244, 67, 54, 0.05));
                margin-top: 10px;
            }
            
            QTabWidget::tab-bar {
                alignment: center;
                background: transparent;
            }
            
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(30, 41, 59, 0.6), stop:1 rgba(244, 67, 54, 0.1));
                color: rgba(203, 213, 225, 0.9);
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                margin: 0 2px;
                font-weight: 500;
                font-size: 13px;
                min-width: 100px;
            }
            
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F55336, stop:1 #E33F2F);
                color: white;
            }
            
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F44336, stop:1 #D32F2F);
                color: white;
                font-weight: 600;
            }
            
            QGroupBox {
                font-weight: 600;
                border: none;
                border-radius: 12px;
                margin-top: 20px;
                padding-top: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(45, 55, 72, 0.3), stop:1 rgba(244, 67, 54, 0.02));
                font-size: 14px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F44336, stop:1 #D32F2F);
                color: white;
                border-radius: 6px;
                font-weight: 600;
            }
            
            QScrollArea {
                border: none;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(30, 41, 59, 0.1), stop:1 rgba(244, 67, 54, 0.02));
                border-radius: 8px;
            }
            
            QScrollBar:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 41, 59, 0.5), stop:1 rgba(244, 67, 54, 0.1));
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }
            
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F44336, stop:1 #D32F2F);
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F55336, stop:1 #E33F2F);
            }
            
            QCheckBox {
                color: rgba(226, 232, 240, 0.9);
                font-size: 13px;
                font-weight: 400;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid rgba(100, 116, 139, 0.3);
                background: rgba(30, 41, 59, 0.4);
            }
            
            QCheckBox::indicator:hover {
                border: 2px solid #F44336;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(244, 67, 54, 0.1), stop:1 rgba(211, 47, 47, 0.05));
            }
            
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F44336, stop:1 #D32F2F);
                border: 2px solid #F44336;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSI+CjxwYXRoIGQ9Ik0xMCAzTDQuNSA4LjVMMiA2IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
            
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(45, 55, 72, 0.6), stop:1 rgba(244, 67, 54, 0.1));
                color: rgba(226, 232, 240, 0.9);
                border: 2px solid rgba(100, 116, 139, 0.2);
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: 500;
                font-size: 13px;
                min-width: 100px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F55336, stop:1 #E33F2F);
                border: 2px solid #F44336;
                color: white;
            }
            
            QPushButton[class="primary"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F44336, stop:1 #D32F2F);
                color: white;
                border: 2px solid #F44336;
                font-weight: 600;
            }
            
            QPushButton[class="primary"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F55336, stop:1 #E33F2F);
                border: 2px solid #F55336;
            }
            
            QSpinBox, QSlider {
                background: rgba(30, 41, 59, 0.4);
                border: 2px solid rgba(100, 116, 139, 0.3);
                border-radius: 6px;
                padding: 6px 10px;
                color: rgba(226, 232, 240, 0.9);
                font-size: 13px;
            }
            
            QSpinBox:focus, QSlider:focus {
                border: 2px solid #F44336;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(244, 67, 54, 0.1), stop:1 rgba(30, 41, 59, 0.4));
            }
            
            QSlider::groove:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 41, 59, 0.6), stop:1 rgba(244, 67, 54, 0.2));
                height: 6px;
                border-radius: 3px;
            }
            
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F44336, stop:1 #D32F2F);
                border: 2px solid #F44336;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F55336, stop:1 #E33F2F);
                border: 2px solid #F55336;
            }
            
            QLabel {
                color: rgba(203, 213, 225, 0.9);
                font-size: 13px;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # Header
        self.create_header(main_layout)
        
        # Tab widget
        self.create_tabs(main_layout)
        
        # Buttons
        self.create_buttons(main_layout)
        
    def create_header(self, parent_layout):
        """Create dialog header with gradient styling"""
        header_layout = QVBoxLayout()
        
        title_label = QLabel("⚙️ Settings")
        title_label.setFont(QFont("Inter", 24, QFont.Bold))
        title_label.setStyleSheet("""
            color: transparent;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #F44336, stop:1 #D32F2F);
            -webkit-background-clip: text;
            background-clip: text;
            margin-bottom: 8px; 
            font-weight: 700;
        """)
        
        subtitle_label = QLabel("Customize your Custom Server File Manager Client")
        subtitle_label.setFont(QFont("Inter", 12, QFont.Normal))
        subtitle_label.setStyleSheet("color: rgba(203, 213, 225, 0.8); font-weight: 400;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        parent_layout.addLayout(header_layout)
        
        # Enhanced gradient separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 #F44336, stop:0.5 #D32F2F, stop:1 #F44336); 
            max-height: 3px; 
            border: none; 
            border-radius: 2px;
            margin: 15px 0;
        """)
        parent_layout.addWidget(separator)
    
    def create_tabs(self, parent_layout):
        """Create settings tabs"""
        self.tab_widget = QTabWidget()
        
        # General tab
        self.create_general_tab()
        
        # Upload tab
        self.create_upload_tab()
        
        # Theme tab
        self.create_theme_tab()
        
        # Advanced tab
        self.create_advanced_tab()
        
        parent_layout.addWidget(self.tab_widget)
    
    def create_general_tab(self):
        """Create general settings tab with scroll area"""
        general_widget = QWidget()
        general_layout = QVBoxLayout(general_widget)
        general_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Content widget for scroll area
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(20)
        
        # Auto Upload Group
        auto_upload_group = QGroupBox("📤 Auto Upload Settings")
        auto_upload_layout = QVBoxLayout(auto_upload_group)
        auto_upload_layout.setSpacing(10)
        
        self.auto_upload_checkbox = QCheckBox("Enable auto-upload for new photos")
        self.auto_upload_checkbox.setChecked(True)
        
        self.auto_clipboard_checkbox = QCheckBox("Auto-copy URLs to clipboard")
        self.auto_clipboard_checkbox.setChecked(True)
        
        self.auto_notifications_checkbox = QCheckBox("Show upload notifications")
        self.auto_notifications_checkbox.setChecked(True)
        
        auto_upload_layout.addWidget(self.auto_upload_checkbox)
        auto_upload_layout.addWidget(self.auto_clipboard_checkbox)
        auto_upload_layout.addWidget(self.auto_notifications_checkbox)
        
        # Startup Group
        startup_group = QGroupBox("🚀 Startup Settings")
        startup_layout = QVBoxLayout(startup_group)
        startup_layout.setSpacing(10)
        
        self.auto_connect_checkbox = QCheckBox("Auto-connect to last server on startup")
        self.minimize_to_tray_checkbox = QCheckBox("Minimize to system tray")
        self.start_monitoring_checkbox = QCheckBox("Start folder monitoring automatically")
        
        startup_layout.addWidget(self.auto_connect_checkbox)
        startup_layout.addWidget(self.minimize_to_tray_checkbox)
        startup_layout.addWidget(self.start_monitoring_checkbox)
        
        scroll_layout.addWidget(auto_upload_group)
        scroll_layout.addWidget(startup_group)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        general_layout.addWidget(scroll_area)
        self.tab_widget.addTab(general_widget, "🏠 General")
    
    def create_upload_tab(self):
        """Create upload settings tab with scroll area"""
        upload_widget = QWidget()
        upload_layout = QVBoxLayout(upload_widget)
        upload_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Content widget for scroll area
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(20)
        
        # Image Processing Group
        image_group = QGroupBox("🖼️ Image Processing")
        image_layout = QFormLayout(image_group)
        image_layout.setSpacing(15)
        
        self.auto_resize_checkbox = QCheckBox("Auto-resize large images")
        
        self.max_resolution_spinbox = QSpinBox()
        self.max_resolution_spinbox.setRange(512, 4096)
        self.max_resolution_spinbox.setValue(2048)
        self.max_resolution_spinbox.setSuffix(" px")
        
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(50, 100)
        self.quality_slider.setValue(85)
        
        self.quality_label = QLabel("85%")
        self.quality_slider.valueChanged.connect(lambda v: self.quality_label.setText(f"{v}%"))
        
        image_layout.addRow("", self.auto_resize_checkbox)
        image_layout.addRow("Maximum resolution:", self.max_resolution_spinbox)
        image_layout.addRow("JPEG quality:", self.quality_slider)
        image_layout.addRow("", self.quality_label)
        
        # File Types Group
        types_group = QGroupBox("📁 Supported File Types")
        types_layout = QVBoxLayout(types_group)
        types_layout.setSpacing(10)
        
        self.images_checkbox = QCheckBox("Images (JPG, PNG, GIF, WEBP, etc.)")
        self.images_checkbox.setChecked(True)
        
        self.videos_checkbox = QCheckBox("Videos (MP4, AVI, MOV, etc.)")
        self.videos_checkbox.setChecked(True)
        
        self.audio_checkbox = QCheckBox("Audio files (MP3, WAV, FLAC, etc.)")
        self.audio_checkbox.setChecked(True)
        
        self.documents_checkbox = QCheckBox("Documents (PDF, TXT, DOC, etc.)")
        self.documents_checkbox.setChecked(True)
        
        self.archives_checkbox = QCheckBox("Archives (ZIP, RAR, 7Z)")
        self.archives_checkbox.setChecked(False)
        
        types_layout.addWidget(self.images_checkbox)
        types_layout.addWidget(self.videos_checkbox)
        types_layout.addWidget(self.audio_checkbox)
        types_layout.addWidget(self.documents_checkbox)
        types_layout.addWidget(self.archives_checkbox)
        
        scroll_layout.addWidget(image_group)
        scroll_layout.addWidget(types_group)
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        upload_layout.addWidget(scroll_area)
        self.tab_widget.addTab(upload_widget, "📤 Upload")
    
    def create_theme_tab(self):
        """Create simplified theme settings tab - Red Theme Default"""
        theme_widget = QWidget()
        theme_layout = QVBoxLayout(theme_widget)
        theme_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Content widget for scroll area
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(20)
        
        # Theme Info Group with enhanced gradient
        theme_info_group = QGroupBox("🎨 Current Theme")
        theme_info_layout = QVBoxLayout(theme_info_group)
        theme_info_layout.setSpacing(15)
        
        # Show current theme as red with enhanced gradient
        current_theme_label = QLabel("🔴 Red Theme (Default)")
        current_theme_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F44336, stop:0.3 #E53935, stop:0.7 #D32F2F, stop:1 #F44336);
                color: white;
                padding: 18px;
                border-radius: 12px;
                font-weight: 700;
                font-size: 16px;
                text-align: center;
                border: 2px solid rgba(244, 67, 54, 0.3);
            }
        """)
        current_theme_label.setAlignment(Qt.AlignCenter)
        
        theme_description = QLabel("The application uses a beautiful red gradient theme with modern design elements and enhanced visual effects.")
        theme_description.setStyleSheet("""
            color: rgba(203, 213, 225, 0.8); 
            font-size: 13px; 
            padding: 10px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(244, 67, 54, 0.05), stop:1 rgba(30, 41, 59, 0.1));
            border-radius: 8px;
        """)
        theme_description.setWordWrap(True)
        
        theme_info_layout.addWidget(current_theme_label)
        theme_info_layout.addWidget(theme_description)
        
        # Interface Group
        interface_group = QGroupBox("🖥️ Interface Settings")
        interface_layout = QFormLayout(interface_group)
        interface_layout.setSpacing(15)
        
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 18)
        self.font_size_spinbox.setValue(12)
        self.font_size_spinbox.setSuffix(" pt")
        
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(80, 100)
        self.opacity_slider.setValue(100)
        self.opacity_label = QLabel("100%")
        self.opacity_slider.valueChanged.connect(lambda v: self.opacity_label.setText(f"{v}%"))
        
        interface_layout.addRow("Font size:", self.font_size_spinbox)
        interface_layout.addRow("Window opacity:", self.opacity_slider)
        interface_layout.addRow("", self.opacity_label)
        
        scroll_layout.addWidget(theme_info_group)
        scroll_layout.addWidget(interface_group)
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        theme_layout.addWidget(scroll_area)
        self.tab_widget.addTab(theme_widget, "🎨 Theme")
    
    def create_advanced_tab(self):
        """Create advanced settings tab with scroll area"""
        advanced_widget = QWidget()
        advanced_layout = QVBoxLayout(advanced_widget)
        advanced_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Content widget for scroll area
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(20)
        
        # Network Group
        network_group = QGroupBox("🌐 Network Settings")
        network_layout = QFormLayout(network_group)
        network_layout.setSpacing(15)
        
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(5, 120)
        self.timeout_spinbox.setValue(30)
        self.timeout_spinbox.setSuffix(" seconds")
        
        self.retry_attempts_spinbox = QSpinBox()
        self.retry_attempts_spinbox.setRange(1, 10)
        self.retry_attempts_spinbox.setValue(3)
        
        self.concurrent_uploads_spinbox = QSpinBox()
        self.concurrent_uploads_spinbox.setRange(1, 10)
        self.concurrent_uploads_spinbox.setValue(3)
        
        network_layout.addRow("Connection timeout:", self.timeout_spinbox)
        network_layout.addRow("Retry attempts:", self.retry_attempts_spinbox)
        network_layout.addRow("Concurrent uploads:", self.concurrent_uploads_spinbox)
        
        # Monitoring Group
        monitoring_group = QGroupBox("👁️ File Monitoring")
        monitoring_layout = QFormLayout(monitoring_group)
        monitoring_layout.setSpacing(15)
        
        self.scan_interval_spinbox = QSpinBox()
        self.scan_interval_spinbox.setRange(1, 60)
        self.scan_interval_spinbox.setValue(5)
        self.scan_interval_spinbox.setSuffix(" seconds")
        
        self.ignore_hidden_checkbox = QCheckBox("Ignore hidden files")
        self.ignore_hidden_checkbox.setChecked(True)
        
        self.ignore_temp_checkbox = QCheckBox("Ignore temporary files")
        self.ignore_temp_checkbox.setChecked(True)
        
        monitoring_layout.addRow("Scan interval:", self.scan_interval_spinbox)
        monitoring_layout.addRow("", self.ignore_hidden_checkbox)
        monitoring_layout.addRow("", self.ignore_temp_checkbox)
        
        # Debug Group
        debug_group = QGroupBox("🐛 Debug Settings")
        debug_layout = QVBoxLayout(debug_group)
        debug_layout.setSpacing(10)
        
        self.verbose_logging_checkbox = QCheckBox("Enable verbose logging")
        self.debug_mode_checkbox = QCheckBox("Enable debug mode")
        self.save_logs_checkbox = QCheckBox("Save logs to file")
        
        debug_layout.addWidget(self.verbose_logging_checkbox)
        debug_layout.addWidget(self.debug_mode_checkbox)
        debug_layout.addWidget(self.save_logs_checkbox)
        
        scroll_layout.addWidget(network_group)
        scroll_layout.addWidget(monitoring_group)
        scroll_layout.addWidget(debug_group)
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        advanced_layout.addWidget(scroll_area)
        self.tab_widget.addTab(advanced_widget, "🔧 Advanced")
    
    def create_buttons(self, parent_layout):
        """Create dialog buttons with enhanced gradient styling"""
        button_layout = QHBoxLayout()
        
        # Reset button
        reset_button = QPushButton("🔄 Reset to Defaults")
        reset_button.setProperty("class", "secondary")
        reset_button.clicked.connect(self.reset_to_defaults)
        
        button_layout.addWidget(reset_button)
        button_layout.addStretch()
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setProperty("class", "secondary")
        cancel_button.clicked.connect(self.reject)
        
        # Save button
        save_button = QPushButton("💾 Save Settings")
        save_button.setProperty("class", "primary")
        save_button.clicked.connect(self.save_and_close)
        save_button.setDefault(True)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        parent_layout.addLayout(button_layout)
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self, 
            "Reset Settings",
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.load_default_settings()
            self.mark_settings_dirty()
    
    def load_default_settings(self):
        """Load default settings"""
        # General
        self.auto_upload_checkbox.setChecked(True)
        self.auto_clipboard_checkbox.setChecked(True)
        self.auto_notifications_checkbox.setChecked(True)
        self.auto_connect_checkbox.setChecked(False)
        self.minimize_to_tray_checkbox.setChecked(False)
        self.start_monitoring_checkbox.setChecked(False)
        
        # Upload
        self.auto_resize_checkbox.setChecked(False)
        self.max_resolution_spinbox.setValue(2048)
        self.quality_slider.setValue(85)
        self.images_checkbox.setChecked(True)
        self.videos_checkbox.setChecked(True)
        self.audio_checkbox.setChecked(True)
        self.documents_checkbox.setChecked(True)
        self.archives_checkbox.setChecked(False)
        
        # Theme
        self.font_size_spinbox.setValue(12)
        self.opacity_slider.setValue(100)
        
        # Advanced
        self.timeout_spinbox.setValue(30)
        self.retry_attempts_spinbox.setValue(3)
        self.concurrent_uploads_spinbox.setValue(3)
        self.scan_interval_spinbox.setValue(5)
        self.ignore_hidden_checkbox.setChecked(True)
        self.ignore_temp_checkbox.setChecked(True)
        self.verbose_logging_checkbox.setChecked(False)
        self.debug_mode_checkbox.setChecked(False)
        self.save_logs_checkbox.setChecked(False)
    
    def load_settings(self):
        """Load settings from file with enhanced error handling"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                # Check if settings format needs migration
                if settings.get('version', '1.0') < '2.0':
                    print("📦 Migrating settings to new format...")
                    self.migrate_settings(settings)
                
                self.apply_settings(settings)
                print(f"✅ Settings loaded from {self.settings_file}")
                
                # Load theme gradients if available
                if 'theme_settings' in settings:
                    self.apply_gradient_theme(settings['theme_settings'])
                    
            else:
                print("📝 No settings file found, loading defaults...")
                self.load_default_settings()
                # Save defaults to create initial file
                self.save_settings_internal(silent=True)
                
        except json.JSONDecodeError as e:
            print(f"⚠️ Settings file corrupted: {e}")
            self.restore_from_backup()
        except Exception as e:
            print(f"⚠️ Failed to load settings: {e}")
            self.load_default_settings()
    
    def migrate_settings(self, settings):
        """Migrate old settings format to new format"""
        # Add migration logic for future versions
        settings['version'] = '2.0'
        print("✅ Settings migration completed")
    
    def restore_from_backup(self):
        """Restore settings from the most recent backup"""
        try:
            if not self.backup_dir.exists():
                self.load_default_settings()
                return
                
            backups = sorted(self.backup_dir.glob("settings_backup_*.json"))
            if not backups:
                self.load_default_settings()
                return
                
            latest_backup = backups[-1]
            with open(latest_backup, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                self.apply_settings(settings)
                
            print(f"✅ Settings restored from backup: {latest_backup.name}")
            
            # Copy backup to main settings file
            shutil.copy2(latest_backup, self.settings_file)
            
        except Exception as e:
            print(f"⚠️ Failed to restore from backup: {e}")
            self.load_default_settings()
    
    def apply_gradient_theme(self, theme_settings):
        """Apply gradient theme settings to the interface"""
        if self.parent_window:
            try:
                # Apply gradients to parent window if it has the method
                if hasattr(self.parent_window, 'apply_gradient_theme'):
                    self.parent_window.apply_gradient_theme(theme_settings)
                print("✅ Gradient theme applied")
            except Exception as e:
                print(f"⚠️ Failed to apply gradient theme: {e}")
    
    def apply_settings(self, settings):
        """Apply loaded settings to UI"""
        # General
        self.auto_upload_checkbox.setChecked(settings.get('auto_upload_enabled', True))
        self.auto_clipboard_checkbox.setChecked(settings.get('auto_clipboard', True))
        self.auto_notifications_checkbox.setChecked(settings.get('auto_notifications', True))
        self.auto_connect_checkbox.setChecked(settings.get('auto_connect', False))
        self.minimize_to_tray_checkbox.setChecked(settings.get('minimize_to_tray', False))
        self.start_monitoring_checkbox.setChecked(settings.get('start_monitoring', False))
        
        # Upload
        self.auto_resize_checkbox.setChecked(settings.get('auto_resize', False))
        self.max_resolution_spinbox.setValue(settings.get('max_resolution', 2048))
        self.quality_slider.setValue(settings.get('jpeg_quality', 85))
        self.images_checkbox.setChecked(settings.get('allow_images', True))
        self.videos_checkbox.setChecked(settings.get('allow_videos', True))
        self.audio_checkbox.setChecked(settings.get('allow_audio', True))
        self.documents_checkbox.setChecked(settings.get('allow_documents', True))
        self.archives_checkbox.setChecked(settings.get('allow_archives', False))
        
        # Theme
        self.font_size_spinbox.setValue(settings.get('font_size', 12))
        self.opacity_slider.setValue(settings.get('window_opacity', 100))
        
        # Advanced
        self.timeout_spinbox.setValue(settings.get('connection_timeout', 30))
        self.retry_attempts_spinbox.setValue(settings.get('retry_attempts', 3))
        self.concurrent_uploads_spinbox.setValue(settings.get('concurrent_uploads', 3))
        self.scan_interval_spinbox.setValue(settings.get('scan_interval', 5))
        self.ignore_hidden_checkbox.setChecked(settings.get('ignore_hidden', True))
        self.ignore_temp_checkbox.setChecked(settings.get('ignore_temp', True))
        self.verbose_logging_checkbox.setChecked(settings.get('verbose_logging', False))
        self.debug_mode_checkbox.setChecked(settings.get('debug_mode', False))
        self.save_logs_checkbox.setChecked(settings.get('save_logs', False))
    
    def get_settings(self):
        """Get current settings as dictionary"""
        return {
            # General
            'auto_upload_enabled': self.auto_upload_checkbox.isChecked(),
            'auto_clipboard': self.auto_clipboard_checkbox.isChecked(),
            'auto_notifications': self.auto_notifications_checkbox.isChecked(),
            'auto_connect': self.auto_connect_checkbox.isChecked(),
            'minimize_to_tray': self.minimize_to_tray_checkbox.isChecked(),
            'start_monitoring': self.start_monitoring_checkbox.isChecked(),
            
            # Upload
            'auto_resize': self.auto_resize_checkbox.isChecked(),
            'max_resolution': self.max_resolution_spinbox.value(),
            'jpeg_quality': self.quality_slider.value(),
            'allow_images': self.images_checkbox.isChecked(),
            'allow_videos': self.videos_checkbox.isChecked(),
            'allow_audio': self.audio_checkbox.isChecked(),
            'allow_documents': self.documents_checkbox.isChecked(),
            'allow_archives': self.archives_checkbox.isChecked(),
            
            # Theme
            'font_size': self.font_size_spinbox.value(),
            'window_opacity': self.opacity_slider.value(),
            'primary_color': self.current_primary_color,
            'accent_color': self.current_accent_color,
            
            # Advanced
            'connection_timeout': self.timeout_spinbox.value(),
            'retry_attempts': self.retry_attempts_spinbox.value(),
            'concurrent_uploads': self.concurrent_uploads_spinbox.value(),
            'scan_interval': self.scan_interval_spinbox.value(),
            'ignore_hidden': self.ignore_hidden_checkbox.isChecked(),
            'ignore_temp': self.ignore_temp_checkbox.isChecked(),
            'verbose_logging': self.verbose_logging_checkbox.isChecked(),
            'debug_mode': self.debug_mode_checkbox.isChecked(),
            'save_logs': self.save_logs_checkbox.isChecked(),
        }
    
    def save_settings(self):
        """Save settings to file using enhanced method"""
        success = self.save_settings_internal(silent=False)
        if success:
            self.settings_dirty = False
        return success
    
    def save_and_close(self):
        """Save settings and close dialog with enhanced feedback"""
        if self.save_settings():
            # Show success message briefly
            if hasattr(self, 'parent_window') and self.parent_window:
                try:
                    # Try to show success in parent window status bar
                    if hasattr(self.parent_window, 'show_status_message'):
                        self.parent_window.show_status_message("💾 Settings saved successfully!", 3000)
                    elif hasattr(self.parent_window, 'statusBar'):
                        self.parent_window.statusBar().showMessage("💾 Settings saved successfully!", 3000)
                except Exception:
                    pass
            
            # Emit settings changed signal
            self.settings_changed.emit()
            
            # Close dialog
            self.accept()
        else:
            # Save failed, show error and keep dialog open
            QMessageBox.critical(self, "Save Failed", 
                               "Failed to save settings. Please check file permissions and try again.")
        
        # Reset dirty flag regardless
        self.settings_dirty = False
    
    def setup_auto_save(self):
        """Setup auto-save functionality for settings"""
        # Connect all widgets to mark settings as dirty
        self.connect_settings_changed()
    
    def connect_settings_changed(self):
        """Connect all settings widgets to mark settings as dirty when changed"""
        # General tab
        self.auto_upload_checkbox.toggled.connect(self.mark_settings_dirty)
        self.auto_clipboard_checkbox.toggled.connect(self.mark_settings_dirty)
        self.auto_notifications_checkbox.toggled.connect(self.mark_settings_dirty)
        self.auto_connect_checkbox.toggled.connect(self.mark_settings_dirty)
        self.minimize_to_tray_checkbox.toggled.connect(self.mark_settings_dirty)
        self.start_monitoring_checkbox.toggled.connect(self.mark_settings_dirty)
        
        # Upload tab
        self.auto_resize_checkbox.toggled.connect(self.mark_settings_dirty)
        self.max_resolution_spinbox.valueChanged.connect(self.mark_settings_dirty)
        self.quality_slider.valueChanged.connect(self.mark_settings_dirty)
        self.images_checkbox.toggled.connect(self.mark_settings_dirty)
        self.videos_checkbox.toggled.connect(self.mark_settings_dirty)
        self.audio_checkbox.toggled.connect(self.mark_settings_dirty)
        self.documents_checkbox.toggled.connect(self.mark_settings_dirty)
        self.archives_checkbox.toggled.connect(self.mark_settings_dirty)
        
        # Theme tab
        self.font_size_spinbox.valueChanged.connect(self.mark_settings_dirty)
        self.opacity_slider.valueChanged.connect(self.mark_settings_dirty)
        
        # Advanced tab
        self.timeout_spinbox.valueChanged.connect(self.mark_settings_dirty)
        self.retry_attempts_spinbox.valueChanged.connect(self.mark_settings_dirty)
        self.concurrent_uploads_spinbox.valueChanged.connect(self.mark_settings_dirty)
        self.scan_interval_spinbox.valueChanged.connect(self.mark_settings_dirty)
        self.ignore_hidden_checkbox.toggled.connect(self.mark_settings_dirty)
        self.ignore_temp_checkbox.toggled.connect(self.mark_settings_dirty)
        self.verbose_logging_checkbox.toggled.connect(self.mark_settings_dirty)
        self.debug_mode_checkbox.toggled.connect(self.mark_settings_dirty)
        self.save_logs_checkbox.toggled.connect(self.mark_settings_dirty)
    
    def mark_settings_dirty(self):
        """Mark settings as needing save"""
        self.settings_dirty = True
        if hasattr(self, 'auto_save_enabled') and self.auto_save_enabled:
            # Auto-save after 2 seconds of inactivity
            if hasattr(self, 'auto_save_timer'):
                self.auto_save_timer.stop()
            
            self.auto_save_timer = QTimer()
            self.auto_save_timer.timeout.connect(self.auto_save_settings)
            self.auto_save_timer.setSingleShot(True)
            self.auto_save_timer.start(2000)  # 2 seconds delay
    
    def auto_save_settings(self):
        """Auto-save settings without user interaction"""
        if self.settings_dirty:
            self.save_settings_internal(silent=True)
            self.settings_dirty = False
    
    def create_backup(self):
        """Create a backup of current settings"""
        try:
            if not self.settings_file.exists():
                return True
                
            # Create backup directory
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create timestamped backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"settings_backup_{timestamp}.json"
            
            # Copy current settings to backup
            shutil.copy2(self.settings_file, backup_file)
            
            # Keep only last 10 backups
            backups = sorted(self.backup_dir.glob("settings_backup_*.json"))
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    old_backup.unlink()
            
            return True
        except Exception as e:
            print(f"Warning: Failed to create backup: {e}")
            return False
    
    def save_settings_internal(self, silent=False):
        """Enhanced internal save method with backup and validation"""
        try:
            # Create backup before saving
            self.create_backup()
            
            # Ensure config directory exists
            config_dir = Path.home() / ".custom_server_client"
            config_dir.mkdir(exist_ok=True)
            
            # Get current settings
            settings = self.get_comprehensive_settings()
            
            # Validate settings before saving
            if not self.validate_settings(settings):
                if not silent:
                    QMessageBox.warning(self, "Validation Error", 
                                      "Some settings have invalid values. Please check your configuration.")
                return False
            
            # Write to temporary file first, then rename (atomic operation)
            temp_file = self.settings_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            temp_file.replace(self.settings_file)
            
            if not silent:
                print(f"✅ Settings saved successfully to {self.settings_file}")
            
            return True
            
        except Exception as e:
            if not silent:
                QMessageBox.critical(self, "Save Error", 
                                   f"Failed to save settings: {str(e)}")
            print(f"❌ Failed to save settings: {e}")
            return False
    
    def validate_settings(self, settings):
        """Validate settings before saving"""
        try:
            # Validate numeric ranges
            if not (512 <= settings.get('max_resolution', 2048) <= 4096):
                return False
            if not (50 <= settings.get('jpeg_quality', 85) <= 100):
                return False
            if not (8 <= settings.get('font_size', 12) <= 18):
                return False
            if not (80 <= settings.get('window_opacity', 100) <= 100):
                return False
            if not (5 <= settings.get('connection_timeout', 30) <= 120):
                return False
            if not (1 <= settings.get('retry_attempts', 3) <= 10):
                return False
            if not (1 <= settings.get('concurrent_uploads', 3) <= 10):
                return False
            if not (1 <= settings.get('scan_interval', 5) <= 60):
                return False
            
            # Validate colors
            primary_color = settings.get('primary_color', 'rgb(244, 67, 54)')
            accent_color = settings.get('accent_color', 'rgb(211, 47, 47)')
            
            if not (primary_color.startswith('rgb(') or primary_color.startswith('#')):
                return False
            if not (accent_color.startswith('rgb(') or accent_color.startswith('#')):
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_comprehensive_settings(self):
        """Get comprehensive settings including metadata"""
        base_settings = self.get_settings()
        
        # Add metadata
        base_settings.update({
            # Metadata
            'version': '2.0',
            'saved_at': datetime.now().isoformat(),
            'theme_version': 'red_gradient_v2',
            'client_version': '1.0.0',
            
            # System info for debugging
            'system_info': {
                'platform': os.name,
                'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
                'settings_format': 'comprehensive_v2'
            },
            
            # Enhanced theme settings with gradients
            'theme_settings': {
                'primary_gradient': 'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F44336, stop:0.3 #E53935, stop:0.7 #D32F2F, stop:1 #F44336)',
                'secondary_gradient': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(45, 55, 72, 0.7), stop:1 rgba(244, 67, 54, 0.1))',
                'hover_gradient': 'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F55336, stop:1 #E33F2F)',
                'focus_gradient': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(30, 41, 59, 0.9), stop:1 rgba(244, 67, 54, 0.1))',
                'background_gradient': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgb(15, 15, 35), stop:0.3 rgb(20, 20, 40), stop:0.7 rgb(22, 22, 42), stop:1 rgb(26, 26, 46))'
            },
            
            # Advanced configuration
            'advanced_config': {
                'auto_save_enabled': getattr(self, 'auto_save_enabled', True),
                'backup_enabled': True,
                'gradient_animations': True,
                'enhanced_ui': True,
                'red_theme_fixed': True
            }
        })
        
        return base_settings
    
    def closeEvent(self, event):
        """Handle dialog close event - warn about unsaved changes"""
        if self.settings_dirty:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                if self.save_settings():
                    event.accept()
                else:
                    event.ignore()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
    
    def apply_theme_color(self, color, color_type='primary'):
        """Apply theme color to parent window with gradient support"""
        if self.parent_window and hasattr(self.parent_window, 'apply_modern_theme'):
            try:
                # Apply red gradient theme
                if color_type == 'primary':
                    self.parent_window.apply_modern_theme(QColor(244, 67, 54))  # Red
                else:
                    self.parent_window.apply_modern_theme(QColor(211, 47, 47))  # Dark red
                print(f"✅ Applied {color_type} red gradient theme to parent window")
            except Exception as e:
                print(f"⚠️ Failed to apply theme color: {e}")
