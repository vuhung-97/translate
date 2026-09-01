"""
Unit tests cho quy trình làm sạch văn bản OCR và OCR Factory.
"""

import unittest
from core.ocr.base import BaseOCREngine
from core.ocr.factory import OCRFactory
from core.ocr.tesseract_ocr import TesseractOCREngine
from core.ocr.easy_ocr import EasyOCREngine


class TestOCR(unittest.TestCase):

    def test_clean_text_formatting(self):
        # 1. Dấu câu lặp lại
        raw = "Hello world!!!! How are you???"
        cleaned = BaseOCREngine.clean_text_formatting(raw)
        self.assertEqual(cleaned, "Hello world! How are you?")

        # 2. Khoảng trắng thừa và ký tự nhiễu
        raw = "  This   is a test...   "
        cleaned = BaseOCREngine.clean_text_formatting(raw)
        self.assertEqual(cleaned, "This is a test...")

        # 3. Tự động thêm dấu chấm nếu lửng lơ
        raw = "Hello world"
        cleaned = BaseOCREngine.clean_text_formatting(raw)
        self.assertEqual(cleaned, "Hello world.")

    def test_ocr_factory(self):
        tess_engine = OCRFactory.get_engine("tesseract")
        self.assertIsInstance(tess_engine, TesseractOCREngine)

        easy_engine = OCRFactory.get_engine("easyocr")
        self.assertIsInstance(easy_engine, EasyOCREngine)


if __name__ == "__main__":
    unittest.main()
