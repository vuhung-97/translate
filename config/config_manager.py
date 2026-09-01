"""
Quản lý cấu hình toàn bộ ứng dụng SmartTranslator theo mẫu thiết kế Singleton.
Đảm bảo type-safe với Dataclass và cung cấp khả năng tự động nạp/lưu cài đặt.
"""

import json
import os
import sys
from dataclasses import dataclass, asdict, fields
from typing import Dict, Any, Optional

from utils.logger import logger
from utils.path_manager import PathManager
from utils.exceptions import ConfigError

# Khởi tạo môi trường hệ thống
THREADS_COUNT = "4"
IS_WINDOWS = sys.platform == "win32"

def _initialize_environment():
    """Đóng gói các thiết lập biến môi trường."""
    os.environ["OMP_NUM_THREADS"] = THREADS_COUNT
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    os.environ["KMP_INIT_AT_FORK"] = "FALSE"

    if IS_WINDOWS and hasattr(sys, "_MEIPASS"):
        try:
            os.add_dll_directory(getattr(sys, "_MEIPASS"))
        except (AttributeError, OSError):
            pass

_initialize_environment()


@dataclass
class TranslationSettings:
    """Dataclass đóng gói toàn bộ thông số cấu hình ứng dụng."""
    direction: str = "en-vi"
    ocr_engine: str = "tesseract"  # 'tesseract' hoặc 'easyocr'
    beam_size: int = 5
    repetition_penalty: float = 1.5
    no_repeat_ngram_size: int = 3
    max_decoding_length: int = 256
    font_size: int = 17
    theme: str = "Sáng"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TranslationSettings":
        valid_keys = {f.name for f in fields(cls)}
        filtered_data = {}
        for k, v in data.items():
            # Chuẩn hóa nếu key bắt đầu bằng dấu gạch dưới (từ bản cũ _direction)
            clean_k = k.lstrip("_")
            if clean_k in valid_keys:
                filtered_data[clean_k] = v
        return cls(**filtered_data)


class ConfigManager:
    """
    Singleton Class quản lý cấu hình và đường dẫn tài nguyên.
    """
    _instance: Optional["ConfigManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        # 1. Đường dẫn hằng số hệ thống
        self.MODEL_DIR = PathManager.get_path(os.path.join("models", "model_envit5_fast"))
        self.TESSERACT_DIR = PathManager.get_path(os.path.join("bin", "Tesseract-OCR"))
        self.HELP_DIALOG_DIR = PathManager.get_path("gui")
        self.TESSDATA_DIR = os.path.join(self.TESSERACT_DIR, "tessdata")
        self.TESSERACT_EXE = os.path.join(self.TESSERACT_DIR, "tesseract.exe")
        self.HELP_DIALOG_HTML = os.path.join(self.HELP_DIALOG_DIR, "help.html")
        self.ICON_PATH = PathManager.get_path(os.path.join("resources", "app_icon.ico"))
        self.EASYOCR_MODEL_DIR = PathManager.get_path(os.path.join("models", ".EasyOCR", "model"))
        
        self.SETTINGS_JSON_PATH = PathManager.get_user_data_path("settings.json")
        
        # 2. Nạp cài đặt
        self.default_settings = TranslationSettings()
        self._settings = self._load_settings()
        logger.info("ConfigManager đã khởi tạo thành công.")

    def _load_settings(self) -> TranslationSettings:
        """Đọc cài đặt từ file settings.json, nếu lỗi/không có thì dùng mặc định."""
        if os.path.exists(self.SETTINGS_JSON_PATH):
            try:
                with open(self.SETTINGS_JSON_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                logger.info(f"Đã nạp file cấu hình từ {self.SETTINGS_JSON_PATH}")
                return TranslationSettings.from_dict(data)
            except Exception as e:
                logger.error(f"Lỗi khi đọc file settings.json: {e}. Sử dụng mặc định.")
        return TranslationSettings()

    def save_settings(self, new_data: Optional[Dict[str, Any]] = None):
        """Cập nhật và ghi cấu hình xuống file JSON."""
        if new_data:
            updated_dict = self._settings.to_dict()
            updated_dict.update(new_data)
            self._settings = TranslationSettings.from_dict(updated_dict)

        try:
            with open(self.SETTINGS_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(self._settings.to_dict(), f, ensure_ascii=False, indent=4)
            logger.info("Đã ghi thành công cấu hình vào settings.json")
        except Exception as e:
            logger.error(f"Lỗi khi lưu cài đặt: {e}")
            raise ConfigError(f"Không thể lưu settings: {e}", e)

    def reset_to_defaults(self):
        """Khôi phục cấu hình về mặc định."""
        self._settings = TranslationSettings()
        self.save_settings()

    @property
    def settings(self) -> TranslationSettings:
        return self._settings

    # Các hàm hỗ trợ dict-like interface tương thích ngược
    def get(self, key: str, default: Any = None) -> Any:
        d = self._settings.to_dict()
        return d.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self._settings.to_dict()[key]

    def __setitem__(self, key: str, value: Any):
        current = self._settings.to_dict()
        current[key] = value
        self._settings = TranslationSettings.from_dict(current)

    def update(self, data: Dict[str, Any]):
        self.save_settings(data)

# Singleton global instance
config_manager = ConfigManager()
