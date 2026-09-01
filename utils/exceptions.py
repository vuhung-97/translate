"""
Định nghĩa các Custom Exceptions cho ứng dụng SmartTranslator.
Giúp dễ dàng phân loại, khoanh vùng và xử lý lỗi cụ thể.
"""

class SmartTranslatorError(Exception):
    """Lớp ngoại lệ cơ sở cho toàn bộ ứng dụng."""
    def __init__(self, message: str, original_exception: Exception = None):
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception

    def __str__(self):
        if self.original_exception:
            return f"{self.message} (Lỗi gốc: {self.original_exception})"
        return self.message


class ConfigError(SmartTranslatorError):
    """Ngoại lệ liên quan đến việc nạp/lưu cấu hình cài đặt."""
    pass


class ModelNotFoundError(SmartTranslatorError):
    """Không tìm thấy file mô hình AI hoặc OCR."""
    pass


class AIModelLoadError(SmartTranslatorError):
    """Xảy ra lỗi khi nạp mô hình CTranslate2 hoặc Tokenizer."""
    pass


class OCRError(SmartTranslatorError):
    """Lỗi xảy ra trong quá trình nhận diện hình ảnh (OCR)."""
    pass


class TranslationError(SmartTranslatorError):
    """Lỗi xảy ra trong quá trình dịch thuật AI."""
    pass
