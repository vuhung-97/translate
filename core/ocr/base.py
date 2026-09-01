"""
Định nghĩa Interface/Abstract Base Class cho tất cả các OCR Engines trong hệ thống.
"""

import re
from abc import ABC, abstractmethod
from PIL import Image
import numpy as np
import cv2

class BaseOCREngine(ABC):
    """
    Abstract Base Class đại diện cho một OCR Engine.
    """

    @abstractmethod
    def process(self, pil_img: Image.Image, lang: str = "eng") -> str:
        """
        Nhận vào một PIL Image và mã ngôn ngữ, trả về văn bản đã nhận diện và làm sạch.
        """
        pass

    def _prepare_cv2_image(self, pil_img: Image.Image) -> np.ndarray:
        """Chuyển đổi từ PIL Image sang OpenCV BGR ndarray."""
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    @staticmethod
    def clean_text_formatting(raw_text: str) -> str:
        """
        Hậu xử lý văn bản thô từ OCR để chuẩn hóa dấu câu và loại bỏ ký tự nhiễu.
        """
        if not raw_text:
            return ""

        # 1. Chuẩn hóa dấu câu lặp (!! -> !, ?? -> ?, .... -> ...)
        raw_text = re.sub(r'([!?:;,])\1+', r'\1', raw_text)
        raw_text = re.sub(r'\.{2,}', '...', raw_text)

        # 2. Loại bỏ các ký tự rác không phải Unicode từ/dấu câu
        raw_text = re.sub(r'[^\w .!?:;,\"\'\(\)\[\]\{\}\-]+', '', raw_text, flags=re.UNICODE)

        # 3. Chuẩn hóa khoảng trắng dư thừa
        raw_text = " ".join(raw_text.split())

        # 4. Loại bỏ dấu câu nhiễu ở đầu câu
        raw_text = re.sub(r'^[^\w\"\'\(\[\{\-]+', '', raw_text, flags=re.UNICODE)

        # 5. Loại bỏ dấu câu nhiễu ở cuối câu nhưng GIỮ lại dấu kết thúc câu và dấu đóng ngoặc
        raw_text = re.sub(r'[^\w.!?\"\'\)\]\}]+$', '', raw_text, flags=re.UNICODE)

        # 6. Tự động sửa/thêm dấu chấm nếu câu kết thúc lửng lơ
        raw_text = raw_text.strip()
        if raw_text:
            if not raw_text.endswith(('.', '!', '?', '"', "'", ')', ']', '}')):
                if raw_text.endswith((',', ';', ':')):
                    raw_text = raw_text[:-1] + '.'
                else:
                    raw_text += '.'

        return raw_text
