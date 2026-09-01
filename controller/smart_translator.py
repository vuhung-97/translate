"""
Controller chính của ứng dụng SmartTranslator.
Điều phối kết nối giữa Toolbar UI, Overlay Scan Window, Result Overlays và TranslationService.
Loại bỏ hoàn toàn đa thừa kế (Multiple Inheritance).
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QRect

from config import config_manager
from gui.windows.toolbar_window import ToolbarWindow
from gui.windows.selection_window import SelectionOverlayWindow
from gui.windows.settings_dialog import SettingsDialog
from gui.windows.help_dialog import HelpDialog
from gui.components.result_overlay import ResultOverlayManager
from core.services.translation_service import TranslationService
from utils.logger import logger


class SmartTranslator(ToolbarWindow):
    """
    Class điều phối chính của ứng dụng SmartTranslator.
    """

    def __init__(self):
        super().__init__()

        # 1. Khởi tạo các thành phần chuyên biệt (Composition)
        self.overlay_manager = ResultOverlayManager(parent_widget=None)
        self.trans_service = TranslationService(config_manager)
        self.selection_window = None

        # 2. Kết nối Tín hiệu (Signals)
        self._connect_controller_signals()
        
        # 3. Hiển thị giao diện toolbar ở góc màn hình
        self.adjustSize()
        self.move(100, 100)
        self.show()
        logger.info("SmartTranslator Controller đã khởi chạy thành công.")

    def _connect_controller_signals(self):
        """Kết nối các signal từ ToolbarWindow tới phương thức xử lý controller."""
        self.scan_toggled.connect(self._toggle_scan_mode)
        self.clear_clicked.connect(self.overlay_manager.clear_all)
        self.direction_switched.connect(self._switch_direction)
        self.help_clicked.connect(self._open_help)
        self.settings_clicked.connect(self._open_settings)
        self.exit_clicked.connect(QApplication.quit)

    def _toggle_scan_mode(self):
        """Khởi động cửa sổ quét toàn màn hình (SelectionOverlayWindow)."""
        if self.selection_window is not None:
            try:
                self.selection_window.close()
            except Exception:
                pass

        self.selection_window = SelectionOverlayWindow()
        self.selection_window.selection_completed.connect(self._on_selection_completed)
        self.selection_window.cancelled.connect(self._on_selection_cancelled)
        self.selection_window.clear_requested.connect(self.overlay_manager.clear_all)
        self.selection_window.direction_switch_requested.connect(self._switch_direction)
        
        self.selection_window.start_selection()

    def _on_selection_completed(self, pil_img, rect: QRect):
        """Xử lý khi người dùng hoàn thành việc khoanh vùng chữ trên màn hình."""
        font_size = config_manager.get("font_size", 17)
        theme_name = config_manager.get("theme", "Sáng")

        # 1. Tạo ô hiển thị kết quả tại vùng chọn
        target_label = self.overlay_manager.create_result_box(
            rect=rect, font_size=font_size, theme_name=theme_name
        )

        # 2. Gọi TranslationService để nhận diện OCR và dịch thuật
        self.trans_service.process_image(pil_img, target_label)

    def _on_selection_cancelled(self):
        logger.info("Đã hủy chế độ chọn vùng màn hình.")

    def _switch_direction(self):
        """Đổi hướng dịch En -> Vi hoặc Vi -> En."""
        current_direction = config_manager.get("direction", "en-vi")
        new_direction = "vi-en" if current_direction == "en-vi" else "en-vi"
        
        config_manager["direction"] = new_direction
        self.apply_theme()
        logger.info(f"Đã chuyển hướng dịch sang: {new_direction}")

    def _open_help(self):
        """Mở cửa sổ Hướng dẫn."""
        dialog = HelpDialog(self)
        dialog.exec()

    def _open_settings(self):
        """Mở cửa sổ Cài đặt."""
        dialog = SettingsDialog(config_manager.settings.to_dict(), self)
        if dialog.exec():
            self.apply_theme()
