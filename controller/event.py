# pylint: disable=no-name-in-module, import-error, too-few-public-methods, invalid-name, unused-argument, attribute-defined-outside-init, no-member, too-many-instance-attributes, too-many-public-methods

"""
Module này định nghĩa lớp MouseEvent
Lớp bổ trợ xử lý di chuyển và quét vùng chọn.
"""

import io
from PIL import Image
from PyQt6.QtCore import QPoint, QRect, QBuffer, QIODevice, Qt
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import QWidget, QApplication
from core.translation_service import TranslationService
from gui.theme_config import ThemeConfig
from gui.ui_components import OverlayManager
from config import SETTINGS


# ================================================================
# XỬ LÝ SỰ KIỆN CHUỘT
# ================================================================
class Event(QWidget):
    """Lớp cơ sở cho các sự kiện chuột và giao diện."""
    def __init__(self):
        super().__init__()

        # 1. Khởi tạo dữ liệu & Cấu hình
        self.trans_settings = SETTINGS
        self.theme_manager = ThemeConfig()

        # 2. Khởi tạo các thành phần chuyên biệt
        self.overlay_manager = OverlayManager(self, self.theme_manager)
        self.trans_service = TranslationService(self.trans_settings)

        # 3. Trạng thái giao diện
        self._is_scanning_mode = False
        self._is_selecting = False
        self._start_pt = QPoint()
        self._end_pt = QPoint()
        self._snapshot = None
        self._drag_offset = None


class MouseEvent(Event):
    """
    Lớp bổ trợ xử lý di chuyển và quét vùng chọn.
    """

    def mousePressEvent(self, event):
        """Bắt đầu quét hoặc di chuyển cửa sổ khi nhấn chuột."""
        if self._is_scanning_mode and not self.panel.geometry().contains(event.pos()):
            self._is_selecting = True
            self._start_pt = event.pos()
            self._end_pt = event.pos()
        else:
            self._drag_offset = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        """Xử lý sự kiện di chuyển chuột."""
        if self._is_selecting:
            self._end_pt = event.pos()
            self.update()
        elif self._drag_offset:
            self.move(event.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, event):
        """Xử lý sự kiện thả chuột."""
        if self._is_selecting:
            self._is_selecting = False
            self._handle_selection_done()
        self._drag_offset = None

    def _handle_selection_done(self):
        """Xử lý khi người dùng hoàn thành việc chọn vùng dịch."""
        rect = QRect(self._start_pt, self._end_pt).normalized()
        if rect.width() < 10 or rect.height() < 10:
            return

        # 1. Cắt ảnh từ snapshot
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.ReadWrite)
        self._snapshot.copy(rect).save(buffer, "PNG")
        pil_img = Image.open(io.BytesIO(buffer.data()))

        # 2. Tạo khung hiển thị qua OverlayManager
        target_label = self.overlay_manager.create_result_box(
            rect, self.trans_settings.get("font_size", 12)
        )

        # 3. Yêu cầu TranslationService xử lý
        self.trans_service.process_image(pil_img, target_label)


# ================================================================
# VẼ GIAO DIỆN & PHÍM TẮT
# ================================================================
class UIHandler(Event):
    """Lớp bổ trợ vẽ khung chọn và phím tắt.""" 

    def __init__(self):
        super().__init__()

    def paintEvent(self, event):
        """Vẽ lớp phủ mờ và khung chọn khi ở chế độ quét."""
        if not self._is_scanning_mode:
            return

        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))  # Lớp phủ mờ

        if self._is_selecting:
            pen = QPen(QColor("#2ecc71"), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRoundedRect(
                QRect(self._start_pt, self._end_pt).normalized(), 10, 10
            )

    def keyPressEvent(self, event):
        """Xử lý sự kiện nhấn phím."""
        if event.key() == Qt.Key.Key_Escape:
            self._toggle_scan_mode()
            event.accept()
            return

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.overlay_manager.clear_all()
            event.accept()
            return
        
        if event.key() == Qt.Key.Key_Space:
            self._switch_direction()
            event.accept()
            return

        super().keyPressEvent(event)

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
        self.btn_quet_toggle.setText("🔙 Thu nhỏ (Esc)")
        self.btn_help.setVisible(False)
        self.setFocus()
        self.update()

    def _set_compact_mode(self):
        self._is_scanning_mode = False
        self.btn_quet_toggle.setText("🔍 Quét (Esc)")
        self.btn_help.setVisible(True)
        self.panel.adjustSize()
        self.resize(self.panel.size())
        self.move(0, 0)
        self.setFocus()
        self.update()
