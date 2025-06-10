#!/usr/bin/env python3
"""
Settings Dialog for Custom Server File Manager Client
Modern settings interface with theme customization
"""

import json
import os
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QSpinBox,
    QFrame, QTabWidget, QWidget, QGroupBox, QComboBox,
    QGridLayout, QSlider, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

class SettingsDialog(QDialog):
    """Mo        button_layout.addStretch()
        
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
        parent_layout.addLayout(button_layout)dialog with multiple categories"""
    
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
        self.setMinimumSize(700, 550)  # Set minimum size instead of fixed
        self.resize(800, 650)  # Set initial size but allow resizing
        self.setModal(True)
        
        # Apply modern styling with web interface theme
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgb(15, 15, 35), stop:1 rgb(26, 26, 46));
                color: #ffffff;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                font-weight: 400;
            }            QTabWidget::pane {
                border: none;
                border-radius: 12px;
                background: rgba(45, 55, 72, 0.4);
                margin-top: 10px;
            }
            QTabBar::tab {
                background: rgba(45, 55, 72, 0.6);
                color: rgba(203, 213, 225, 0.9);
                padding: 12px 20px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
                font-size: 13px;
                min-width: 80px;
                border: none;
            }            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F44336, stop:1 #D32F2F);
                color: white;
                font-weight: 600;
            }
            QTabBar::tab:hover:!selected {
                background: rgba(244, 67, 54, 0.3);
                color: white;
            }QGroupBox {
                font-weight: 600;
                border: none;
                border-radius: 12px;
                margin-top: 20px;
                padding-top: 15px;
                background: rgba(45, 55, 72, 0.3);
                font-size: 14px;
            }            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 15px 0 15px;
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F44336, stop:1 #D32F2F);
                font-weight: 600;
            }
            QLineEdit, QSpinBox {
                padding: 10px 12px;
                border: none;
                border-radius: 8px;
                background: rgba(30, 41, 59, 0.7);
                color: #ffffff;
                font-size: 13px;
                font-weight: 400;
                min-height: 16px;
            }            QLineEdit:focus, QSpinBox:focus {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(30, 41, 59, 0.9), stop:1 rgba(244, 67, 54, 0.1));
                outline: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F44336, stop:1 #D32F2F);
            }
            QPushButton {
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-weight: 500;
                font-size: 13px;
                min-height: 16px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            }            QPushButton[class="primary"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F44336, stop:1 #D32F2F);
                color: white;
                font-weight: 600;
            }            QPushButton[class="primary"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F55336, stop:1 #E33F2F);
            }
            QPushButton[class="primary"]:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E33336, stop:1 #C22F2F);
            }            QPushButton[class="secondary"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(45, 55, 72, 0.7), stop:1 rgba(244, 67, 54, 0.1));
                color: rgba(203, 213, 225, 0.9);
                border: 1px solid rgba(244, 67, 54, 0.3);
            }
            QPushButton[class="secondary"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(45, 55, 72, 0.9), stop:1 rgba(244, 67, 54, 0.2));
                color: white;
                border: 1px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F44336, stop:1 #D32F2F);
            }QPushButton[class="secondary"]:pressed {
                background: rgba(35, 45, 62, 0.9);
            }
            QPushButton[class="preset"] {
                min-width: 80px;
                min-height: 36px;
                border-radius: 18px;
                font-weight: 600;
                font-size: 12px;
                border: 2px solid transparent;
            }
            QCheckBox {
                color: rgba(203, 213, 225, 0.9);
                font-size: 13px;
                font-weight: 400;
                spacing: 8px;
            }            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid rgba(244, 67, 54, 0.4);
                border-radius: 4px;
                background: rgba(30, 41, 59, 0.7);
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F44336, stop:1 #D32F2F);
                border: 2px solid #F44336;
            }            QCheckBox::indicator:hover {
                border: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F44336, stop:1 #D32F2F);
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(30, 41, 59, 0.7), stop:1 rgba(244, 67, 54, 0.1));
            }
            QComboBox {
                padding: 10px 12px;
                border: none;
                border-radius: 8px;
                background: rgba(30, 41, 59, 0.7);
                color: #ffffff;
                font-size: 13px;
                min-height: 16px;
            }            QComboBox:focus {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(30, 41, 59, 0.9), stop:1 rgba(244, 67, 54, 0.1));
                outline: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F44336, stop:1 #D32F2F);
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                image: none;
                border: none;
            }
            QSlider::groove:horizontal {
                border: none;
                height: 8px;
                background: rgba(30, 41, 59, 0.7);
                border-radius: 4px;
            }            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F44336, stop:1 #D32F2F);
                border: none;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F55336, stop:1 #E33F2F);
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F44336, stop:1 #D32F2F);
                border-radius: 4px;
            }
            QLabel {
                color: rgba(203, 213, 225, 0.9);
                font-size: 13px;
                font-weight: 400;
            }        """)
        
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
        """Create dialog header"""
        header_layout = QVBoxLayout()
        
        title_label = QLabel("⚙️ Settings")
        title_label.setFont(QFont("Inter", 24, QFont.Bold))
        title_label.setStyleSheet("color: #F44336; margin-bottom: 8px; font-weight: 700;")
        
        subtitle_label = QLabel("Customize your Custom Server File Manager Client")
        subtitle_label.setFont(QFont("Inter", 12, QFont.Normal))
        subtitle_label.setStyleSheet("color: rgba(203, 213, 225, 0.8); font-weight: 400;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        parent_layout.addLayout(header_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F44336, stop:1 #D32F2F); max-height: 2px; border: none; margin: 15px 0;")
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
        
        # Theme Info Group
        theme_info_group = QGroupBox("🎨 Current Theme")
        theme_info_layout = QVBoxLayout(theme_info_group)
        theme_info_layout.setSpacing(15)
        
        # Show current theme as red
        current_theme_label = QLabel("🔴 Red Theme (Default)")
        current_theme_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F44336, stop:1 #D32F2F);
                color: white;
                padding: 15px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                text-align: center;
            }
        """)
        current_theme_label.setAlignment(Qt.AlignCenter)
        
        theme_description = QLabel("The application is using a beautiful red theme with modern design elements.")
        theme_description.setStyleSheet("color: rgba(203, 213, 225, 0.8); font-size: 12px;")
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
        """Create dialog buttons"""
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
            config_file = Path.home() / ".custom_server_client" / "settings.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                # Check if settings format needs migration
                if settings.get('version', '1.0') < '2.0':
                    print("📦 Migrating settings to new format...")
                    self.migrate_settings(settings)
                
                self.apply_settings(settings)
                print(f"✅ Settings loaded from {config_file}")
                
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
        # Add any migration logic here for future versions
        print("✅ Settings migration completed")
    
    def restore_from_backup(self):
        """Restore settings from the most recent backup"""
        try:
            backup_dir = Path.home() / ".custom_server_client" / "backups"
            if not backup_dir.exists():
                self.load_default_settings()
                return
                
            backups = sorted(backup_dir.glob("settings_backup_*.json"))
            if not backups:
                self.load_default_settings()
                return
                
            latest_backup = backups[-1]
            with open(latest_backup, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                self.apply_settings(settings)
                
            print(f"✅ Settings restored from backup: {latest_backup.name}")
            
            # Copy backup to main settings file
            import shutil
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
        
        # Apply saved colors if they exist
        primary_color = settings.get('primary_color', 'rgb(102, 126, 234)')
        accent_color = settings.get('accent_color', 'rgb(118, 75, 162)')
        
        if hasattr(self, 'primary_color_preview'):
            self.primary_color_preview.setStyleSheet(f"color: {primary_color}; font-size: 24px;")
            self.primary_color_button.setText(f"Primary: {primary_color}")
            self.current_primary_color = primary_color
            
        if hasattr(self, 'accent_color_preview'):
            self.accent_color_preview.setStyleSheet(f"color: {accent_color}; font-size: 24px;")
            self.accent_color_button.setText(f"Accent: {accent_color}")
            self.current_accent_color = accent_color
        
        # Apply theme colors to parent window
        if self.parent_window and primary_color != 'rgb(102, 126, 234)':
            self.apply_theme_color(primary_color, 'primary')
        
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
            'primary_color': getattr(self, 'current_primary_color', 'rgb(102, 126, 234)'),
            'accent_color': getattr(self, 'current_accent_color', 'rgb(118, 75, 162)'),
            
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
            from PySide6.QtWidgets import QMessageBox
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
        self.retry_attempts_spinbox.valueChanged.connect(self.mark_settings_dirty)        self.concurrent_uploads_spinbox.valueChanged.connect(self.mark_settings_dirty)
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
            
            from PySide6.QtCore import QTimer
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
            import shutil
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
                    from PySide6.QtWidgets import QMessageBox
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
                from PySide6.QtWidgets import QMessageBox
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
            'theme_version': 'red_gradient_v1',
            'client_version': '1.0.0',
            
            # System info for debugging
            'system_info': {
                'platform': os.name,
                'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
                'settings_format': 'comprehensive_v2'
            },
            
            # Theme specific settings
            'theme_settings': {
                'primary_gradient': 'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F44336, stop:1 #D32F2F)',
                'secondary_gradient': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(45, 55, 72, 0.7), stop:1 rgba(244, 67, 54, 0.1))',
                'hover_gradient': 'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F55336, stop:1 #E33F2F)',
                'focus_gradient': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(30, 41, 59, 0.9), stop:1 rgba(244, 67, 54, 0.1))'
            },
            
            # Advanced configuration
            'advanced_config': {
                'auto_save_enabled': getattr(self, 'auto_save_enabled', True),
                'backup_enabled': True,
                'gradient_animations': True,
                'enhanced_ui': True
            }
        })
        
        return base_settings
    
    def closeEvent(self, event):
        """Handle dialog close event - warn about unsaved changes"""
        if self.settings_dirty:
            from PySide6.QtWidgets import QMessageBox
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
                    event.ignore()  # Don't close if save failed
            elif reply == QMessageBox.Discard:
                event.accept()
            else:  # Cancel
                event.ignore()
        else:
            event.accept()
    
    def apply_theme_color(self, color, color_type='primary'):
        """Apply theme color to parent window with gradient support"""
        if self.parent_window and hasattr(self.parent_window, 'apply_modern_theme'):
            try:
                # Apply color with gradient enhancement
                if color_type == 'primary':
                    self.current_primary_color = color
                    # Apply with gradient support
                    self.parent_window.apply_modern_theme(custom_primary_color=color)
                    print(f"✅ Applied {color_type} color: {color}")
                else:
                    self.current_accent_color = color
                    print(f"✅ Applied {color_type} color: {color}")
                
                # Update interface with new gradients
                self.update_gradient_styles()
                
            except Exception as e:
                print(f"⚠️ Failed to apply {color_type} color: {e}")

    def update_gradient_styles(self):
        """Update gradient styles based on current colors"""
        # Create dynamic gradients based on current red theme
        primary_gradient = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F44336, stop:1 #D32F2F)"
        hover_gradient = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F55336, stop:1 #E33F2F)"
        focus_gradient = f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(30, 41, 59, 0.9), stop:1 rgba(244, 67, 54, 0.1))"
        
        # Update dialog background with enhanced gradient
        enhanced_stylesheet = f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgb(15, 15, 35), stop:0.3 rgb(20, 20, 40), 
                    stop:0.7 rgb(22, 22, 42), stop:1 rgb(26, 26, 46));
                color: #ffffff;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                font-weight: 400;
            }}
            
            QTabWidget::pane {{
                border: none;
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(45, 55, 72, 0.4), stop:1 rgba(244, 67, 54, 0.05));
                margin-top: 10px;
            }}
            
            QGroupBox {{
                font-weight: 600;
                border: none;
                border-radius: 12px;
                margin-top: 20px;
                padding-top: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(45, 55, 72, 0.3), stop:1 rgba(244, 67, 54, 0.02));
                font-size: 14px;
            }}
            
            QScrollArea {{
                border: none;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(30, 41, 59, 0.1), stop:1 rgba(244, 67, 54, 0.02));
                border-radius: 8px;
            }}
            
            QScrollBar:vertical {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 41, 59, 0.5), stop:1 rgba(244, 67, 54, 0.1));
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }}
            
            QScrollBar::handle:vertical {{
                background: {primary_gradient};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {hover_gradient};
            }}
        """
        
        # Update the main stylesheet with enhanced gradients
        current_style = self.styleSheet()
        # Append enhanced styles
        self.setStyleSheet(current_style + enhanced_stylesheet)

    def setup_enhanced_ui_feedback(self):
        """Setup enhanced UI feedback for settings changes"""
        # Add visual feedback when settings change
        for widget in [self.auto_upload_checkbox, self.auto_clipboard_checkbox, 
                      self.auto_notifications_checkbox, self.font_size_spinbox, 
                      self.opacity_slider, self.quality_slider]:
            if hasattr(widget, 'toggled'):
                widget.toggled.connect(self.show_settings_changed_feedback)
            elif hasattr(widget, 'valueChanged'):
                widget.valueChanged.connect(self.show_settings_changed_feedback)

    def show_settings_changed_feedback(self):
        """Show visual feedback when settings are changed"""
        # Add a subtle animation or color change to indicate unsaved changes
        if hasattr(self, 'save_button'):
            self.save_button.setStyleSheet("""
                QPushButton[class="primary"] {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FF6B35, stop:1 #FF4419);
                    color: white;
                    font-weight: 600;
                    animation: pulse 1s infinite;
                }
                QPushButton[class="primary"]:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FF7B45, stop:1 #FF5529);
                }
            """)

    def reset_save_button_style(self):
        """Reset save button to normal style after saving"""
        if hasattr(self, 'save_button'):
            # Reset to normal red gradient
            self.save_button.setStyleSheet("")  # Use default from main stylesheet

    def create_enhanced_theme_preview(self):
        """Create an enhanced theme preview with live gradients"""
        preview_widget = QWidget()
        preview_widget.setFixedHeight(120)
        preview_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #F44336, stop:0.3 #E91E63, stop:0.6 #D32F2F, stop:1 #F44336);
                border-radius: 12px;
                margin: 10px;
            }
        """)
        
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("🎨 Live Theme Preview")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: 700;
                background: transparent;
            }
        """)
        
        desc_label = QLabel("Dynamic red gradients with modern animations")
        desc_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 12px;
                background: transparent;
            }
        """)
        
        preview_layout.addWidget(title_label)
        preview_layout.addWidget(desc_label)
        preview_layout.addStretch()
        
        return preview_widget

    def add_export_import_functionality(self):
        """Add settings export/import functionality"""
        export_button = QPushButton("📤 Export Settings")
        export_button.setProperty("class", "secondary")
        export_button.clicked.connect(self.export_settings)
        
        import_button = QPushButton("📥 Import Settings")
        import_button.setProperty("class", "secondary")
        import_button.clicked.connect(self.import_settings)
        
        # Add to button layout if it exists
        if hasattr(self, 'button_layout'):
            self.button_layout.insertWidget(0, export_button)
            self.button_layout.insertWidget(1, import_button)

    def export_settings(self):
        """Export current settings to a file"""
        from PySide6.QtWidgets import QFileDialog
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Export Settings",
                f"vrcphoto2url_settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                settings = self.get_comprehensive_settings()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
                
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Export Successful", 
                                      f"Settings exported successfully to:\n{file_path}")
                
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Export Failed", f"Failed to export settings:\n{str(e)}")

    def import_settings(self):
        """Import settings from a file"""
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Import Settings",
                "",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # Validate imported settings
                if self.validate_settings(settings):
                    self.apply_settings(settings)
                    self.mark_settings_dirty()
                    QMessageBox.information(self, "Import Successful", 
                                          f"Settings imported successfully from:\n{file_path}")
                else:
                    QMessageBox.warning(self, "Import Failed", 
                                      "Invalid settings file format or values.")
                
        except Exception as e:
            QMessageBox.critical(self, "Import Failed", f"Failed to import settings:\n{str(e)}")

    # ...existing code...
