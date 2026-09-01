"""
Module ghi log tập trung cho toàn ứng dụng SmartTranslator.
Hỗ trợ ghi out console và ghi lưu file app.log.
"""

import os
import sys
import logging
import io

class SafeStreamHandler(logging.StreamHandler):
    """StreamHandler hỗ trợ encode Unicode an toàn trên Windows Console."""
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            try:
                stream.write(msg + self.terminator)
            except UnicodeEncodeError:
                # Nếu console mã hóa cp1252 không hỗ trợ Unicode tiếng Việt, encode utf-8 hoặc replace
                encoded_msg = msg.encode(stream.encoding or "utf-8", errors="replace").decode(stream.encoding or "utf-8")
                stream.write(encoded_msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)


class CustomFormatter(logging.Formatter):
    """Formatter tùy chỉnh định dạng log cho Console và File."""
    
    fmt = "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    def __init__(self):
        super().__init__(fmt=self.fmt, datefmt=self.datefmt)


def get_logger(name: str = "SmartTranslator") -> logging.Logger:
    """
    Hàm khởi tạo hoặc lấy Logger duy nhất của ứng dụng.
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # 1. Console Handler
        console_handler = SafeStreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(CustomFormatter())
        logger.addHandler(console_handler)
        
        # 2. File Handler (app.log)
        try:
            log_file_path = os.path.join(os.path.abspath("."), "app.log")
            file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(CustomFormatter())
            logger.addHandler(file_handler)
        except Exception as e:
            console_handler.setLevel(logging.DEBUG)
            logger.warning(f"Không thể khởi tạo file log app.log: {e}")

    return logger

# Single default logger instance for easy import
logger = get_logger()
