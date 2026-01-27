# main.py
import sys
import os
import psutil
import ctranslate2 
import sentencepiece as spm
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# 1. CẤU HÌNH HỆ THỐNG & ĐƯỜNG DẪN
# Phải import config đầu tiên để thiết lập biến môi trường OMP/KMP
import config 

# 2. KHỞI TẠO TÀI NGUYÊN AI (CORE LOADING)
def load_ai_assets():
    """Nạp bộ giải mã CTranslate2 và bộ mã hóa SentencePiece vào bộ nhớ."""
    print("[DEBUG] Đang nạp BỘ NÃO AI tại Main Thread...", flush=True)
    try:
        # Khởi tạo Translator với cấu hình tối ưu CPU
        # inter_threads: Số lượng batch xử lý song song
        # intra_threads: Số luồng CPU tối đa cho mỗi tác vụ (đã chỉnh theo config)
        translator = ctranslate2.Translator(
            config.MODEL_DIR, 
            device="cpu", 
            compute_type="int8", 
            inter_threads=1, 
            intra_threads=4 
        )
        
        # Nạp tệp mẫu ngôn ngữ (Tokenizer)
        tokenizer = spm.SentencePieceProcessor(
            model_file=os.path.join(config.MODEL_DIR, "spiece.model")
        )
        
        print("✅ Hệ thống AI đã sẵn sàng!", flush=True)
        return translator, tokenizer
        
    except Exception as e:
        print(f"❌ Lỗi nghiêm trọng khi nạp AI: {e}", flush=True)
        # Thoát chương trình nếu không nạp được "bộ não"
        sys.exit(1)

# 3. ĐIỀU PHỐI HỆ THỐNG (ORCHESTRATION)
def bootstrap_application():
    """Khởi động toàn bộ thành phần hệ thống và giao diện."""
    
    # --- Thiết lập ưu tiên hệ thống ---
    try:
        # Tăng mức ưu tiên xử lý của Windows để giảm độ trễ khi quét dịch
        p = psutil.Process(os.getpid())
        p.nice(psutil.HIGH_PRIORITY_CLASS)
    except Exception:
        pass

    # --- Khởi tạo tài nguyên AI ---
    raw_translator, raw_tokenizer = load_ai_assets()

    # --- Kết nối Model với Engine xử lý ---
    from engine import ai_engine
    ai_engine.set_models(raw_translator, raw_tokenizer)

    # --- Khởi chạy Giao diện người dùng (UI) ---
    # Kích hoạt chế độ hỗ trợ màn hình độ phân giải cao (High DPI)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    
    # Nạp giao diện chính từ main_window.py
    from main_window import SmartTranslator
    main_window = SmartTranslator() 
    
    # Bắt đầu vòng lặp sự kiện của ứng dụng
    sys.exit(app.exec_())

# ================================================================
# ĐIỂM KHỞI CHẠY DUY NHẤT (ENTRY POINT)
# ================================================================
if __name__ == '__main__':
    bootstrap_application()