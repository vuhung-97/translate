# config.py
import os
import sys

# ================================================================
# 1. CẤU HÌNH HỆ THỐNG & MÔI TRƯỜNG
# ================================================================
# Tối ưu số luồng xử lý cho CPU (Phù hợp với đa số máy tính cá nhân)
os.environ["OMP_NUM_THREADS"] = "4"
# Xử lý lỗi xung đột thư viện Libiomp5md.dll trên Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# Ngăn chặn lỗi khởi tạo luồng khi chạy đa nhiệm
os.environ["KMP_INIT_AT_FORK"] = "FALSE"

# Hỗ trợ nạp DLL khi đóng gói bằng PyInstaller
if hasattr(sys, '_MEIPASS'):
    try:
        os.add_dll_directory(sys._MEIPASS)
    except Exception:
        pass

# ================================================================
# 2. QUẢN LÝ ĐƯỜNG DẪN TÀI NGUYÊN (RESOURCE PATHS)
# ================================================================
def get_resource_path(relative_path):
    """
    Xác định đường dẫn tuyệt đối đến tài nguyên.
    Hỗ trợ cả môi trường phát triển (Dev) và khi đã đóng gói (EXE).
    """
    if hasattr(sys, '_MEIPASS'):
        # Đường dẫn thư mục tạm khi chạy file EXE
        return os.path.join(sys._MEIPASS, relative_path)
    # Đường dẫn thư mục gốc khi chạy file .py
    return os.path.join(os.path.abspath("."), relative_path)

# --- Đường dẫn các thành phần chính ---
# Thư mục chứa bộ não AI EnViT5 (Định dạng CTranslate2)
MODEL_DIR = get_resource_path("model_envit5_fast")

# Thư mục chứa công cụ quét chữ Tesseract OCR
TESSERACT_FOLDER = get_resource_path("Tesseract-OCR")

# Thư mục chứa dữ liệu ngôn ngữ (eng.traineddata, vie.traineddata)
TESSDATA_DIR = os.path.join(TESSERACT_FOLDER, "tessdata")

# Đường dẫn đến file thực thi của Tesseract
TESSERACT_EXE = os.path.join(TESSERACT_FOLDER, "tesseract.exe")

# ================================================================
# 3. CẤU HÌNH MẶC ĐỊNH (DEFAULT SETTINGS)
# ================================================================
DEFAULT_SETTINGS = {
    'direction': 'en-vi',             # Chiều dịch mặc định: Anh -> Việt
    'beam_size': 2,                  # Độ sâu tìm kiếm của AI
    'repetition_penalty': 1.5,       # Phạt lặp từ (ngăn AI bị quẩn)
    'no_repeat_ngram_size': 3,       # Ngăn lặp cụm 3 từ
    'max_decoding_length': 256,      # Độ dài tối đa câu dịch
    'font_size': 14,                 # Kích thước chữ hiển thị
    'theme': 'Tối'                   # Giao diện kết quả
}