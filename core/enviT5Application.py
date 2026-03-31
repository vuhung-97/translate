"""
Module chính khởi chạy ứng dụng. 
Đóng vai trò là điểm vào duy nhất, chịu trách nhiệm:
- Thiết lập môi trường hệ thống (ưu tiên CPU, biến môi trường)
- Khởi tạo và cấu hình bộ não AI (CTranslate2 + SentencePiece)
- Khởi tạo giao diện người dùng (SmartTranslator)
- Điều phối các thành phần chính và bắt đầu vòng lặp sự kiện của Qt
"""
import sys
import os
from psutil import Process, HIGH_PRIORITY_CLASS, AccessDenied, NoSuchProcess
import ctranslate2
import sentencepiece as spm
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import config
from controller.smart_translator import SmartTranslator
from core.translation_engine import ai_engine


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
        """Thiết lập ưu tiên xử lý cho CPU."""
        if sys.platform == "win32":  # Kiểm tra hệ điều hành để tránh crash
            try:
                p = Process(os.getpid())
                p.nice(HIGH_PRIORITY_CLASS)
            except (OSError, AccessDenied, NoSuchProcess):
                print("⚠️ Không thể thiết lập ưu tiên cao.")

    def _init_qt_environment(self):
        """Cấu hình môi trường hiển thị."""
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
                intra_threads=getattr(
                    config, "DEFAULT_THREADS", 4
                ),  # Dùng config thay vì hard-code
            )
            self._tokenizer = spm.SentencePieceProcessor()
            self._tokenizer.load(os.path.join(config.MODEL_DIR, "spiece.model"))

            # Đẩy vào engine trung tâm
            ai_engine.set_models(self._translator, self._tokenizer)
            print("✅ Hệ thống AI đã sẵn sàng!", flush=True)
        except (OSError, RuntimeError) as e:
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
        self._main_window = SmartTranslator()
        self._main_window.show()

        return self._app.exec_()