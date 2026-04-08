# pylint: disable=missing-module-docstring, too-few-public-methods
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

    if IS_WINDOWS and hasattr(sys, "_MEIPASS"):
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
        """Lấy đường dẫn tuyệt đối từ đường dẫn tương đối."""
        base = getattr(sys, "_MEIPASS", os.path.abspath("."))
        return os.path.join(base, relative_path)


# Các hằng số đường dẫn được định nghĩa tập trung
MODEL_DIR = PathManager.get_path("models\\model_envit5_fast")
TESSERACT_DIR = PathManager.get_path("bin\\Tesseract-OCR")
HELP_DIALOG_DIR = PathManager.get_path("gui")

TESSDATA_DIR = os.path.join(TESSERACT_DIR, "tessdata")
TESSERACT_EXE = os.path.join(TESSERACT_DIR, "tesseract.exe")
HELP_DIALOG_HTML = os.path.join(HELP_DIALOG_DIR, "help.html")
ICON_PATH = PathManager.get_path("resources/app_icon.ico")

EASYOCR_MODEL_DIR = PathManager.get_path("models\\.EasyOCR\\model") 

import json

# ================================================================
# 3. ĐỐI TƯỢNG CẤU HÌNH (APP SETTINGS)
# ================================================================
@dataclass
class TranslationSettings:
    """
    Thay thế Dictionary bằng Dataclass để có gợi ý code và kiểm soát kiểu dữ liệu.
    """

    _direction: str = "en-vi"
    _beam_size: int = 5
    _repetition_penalty: float = 1.5
    _no_repeat_ngram_size: int = 3
    _max_decoding_length: int = 256
    _font_size: int = 17
    _theme: str = "Sáng"

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi dataclass thành dictionary."""
        results = {
            "direction": self._direction,
            "beam_size": self._beam_size,
            "repetition_penalty": self._repetition_penalty,
            "no_repeat_ngram_size": self._no_repeat_ngram_size,
            "max_decoding_length": self._max_decoding_length,
            "font_size": self._font_size,
            "theme": self._theme,
        }
        return results

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Tạo instance từ dictionary."""
        return cls(
            _direction=data.get("direction", "en-vi"),
            _beam_size=data.get("beam_size", 5),
            _repetition_penalty=data.get("repetition_penalty", 1.5),
            _no_repeat_ngram_size=data.get("no_repeat_ngram_size", 3),
            _max_decoding_length=data.get("max_decoding_length", 256),
            _font_size=data.get("font_size", 17),
            _theme=data.get("theme", "Sáng"),
        )


# Đường dẫn file settings.json
SETTINGS_JSON_PATH = PathManager.get_path("settings.json")

DEFAULT_SETTINGS = TranslationSettings().to_dict()


def save_settings(settings: Dict[str, Any], path: str = SETTINGS_JSON_PATH):
    """Lưu cài đặt vào file JSON."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Lỗi khi lưu settings: {e}")

def load_settings(path: str = SETTINGS_JSON_PATH) -> Dict[str, Any]:
    """Đọc cài đặt từ file JSON, nếu không có thì trả về mặc định."""
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return TranslationSettings.from_dict(data).to_dict()
        except Exception as e:
            print(f"Lỗi khi đọc settings: {e}")
    return DEFAULT_SETTINGS.copy()

def reset_settings(path: str = SETTINGS_JSON_PATH):
    """Đặt lại cài đặt về mặc định và lưu vào file JSON."""
    save_settings(DEFAULT_SETTINGS, path)


# Tạo một instance mặc định để sử dụng trong toàn bộ ứng dụng
SETTINGS = load_settings()
