"""
Quản lý các đường dẫn tài nguyên trong hệ thống.
Hỗ trợ cả môi trường phát triển (Dev) và đóng gói EXE (PyInstaller).
"""

import os
import sys

class PathManager:
    """Đóng gói logic xác định đường dẫn tuyệt đối cho ứng dụng."""

    @staticmethod
    def get_path(relative_path: str) -> str:
        """
        Lấy đường dẫn tuyệt đối từ đường dẫn tương đối.
        Tự động xử lý đường dẫn trong PyInstaller (`sys._MEIPASS`).
        """
        base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
        return os.path.normpath(os.path.join(base_path, relative_path))

    @staticmethod
    def get_user_data_path(file_name: str) -> str:
        """Lấy đường dẫn file lưu dữ liệu người dùng (nằm ở gốc làm việc)."""
        return os.path.normpath(os.path.join(os.path.abspath("."), file_name))
