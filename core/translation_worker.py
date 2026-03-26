from PyQt5.QtCore import QThread, pyqtSignal

# Các import từ dự án (giữ nguyên)
from core.translation_engine import ai_engine

# ================================================================
# LUỒNG XỬ LÝ DỊCH THUẬT (BACKGROUND WORKER)
# ================================================================
class TranslationWorker(QThread):
    """
    Luồng xử lý riêng biệt để thực hiện dịch thuật mà không gây treo giao diện chính (UI).
    """
    # Tín hiệu phát ra khi dịch xong: (kết quả, x, y, width)
    finished = pyqtSignal(str, int, int, int)

    def __init__(self, text: str, x: int, y: int, w: int, settings: dict[str, any], engine=ai_engine):
        super().__init__()
        self.engine = engine
        self.text = text
        self.x, self.y, self.w = x, y, w
        self.settings = settings

    def run(self):
        """Thực thi tác vụ dịch thuật trong luồng phụ."""
        try:
            # Gọi hàm dịch từ engine trung tâm
            result = self.engine.translate_text(self.text, self.settings)
            self.finished.emit(result, self.x, self.y, self.w)
        except Exception as e:
            # Trả về thông báo lỗi nếu quá trình dịch thất bại
            self.finished.emit(f"⚠️ Lỗi AI: {str(e)}", self.x, self.y, self.w)