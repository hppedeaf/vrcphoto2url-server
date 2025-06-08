from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QSpinBox, QComboBox, QPushButton, QHBoxLayout, QFormLayout, QGroupBox, QScrollArea, QWidget
from PySide6.QtCore import Qt

class SettingsDialog(QDialog):
    """Settings dialog for configuring client options."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Client Settings")
        self.setFixedSize(550, 500)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("⚙️ Client Settings")
        header.setAlignment(Qt.AlignCenter)
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
        save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        # Set scroll area
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)