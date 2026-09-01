# 📋 KẾ HOẠCH REFACTOR & NÂNG CẤP TOÀN BỘ DỰ ÁN `translate2`

## 🎯 1. Mục tiêu & Nguyên tắc Kỹ thuật (Core Principles)
1. **Dễ Bảo Trì (Maintainability)**: Tách biệt rõ ràng từng lớp/tầng (Clean Architecture / Layered Architecture).
2. **Nguyên tắc Đơn trách nhiệm (Single Responsibility Principle - SRP)**: Mỗi class/module chỉ chịu trách nhiệm duy nhất cho một công việc.
3. **Mẫu Thiết Kế Singleton (Singleton Pattern)**: Áp dụng cho các thành phần quản lý tài nguyên duy nhất: `ConfigManager`, `TranslationEngine`, `AppLogger`.
4. **Mẫu Thiết Kế Strategy (Strategy Pattern)**: Trừu tượng hoá các công cụ OCR (`Tesseract` và `EasyOCR`), giúp dễ dàng chuyển đổi hoặc thêm engine OCR mới (PaddleOCR, RapidOCR...) trong tương lai.
5. **Loại bỏ Đa Thừa Kế phức tạp**: Thay thế cấu trúc kế thừa `SmartTranslator(MouseEvent, UIHandler)` bằng mô hình Composition (gộp thành phần) và Component-based UI.
6. **Quản lý Trạng thái & Debug chuyên nghiệp**: Thay thế hoàn toàn `print()` rải rác bằng hệ thống `AppLogger` ghi log vào console và file `app.log`. Khởi tạo custom exceptions (`OCRError`, `TranslationError`, `ModelLoadError`).

---

## 🏛️ 2. Cấu trúc Thư mục Đề xuất (Target Directory Structure)

```text
translate2/
│
├── main.py                   # Entry point gọn nhẹ
├── config.py                 # (Re-export / Backward compatibility) Đóng gói ConfigManager
├── kehoach.md                # File kế hoạch refactor chi tiết
├── requirements.txt          # Danh sách thư viện phụ thuộc
├── settings.json             # File lưu thông số người dùng
├── SmartTranslator.spec      # File cấu hình PyInstaller duy nhất
│
├── utils/                    # Các tiện ích chung hệ thống
│   ├── __init__.py
│   ├── logger.py             # Singleton Logger cho toàn app
│   ├── exceptions.py         # Định nghĩa các Custom Exceptions
│   └── path_manager.py       # Quản lý đường dẫn tài nguyên (PyInstaller compatible)
│
├── config/                   # Quản lý cấu hình
│   ├── __init__.py
│   └── config_manager.py     # Singleton ConfigManager (Type-safe dataclass)
│
├── core/                     # Tầng Lõi (Domain & Processing Logic)
│   ├── __init__.py
│   ├── translation_engine.py # Singleton EnViT5 Engine (CTranslate2 + SentencePiece)
│   ├── ocr/                  # Tầng OCR Strategy
│   │   ├── __init__.py
│   │   ├── base.py           # BaseOCREngine (Abstract Base Class)
│   │   ├── tesseract_ocr.py  # Implementation dùng Tesseract
│   │   ├── easy_ocr.py       # Implementation dùng EasyOCR
│   │   └── factory.py        # OCRFactory chọn engine phù hợp
│   └── services/
│       ├── __init__.py
│       ├── translation_service.py # Điều phối OCR -> AI Dịch
│       └── translation_worker.py  # QThread xử lý dịch thuật không treo UI
│
├── gui/                      # Tầng Giao diện (PyQt6 Views & Components)
│   ├── __init__.py
│   ├── theme.py              # ThemeConfig quản lý bảng màu & style
│   ├── windows/              # Cửa sổ chính & Overlay
│   │   ├── toolbar_window.py # Thanh công cụ nhỏ gọn (Compact Toolbar)
│   │   ├── selection_window.py # Màn hình chụp & chọn vùng mờ (Scan Overlay)
│   │   ├── settings_dialog.py # Dialog Cài đặt AI & Giao diện
│   │   └── help_dialog.py     # Dialog Hướng dẫn HTML
│   └── components/
│       ├── result_overlay.py  # Lớp quản lý các khung hiển thị kết quả dịch
│       └── custom_widgets.py  # Nút bấm, Slider tùy chỉnh
│
└── tests/                    # Unit Tests & Integration Tests
    ├── test_config.py
    ├── test_ocr.py
    └── test_translation.py
```

---

## 🚩 3. Các Giai đoạn Thực thi Chi tiết (Detailed Execution Phases)

### 🔹 Giai đoạn 1: Chuẩn hóa Hạ tầng (Infrastructure, Logging & Config) - [HOÀN THÀNH ✅]
- **Bước 1.1**: Xây dựng `utils/logger.py` cung cấp module ghi log tập trung (hỗ trợ hiển thị console và ghi file `app.log`). [HOÀN THÀNH ✅]
- **Bước 1.2**: Định nghĩa `utils/exceptions.py` và `utils/path_manager.py` với các lớp lỗi tùy chỉnh để dễ khoanh vùng bug. [HOÀN THÀNH ✅]
- **Bước 1.3**: Chuẩn hóa `config/config_manager.py` theo mẫu Singleton & Dataclass:
  - Đóng gói dữ liệu cấu hình type-safe (`TranslationSettings`).
  - Hỗ trợ tự động tải/lưu file `settings.json`, bao gồm cơ chế fallback giá trị mặc định an toàn.
  - Cập nhật `config/__init__.py` tương thích ngược hoàn toàn. [HOÀN THÀNH ✅]

### 🔹 Giai đoạn 2: Tái cấu trúc Tầng Core (AI Engine & OCR Strategy Pattern) - [HOÀN THÀNH ✅]
- **Bước 2.1**: Refactor `core/translation_engine.py` (Singleton `EnViT5Engine`):
  - Tách bạch các phương thức suy luận, bổ sung ghi log thời gian xử lý AI và xử lý ngoại lệ `TranslationError`. [HOÀN THÀNH ✅]
- **Bước 2.2**: Áp dụng Strategy Pattern cho OCR trong `core/ocr/`:
  - Xây dựng `BaseOCREngine` (Abstract Base Class). [HOÀN THÀNH ✅]
  - Chuẩn hóa `TesseractOCREngine` với tiền xử lý ảnh thích ứng (Adaptive Enhancement). [HOÀN THÀNH ✅]
  - Chuẩn hóa `EasyOCREngine` xử lý bounding box theo dòng đọc tự nhiên. [HOÀN THÀNH ✅]
  - Xây dựng `OCRFactory` khởi tạo engine linh hoạt theo cấu hình. [HOÀN THÀNH ✅]
  - Cập nhật wrapper tương thích ngược cho `ocr_processor.py` và `easy_ocr_processor.py`. [HOÀN THÀNH ✅]

### 🔹 Giai đoạn 3: Tái cấu trúc Tầng GUI (Component-based & Loại bỏ Đa Thừa Kế) - [HOÀN THÀNH ✅]
- **Bước 3.1**: Tách nhỏ giao diện phức tạp hiện tại (loại bỏ đa thừa kế `SmartTranslator(MouseEvent, UIHandler)`):
  - `ToolbarWindow` (`gui/windows/toolbar_window.py`): Thanh công cụ chính chứa nút Quét, Đổi chiều ngôn ngữ, Xóa, Cài đặt, Hướng dẫn, Tháo thoát. [HOÀN THÀNH ✅]
  - `SelectionOverlayWindow` (`gui/windows/selection_window.py`): Cửa sổ chụp và chọn vùng mờ toàn màn hình. [HOÀN THÀNH ✅]
- **Bước 3.2**: Tách biệt `OverlayManager` thành `ResultOverlayManager` (`gui/components/result_overlay.py`):
  - Đóng gói logic tạo/xóa các khung hiển thị kết quả dịch (`QScrollArea`). [HOÀN THÀNH ✅]
- **Bước 3.3**: Chuẩn hóa `SettingsDialog` (`gui/windows/settings_dialog.py`), `HelpDialog` (`gui/windows/help_dialog.py`), `ThemeConfig` (`gui/theme.py`) thành các module chuyên biệt. [HOÀN THÀNH ✅]
- **Bước 3.4**: Refactor `SmartTranslator` (`controller/smart_translator.py`) đóng vai trò Controller kết nối UI mượt mà không dùng đa thừa kế. [HOÀN THÀNH ✅]

### 🔹 Giai đoạn 4: Tầng Service & Luồng xử lý Bất đồng bộ (Async Workers) - [HOÀN THÀNH ✅]
- **Bước 4.1**: Tái cấu trúc `TranslationWorker(QThread)`:
  - Gửi dữ liệu qua signals/slots an toàn (thread-safe). [HOÀN THÀNH ✅]
  - Bổ sung cơ chế ghi log và bắt ngoại lệ trong luồng phụ. [HOÀN THÀNH ✅]
- **Bước 4.2**: Refactor `TranslationService`:
  - Nhận yêu cầu dịch từ `SelectionOverlayWindow`, gọi `OCRFactory` thực thi OCR, kích hoạt `TranslationWorker`. [HOÀN THÀNH ✅]
  - Quản lý danh sách luồng đang chạy (`_active_workers`) an toàn và tự động thu hồi tài nguyên `deleteLater()`. [HOÀN THÀNH ✅]

### 🔹 Giai đoạn 5: Tối ưu hóa Trải nghiệm & Tính năng Nâng cao (UX & Upgrades) - [HOÀN THÀNH ✅]
- **Bước 5.1**: Hỗ trợ chuyển đổi Engine OCR trực tiếp trong cửa sổ Cài đặt (`SettingsDialog`). [HOÀN THÀNH ✅]
- **Bước 5.2**: Xử lý DPI Scaling & Đa màn hình (Multi-Monitor) cho tính năng quét toàn màn hình (`SelectionOverlayWindow`). [HOÀN THÀNH ✅]
- **Bước 5.3**: Tích hợp module `logger` và `config_manager` vào `core/enviT5Application.py` và `main.py`. [HOÀN THÀNH ✅]

### 🔹 Giai đoạn 6: Kiểm thử, Dọn dẹp & Đóng gói (Testing & Build) - [HOÀN THÀNH ✅]
- **Bước 6.1**: Viết bộ test kiểm thử trong `tests/` (`test_config.py`, `test_ocr.py`, `test_translation.py`). [HOÀN THÀNH ✅]
- **Bước 6.2**: Dọn dẹp các file `.spec` thừa, hợp nhất thành `SmartTranslator.spec` duy nhất chuẩn hóa build PyInstaller. [HOÀN THÀNH ✅]
- **Bước 6.3**: Kiểm thử toàn bộ hệ thống qua unit test suite (Pass 7/7 tests). [HOÀN THÀNH ✅]

---

## 🏆 TỔNG KẾT TÌNH TRẠNG DỰ ÁN
- ✅ **Giai đoạn 1**: Chuẩn hóa Hạ tầng (Logging, Custom Exceptions, ConfigManager Singleton).
- ✅ **Giai đoạn 2**: Tái cấu trúc Tầng Core (AI Engine Singleton, OCR Strategy Pattern với Tesseract & EasyOCR).
- ✅ **Giai đoạn 3**: Tái cấu trúc Tầng GUI (Component-based GUI, loại bỏ hoàn toàn Đa Thừa Kế Diamond).
- ✅ **Giai đoạn 4**: Tầng Service & QThread (TranslationWorker bất đồng bộ, dọn dẹp bộ nhớ tự động).
- ✅ **Giai đoạn 5**: UX & Upgrades (Multi-Monitor support, High-DPI Scaling, chuyển đổi OCR Engine trực tiếp).
- ✅ **Giai đoạn 6**: Unit Tests & Build Spec (7/7 Unit tests thành công, `SmartTranslator.spec` duy nhất).

---

## 🧪 4. Quy trình Kiểm thử & Xác minh (Verification Plan)
1. **Kiểm thử Đơn vị (Unit Tests)**: Chạy `pytest tests/` đảm bảo logic lõi hoạt động chính xác.
2. **Kiểm thử Giao diện (UI Functional Test)**:
   - Thử nghiệm quét vùng màn hình chứa chữ Tiếng Anh / Tiếng Việt.
   - Kiểm tra đổi theme (Sáng / Tối) và chỉnh cỡ chữ.
   - Kiểm tra đổi chiều dịch `En ➔ Vi` và `Vi ➔ En`.
   - Kiểm tra lưu/khôi phục cài đặt mặc định trong file `settings.json`.
3. **Kiểm thử Đóng gói**: Đóng gói ứng dụng thành `.exe` với PyInstaller và khởi chạy thử nghiệm độc lập.
