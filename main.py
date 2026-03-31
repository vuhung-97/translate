"""
Module chính khởi chạy ứng dụng. 
"""

import sys
from core.enviT5Application import EnViT5Application


# ================================================================
if __name__ == "__main__":
    envi_app = EnViT5Application()
    sys.exit(envi_app.run())
