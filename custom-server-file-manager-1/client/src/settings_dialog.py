#!/usr/bin/env python3
"""
Settings Dialog for Custom Server File Manager Client
Modern settings interface with theme customization
"""

import json
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QSpinBox,
    QFrame, QTabWidget, QWidget, QGroupBox, QComboBox,
    QColorDialog, QGridLayout, QSlider, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

class SettingsDialog(QDialog):
    """Modern settings dialog with multiple categories"""
    
    settings_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("⚙️ Settings")
        self.setFixedSize(600, 500)
        self.setModal(True)
        
        # Apply modern styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTabWidget::pane {
                border: 2px solid #404040;
                border-radius: 8px;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 10px 15px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #505050;
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
            QLineEdit, QSpinBox {
                padding: 6px;
                border: 2px solid #404040;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QLineEdit:focus, QSpinBox:focus {
                border-color: #4CAF50;
            }
            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
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
            QPushButton[class="preset"] {
                min-width: 60px;
                min-height: 30px;
                border-radius: 15px;
                font-weight: bold;
            }
            QCheckBox {
                color: #ffffff;
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
            QComboBox {
                padding: 6px;
                border: 2px solid #404040;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QComboBox:focus {
                border-color: #4CAF50;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #404040;
                height: 6px;
                background: #2d2d2d;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #4CAF50;
                width: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
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
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #4CAF50; margin-bottom: 5px;")
        
        subtitle_label = QLabel("Customize your Custom Server File Manager Client")
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
        """Create general settings tab"""
        general_widget = QWidget()
        general_layout = QVBoxLayout(general_widget)
        general_layout.setContentsMargins(20, 20, 20, 20)
        general_layout.setSpacing(20)
        
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
        
        general_layout.addWidget(auto_upload_group)
        general_layout.addWidget(startup_group)
        general_layout.addStretch()
        
        self.tab_widget.addTab(general_widget, "🏠 General")
    
    def create_upload_tab(self):
        """Create upload settings tab"""
        upload_widget = QWidget()
        upload_layout = QVBoxLayout(upload_widget)
        upload_layout.setContentsMargins(20, 20, 20, 20)
        upload_layout.setSpacing(20)
        
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
        
        upload_layout.addWidget(image_group)
        upload_layout.addWidget(types_group)
        upload_layout.addStretch()
        
        self.tab_widget.addTab(upload_widget, "📤 Upload")
    
    def create_theme_tab(self):
        """Create theme settings tab"""
        theme_widget = QWidget()
        theme_layout = QVBoxLayout(theme_widget)
        theme_layout.setContentsMargins(20, 20, 20, 20)
        theme_layout.setSpacing(20)
        
        # Color Presets Group
        presets_group = QGroupBox("🎨 Color Presets")
        presets_layout = QGridLayout(presets_group)
        presets_layout.setSpacing(15)
        
        # Preset buttons
        self.create_preset_button("🟢 Green", "#4CAF50", 0, 0, presets_layout)
        self.create_preset_button("🔵 Blue", "#2196F3", 0, 1, presets_layout)
        self.create_preset_button("🟣 Purple", "#9C27B0", 1, 0, presets_layout)
        self.create_preset_button("🟠 Orange", "#FF9800", 1, 1, presets_layout)
        
        # Custom Colors Group
        custom_group = QGroupBox("🎯 Custom Colors")
        custom_layout = QFormLayout(custom_group)
        custom_layout.setSpacing(15)
        
        self.primary_color_button = QPushButton("Choose Primary Color")
        self.primary_color_button.setProperty("class", "secondary")
        self.primary_color_button.clicked.connect(self.choose_primary_color)
        
        self.accent_color_button = QPushButton("Choose Accent Color")
        self.accent_color_button.setProperty("class", "secondary")
        self.accent_color_button.clicked.connect(self.choose_accent_color)
        
        custom_layout.addRow("Primary Color:", self.primary_color_button)
        custom_layout.addRow("Accent Color:", self.accent_color_button)
        
        # Interface Group
        interface_group = QGroupBox("🖥️ Interface")
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
        
        theme_layout.addWidget(presets_group)
        theme_layout.addWidget(custom_group)
        theme_layout.addWidget(interface_group)
        theme_layout.addStretch()
        
        self.tab_widget.addTab(theme_widget, "🎨 Theme")
    
    def create_advanced_tab(self):
        """Create advanced settings tab"""
        advanced_widget = QWidget()
        advanced_layout = QVBoxLayout(advanced_widget)
        advanced_layout.setContentsMargins(20, 20, 20, 20)
        advanced_layout.setSpacing(20)
        
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
        
        advanced_layout.addWidget(network_group)
        advanced_layout.addWidget(monitoring_group)
        advanced_layout.addWidget(debug_group)
        advanced_layout.addStretch()
        
        self.tab_widget.addTab(advanced_widget, "🔧 Advanced")
    
    def create_preset_button(self, text, color, row, col, layout):
        """Create a color preset button"""
        button = QPushButton(text)
        button.setProperty("class", "preset")
        button.setStyleSheet(f"""
            QPushButton[class="preset"] {{
                background-color: {color};
                color: white;
                border: 2px solid {color};
            }}
            QPushButton[class="preset"]:hover {{
                background-color: {color};
                border: 2px solid white;
            }}
        """)
        button.clicked.connect(lambda: self.apply_color_preset(color))
        layout.addWidget(button, row, col)
    
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
    
    def apply_color_preset(self, color):
        """Apply a color preset"""
        # This would update the application theme
        if self.parent_window:
            # Apply theme to parent window
            pass
    
    def choose_primary_color(self):
        """Choose custom primary color"""
        color = QColorDialog.getColor(QColor("#4CAF50"), self, "Choose Primary Color")
        if color.isValid():
            self.primary_color_button.setText(f"Primary: {color.name()}")
    
    def choose_accent_color(self):
        """Choose custom accent color"""
        color = QColorDialog.getColor(QColor("#2E7D32"), self, "Choose Accent Color")
        if color.isValid():
            self.accent_color_button.setText(f"Accent: {color.name()}")
    
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
        """Load settings from file"""
        try:
            config_file = Path.home() / ".custom_server_client" / "settings.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    settings = json.load(f)
                    self.apply_settings(settings)
            else:
                self.load_default_settings()
        except Exception:
            self.load_default_settings()
    
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
        """Save settings to file"""
        try:
            config_dir = Path.home() / ".custom_server_client"
            config_dir.mkdir(exist_ok=True)
            
            settings_file = config_dir / "settings.json"
            settings = self.get_settings()
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
                
            return True
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Failed to save settings: {str(e)}")
            return False
    
    def save_and_close(self):
        """Save settings and close dialog"""
        if self.save_settings():
            self.settings_changed.emit()
            self.accept()
        # If save failed, dialog stays open
