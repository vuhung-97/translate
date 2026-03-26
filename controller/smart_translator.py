import io
from PIL import Image
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QPoint, QRect, QBuffer, QIODevice
from PyQt5.QtGui import QPainter, QColor, QPen

# Các import từ dự án (giữ nguyên)
from gui.ui_components import SettingsDialog, HelpDialog, SmartTranslatorUI, OverlayManager
from config import DEFAULT_SETTINGS
from gui.theme_config import ThemeConfig
from core.translation_service import TranslationService
from controller.mouse_event import MouseEvent
from controller.ui_handler import UIHandler

# ================================================================
# LỚP ĐIỀU KHIỂN CHÍNH (SỬ DỤNG ĐA KẾ THỪA)
# ================================================================
class SmartTranslator(QWidget, MouseEvent, UIHandler):
    """Lớp điều phối chính - Kết nối UI, Chụp màn hình và Dịch thuật."""
    def __init__(self):
        super().__init__()
        # 1. Khởi tạo dữ liệu & Cấu hình
        self._trans_settings = DEFAULT_SETTINGS.copy()
        self.theme_manager = ThemeConfig()
        
        # 2. Khởi tạo các thành phần chuyên biệt
        self.overlay_manager = OverlayManager(self, self.theme_manager)
        self.trans_service = TranslationService(self._trans_settings)
        
        # 3. Trạng thái giao diện (Được các Mixin sử dụng)
        self._is_scanning_mode = False
        self._is_selecting = False
        self._start_pt = QPoint()
        self._end_pt = QPoint()
        self._snapshot = None
        self._drag_offset = None

        # 4. Setup UI
        self.ui_builder = SmartTranslatorUI()
        self.ui_builder.setup_ui(self)
        self.setFocusPolicy(Qt.StrongFocus)
        self._connect_signals()
        
        self._set_compact_mode()
        self.show()

    def _connect_signals(self):
        """Kết nối tín hiệu từ các nút bấm với các phương thức xử lý."""
        self._btn_quet_toggle.clicked.connect(self._toggle_scan_mode)
        self._btn_clear.clicked.connect(self.overlay_manager.clear_all)
        self._btn_direction.clicked.connect(self._switch_direction)
        self._btn_help.clicked.connect(self._open_help)
        self._btn_settings.clicked.connect(self._open_settings)
        self._btn_exit.clicked.connect(QApplication.quit)

    def _switch_direction(self):
        btn_colors = self.theme_manager.get_theme(self._trans_settings.get('theme', 'Tối'))['button_colors']
        if self._trans_settings.get('direction') == 'en-vi':
            self._trans_settings['direction'] = 'vi-en'
            self._btn_direction.setText("Vi ➔ En")
            self._btn_direction.setStyleSheet(f"background-color: {btn_colors['direction_active']}; width: 85px;")
        else:
            self._trans_settings['direction'] = 'en-vi'
            self._btn_direction.setText("En ➔ Vi")
            self._btn_direction.setStyleSheet(f"background-color: {btn_colors['direction']}; width: 85px;")

    def _open_help(self):
        dialog = HelpDialog(self)
        dialog.exec_()

    def _open_settings(self):
        dialog = SettingsDialog(self._trans_settings, self)
        if dialog.exec_():
            self._trans_settings.update(dialog.get_values())

    def _toggle_scan_mode(self):
        if self._is_scanning_mode:
            self._set_compact_mode()
        else:
            self._set_full_scan_mode()

    def _set_full_scan_mode(self):
        self._is_scanning_mode = True
        self.setWindowOpacity(0)
        QApplication.processEvents()
        self._snapshot = QApplication.primaryScreen().grabWindow(0)
        self.setWindowOpacity(1)
        
        self.setGeometry(QApplication.primaryScreen().geometry())
        self._btn_quet_toggle.setText("🔙 Thu nhỏ (Esc)")
        self._btn_help.setVisible(False)
        self.setFocus()
        self.update()

    def _set_compact_mode(self):
        self._is_scanning_mode = False
        self._btn_quet_toggle.setText("🔍 Quét (Esc)")
        self._btn_help.setVisible(True)
        self.panel.adjustSize()
        self.resize(self.panel.size())
        self.move(0, 0)
        self.setFocus()
        self.update()