"""
OCRFactory cung cấp phương thức tạo và lấy OCR Engine phù hợp theo cấu hình.
"""

from typing import Dict
from core.ocr.base import BaseOCREngine
from core.ocr.tesseract_ocr import TesseractOCREngine
from core.ocr.easy_ocr import EasyOCREngine
from config import SETTINGS
from utils.logger import logger

class OCRFactory:
    """
    Factory Class khởi tạo và quản lý các thể hiện của OCR Engine (Strategy Pattern).
    """

    _instances: Dict[str, BaseOCREngine] = {}

    @classmethod
    def get_engine(cls, engine_name: str = None) -> BaseOCREngine:
        """
        Lấy instance của OCR Engine theo tên ('tesseract' hoặc 'easyocr').
        Nếu không truyền tên, sẽ lấy từ cấu hình mặc định trong SETTINGS.
        """
        if engine_name is None:
            engine_name = SETTINGS.get("ocr_engine", "tesseract").lower()

        engine_name = engine_name.lower().strip()

        if engine_name not in cls._instances:
            if engine_name == "easyocr":
                logger.info("OCRFactory khởi tạo EasyOCREngine")
                cls._instances[engine_name] = EasyOCREngine()
            else:
                logger.info("OCRFactory khởi tạo TesseractOCREngine")
                cls._instances[engine_name] = TesseractOCREngine()

        return cls._instances[engine_name]
