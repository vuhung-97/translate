"""
Wrapper tương thích ngược cho OCRProcessor sử dụng TesseractOCREngine từ core/ocr.
"""

from core.ocr.tesseract_ocr import TesseractOCREngine

class OCRProcessor(TesseractOCREngine):
    """Lớp wrapper tương thích ngược cho OCRProcessor cũ."""
    pass
