# pylint: disable=no-name-in-module, import-error, too-few-public-methods, broad-exception-caught
"""
Module này định nghĩa lớp TranslationWorker
Một luồng xử lý riêng biệt để thực hiện tác vụ dịch thuật.
Nó giúp đảm bảo rằng giao diện người dùng (UI) vẫn mượt mà 
và phản hồi nhanh chóng trong khi AI đang xử lý văn bản.
TranslationWorker sử dụng PyQt5.QtCore.QThread để chạy tác vụ dịch thuật trong nền
"""
from dataclasses import dataclass
from PyQt5.QtCore import QThread, pyqtSignal

# Các import từ dự án (giữ nguyên)
from core.translation_engine import ai_engine

@dataclass
class TranslationResult:
    """Đóng gói kết quả dịch thuật cùng với thông tin vị trí."""
    text: str
    x: int
    y: int
    width: int

# ================================================================
# LUỒNG XỬ LÝ DỊCH THUẬT (BACKGROUND WORKER)
# ================================================================
class TranslationWorker(QThread):
    """
    Luồng xử lý riêng biệt để thực hiện dịch thuật mà không gây treo giao diện chính (UI).
    """

    # Tín hiệu phát ra khi dịch xong: (kết quả, x, y, width)
    finished = pyqtSignal(str, int, int, int)

    def __init__(
        self,
        result: TranslationResult,
        settings: dict[str, any],
        engine=ai_engine,
    ):
        super().__init__()
        self.engine = engine
        self.result = result
        self.settings = settings

    def run(self):
        """Thực thi tác vụ dịch thuật trong luồng phụ."""
        try:
            # Gọi hàm dịch từ engine trung tâm
            result = self.engine.translate_text(self.result.text, self.settings)
            self.finished.emit(result, self.result.x, self.result.y, self.result.width)
        except Exception as e:
            # Trả về thông báo lỗi nếu quá trình dịch thất bại
            self.finished.emit(
                f"⚠️ Lỗi AI: {str(e)}",
                self.result.x,
                self.result.y,
                self.result.width)
