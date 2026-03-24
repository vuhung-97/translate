import os
import sys
from dataclasses import dataclass, asdict
from typing import Dict, Any

# ================================================================
# 1. HẰNG SỐ HỆ THỐNG (SYSTEM CONSTANTS)
# ================================================================
# Tách các giá trị cấu hình môi trường ra khỏi logic thực thi
THREADS_COUNT = "4"
IS_WINDOWS = sys.platform == "win32"

def _initialize_environment():
    """Extract Method: Đóng gói các thiết lập biến môi trường."""
    os.environ["OMP_NUM_THREADS"] = THREADS_COUNT
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    os.environ["KMP_INIT_AT_FORK"] = "FALSE"
    
    if IS_WINDOWS and hasattr(sys, '_MEIPASS'):
        try:
            os.add_dll_directory(sys._MEIPASS)
        except (AttributeError, OSError):
            pass

_initialize_environment()

# ================================================================
# 2. LỚP QUẢN LÝ ĐƯỜNG DẪN (PATH MANAGER)
# ================================================================
class PathManager:
    """
    Đóng gói logic xác định đường dẫn tài nguyên.
    Hỗ trợ cả môi trường Dev và EXE (PyInstaller).
    """
    @staticmethod
    def get_path(relative_path: str) -> str:
        # Sử dụng thuộc tính _MEIPASS nếu chạy từ file đóng gói
        base = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base, relative_path)

# Các hằng số đường dẫn được định nghĩa tập trung
MODEL_DIR = PathManager.get_path("models/model_envit5_fast")
TESSERACT_DIR = PathManager.get_path("bin/Tesseract-OCR")
HELP_DIALOG_DIR = PathManager.get_path("gui")

TESSDATA_DIR = os.path.join(TESSERACT_DIR, "tessdata")
TESSERACT_EXE = os.path.join(TESSERACT_DIR, "tesseract.exe")
HELP_DIALOG_HTML = os.path.join(HELP_DIALOG_DIR, "help.html")

# ================================================================
# 3. ĐỐI TƯỢNG CẤU HÌNH (APP SETTINGS)
# ================================================================
@dataclass
class TranslationSettings:
    """
    Thay thế Dictionary bằng Dataclass để có gợi ý code và kiểm soát kiểu dữ liệu.
    Giải quyết Bad Smell: Data Clump (Nhóm dữ liệu rời rạc).
    """
    direction: str = 'en-vi'
    beam_size: int = 2
    repetition_penalty: float = 1.5
    no_repeat_ngram_size: int = 3
    max_decoding_length: int = 256
    font_size: int = 14
    theme: str = 'Tối'

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

# Tạo một instance mặc định
DEFAULT_SETTINGS = TranslationSettings().to_dict()