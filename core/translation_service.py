from PyQt5.QtCore import pyqtSignal, QObject

# Các import từ dự án (giữ nguyên)
from core.ocr_utils import clean_image_for_ocr, perform_ocr
from core.engine import TranslationWorker
# ================================================================
# 1. DỊCH THUẬT & OCR (LOGIC LAYER)
# ================================================================
class TranslationService(QObject):
    """Chuyên xử lý logic chuyển đổi từ Ảnh -> Chữ -> Bản dịch."""
    translation_ready = pyqtSignal(str, object)  # Trả về (văn bản dịch, label cần cập nhật)

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self._active_workers = []

    def process_image(self, pil_img, target_label):
        """Thực hiện OCR và bắt đầu luồng dịch."""
        processed = clean_image_for_ocr(pil_img)
        lang = 'vie' if self.settings.get('direction') == 'vi-en' else 'eng'
        text = perform_ocr(processed, lang=lang)

        if text.strip():
            self._start_worker(text, target_label)
        else:
            target_label.setText("Không tìm thấy chữ!")

    def _start_worker(self, text, target_label):
        worker = TranslationWorker(text, 0, 0, 0, self.settings)
        worker.finished.connect(lambda result, _x, _y, _w: target_label.setText(result))
        worker.finished.connect(lambda _result, _x, _y, _w: self._cleanup_worker(worker))
        self._active_workers.append(worker)
        worker.start()

    def _cleanup_worker(self, worker):
        if worker in self._active_workers:
            self._active_workers.remove(worker)
