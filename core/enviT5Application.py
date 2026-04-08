# 1. IMPORT CÁC THƯ VIỆN CẦN THIẾT
import os
import sys

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# Ngăn Qt can thiệp vào bộ nhớ trước khi AI sẵn sàng
os.environ["QT_NO_LIBREALSENSE"] = "1"

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import sentencepiece as spm
import ctranslate2 
import config

class EnViT5_Application:
    # 2. KHỞI TẠO TÀI NGUYÊN AI
    def load_ai_assets(self):
        print("[DEBUG] Đang nạp BỘ NÃO AI...", flush=True)

        model_dir = config.MODEL_DIR
        spiece_path = os.path.join(model_dir, "spiece.model")
        print(f"[*] Model Dir: {model_dir}")
        print(f"[*] Spiece Path: {spiece_path}")

        try:
            # --- BƯỚC 1: NẠP SENTENCEPIECE TỪ BỘ NHỚ (GIẢI PHÁP MẠNH NHẤT) ---

            print("\n[1/2] Dang nap SentencePiece...")
            tokenizer = spm.SentencePieceProcessor()

            with open(spiece_path, "rb") as f:
                model_bytes = f.read()

            tokenizer.load_from_serialized_proto(model_bytes)

            # tokenizer.load(spiece_path)
            print("✅ SentencePiece: OK!")

            # --- BƯỚC 2: NẠP TRANSLATOR ---
            print("\n[2/2] Dang nap CTranslate2 Translator...")
            
            translator = ctranslate2.Translator(
                str(model_dir), 
                device="cpu", 
                compute_type="int8",
                inter_threads=1, 
                intra_threads=4 
            )
            
            print("✅ CTranslate2: OK!", flush=True)

            from core.translation_engine import ai_engine
            ai_engine.set_models(translator, tokenizer)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"❌ Lỗi: {e}", flush=True)
            sys.exit(1)

    # 3. ĐIỀU PHỐI HỆ THỐNG VÀ GIAO DIỆN
    def bootstrap_application(self):
        """Khởi động toàn bộ thành phần hệ thống và giao diện."""

        # --- Khởi chạy Giao diện người dùng ---
        # Kích hoạt chế độ hỗ trợ màn hình độ phân giải cao (High DPI)
        
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QIcon
        from config import ICON_PATH

        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon(ICON_PATH))  # Thêm icon cho ứng dụng

        # Nạp giao diện chính từ main_window.py
        from controller.smart_translator import SmartTranslator
        main_window = SmartTranslator() 
        
        # Bắt đầu vòng lặp sự kiện của ứng dụng
        sys.exit(app.exec())
