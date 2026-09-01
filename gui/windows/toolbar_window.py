"""
ToolbarWindow: Thanh công cụ điều khiển chính của SmartTranslator.
Thiết kế gọn nhẹ, hỗ trợ di chuyển window và phím tắt bàn phím (Esc, Space, Enter).
"""

from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QApplication

from config import config_manager
from gui.theme import theme_manager
from utils.logger import logger


class ToolbarWindow(QWidget):
    """
    Cửa sổ thanh công cụ thu nhỏ (Toolbar Compact Mode).
    """

    # Signals
    scan_toggled = pyqtSignal()
    clear_clicked = pyqtSignal()
    direction_switched = pyqtSignal()
    help_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    exit_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._drag_offset: QPoint = None
        self._init_ui()
        self.apply_theme()

    def _init_ui(self):
        self.panel = QWidget(self)
        layout = QHBoxLayout(self.panel)
        layout.setContentsMargins(10, 5, 10, 5)

        # Buttons
        self.btn_direction = QPushButton("En ➔ Vi (Space)")
        self.btn_quet_toggle = QPushButton("🔍 Quét (Esc)")
        self.btn_clear = QPushButton("Xóa (Enter)")
        self.btn_help = QPushButton("❓ HDSD")
        self.btn_settings = QPushButton("⚙️")
        self.btn_settings.setFixedWidth(40)
        self.btn_exit = QPushButton("✕")
        self.btn_exit.setFixedWidth(40)

        widgets = [
            self.btn_direction,
            self.btn_quet_toggle,
            self.btn_clear,
            self.btn_help,
            self.btn_settings,
            self.btn_exit,
        ]
        for w in widgets:
            # Ngăn nút bấm cướp Focus bàn phím để phím tắt Space, Esc, Enter luôn hoạt động đúng
            w.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            layout.addWidget(w)

        # Connect internal signals
        self.btn_quet_toggle.clicked.connect(self.scan_toggled.emit)
        self.btn_clear.clicked.connect(self.clear_clicked.emit)
        self.btn_direction.clicked.connect(self.direction_switched.emit)
        self.btn_help.clicked.connect(self.help_clicked.emit)
        self.btn_settings.clicked.connect(self.settings_clicked.emit)
        self.btn_exit.clicked.connect(self.exit_clicked.emit)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.panel)
        self.setLayout(main_layout)

    def apply_theme(self):
        """Áp dụng màu sắc theo cài đặt theme hiện tại."""
        theme_name = config_manager.get("theme", "Sáng")
        direction = config_manager.get("direction", "en-vi")

        colors = theme_manager.get_theme(theme_name)
        btn_colors = colors["button_colors"]

        self.panel.setStyleSheet(f"""
            QWidget {{
                background-color: {colors['panel_bg']};
                border-radius: 8px;
                border: 1px solid {colors['panel_border']}; 
            }}
            QPushButton {{
                color: {colors['btn_fg']};
                font-weight: bold;
                border-radius: 4px;
                padding: 6px 10px;
                border: none; 
            }}
            QPushButton:hover {{
                background-color: {colors['btn_hover']}; 
            }}
        """)

        # Style từng button
        if direction == "vi-en":
            self.btn_direction.setText("Vi ➔ En (Space)")
            self.btn_direction.setStyleSheet(f"background-color: {btn_colors['direction_active']}; width: 85px;")
        else:
            self.btn_direction.setText("En ➔ Vi (Space)")
            self.btn_direction.setStyleSheet(f"background-color: {btn_colors['direction']}; width: 85px;")

        self.btn_quet_toggle.setStyleSheet(f"background-color: {btn_colors['scan']};")
        self.btn_clear.setStyleSheet(f"background-color: {btn_colors['clear']};")
        self.btn_help.setStyleSheet(f"background-color: {btn_colors['help']};")
        self.btn_settings.setStyleSheet(f"background-color: {btn_colors['settings']};")
        self.btn_exit.setStyleSheet(f"background-color: {btn_colors['exit']};")

    def keyPressEvent(self, event):
        """Xử lý các phím tắt bàn phím toàn cục cho Toolbar."""
        if event.key() == Qt.Key.Key_Escape:
            self.scan_toggled.emit()
            event.accept()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.clear_clicked.emit()
            event.accept()
        elif event.key() == Qt.Key.Key_Space:
            self.direction_switched.emit()
            event.accept()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if self._drag_offset and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, event):
        self._drag_offset = None
