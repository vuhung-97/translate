"""
Module định nghĩa TranslationService.
Điều phối quy trình Ảnh -> OCR -> AI Translation -> Cập nhật UI.
"""

from PyQt6.QtCore import pyqtSignal, QObject
from PIL import Image

from core.ocr.factory import OCRFactory
from core.translation_worker import TranslationResult, TranslationWorker
from utils.logger import logger


class TranslationService(QObject):
    """
    Service điều phối quy trình dịch thuật từ hình ảnh tới văn bản hoàn chỉnh.
    """
    translation_ready = pyqtSignal(str, object)

    def __init__(self, config_or_settings):
        super().__init__()
        self.settings = config_or_settings
        self._active_workers = []

    def process_image(self, pil_img: Image.Image, target_label):
        """
        Thực hiện OCR dựa theo OCR Engine được cấu hình và bắt đầu luồng dịch AI.
        """
        try:
            # 1. Lấy OCR Engine từ Factory dựa trên settings hiện tại
            ocr_engine_name = self.settings.get("ocr_engine", "tesseract")
            ocr_engine = OCRFactory.get_engine(ocr_engine_name)

            direction = self.settings.get("direction", "en-vi")
            lang = "vie" if direction == "vi-en" else "eng"

            # 2. Chạy OCR nhận diện chữ
            text = ocr_engine.process(pil_img, lang=lang)

            if text and text.strip():
                self._start_worker(text, target_label)
            else:
                logger.info("OCR không nhận diện được chữ nào trong ảnh.")
                target_label.setText("Không tìm thấy chữ!")

        except Exception as e:
            logger.error(f"Lỗi trong quá trình xử lý ảnh Dịch thuật: {e}", exc_info=True)
            target_label.setText(f"⚠️ Lỗi OCR: {e}")

    def _start_worker(self, text: str, target_label):
        """Khởi động QThread dịch thuật trong nền."""
        result = TranslationResult(text=text, x=0, y=0, width=0)
        
        # Lấy dict settings
        settings_dict = self.settings.settings.to_dict() if hasattr(self.settings, "settings") else self.settings
        
        worker = TranslationWorker(result, settings_dict)
        worker.finished.connect(lambda res_text, _x, _y, _w: target_label.setText(res_text))
        worker.finished.connect(lambda _res, _x, _y, _w: self._cleanup_worker(worker))
        
        self._active_workers.append(worker)
        worker.start()

    def _cleanup_worker(self, worker):
        if worker in self._active_workers:
            self._active_workers.remove(worker)
