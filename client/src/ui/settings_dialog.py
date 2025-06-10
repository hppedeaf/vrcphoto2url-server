from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QSpinBox, QComboBox, QPushButton, QHBoxLayout, QFormLayout, QGroupBox, QScrollArea, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class SettingsDialog(QDialog):
    """Settings dialog for configuring client options."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Client Settings")
        self.setMinimumSize(550, 450)  # Set minimum size instead of fixed
        self.resize(650, 580)  # Set initial size but allow resizing
        self.setup_ui()
        
    def setup_ui(self):
        # Apply modern styling with web interface theme
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgb(15, 15, 35), stop:1 rgb(26, 26, 46));
                color: #ffffff;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                font-weight: 400;
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
            QSpinBox, QComboBox {
                padding: 10px 12px;
                border: none;
                border-radius: 8px;
                background: rgba(30, 41, 59, 0.7);
                color: #ffffff;
                font-size: 13px;
                font-weight: 400;
                min-height: 16px;
            }
            QSpinBox:focus, QComboBox:focus {
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
            QLabel {
                color: rgba(203, 213, 225, 0.9);
                font-size: 13px;
                font-weight: 400;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Header
        header = QLabel("⚙️ Client Settings")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Inter", 20, QFont.Bold))
        header.setStyleSheet("color: rgb(102, 126, 234); margin-bottom: 15px; font-weight: 700;")
        layout.addWidget(header)
        
        # Create scroll area for all settings
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Auto-upload settings
        upload_group = QGroupBox("📤 Auto Upload")
        upload_layout = QFormLayout(upload_group)
        
        self.auto_upload_check = QCheckBox("Enable auto-upload for new files")
        self.auto_upload_check.setChecked(True)
        upload_layout.addRow(self.auto_upload_check)
        
        scroll_layout.addWidget(upload_group)
        
        # Auto-delete settings
        delete_group = QGroupBox("🗑️ Auto Delete")
        delete_layout = QFormLayout(delete_group)
        
        self.auto_delete_check = QCheckBox("Enable auto-delete for old files")
        delete_layout.addRow(self.auto_delete_check)
        
        self.delete_after_value = QSpinBox()
        self.delete_after_value.setRange(1, 999)
        self.delete_after_value.setValue(30)
        delete_layout.addRow("Delete files older than (days):", self.delete_after_value)
        
        scroll_layout.addWidget(delete_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        save_btn = QPushButton("💾 Save")
        save_btn.setProperty("class", "primary")
        save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        # Set scroll area
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)