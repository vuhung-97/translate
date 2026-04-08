# pylint: disable=no-name-in-module, import-error, too-few-public-methods, no-member
"""
Module này định nghĩa lớp OCRProcessor
Dịch vụ xử lý hình ảnh và nhận diện chữ viết (OCR).
"""

import re
import cv2
import numpy as np
import easyocr
from PIL import Image
from config import EASYOCR_MODEL_DIR

class EasyOCRProcessor:
    """
    Dịch vụ xử lý hình ảnh và nhận diện chữ viết (OCR).
    Sử dụng EasyOCR làm công cụ cốt lõi. direction
    """

    def __init__(self):
        # 1. Cấu hình hệ thống EasyOCR
        self.reader = easyocr.Reader(
			["en", "vi"],
			model_storage_directory=str(EASYOCR_MODEL_DIR),
			download_enabled=False,
		)

    def _prepare_cv2_image(self, pil_img: Image.Image) -> np.ndarray:
        """Chuyển đổi PIL Image sang OpenCV BGR format."""
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    def clean_text_formatting(self, raw_text: str) -> str:
        """Hậu xử lý văn bản thô từ OCR để chuẩn hóa đầu ra."""
        if not raw_text:
            return ""

        # 1. Xóa ký tự nhiễu ở biên (thanh dọc, dấu chấm, gạch ngang, gạch chéo, dấu ngoặc, dấu nháy, v.v.)
        raw_text = re.sub(r'^[|I._/\-~`\[\]{}()<>"\'\\]+|[|I._/\-~`\[\]{}()<>"\'\\]+$', '', raw_text).strip()

        # 2. Loại bỏ các ký tự không phải chữ/câu ở đầu/cuối
        raw_text = re.sub(r'^[^\w\d]+|[^\w\d]+$', '', raw_text, flags=re.UNICODE)

        # 3. Chuẩn hóa khoảng trắng, loại bỏ dòng trống
        raw_text = " ".join(raw_text.split())

        # 4. Thay thế nhiều dấu liên tiếp thành một dấu
        raw_text = re.sub(r'([.!?:;,])\\1+', r'\\1', raw_text)

        # 5. Loại bỏ các ký tự lặp vô nghĩa ở đầu/cuối dòng
        raw_text = re.sub(r'^[\\W_]+|[\\W_]+$', '', raw_text)

        # 6. Tự động thêm dấu chấm kết thúc nếu thiếu (giúp AI dịch chuẩn hơn)
        if raw_text and not raw_text.endswith(('.', '!', '?', '\"', ':')):
            raw_text += '.'

        return raw_text

    def process(self, pil_img: Image.Image, lang: str = "eng") -> str:
        """
        Phương thức chính: Thực hiện toàn bộ quy trình từ ảnh -> chữ chuẩn hóa.
        """
        try:
            # Bước 1: Chuyển đổi và Tiền xử lý
            cv_img = self._prepare_cv2_image(pil_img)

            # Bước 2: Nhận diện bằng EasyOCR
            result = self.run_ocr(cv_img)

            # Bước 3: Hậu xử lý văn bản
            return self.clean_text_formatting(result)

        except (ValueError, RuntimeError) as e:
            print(f"❌ Critical OCR Error: {e}")
            return ""
		
    def run_ocr(self, cv_img):
        try:
            # Đọc ảnh bằng easyocr
            result = self.reader.readtext(cv_img)

            # Gom nội dung thành một câu văn hoàn chỉnh
            merged_text = self._merge_ocr_by_coordinates(result)

            return merged_text
        except Exception as exc:
            return "OCR lỗi" + str(exc)

    def _merge_ocr_by_coordinates(self, result):
        if not result:
            return ""

        items = []
        for box, text, confidence in result:
            clean = text.strip()
            if not clean or confidence < 0.1:
                continue

            xs = [point[0] for point in box]
            ys = [point[1] for point in box]
            x_min = min(xs)
            x_max = max(xs)
            y_min = min(ys)
            y_max = max(ys)
            y_center = (y_min + y_max) / 2.0
            height = max(1.0, y_max - y_min)

            items.append(
                {
                    "text": clean,
                    "x_min": x_min,
                    "x_max": x_max,
                    "y_center": y_center,
                    "height": height,
                }
            )

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