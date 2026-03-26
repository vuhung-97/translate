import cv2
import numpy as np
import pytesseract
import os
import re
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

        # 1. Xóa ký tự nhiễu ở biên (thanh dọc, dấu chấm, gạch ngang vô nghĩa)
        text = re.sub(r'^[|I_._-]+|[|I_._-]+$', '', raw_text).strip()
        
        # 2. Loại bỏ khoảng trắng thừa và nối dòng giữa câu
        text = " ".join(text.split())
        
        # 3. Tự động thêm dấu chấm kết thúc nếu thiếu (giúp AI dịch chuẩn hơn)
        if text and not text.endswith(('.', '!', '?', '\"', ':')):
            text += '.'
            
        return text

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
            
        except Exception as e:
            print(f"❌ Critical OCR Error: {e}")
            return ""

# ================================================================
# VÍ DỤ SỬ DỤNG:
# ocr_service = OCRProcessor()
# result = ocr_service.process(my_pil_image, lang="eng")
# ================================================================