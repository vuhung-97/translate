"""
Khởi tạo toàn bộ ứng dụng EnViT5 Smart Translator.
Quản lý vòng đời khởi chạy tài nguyên AI và QApplication PyQt6.
"""

import os
import sys
import sentencepiece as spm
import ctranslate2

from config import config_manager
from core.translation_engine import ai_engine
from utils.logger import logger
from utils.exceptions import AIModelLoadError

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["QT_NO_LIBREALSENSE"] = "1"
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"


class EnViT5_Application:
    """
    Class quản lý vòng đời nạp mô hình AI và khởi chạy giao diện ứng dụng.
    """

    def load_ai_assets(self):
        """Nạp SentencePiece Tokenizer và CTranslate2 Translator."""
        logger.info("Đang bắt đầu nạp tài nguyên mô hình AI...")

        model_dir = config_manager.MODEL_DIR
        spiece_path = os.path.join(model_dir, "spiece.model")

        if not os.path.exists(spiece_path):
            raise AIModelLoadError(f"Không tìm thấy file mô hình spiece.model tại {spiece_path}")

        try:
            # 1. Nạp SentencePiece
            logger.info("Nạp SentencePiece Tokenizer...")
            tokenizer = spm.SentencePieceProcessor()
            with open(spiece_path, "rb") as f:
                model_bytes = f.read()
            tokenizer.load_from_serialized_proto(model_bytes)
            logger.info("SentencePiece Tokenizer: OK!")

            # 2. Nạp CTranslate2 Translator
            logger.info("Nạp CTranslate2 Translator...")
            translator = ctranslate2.Translator(
                str(model_dir),
                device="cpu",
                compute_type="int8",
                inter_threads=1,
                intra_threads=4
            )
            logger.info("CTranslate2 Translator: OK!")

            # 3. Gán vào Engine trung tâm
            ai_engine.set_models(translator, tokenizer)
            logger.info("Tất cả tài nguyên AI đã nạp thành công.")

        except Exception as e:
            logger.error(f"Lỗi khi nạp tài nguyên AI: {e}", exc_info=True)
            sys.exit(1)

    def bootstrap_application(self):
        """Khởi chạy ứng dụng PyQt6 và Controller chính."""
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QIcon
        from controller.smart_translator import SmartTranslator

        logger.info("Khởi động giao diện PyQt6...")
        app = QApplication(sys.argv)
        
        if os.path.exists(config_manager.ICON_PATH):
            app.setWindowIcon(QIcon(config_manager.ICON_PATH))

        main_window = SmartTranslator()
        sys.exit(app.exec())
