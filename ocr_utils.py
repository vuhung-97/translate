import cv2
import numpy as np
import pytesseract
import os
import re
from typing import Optional
from config import TESSERACT_FOLDER # Đảm bảo file config.py có định nghĩa này

# ================================================================
# 1. CẤU HÌNH HỆ THỐNG TESSERACT
# ================================================================

# Chỉ định đường dẫn tệp thực thi tesseract.exe
pytesseract.pytesseract.tesseract_cmd = os.path.join(TESSERACT_FOLDER, "tesseract.exe")

# Thiết lập biến môi trường để Tesseract tìm thấy thư mục chứa dữ liệu ngôn ngữ (tessdata)
os.environ['TESSDATA_PREFIX'] = os.path.join(TESSERACT_FOLDER, "tessdata")


# ================================================================
# 2. XỬ LÝ HÌNH ẢNH (IMAGE PRE-PROCESSING)
# ================================================================

def clean_image_for_ocr(pil_img: object) -> np.ndarray:
    """
    Tiền xử lý hình ảnh để tăng độ chính xác cho việc nhận diện văn bản.
    
    Quy trình: 
    PIL Image -> OpenCV BGR -> Resize x2 -> Grayscale -> Otsu Thresholding (Nhị phân)
    """
    # Chuyển đổi từ định dạng PIL Image sang mảng NumPy (OpenCV BGR)
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    # Phóng to ảnh gấp 2 lần giúp các nét chữ nhỏ trở nên rõ ràng hơn
    # Sử dụng phép nội suy Cubic để giữ độ sắc nét khi phóng to
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    # Chuyển ảnh về thang màu xám
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Áp dụng thuật toán Otsu's Thresholding để chuyển ảnh về nhị phân (Đen/Trắng tuyệt đối)
    # Giúp loại bỏ các bóng mờ và làm nổi bật hẳn nét chữ khỏi nền
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return thresh


# ================================================================
# 3. NHẬN DIỆN VĂN BẢN (OCR CORE)
# ================================================================

def perform_ocr(processed_img: np.ndarray, lang: str = "eng") -> str:
    """
    Thực hiện quét chữ từ hình ảnh và xử lý nhiễu văn bản đầu ra.
    
    Args:
        processed_img: Ảnh đã qua xử lý nhị phân.
        lang: Mã ngôn ngữ ('eng' cho tiếng Anh, 'vie' cho tiếng Việt).
    """
    try:
        # 1. Gọi Tesseract thực hiện nhận diện văn bản
        # --psm 6: Coi vùng ảnh là một khối văn bản duy nhất (phù hợp cho câu/đoạn văn)
        raw_text = pytesseract.image_to_string(
            processed_img, 
            lang=lang, 
            config='--psm 6'
        ).strip()
        
        # 2. Hậu xử lý: Xóa nhiễu ký tự lạ ở biên
        # Xóa các ký tự thường bị nhận nhầm từ đường viền vùng chọn như | I _ . -
        noise_cleaned = re.sub(r'^[|I_._-]+|[|I_._-]+$', '', raw_text).strip()
        
        # 3. Chuẩn hóa văn bản: Xóa khoảng trắng thừa và xuống dòng giữa câu
        clean_text = " ".join(noise_cleaned.split())
        
        # 4. Kiểm tra và bổ sung dấu kết thúc câu nếu thiếu giúp AI dịch mượt hơn
        if clean_text and not clean_text.endswith(('.', '!', '?', '\"', ':')): 
            clean_text += '.'
            
        return clean_text
        
    except Exception as e:
        print(f"❌ Lỗi hệ thống OCR: {e}")
        return ""