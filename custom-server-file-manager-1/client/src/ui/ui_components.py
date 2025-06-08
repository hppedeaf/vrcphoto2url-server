#!/usr/bin/env python3
"""
Enhanced UI Components for Custom Server File Manager
Modern components with CSS transform fixes to eliminate warnings
"""

import os
from typing import Optional, List
from PySide6.QtWidgets import (
    QFrame, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QWidget, QProgressBar, QListWidget, QTextEdit, QCheckBox,
    QGraphicsDropShadowEffect, QApplication, QMessageBox, QDialog,
    QGroupBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, QRect, QMimeData
from PySide6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QDragEnterEvent, QDropEvent, QPixmap, QPalette

class ModernCard(QGroupBox):
    """Modern card component with beautiful styling and CSS fixes"""
    
    def __init__(self, title: str = "", icon: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self.icon = icon
        self.setup_ui()
        self.apply_styling()
        
    def setup_ui(self):
        """Setup card layout"""
        # Set the title with icon
        display_title = f"{self.icon} {self.title}" if self.icon else self.title
        self.setTitle(display_title)
        
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 25, 20, 20)
        self.main_layout.setSpacing(15)
        
        # Create content container
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        
        self.main_layout.addWidget(self.content_widget)
        
    def apply_styling(self):
        """Apply modern card styling with CSS fixes"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                color: #ffffff;
                border: 2px solid #404040;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 20px;
                background-color: #2d2d2d;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px;
                background-color: #2d2d2d;
                color: #4CAF50;
                font-weight: bold;
                font-size: 16px;
                border: none;
            }
            QWidget {
                background-color: transparent;
                color: #ffffff;
            }
        """)
    
    def add_content(self, widget_or_layout):
        """Add content to the card"""
        from PySide6.QtWidgets import QWidget, QLayout
        if isinstance(widget_or_layout, QWidget):  # It's a widget
            self.content_layout.addWidget(widget_or_layout)
        elif isinstance(widget_or_layout, QLayout):  # It's a layout
            self.content_layout.addLayout(widget_or_layout)
        else:
            # Fallback: try to add as widget first, then as layout
            try:
                self.content_layout.addWidget(widget_or_layout)
            except:
                self.content_layout.addLayout(widget_or_layout)
    
    def set_value(self, value: str):
        """Set a main value (for stats cards)"""
        # Find existing value label or create new one
        value_label = getattr(self, '_value_label', None)
        if not value_label:
            value_label = QLabel()
            value_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
            value_label.setStyleSheet("""
                QLabel {
                    color: #4CAF50; 
                    margin: 10px 0;
                    background-color: transparent;
                }
            """)
            value_label.setAlignment(Qt.AlignCenter)
            self.content_layout.addWidget(value_label)
            self._value_label = value_label
        
        value_label.setText(value)

class ActionButton(QPushButton):
    """Enhanced action button with CSS fixes and reliable styling"""
    
    def __init__(self, text: str, style_type: str = "primary", parent=None):
        super().__init__(text, parent)
        self.style_type = style_type
        self.setup_button()
        self.apply_style()
        
    def setup_button(self):
        """Setup button properties"""
        self.setMinimumHeight(44)
        self.setMinimumWidth(120)
        self.setFont(QFont("Segoe UI", 13, QFont.Medium))
        self.setCursor(Qt.PointingHandCursor)
        
    def apply_style(self):
        """Apply button styling with CSS fixes"""
        styles = {
            "primary": {
                "background": "#4CAF50",
                "hover": "#45a049",
                "text": "#ffffff",
                "border": "none"
            },
            "secondary": {
                "background": "#404040", 
                "hover": "#505050",
                "text": "#ffffff",
                "border": "none"
            },
            "danger": {
                "background": "#f44336",
                "hover": "#da190b",
                "text": "#ffffff",
                "border": "none"
            },
            "success": {
                "background": "#2E7D32",
                "hover": "#1B5E20",
                "text": "#ffffff",
                "border": "none"
            },
            "outline": {
                "background": "transparent",
                "hover": "#4CAF50",
                "text": "#4CAF50",
                "border": "2px solid #4CAF50"
            }
        }
        
        style = styles.get(self.style_type, styles["primary"])
        
        if self.style_type == "outline":
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {style["background"]};
                    color: {style["text"]};
                    border: {style["border"]};
                    border-radius: 8px;
                    padding: 12px 20px;
                    font-weight: bold;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: {style["hover"]};
                    color: white;
                    border-color: {style["hover"]};
                }}
                QPushButton:pressed {{
                    background-color: {style["hover"]};
                }}
                QPushButton:disabled {{
                    background-color: transparent;
                    color: #666666;
                    border-color: #666666;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {style["background"]};
                    color: {style["text"]};
                    border: {style["border"]};
                    border-radius: 8px;
                    padding: 12px 20px;
                    font-weight: bold;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: {style["hover"]};
                }}
                QPushButton:pressed {{
                    background-color: {style["background"]};
                }}
                QPushButton:disabled {{
                    background-color: #666666;
                    color: #999999;
                }}
            """)
    
    def setStyleType(self, style_type: str):
        """Change button style type"""
        self.style_type = style_type
        self.apply_style()

class StatusIndicator(QLabel):
    """Enhanced status indicator with proper styling"""
    
    def __init__(self, text: str, status_type: str = "info", parent=None):
        super().__init__(text, parent)
        self.status_type = status_type
        self.setup_indicator()
        
    def setup_indicator(self):
        """Setup indicator styling"""
        self.setFont(QFont("Segoe UI", 11, QFont.Medium))
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(30)
        self.setMinimumWidth(150)
        self.update_style()
        
    def update_style(self):
        """Update styling based on status type"""
        colors = {
            "success": {"bg": "#2E7D32", "text": "#ffffff"},
            "error": {"bg": "#d32f2f", "text": "#ffffff"},
            "warning": {"bg": "#f57c00", "text": "#ffffff"},
            "info": {"bg": "#1976d2", "text": "#ffffff"}
        }
        
        color = colors.get(self.status_type, colors["info"])
        
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color["bg"]};
                color: {color["text"]};
                border-radius: 15px;
                padding: 6px 12px;
                font-weight: bold;
            }}
        """)

class FileDropZone(QFrame):
    """Enhanced drop zone with better visual feedback and CSS fixes"""
    
    files_dropped = Signal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.dragging = False
        self.setup_ui()
        self.apply_styling()
        
    def setup_ui(self):
        """Setup drop zone UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        
        # Icon
        icon_label = QLabel("📁")
        icon_label.setFont(QFont("Segoe UI", 48))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("color: #cccccc; background: transparent;")
        layout.addWidget(icon_label)
        
        # Main text
        main_label = QLabel("Drop files here to upload")
        main_label.setFont(QFont("Segoe UI", 16, QFont.Medium))
        main_label.setAlignment(Qt.AlignCenter)
        main_label.setStyleSheet("color: #ffffff; background: transparent;")
        layout.addWidget(main_label)
        
        # Hint text
        hint_label = QLabel("or click to browse files")
        hint_label.setFont(QFont("Segoe UI", 12))
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("color: #cccccc; background: transparent;")
        layout.addWidget(hint_label)
        
    def apply_styling(self):
        """Apply drop zone styling with CSS fixes"""
        self.setStyleSheet("""
            QFrame {
                border: 3px dashed #666666;
                border-radius: 12px;
                background-color: #333333;
            }
        """)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.dragging = True
            self.setStyleSheet("""
                QFrame {
                    border: 3px dashed #4CAF50;
                    border-radius: 12px;
                    background-color: rgba(76, 175, 80, 0.1);
                }
            """)
    
    def dragLeaveEvent(self, event):
        self.dragging = False
        self.apply_styling()
    
    def dropEvent(self, event: QDropEvent):
        self.dragging = False
        self.apply_styling()
        
        files = []
        for url in event.mimeData().urls():
            files.append(url.toLocalFile())
        
        if files:
            self.files_dropped.emit(files)

class ModernProgressBar(QProgressBar):
    """Enhanced progress bar with modern styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(8)
        self.setMaximumHeight(8)
        self.setTextVisible(False)
        self.apply_styling()
        
    def apply_styling(self):
        """Apply modern progress bar styling"""
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #404040;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 4px;
            }
        """)

class NotificationCard(QDialog):
    """Enhanced notification popup with modern design"""
    
    def __init__(self, title: str, message: str, notification_type: str = "info", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.notification_type = notification_type
        self.setup_ui(title, message)
        self.apply_styling()
        
    def setup_ui(self, title: str, message: str):
        """Setup notification UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title_label)
        
        # Message
        message_label = QLabel(message)
        message_label.setFont(QFont("Segoe UI", 12))
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = ActionButton("OK", "primary")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
    def apply_styling(self):
        """Apply notification styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 12px;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
        """)

def apply_modern_theme(app_or_widget):
    """Apply enhanced modern theme with CSS fixes"""
    if hasattr(app_or_widget, 'setStyleSheet'):
        # Enhanced theme without CSS transform warnings
        app_or_widget.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            }
            QWidget {
                background-color: transparent;
                color: #ffffff;
                font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            }
            QTabWidget::pane {
                border: 2px solid #404040;
                background-color: #2d2d2d;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                border: 2px solid #404040;
                padding: 15px 25px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background-color: #2d2d2d;
                color: #4CAF50;
                border-bottom: 2px solid #2d2d2d;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background-color: #525252;
                color: #ffffff;
            }
            QTextEdit {
                border: 2px solid #404040;
                border-radius: 6px;
                background-color: #2d2d2d;
                color: #ffffff;
                selection-background-color: #4CAF50;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
            QLineEdit {
                border: 2px solid #404040;
                border-radius: 6px;
                padding: 12px;
                background-color: #2d2d2d;
                color: #ffffff;
                selection-background-color: #4CAF50;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
                background-color: #404040;
            }
            QListWidget {
                border: 2px solid #404040;
                border-radius: 6px;
                background-color: #2d2d2d;
                selection-background-color: #4CAF50;
                outline: none;
                color: #ffffff;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #404040;
                color: #ffffff;
                background-color: transparent;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: #ffffff;
                font-weight: 600;
            }
            QListWidget::item:hover {
                background-color: #404040;
                color: #ffffff;
            }
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #404040;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 4px;
            }
            QStatusBar {
                background-color: #404040;
                border-top: 2px solid #525252;
                color: #ffffff;
                font-size: 12px;
                padding: 8px;
                font-weight: 500;
            }
        """)

# Utility functions for consistent UI creation
def create_icon_label(icon: str, size: int = 24, color: str = "#4CAF50") -> QLabel:
    """Create consistent icon label"""
    label = QLabel(icon)
    label.setFont(QFont("Segoe UI", size))
    label.setStyleSheet(f"color: {color}; background: transparent;")
    label.setAlignment(Qt.AlignCenter)
    return label

def create_title_label(text: str, size: int = 18, color: str = "#ffffff") -> QLabel:
    """Create consistent title label"""
    label = QLabel(text)
    label.setFont(QFont("Segoe UI", size, QFont.Bold))
    label.setStyleSheet(f"color: {color}; background: transparent;")
    return label

def create_subtitle_label(text: str, size: int = 12, color: str = "#b0b0b0") -> QLabel:
    """Create consistent subtitle label"""
    label = QLabel(text)
    label.setFont(QFont("Segoe UI", size))
    label.setStyleSheet(f"color: {color}; background: transparent;")
    return label
