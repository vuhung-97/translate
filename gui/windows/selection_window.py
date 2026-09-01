"""
Cửa sổ lớp phủ toàn màn hình (SelectionOverlayWindow) xử lý việc chọn vùng màn hình cần dịch.
Hỗ trợ High-DPI Scaling, Đa màn hình (Multi-Monitor) và giữ nguyên lớp phủ mờ khi khoanh vùng xong.
"""

import io
from PIL import Image
from PyQt6.QtCore import Qt, QPoint, QRect, QBuffer, QIODevice, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap, QCursor, QGuiApplication
from PyQt6.QtWidgets import QWidget, QApplication

from utils.logger import logger


class SelectionOverlayWindow(QWidget):
    """
    Cửa sổ phủ toàn màn hình hỗ trợ kéo thả chọn vùng dịch (Scan Mode).
    """

    # Signals
    selection_completed = pyqtSignal(object, QRect)
    cancelled = pyqtSignal()
    clear_requested = pyqtSignal()
    direction_switch_requested = pyqtSignal()

    def __init__(self, toolbar_rect_provider=None):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.toolbar_rect_provider = toolbar_rect_provider
        self._is_selecting = False
        self._start_pt = QPoint()
        self._end_pt = QPoint()
        self._snapshot: QPixmap = QPixmap()
        self._screen_rect: QRect = QRect()

    def start_selection(self):
        """Khởi động chế độ quét màn hình thích ứng Đa màn hình (Multi-Monitor)."""
        cursor_pos = QCursor.pos()
        screen = QGuiApplication.screenAt(cursor_pos) or QGuiApplication.primaryScreen()
        
        if screen:
            self._screen_rect = screen.geometry()
            self.setGeometry(self._screen_rect)
            
            self.setWindowOpacity(0)
            QApplication.processEvents()
            
            # Chụp ảnh snapshot màn hình hiện tại
            self._snapshot = screen.grabWindow(0)
            logger.info(f"Đã chụp snapshot màn hình '{screen.name()}' size={self._snapshot.width()}x{self._snapshot.height()}")

        self.setWindowOpacity(1)
        self.showFullScreen()
        self.setFocus()
        self.update()

    def paintEvent(self, event):
        """Vẽ lớp phủ mờ và khung chọn nét đứt."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))  # Lớp phủ mờ

        if self._is_selecting:
            pen = QPen(QColor("#2ecc71"), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRoundedRect(
                QRect(self._start_pt, self._end_pt).normalized(), 8, 8
            )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Nếu vị trí click nằm trong vùng Toolbar Window thì không chọn
            if self.toolbar_rect_provider:
                toolbar_rect = self.toolbar_rect_provider()
                if toolbar_rect.contains(event.globalPosition().toPoint()):
                    return

            self._is_selecting = True
            self._start_pt = event.pos()
            self._end_pt = event.pos()
            self.update()

    def mouseMoveEvent(self, event):
        if self._is_selecting:
            self._end_pt = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._is_selecting:
            self._is_selecting = False
            rect = QRect(self._start_pt, self._end_pt).normalized()
            
            if rect.width() >= 10 and rect.height() >= 10 and not self._snapshot.isNull():
                # Xử lý tỉ lệ High DPI Scaling nếu có
                dpr = self.devicePixelRatio()
                crop_rect = QRect(
                    int(rect.x() * dpr),
                    int(rect.y() * dpr),
                    int(rect.width() * dpr),
                    int(rect.height() * dpr)
                )

                cropped_pixmap = self._snapshot.copy(crop_rect)
                buffer = QBuffer()
                buffer.open(QIODevice.OpenModeFlag.ReadWrite)
                cropped_pixmap.save(buffer, "PNG")
                raw_bytes = bytes(buffer.data())
                buffer.close()

                # KHÓA CỨNG ĐIỂM ẢNH TRONG BỘ NHỚ RAM TRÁNH LAZY LOADING CỦA PIL
                pil_img = Image.open(io.BytesIO(raw_bytes)).convert("RGB").copy()

                # Giữ nguyên SelectionOverlayWindow (không đóng tự động)
                self.update()
                self.selection_completed.emit(pil_img, rect)
            else:
                self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            self.cancelled.emit()
            event.accept()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.clear_requested.emit()
            event.accept()
        elif event.key() == Qt.Key.Key_Space:
            self.direction_switch_requested.emit()
            event.accept()
        else:
            super().keyPressEvent(event)
