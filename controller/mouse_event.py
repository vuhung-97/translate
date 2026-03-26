import io
from PIL import Image
from PyQt5.QtCore import QRect, QBuffer, QIODevice

# ================================================================
# XỬ LÝ SỰ KIỆN CHUỘT
# ================================================================
class MouseEvent:
    """Lớp bổ trợ xử lý di chuyển và quét vùng chọn."""
    def mousePressEvent(self, event):
        if self._is_scanning_mode and not self.panel.geometry().contains(event.pos()):
            self._is_selecting = True
            self._start_pt = event.pos()
            self._end_pt = event.pos()
        else:
            self._drag_offset = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        if self._is_selecting:
            self._end_pt = event.pos()
            self.update()
        elif self._drag_offset:
            self.move(event.globalPos() - self._drag_offset)

    def mouseReleaseEvent(self, event):
        if self._is_selecting:
            self._is_selecting = False
            self._handle_selection_done()
        self._drag_offset = None

    def _handle_selection_done(self):
        rect = QRect(self._start_pt, self._end_pt).normalized()
        if rect.width() < 10 or rect.height() < 10: return

        # 1. Cắt ảnh từ snapshot
        buffer = QBuffer()
        buffer.open(QIODevice.ReadWrite)
        self._snapshot.copy(rect).save(buffer, "PNG")
        pil_img = Image.open(io.BytesIO(buffer.data()))

        # 2. Tạo khung hiển thị qua OverlayManager
        target_label = self.overlay_manager.create_result_box(
            rect, self._trans_settings.get('font_size', 12)
        )

        # 3. Yêu cầu TranslationService xử lý
        self.trans_service.process_image(pil_img, target_label)