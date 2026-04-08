# 1. IMPORT CÁC THƯ VIỆN CẦN THIẾT
import os
import sys
from core.enviT5Application import EnViT5_Application
# ================================================================
# ĐIỂM KHỞI CHẠY DUY NHẤT (ENTRY POINT)
# ================================================================
if __name__ == '__main__':
    app = EnViT5_Application()
    app.load_ai_assets()
    app.bootstrap_application()