import sys
import os
from psutil import Process, HIGH_PRIORITY_CLASS
import ctranslate2 
import sentencepiece as spm
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import config 

class EnViT5Application:
    """
    Class đóng gói toàn bộ quy trình khởi tạo và điều phối ứng dụng.
    """
    def __init__(self):
        self._app = None
        self._main_window = None
        self._translator = None
        self._tokenizer = None

    def _setup_system_priority(self):
        """Thiết lập ưu tiên xử lý cho CPU (Private Method)."""
        if sys.platform == "win32": # Kiểm tra hệ điều hành để tránh crash
            try:
                p = Process(os.getpid())
                p.nice(HIGH_PRIORITY_CLASS)
            except Exception:
                print("⚠️ Không thể thiết lập ưu tiên cao.")

    def _init_qt_environment(self):
        """Cấu hình môi trường hiển thị (High DPI)."""
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        self._app = QApplication(sys.argv)

    def _load_ai_engine(self):
        """Khởi tạo và cấu hình bộ não AI."""
        print("[DEBUG] Đang nạp BỘ NÃO AI...", flush=True)
        try:
            self._translator = ctranslate2.Translator(
                config.MODEL_DIR, 
                device="cpu", 
                compute_type="int8", 
                inter_threads=1, 
                intra_threads=getattr(config, 'DEFAULT_THREADS', 4) # Dùng config thay vì hard-code
            )
            self._tokenizer = spm.SentencePieceProcessor(
                model_file=os.path.join(config.MODEL_DIR, "spiece.model")
            )
            
            # Đẩy vào engine trung tâm
            from core.engine import ai_engine
            ai_engine.set_models(self._translator, self._tokenizer)
            print("✅ Hệ thống AI đã sẵn sàng!", flush=True)
        except Exception as e:
            print(f"❌ Lỗi nạp AI: {e}")
            sys.exit(1)

    def run(self):
        """
        Phương thức Public duy nhất để khởi chạy ứng dụng.
        Mẫu thiết kế: Facade Pattern - ẩn đi sự phức tạp bên trong.
        """
        self._setup_system_priority()
        self._init_qt_environment()
        self._load_ai_engine()

        # Khởi tạo cửa sổ chính
        from controller.controller import SmartTranslator
        self._main_window = SmartTranslator()
        self._main_window.show()

        return self._app.exec_()

# ================================================================
if __name__ == '__main__':
    # Việc khởi chạy giờ đây cực kỳ ngắn gọn
    envi_app = EnViT5Application()
    sys.exit(envi_app.run())