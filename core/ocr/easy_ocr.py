"""
EasyOCR Strategy Engine sử dụng thư viện EasyOCR.
"""

import cv2
import numpy as np
from PIL import Image

from core.ocr.base import BaseOCREngine
from config import EASYOCR_MODEL_DIR
from utils.logger import logger
from utils.exceptions import OCRError


class EasyOCREngine(BaseOCREngine):
    """
    OCR Engine thực thi việc nhận diện bằng EasyOCR.
    """

    def __init__(self):
        super().__init__()
        self._reader = None

    def _get_reader(self):
        if self._reader is None:
            import easyocr
            logger.info("Đang nạp mô hình EasyOCR...")
            self._reader = easyocr.Reader(
                ["en", "vi"],
                model_storage_directory=str(EASYOCR_MODEL_DIR),
                download_enabled=False,
            )
            logger.info("Mô hình EasyOCR đã sẵn sàng.")
        return self._reader

    def process(self, pil_img: Image.Image, lang: str = "eng") -> str:
        """
        Nhận diện văn bản từ PIL Image bằng EasyOCR.
        """
        try:
            cv_img = self._prepare_cv2_image(pil_img)
            reader = self._get_reader()
            
            result = reader.readtext(cv_img)
            merged_text = self._merge_text_by_boxes(result)
            cleaned = self.clean_text_formatting(merged_text)
            
            logger.info(f"[EasyOCR] Nhận diện được ({len(cleaned)} chars): '{cleaned[:50]}...'")
            return cleaned

        except Exception as e:
            logger.error(f"[EasyOCR] Lỗi nhận diện chữ: {e}", exc_info=True)
            raise OCRError(f"EasyOCR thất bại: {e}", e)

    def _merge_text_by_boxes(self, result) -> str:
        """Sắp xếp và hợp nhất các box chữ từ EasyOCR theo dòng đọc tự nhiên."""
        if not result:
            return ""

        items = []
        for box, text, confidence in result:
            clean = text.strip()
            if not clean or confidence < 0.1:
                continue

            xs = [point[0] for point in box]
            ys = [point[1] for point in box]
            x_min, x_max = min(xs), max(xs)
            y_min, y_max = min(ys), max(ys)
            y_center = (y_min + y_max) / 2.0
            height = max(1.0, y_max - y_min)

            items.append({
                "text": clean,
                "x_min": x_min,
                "x_max": x_max,
                "y_center": y_center,
                "height": height,
            })

        if not items:
            return ""

        items.sort(key=lambda item: (item["y_center"], item["x_min"]))
        average_height = sum(item["height"] for item in items) / len(items)
        line_gap_threshold = max(10.0, average_height * 0.7)

        lines = []
        for item in items:
            for line in lines:
                if abs(item["y_center"] - line["y_center"]) <= line_gap_threshold:
                    line["items"].append(item)
                    count = len(line["items"])
                    line["y_center"] = ((line["y_center"] * (count - 1)) + item["y_center"]) / count
                    break
            else:
                lines.append({"y_center": item["y_center"], "items": [item]})

        lines.sort(key=lambda line: line["y_center"])

        ordered_parts = []
        for line in lines:
            line_items = sorted(line["items"], key=lambda item: item["x_min"])
            ordered_parts.extend(item["text"] for item in line_items)

        return " ".join(ordered_parts).strip()
