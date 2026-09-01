"""
Định nghĩa các Custom Exceptions cho ứng dụng SmartTranslator.
Phân loại, khoanh vùng và hỗ trợ thông điệp báo lỗi chi tiết cho từng tác vụ.
"""

from typing import Optional


class SmartTranslatorError(Exception):
    """Lớp ngoại lệ cơ sở cho toàn bộ ứng dụng SmartTranslator."""
    
    default_message: str = "Đã xảy ra lỗi không xác định trong hệ thống SmartTranslator."

    def __init__(self, message: Optional[str] = None, original_exception: Optional[Exception] = None):
        msg = message if message else self.default_message
        super().__init__(msg)
        self.message = msg
        self.original_exception = original_exception

    def __str__(self) -> str:
        if self.original_exception:
            return f"{self.message} | Lỗi gốc: {type(self.original_exception).__name__}: {self.original_exception}"
        return self.message


class ConfigError(SmartTranslatorError):
    """Ngoại lệ xảy ra trong quá trình nạp, lưu hoặc đọc file cấu hình settings.json."""
    default_message = "Lỗi thao tác với file cấu hình hệ thống."


class ModelNotFoundError(SmartTranslatorError):
    """Ngoại lệ xảy ra khi không tìm thấy file trọng số mô hình AI hoặc OCR."""
    default_message = "Không tìm thấy file tài nguyên mô hình AI/OCR."


class AIModelLoadError(SmartTranslatorError):
    """Ngoại lệ xảy ra khi nạp mô hình CTranslate2 hoặc SentencePiece Tokenizer thất bại."""
    default_message = "Nạp mô hình suy luận CTranslate2/Tokenizer thất bại."


class OCRError(SmartTranslatorError):
    """Ngoại lệ xảy ra trong quá trình xử lý hình ảnh hoặc nhận diện chữ OCR."""
    default_message = "Xử lý nhận diện chữ OCR thất bại."


class TranslationError(SmartTranslatorError):
    """Ngoại lệ xảy ra trong quá trình suy luận dịch thuật AI EnViT5."""
    default_message = "Suy luận dịch thuật AI thất bại."
