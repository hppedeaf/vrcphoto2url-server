#!/usr/bin/env python3
"""
Modern UI Components for Custom Server File Manager Client
Beautiful, modern UI components with consistent design
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
    """Modern card component with beautiful styling"""
    
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
        """Apply modern card styling matching web interface"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 16px;
                color: #ffffff;
                border: 1px solid rgb(51, 65, 85);
                border-radius: 12px;
                margin-top: 20px;
                padding-top: 25px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 41, 59, 0.8), stop:1 rgba(26, 26, 46, 0.8));
                backdrop-filter: blur(10px);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 8px 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgb(102, 126, 234), stop:1 rgb(118, 75, 162));
                color: #ffffff;
                font-weight: 700;
                font-size: 14px;
                border-radius: 6px;
                border: none;
            }
            QWidget {
                background-color: transparent;
                color: #ffffff;
                font-size: 14px;
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
    """Modern action button with beautiful styling"""
    
    def __init__(self, text: str, style_type: str = "primary", parent=None):
        super().__init__(text, parent)
        self.style_type = style_type
        self.setup_button()
        self.apply_style()
    
    def setup_button(self):
        """Setup button properties with proper scaling"""
        self.setMinimumHeight(48)
        self.setMinimumWidth(140)
        self.setFont(QFont("Inter", 14, QFont.Medium))
        self.setCursor(Qt.PointingHandCursor)
        
    def apply_style(self):
        """Apply button styling based on type matching web interface"""
        styles = {
            "primary": {
                "background": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgb(102, 126, 234), stop:1 rgb(118, 75, 162))",
                "hover": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgb(124, 141, 240), stop:1 rgb(139, 95, 191))",
                "text": "#ffffff"
            },
            "secondary": {
                "background": "rgba(30, 41, 59, 0.8)", 
                "hover": "rgba(51, 65, 85, 0.9)",
                "text": "#ffffff"
            },
            "danger": {
                "background": "rgba(239, 68, 68, 0.9)",
                "hover": "rgba(220, 38, 38, 1)",
                "text": "#ffffff"
            },
            "success": {
                "background": "rgba(16, 185, 129, 0.9)",
                "hover": "rgba(5, 150, 105, 1)",
                "text": "#ffffff"
            },
            "outline": {
                "background": "transparent",
                "hover": "rgba(102, 126, 234, 0.1)",
                "text": "rgb(102, 126, 234)",
                "border": "2px solid rgb(102, 126, 234)"
            }
        }
        
        style = styles.get(self.style_type, styles["primary"])
        border_style = f"border: {style.get('border', 'none')};"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: {style["background"]};
                color: {style["text"]};
                {border_style}
                border-radius: 8px;
                padding: 14px 24px;
                font-weight: 600;
                font-size: 14px;
                text-align: center;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background: {style["hover"]};
                transform: translateY(-1px);
            }}
            QPushButton:pressed {{
                background: {style["background"]};
                transform: translateY(0px);
            }}
            QPushButton:disabled {{
                background: rgba(148, 163, 184, 0.3);
                color: rgba(148, 163, 184, 0.7);
                border: none;
            }}
        """)
    
    def setStyleType(self, style_type: str):
        """Change button style type"""
        self.style_type = style_type
        self.apply_style()

class StatusIndicator(QLabel):
    """Status indicator with icon and text"""
    
    def __init__(self, text: str, status_type: str = "info", parent=None):
        super().__init__(text, parent)
        self.status_type = status_type
        self.setup_indicator()
    
    def setup_indicator(self):
        """Setup indicator styling with proper fonts and sizing"""
        self.setFont(QFont("Inter", 13, QFont.Medium))
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(36)
        self.setMinimumWidth(180)
        self.update_style()
        
    def update_style(self):
        """Update styling based on status type matching web colors"""
        colors = {
            "success": {"bg": "rgba(16, 185, 129, 0.9)", "text": "#ffffff", "border": "rgb(5, 150, 105)"},
            "error": {"bg": "rgba(239, 68, 68, 0.9)", "text": "#ffffff", "border": "rgb(220, 38, 38)"},
            "warning": {"bg": "rgba(245, 158, 11, 0.9)", "text": "#ffffff", "border": "rgb(217, 119, 6)"},
            "info": {"bg": "rgba(59, 130, 246, 0.9)", "text": "#ffffff", "border": "rgb(37, 99, 235)"}
        }
        
        color = colors.get(self.status_type, colors["info"])
        
        self.setStyleSheet(f"""
            QLabel {{
                background: {color["bg"]};
                color: {color["text"]};
                border: 1px solid {color["border"]};
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: 600;
                font-size: 13px;
                letter-spacing: 0.3px;
            }}
        """)
    
    def update_status(self, text: str, status_type: str):
        """Update status text and type"""
        self.setText(text)
        self.status_type = status_type
        self.update_style()

class FileDropZone(QFrame):
    """Modern file drop zone with drag and drop support"""
    
    files_dropped = Signal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setAcceptDrops(True)
    
    def setup_ui(self):
        """Setup drop zone UI with improved scaling"""
        self.setMinimumHeight(240)
        self.setFrameStyle(QFrame.Box)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Icon
        icon_label = QLabel("📁")
        icon_label.setFont(QFont("Segoe UI", 56))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("color: rgb(102, 126, 234); background: transparent;")
        
        # Main text
        main_text = QLabel("Drag photos here or click to browse")
        main_text.setFont(QFont("Inter", 18, QFont.Medium))
        main_text.setAlignment(Qt.AlignCenter)
        main_text.setStyleSheet("color: #ffffff; background: transparent; font-weight: 500;")
        
        # Hint text
        hint_text = QLabel("Supports: JPG, PNG, GIF, WEBP, MP4, PDF and more")
        hint_text.setFont(QFont("Inter", 14))
        hint_text.setAlignment(Qt.AlignCenter)
        hint_text.setStyleSheet("color: rgba(203, 213, 225, 0.8); background: transparent;")
        
        layout.addWidget(icon_label)
        layout.addWidget(main_text)
        layout.addWidget(hint_text)
        
        self.apply_styling()
        
    def apply_styling(self):
        """Apply drop zone styling matching web interface"""
        self.setStyleSheet("""
            QFrame {
                border: 3px dashed rgba(102, 126, 234, 0.6);
                border-radius: 16px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(102, 126, 234, 0.05), stop:1 rgba(118, 75, 162, 0.05));
            }
            QFrame:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(102, 126, 234, 0.1), stop:1 rgba(118, 75, 162, 0.1));
                border-color: rgba(102, 126, 234, 0.8);
            }
        """)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame {
                    border: 3px solid #4CAF50;
                    border-radius: 12px;
                    background-color: rgba(76, 175, 80, 0.3);
                }
            """)
    
    def dragLeaveEvent(self, event):
        """Handle drag leave event"""
        self.apply_styling()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        files = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                files.append(url.toLocalFile())
        
        if files:
            self.files_dropped.emit(files)
        
        self.apply_styling()
        event.acceptProposedAction()
    
    def mousePressEvent(self, event):
        """Handle mouse press for file dialog"""
        if event.button() == Qt.LeftButton:
            from PySide6.QtWidgets import QFileDialog
            files, _ = QFileDialog.getOpenFileNames(
                self, 
                "Select Files to Upload",
                "",
                "All Files (*.*)"
            )
            if files:
                self.files_dropped.emit(files)

class ModernProgressBar(QWidget):
    """Modern progress bar with text"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.progress = 0
        self.status_text = "Ready"
        
    def setup_ui(self):
        """Setup progress bar UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setFont(QFont("Segoe UI", 12))
        self.status_label.setStyleSheet("color: #ffffff; background: transparent;")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #404040;
                border-radius: 8px;
                background-color: #1a1a1a;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #2E7D32);
                border-radius: 6px;
            }
        """)
        
        # Percentage label
        self.percentage_label = QLabel("0%")
        self.percentage_label.setFont(QFont("Segoe UI", 11))
        self.percentage_label.setAlignment(Qt.AlignRight)
        self.percentage_label.setStyleSheet("color: #aaaaaa; background: transparent;")
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.percentage_label)
        
    def update_progress(self, percentage: int, status: str = ""):
        """Update progress bar"""
        self.progress = percentage
        self.progress_bar.setValue(percentage)
        self.percentage_label.setText(f"{percentage}%")
        
        if status:
            self.status_text = status
            self.status_label.setText(status)

class NotificationCard(QFrame):
    """Modern notification card"""
    
    def __init__(self, message: str, notification_type: str = "info", parent=None):
        super().__init__(parent)
        self.message = message
        self.notification_type = notification_type
        self.setup_ui()
        
        # Auto-hide timer
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_notification)
        self.timer.start(3000)  # 3 seconds
        
    def setup_ui(self):
        """Setup notification UI"""
        self.setFixedSize(300, 80)
        self.setFrameStyle(QFrame.StyledPanel)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Icon
        icons = {
            "success": "✅",
            "error": "❌", 
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        icon_label = QLabel(icons.get(self.notification_type, "ℹ️"))
        icon_label.setFont(QFont("Segoe UI", 20))
        
        # Message
        message_label = QLabel(self.message)
        message_label.setFont(QFont("Segoe UI", 11))
        message_label.setWordWrap(True)
        
        layout.addWidget(icon_label)
        layout.addWidget(message_label, 1)
        
        self.apply_styling()
        
    def apply_styling(self):
        """Apply notification styling"""
        colors = {
            "success": {"bg": "#2E7D32", "border": "#4CAF50"},
            "error": {"bg": "#d32f2f", "border": "#f44336"},
            "warning": {"bg": "#f57c00", "border": "#ff9800"},
            "info": {"bg": "#1976d2", "border": "#2196f3"}
        }
        
        color = colors.get(self.notification_type, colors["info"])
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color["bg"]};
                border: 2px solid {color["border"]};
                border-radius: 8px;
                color: #ffffff;
            }}
            QLabel {{
                background-color: transparent;
                color: #ffffff;
            }}
        """)
    
    def hide_notification(self):
        """Hide notification with animation"""
        self.hide()
        self.deleteLater()
    
    @staticmethod
    def show_success(parent, message: str):
        """Show success notification"""
        notification = NotificationCard(message, "success", parent)
        NotificationCard._position_notification(notification, parent)
        notification.show()
        
    @staticmethod
    def show_error(parent, message: str):
        """Show error notification"""
        notification = NotificationCard(message, "error", parent)
        NotificationCard._position_notification(notification, parent)
        notification.show()
        
    @staticmethod
    def show_warning(parent, message: str):
        """Show warning notification"""
        notification = NotificationCard(message, "warning", parent)
        NotificationCard._position_notification(notification, parent)
        notification.show()
        
    @staticmethod
    def show_info(parent, message: str):
        """Show info notification"""
        notification = NotificationCard(message, "info", parent)
        NotificationCard._position_notification(notification, parent)
        notification.show()
    
    @staticmethod
    def _position_notification(notification, parent):
        """Position notification in top-right corner"""
        if parent:
            parent_rect = parent.geometry()
            x = parent_rect.right() - notification.width() - 20
            y = parent_rect.top() + 20
            notification.move(x, y)

def apply_modern_theme(app_or_widget):
    """Apply modern dark theme to application or widget"""
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
    
    if hasattr(app_or_widget, 'setPalette'):
        app_or_widget.setPalette(palette)
    
    # Set global stylesheet
    style = """
        QWidget {
            background-color: #1a1a1a;
            color: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QMainWindow {
            background-color: #1a1a1a;
        }
        QFrame {
            border: none;
        }
        QScrollArea {
            border: none;
            background-color: transparent;
        }
        QScrollBar:vertical {
            background-color: #404040;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: #4CAF50;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #45a049;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
    """
    
    if hasattr(app_or_widget, 'setStyleSheet'):
        app_or_widget.setStyleSheet(style)
