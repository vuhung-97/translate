# pylint: disable=no-name-in-module, import-error, too-few-public-methods, no-member
"""
Module này định nghĩa lớp OCRProcessor
Dịch vụ xử lý hình ảnh và nhận diện chữ viết (OCR).
"""

import os
import re
import cv2
import numpy as np
import pytesseract
from PIL import Image
from config import TESSERACT_EXE, TESSDATA_DIR

class OCRProcessor:
    """
    Dịch vụ xử lý hình ảnh và nhận diện chữ viết (OCR).
    Sử dụng Tesseract OCR làm công cụ cốt lõi.
    """

    def __init__(self):
        # 1. Cấu hình hệ thống Tesseract
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE
        os.environ['TESSDATA_PREFIX'] = TESSDATA_DIR

        # Cấu hình OCR mặc định: --psm 6 (Coi là 1 khối văn bản thống nhất)
        self.tess_config = '--psm 6'

    def _prepare_cv2_image(self, pil_img: Image.Image) -> np.ndarray:
        """Chuyển đổi PIL Image sang OpenCV BGR format."""
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    def enhance_image(self, cv_img: np.ndarray) -> np.ndarray:
        """
        Quy trình tiền xử lý ảnh để tối ưu hóa nhận diện.
        Gồm: Phóng to -> Thang xám -> Nhị phân hóa (Otsu).
        """
        # 1. Resize x2 giúp chữ rõ nét hơn (Cubic Interpolation)
        img = cv2.resize(cv_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # 2. Chuyển sang Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 3. Khử nhiễu nhẹ (Tùy chọn: giúp loại bỏ hạt nhiễu nhỏ trước khi nhị phân)
        gray = cv2.medianBlur(gray, 3)

        # 4. Otsu Thresholding (Nhị phân hóa)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return thresh

    def clean_text_formatting(self, raw_text: str) -> str:
        """Hậu xử lý văn bản thô từ OCR để chuẩn hóa đầu ra."""
        if not raw_text:
            return ""

        # 1. Xử lý các dấu câu lặp lại
        # Biến các loại !! hoặc !!! thành ! | tương tự với ? : ; ,
        raw_text = re.sub(r'([!?:;,])\1+', r'\1', raw_text)
        # Biến bất kỳ chuỗi dấu chấm nào (.. , .... , .....) thành đúng 3 dấu chấm (...)
        raw_text = re.sub(r'\.{2,}', '...', raw_text)

        # 2. Loại bỏ tất cả ký tự nhiễu
        raw_text = re.sub(r'[^\w .!?:;,\"\'\(\)\[\]\{\}\-]+', '', raw_text, flags=re.UNICODE)
        
        # 3. Chuẩn hóa khoảng trắng trước để các Regex sau không bị sai lệch bởi \n hoặc \t
        raw_text = " ".join(raw_text.split())

        # 4. Loại bỏ dấu câu ở đầu câu (Chỉ giữ lại chữ, số và các dấu mở ngoặc/nháy)
        raw_text = re.sub(r'^[^\w\"\'\(\[\{\-]+', '', raw_text, flags=re.UNICODE)

        # 5. Loại bỏ ký tự nhiễu ở cuối câu nhưng GIỮ lại dấu câu kết thúc và dấu đóng ngoặc
        # Danh sách giữ lại: . ! ? " ' ) ] } 
        raw_text = re.sub(r'[^\w.!?\"\'\)\]\}]+$', '', raw_text, flags=re.UNICODE)

        # 6. Tự động thêm dấu chấm nếu câu kết thúc lửng lơ
        raw_text = raw_text.strip()
        if raw_text:
            # Nếu kết thúc bằng dấu phẩy, dấu hai chấm hoặc không có dấu gì
            if not raw_text.endswith(('.', '!', '?')):
                # Nếu kết thúc bằng dấu câu lửng lơ ( , ; : ), ta thay bằng dấu chấm luôn
                if raw_text.endswith((',', ';', ':')):
                    raw_text = raw_text[:-1] + '.'
                else:
                    raw_text += '.'

        return raw_text

    def process(self, pil_img: Image.Image, lang: str = "eng") -> str:
        """
        Phương thức chính: Thực hiện toàn bộ quy trình từ ảnh -> chữ chuẩn hóa.
        """
        try:
            # Bước 1: Chuyển đổi và Tiền xử lý
            cv_img = self._prepare_cv2_image(pil_img)
            processed_img = self.enhance_image(cv_img)

            # Bước 2: Nhận diện bằng Tesseract
            raw_text = pytesseract.image_to_string(
                processed_img,
                lang=lang,
                config=self.tess_config
            )

            # Bước 3: Hậu xử lý văn bản
            return self.clean_text_formatting(raw_text)

        except (ValueError, RuntimeError) as e:
            print(f"❌ Critical OCR Error: {e}")
            return ""
