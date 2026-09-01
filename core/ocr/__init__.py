"""
Package core.ocr cung cấp kiến trúc Strategy Pattern cho các OCR Engine khác nhau.
"""

from core.ocr.base import BaseOCREngine
from core.ocr.tesseract_ocr import TesseractOCREngine
from core.ocr.easy_ocr import EasyOCREngine
from core.ocr.factory import OCRFactory

__all__ = ["BaseOCREngine", "TesseractOCREngine", "EasyOCREngine", "OCRFactory"]
