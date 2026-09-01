"""
TranslationWorker xử lý tác vụ dịch thuật bất đồng bộ trên luồng QThread phụ.
Giúp giữ cho giao diện PyQt6 mượt mà không bị treo/đóng băng khi AI đang suy luận.
"""

from dataclasses import dataclass
from typing import Dict, Any
from PyQt6.QtCore import QThread, pyqtSignal

from core.translation_engine import ai_engine, EnViT5Engine
from utils.logger import logger
from utils.exceptions import TranslationError


@dataclass
class TranslationResult:
    """Đóng gói dữ liệu văn bản nhận diện cùng tọa độ hiển thị."""
    text: str
    x: int = 0
    y: int = 0
    width: int = 0


class TranslationWorker(QThread):
    """
    Luồng phụ thực thi suy luận mô hình AI trong nền.
    """

    # Signal phát ra khi hoàn thành: (kết quả dịch, x, y, width)
    finished = pyqtSignal(str, int, int, int)
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        result: TranslationResult,
        settings: Dict[str, Any],
        engine: EnViT5Engine = ai_engine,
        parent=None
    ):
        super().__init__(parent)
        self.result = result
        self.settings = settings
        self.engine = engine

    def run(self):
        """Thực thi dịch thuật trong luồng phụ QThread."""
        logger.info(f"[TranslationWorker] Bắt đầu suy luận cho câu: '{self.result.text[:40]}...'")
        try:
            translated_text = self.engine.translate_text(self.result.text, self.settings)
            logger.info(f"[TranslationWorker] Suy luận thành công ({len(translated_text)} chars).")
            self.finished.emit(
                translated_text,
                self.result.x,
                self.result.y,
                self.result.width
            )
        except Exception as e:
            error_msg = f"⚠️ Lỗi AI: {str(e)}"
            logger.error(f"[TranslationWorker] Xảy ra ngoại lệ: {e}", exc_info=True)
            self.error_occurred.emit(error_msg)
            self.finished.emit(
                error_msg,
                self.result.x,
                self.result.y,
                self.result.width
            )
