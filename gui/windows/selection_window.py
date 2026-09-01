"""
Cửa sổ lớp phủ toàn màn hình (SelectionOverlayWindow) xử lý việc chọn vùng màn hình cần dịch.
"""

import io
from PIL import Image
from PyQt6.QtCore import Qt, QPoint, QRect, QBuffer, QIODevice, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap
from PyQt6.QtWidgets import QWidget, QApplication

from utils.logger import logger


class SelectionOverlayWindow(QWidget):
    """
    Cửa sổ phủ toàn màn hình hỗ trợ kéo thả chọn vùng dịch (Scan Mode).
    """

    # Signal phát ra khi kéo chọn thành công: (PIL Image, QRect vùng chọn)
    selection_completed = pyqtSignal(object, QRect)
    cancelled = pyqtSignal()
    clear_requested = pyqtSignal()
    direction_switch_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self._is_selecting = False
        self._start_pt = QPoint()
        self._end_pt = QPoint()
        self._snapshot: QPixmap = QPixmap()

    def start_selection(self):
        """Khởi động chế độ quét màn hình."""
        # Chụp ảnh toàn bộ màn hình trước khi hiển thị overlay
        self.setWindowOpacity(0)
        QApplication.processEvents()
        screen = QApplication.primaryScreen()
        if screen:
            self._snapshot = screen.grabWindow(0)
            self.setGeometry(screen.geometry())

        self.setWindowOpacity(1)
        self.showFullScreen()
        self.setFocus()
        self.update()
        logger.info("Khởi chạy SelectionOverlayWindow ở chế độ Full Screen Scan.")

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
                # Cắt ảnh từ snapshot
                cropped_pixmap = self._snapshot.copy(rect)
                buffer = QBuffer()
                buffer.open(QIODevice.OpenModeFlag.ReadWrite)
                cropped_pixmap.save(buffer, "PNG")
                pil_img = Image.open(io.BytesIO(buffer.data()))

                self.close()
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
