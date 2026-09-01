"""
Wrapper tương thích ngược cho EasyOCRProcessor sử dụng EasyOCREngine từ core/ocr.
"""

from core.ocr.easy_ocr import EasyOCREngine

class EasyOCRProcessor(EasyOCREngine):
    """Lớp wrapper tương thích ngược cho EasyOCRProcessor cũ."""
    pass
