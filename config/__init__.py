"""
Package config quản lý cấu hình hệ thống và tùy chọn người dùng.
Export các thành phần hằng số và ConfigManager cho toàn bộ ứng dụng.
"""

from config.config_manager import (
    config_manager,
    TranslationSettings,
    THREADS_COUNT,
    IS_WINDOWS,
)

# Export hằng số đường dẫn
MODEL_DIR = config_manager.MODEL_DIR
TESSERACT_DIR = config_manager.TESSERACT_DIR
HELP_DIALOG_DIR = config_manager.HELP_DIALOG_DIR
TESSDATA_DIR = config_manager.TESSDATA_DIR
TESSERACT_EXE = config_manager.TESSERACT_EXE
HELP_DIALOG_HTML = config_manager.HELP_DIALOG_HTML
ICON_PATH = config_manager.ICON_PATH
EASYOCR_MODEL_DIR = config_manager.EASYOCR_MODEL_DIR
SETTINGS_JSON_PATH = config_manager.SETTINGS_JSON_PATH

DEFAULT_SETTINGS = TranslationSettings().to_dict()
SETTINGS = config_manager

def save_settings(settings: dict, path: str = SETTINGS_JSON_PATH):
    config_manager.save_settings(settings)

def load_settings(path: str = SETTINGS_JSON_PATH) -> dict:
    return config_manager.settings.to_dict()

def reset_settings(path: str = SETTINGS_JSON_PATH):
    config_manager.reset_to_defaults()
