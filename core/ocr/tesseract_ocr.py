"""
Tesseract OCR Strategy Engine sử dụng pytesseract và OpenCV.
"""

import os
import cv2
import numpy as np
import pytesseract
from PIL import Image

from core.ocr.base import BaseOCREngine
from config import TESSERACT_EXE, TESSDATA_DIR
from utils.logger import logger
from utils.exceptions import OCRError


class TesseractOCREngine(BaseOCREngine):
    """
    OCR Engine thực thi việc nhận diện bằng Tesseract OCR.
    """

    def __init__(self):
        super().__init__()
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE
        os.environ['TESSDATA_PREFIX'] = TESSDATA_DIR
        self.tess_config = '--psm 6'

    def enhance_image(self, cv_img: np.ndarray) -> np.ndarray:
        """
        Quy trình tiền xử lý ảnh thích ứng (Adaptive Image Enhancement).
        Phóng to ảnh nếu quá nhỏ -> Thang xám -> Khử nhiễu -> Nhị phân hóa Otsu.
        """
        h, w = cv_img.shape[:2]
        
        # Chỉ resize x2 nếu kích thước chiều cao hoặc rộng quá nhỏ (< 300px)
        if h < 300 or w < 300:
            cv_img = cv2.resize(cv_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.medianBlur(gray, 3)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return thresh

    def process(self, pil_img: Image.Image, lang: str = "eng") -> str:
        """
        Nhận diện văn bản từ PIL Image bằng Tesseract.
        """
        try:
            cv_img = self._prepare_cv2_image(pil_img)
            processed_img = self.enhance_image(cv_img)

            # Map mã ngôn ngữ nếu cần ('eng', 'vie')
            tess_lang = "vie" if lang in ("vi", "vie") else "eng"

            raw_text = pytesseract.image_to_string(
                processed_img,
                lang=tess_lang,
                config=self.tess_config
            )

            cleaned = self.clean_text_formatting(raw_text)
            logger.info(f"[TesseractOCR] Nhận diện được ({len(cleaned)} chars): '{cleaned[:50]}...'")
            return cleaned

        except Exception as e:
            logger.error(f"[TesseractOCR] Lỗi nhận diện chữ: {e}", exc_info=True)
            raise OCRError(f"Tesseract OCR thất bại: {e}", e)
