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
    QColorDialog, QGridLayout, QSlider, QMessageBox, QScrollArea
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
            }
            QTabWidget::pane {
                border: none;
                border-radius: 12px;
                background: rgba(45, 55, 72, 0.4);
                backdrop-filter: blur(10px);
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
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgb(102, 126, 234), stop:1 rgb(118, 75, 162));
                color: white;
                font-weight: 600;
            }
            QTabBar::tab:hover:!selected {
                background: rgba(102, 126, 234, 0.3);
                color: white;
            }
            QGroupBox {
                font-weight: 600;
                border: none;
                border-radius: 12px;
                margin-top: 20px;
                padding-top: 15px;
                background: rgba(45, 55, 72, 0.3);
                backdrop-filter: blur(8px);
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 15px 0 15px;
                color: rgb(102, 126, 234);
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
            }
            QLineEdit:focus, QSpinBox:focus {
                background: rgba(30, 41, 59, 0.9);
                outline: 2px solid rgb(102, 126, 234);
            }
            QPushButton {
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-weight: 500;
                font-size: 13px;
                min-height: 16px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            }
            QPushButton[class="primary"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgb(102, 126, 234), stop:1 rgb(118, 75, 162));
                color: white;
                font-weight: 600;
            }
            QPushButton[class="primary"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgb(112, 136, 244), stop:1 rgb(128, 85, 172));
                transform: translateY(-1px);
            }
            QPushButton[class="primary"]:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgb(92, 116, 224), stop:1 rgb(108, 65, 152));
                transform: translateY(0px);
            }
            QPushButton[class="secondary"] {
                background: rgba(45, 55, 72, 0.7);
                color: rgba(203, 213, 225, 0.9);
                border: 1px solid rgba(102, 126, 234, 0.3);
            }
            QPushButton[class="secondary"]:hover {
                background: rgba(45, 55, 72, 0.9);
                color: white;
                border: 1px solid rgba(102, 126, 234, 0.6);
                transform: translateY(-1px);
            }
            QPushButton[class="secondary"]:pressed {
                background: rgba(35, 45, 62, 0.9);
                transform: translateY(0px);
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
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid rgba(102, 126, 234, 0.4);
                border-radius: 4px;
                background: rgba(30, 41, 59, 0.7);
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgb(102, 126, 234), stop:1 rgb(118, 75, 162));
                border: 2px solid rgb(102, 126, 234);
            }
            QCheckBox::indicator:hover {
                border: 2px solid rgba(102, 126, 234, 0.7);
            }
            QComboBox {
                padding: 10px 12px;
                border: none;
                border-radius: 8px;
                background: rgba(30, 41, 59, 0.7);
                color: #ffffff;
                font-size: 13px;
                min-height: 16px;
            }
            QComboBox:focus {
                background: rgba(30, 41, 59, 0.9);
                outline: 2px solid rgb(102, 126, 234);
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
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgb(102, 126, 234), stop:1 rgb(118, 75, 162));
                border: none;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgb(112, 136, 244), stop:1 rgb(128, 85, 172));
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgb(102, 126, 234), stop:1 rgb(118, 75, 162));
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
        title_label.setStyleSheet("color: rgb(102, 126, 234); margin-bottom: 8px; font-weight: 700;")
        
        subtitle_label = QLabel("Customize your Custom Server File Manager Client")
        subtitle_label.setFont(QFont("Inter", 12, QFont.Normal))
        subtitle_label.setStyleSheet("color: rgba(203, 213, 225, 0.8); font-weight: 400;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        parent_layout.addLayout(header_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgb(102, 126, 234), stop:1 rgb(118, 75, 162)); max-height: 2px; border: none; margin: 15px 0;")
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
        """Create theme settings tab with scroll area"""
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
          # Color Presets Group
        presets_group = QGroupBox("🎨 Color Presets")
        presets_layout = QGridLayout(presets_group)
        presets_layout.setSpacing(15)
        
        # Enhanced preset buttons with more color options
        color_presets = [
            ("🟣 Purple", "rgb(102, 126, 234)", 0, 0),
            ("🔵 Blue", "#2196F3", 0, 1),
            ("🟢 Green", "#4CAF50", 0, 2),
            ("🟠 Orange", "#FF9800", 1, 0),
            ("🔴 Red", "#F44336", 1, 1),
            ("🟡 Yellow", "#FFC107", 1, 2),
            ("🟤 Brown", "#795548", 2, 0),
            ("🔵 Cyan", "#00BCD4", 2, 1),
            ("🟢 Lime", "#8BC34A", 2, 2),
            ("🟣 Indigo", "#3F51B5", 3, 0),
            ("🌸 Pink", "#E91E63", 3, 1),
            ("🌊 Teal", "#009688", 3, 2)
        ]
        
        for text, color, row, col in color_presets:
            self.create_preset_button(text, color, row, col, presets_layout)
        
        # Custom Colors Group with enhanced color picker
        custom_group = QGroupBox("🎯 Custom Colors & Advanced Theming")
        custom_layout = QFormLayout(custom_group)
        custom_layout.setSpacing(15)
        
        # Primary color section
        primary_layout = QHBoxLayout()
        self.primary_color_button = QPushButton("Choose Primary Color")
        self.primary_color_button.setProperty("class", "secondary")
        self.primary_color_button.clicked.connect(self.choose_primary_color)
        
        self.primary_color_preview = QLabel("●")
        self.primary_color_preview.setStyleSheet("color: rgb(102, 126, 234); font-size: 24px;")
        
        primary_layout.addWidget(self.primary_color_button)
        primary_layout.addWidget(self.primary_color_preview)
        primary_layout.addStretch()
        
        # Accent color section
        accent_layout = QHBoxLayout()
        self.accent_color_button = QPushButton("Choose Accent Color")
        self.accent_color_button.setProperty("class", "secondary")
        self.accent_color_button.clicked.connect(self.choose_accent_color)
        
        self.accent_color_preview = QLabel("●")
        self.accent_color_preview.setStyleSheet("color: rgb(118, 75, 162); font-size: 24px;")
        
        accent_layout.addWidget(self.accent_color_button)
        accent_layout.addWidget(self.accent_color_preview)
        accent_layout.addStretch()
        
        # Background theme selector
        self.background_combo = QComboBox()
        self.background_combo.addItems([
            "🌌 Dark Gradient (Default)",
            "🌃 Solid Dark",
            "🌆 Dark Blue",
            "🌍 Dark Green",
            "🌸 Dark Purple",        "🔥 Dark Red"
        ])
        
        custom_layout.addRow("Primary Color:", primary_layout)
        custom_layout.addRow("Accent Color:", accent_layout)
        custom_layout.addRow("Background Theme:", self.background_combo)
        
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
        
        scroll_layout.addWidget(presets_group)
        scroll_layout.addWidget(custom_group)
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
    
    def create_preset_button(self, text, color, row, col, layout):
        """Create a color preset button"""
        button = QPushButton(text)
        button.setProperty("class", "preset")
        button.setStyleSheet(f"""
            QPushButton[class="preset"] {{
                background: {color};
                color: white;
                border: none;
                font-weight: 600;
                transition: all 0.2s ease;
            }}
            QPushButton[class="preset"]:hover {{
                background: {color};
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);            }}
            QPushButton[class="preset"]:pressed {{
                transform: translateY(0px);
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
        """Choose custom primary color with enhanced color picker"""
        current_color = QColor("rgb(102, 126, 234)")
        color = QColorDialog.getColor(current_color, self, "Choose Primary Color")
        if color.isValid():
            self.primary_color_button.setText(f"Primary: {color.name()}")
            self.primary_color_preview.setStyleSheet(f"color: {color.name()}; font-size: 24px;")
            # Optionally apply color immediately for preview
            if self.parent_window:
                self.apply_color_live(color, 'primary')
    
    def choose_accent_color(self):
        """Choose custom accent color with enhanced color picker"""
        current_color = QColor("rgb(118, 75, 162)")
        color = QColorDialog.getColor(current_color, self, "Choose Accent Color")
        if color.isValid():
            self.accent_color_button.setText(f"Accent: {color.name()}")
            self.accent_color_preview.setStyleSheet(f"color: {color.name()}; font-size: 24px;")
            # Optionally apply color immediately for preview
            if self.parent_window:
                self.apply_color_live(color, 'accent')
    
    def apply_color_live(self, color, color_type):
        """Apply color changes live for preview"""
        # This could update the parent window's theme in real-time
        # Implementation would depend on how the main window handles theme updates
        pass
    
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
