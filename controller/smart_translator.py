# pylint: disable=no-name-in-module, import-error, too-few-public-methods

"""
Module này định nghĩa lớp SmartTranslator
Lớp điều phối chính - Kết nối UI, Chụp màn hình và Dịch thuật.
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Các import từ dự án (giữ nguyên)
from gui.ui_components import SettingsDialog, HelpDialog, SmartTranslatorUI
from controller.event import MouseEvent, UIHandler

# ================================================================
# LỚP ĐIỀU KHIỂN CHÍNH (SỬ DỤNG ĐA KẾ THỪA)
# ================================================================
class SmartTranslator(MouseEvent, UIHandler):
    """Lớp điều phối chính - Kết nối UI, Chụp màn hình và Dịch thuật."""
    def __init__(self):
        super().__init__()

        self.ui_builder = SmartTranslatorUI()
        self.ui_builder.setup_ui(self)
        self._set_compact_mode()
        self._connect_signals()
        self.setFocusPolicy(Qt.StrongFocus)
        self.show()

    def _connect_signals(self):
        """Kết nối tín hiệu từ các nút bấm với các phương thức xử lý."""
        self.btn_quet_toggle.clicked.connect(self._toggle_scan_mode)
        self.btn_clear.clicked.connect(self.overlay_manager.clear_all)
        self.btn_direction.clicked.connect(self._switch_direction)
        self.btn_help.clicked.connect(self._open_help)
        self.btn_settings.clicked.connect(self._open_settings)
        self.btn_exit.clicked.connect(QApplication.quit)

    def _switch_direction(self):
        btn_colors = self.theme_manager.get_theme(
            self.trans_settings.get('theme', 'Tối'))['button_colors']
        if self.trans_settings.get('direction') == 'en-vi':
            self.trans_settings['direction'] = 'vi-en'
            self.btn_direction.setText("Vi ➔ En")
            self.btn_direction.setStyleSheet(
                f"background-color: {btn_colors['direction_active']}; width: 85px;")
        else:
            self.trans_settings['direction'] = 'en-vi'
            self.btn_direction.setText("En ➔ Vi")
            self.btn_direction.setStyleSheet(
                f"background-color: {btn_colors['direction']}; width: 85px;")

    def _open_help(self):
        dialog = HelpDialog(self)
        dialog.exec_()

    def _open_settings(self):
        dialog = SettingsDialog(self.trans_settings, self)
        if dialog.exec_():
            self.trans_settings.update(dialog.get_values())
