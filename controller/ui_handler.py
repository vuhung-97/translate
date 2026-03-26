from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QColor, QPen

# ================================================================
# VẼ GIAO DIỆN & PHÍM TẮT
# ================================================================
class UIHandler:
    """Lớp bổ trợ vẽ khung chọn và phím tắt."""
    def paintEvent(self, event):
        if not self._is_scanning_mode: return
        
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120)) # Lớp phủ mờ
        
        if self._is_selecting:
            pen = QPen(QColor("#2ecc71"), 2, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRoundedRect(QRect(self._start_pt, self._end_pt).normalized(), 10, 10)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self._toggle_scan_mode()
            event.accept()
            return

        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.overlay_manager.clear_all()
            event.accept()
            return

        super().keyPressEvent(event)