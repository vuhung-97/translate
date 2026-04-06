# EnViT5 Smart Translator

Ứng dụng dịch màn hình offline sử dụng PyQt5, Tesseract OCR và EnViT5 (CTranslate2).

## Mục tiêu dự án

- Quét văn bản trên màn hình, OCR theo vùng chọn, dịch nhanh giữa Anh-Việt hoặc Việt-Anh ngay trên máy cục bộ.
- Dịch hoàn toàn offline, không cần Internet.

## Tính năng chính

- Quét vùng màn hình bằng chuột, hiển thị bản dịch trực tiếp trên giao diện.
- Hỗ trợ 2 chiều dịch: `en-vi` và `vi-en`.
- Hộp cài đặt cho các tham số suy luận: `beam_size`, `repetition_penalty`, `no_repeat_ngram_size`, `max_decoding_length`, `font_size`, chủ đề giao diện.
- OCR nội bộ bằng Tesseract, model OCR và model dịch được đóng gói sẵn.

## Công nghệ sử dụng

- Python 3.13
- PyQt5
- CTranslate2
- sentencepiece
- pytesseract, OpenCV, Pillow

## Yêu cầu hệ thống

- Windows 10/11 (đã kiểm thử chính trên Windows).
- CPU phổ thông chạy tốt với thiết lập mặc định.
- Cần giữ nguyên thư mục model và OCR đi kèm khi chạy app.

## Hướng dẫn chạy ở chế độ phát triển

1. Tạo môi trường ảo:

    ```powershell
    python -m venv venv
    ```

2. Kích hoạt môi trường:

    ```powershell
    .\venv\Scripts\Activate.ps1
    ```

3. Cài dependencies:

    ```powershell
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```

4. Chạy ứng dụng:
    ```powershell
    python .\main.py
    ```

## Hướng dẫn sử dụng nhanh

1. Nhấn nút Quét (hoặc phím `Esc`) để vào chế độ chọn vùng.
2. Kéo chuột khoanh vùng văn bản cần dịch.
3. Ứng dụng sẽ OCR và dịch, kết quả hiển thị ngay trên vùng vừa chọn.
4. Nhấn `Enter` để xóa toàn bộ kết quả hiện có.
5. Nhấn `Esc` lần nữa để thu nhỏ giao diện về thanh công cụ.

## Cấu hình dịch

Trong cửa sổ Cài đặt có các tham số chính:

- `beam_size`: tăng chất lượng tìm kiếm, đổi lại chậm hơn.
- `repetition_penalty`: giảm lặp từ/cụm từ.
- `no_repeat_ngram_size`: chặn lặp cụm theo n-gram.
- `max_decoding_length`: giới hạn độ dài đầu ra.
- `font_size`: cỡ chữ vùng kết quả.
- `theme`: chủ đề giao diện (Sáng/Tối).

Cấu hình mặc định được khai báo trong [`config.py`](config.py) tại `DEFAULT_SETTINGS`. Khi thay đổi, cài đặt sẽ được lưu vào file [`settings.json`](settings.json) và tự động nạp lại khi mở ứng dụng.

## Cấu trúc thư mục

```text
translate2/
├── main.py
├── config.py
├── main.spec
├── requirements.txt
├── core/
│   ├── enviT5Application.py
│   ├── ocr_processor.py
│   ├── translation_engine.py
│   ├── translation_service.py
│   └── translation_worker.py
├── controller/
│   ├── event.py
│   └── smart_translator.py
├── gui/
│   ├── help.html
│   ├── theme_config.py
│   └── ui_components.py
├── models/
│   └── model_envit5_fast/
│       ├── config.json
│       ├── shared_vocabulary.json
│       ├── spiece.model
├── bin/
│   └── Tesseract-OCR/
│       ├── tessdata/
│       └── ...
├── resources/
└── settings.json
```

## Đóng gói phần mềm

### Đóng gói thành thư mục (khuyến nghị)

Chạy lệnh sau để đóng gói toàn bộ ứng dụng vào một thư mục (dist/SmartTranslator_EnViT5):

```powershell
pyinstaller --noconfirm --onedir --windowed --name "SmartTranslator_EnViT5" ^
    --add-data "models;models" ^
    --add-data "bin;bin" ^
    --add-data "gui;gui" ^
    --add-data "core;core" ^
    --add-data "controller;controller" ^
    --add-data "resources;resources" ^
    main.py
```

- Thư mục dist/SmartTranslator_EnViT5 sẽ chứa file thực thi và toàn bộ tài nguyên cần thiết.
- Khi chạy, cần giữ nguyên cấu trúc thư mục như trên.

### Đóng gói thành 1 file (không khuyến nghị với app lớn)

Có thể dùng `--onefile`, nhưng thời gian khởi động sẽ lâu hơn và có thể gặp lỗi với các file dữ liệu lớn.

### Đóng gói bằng file spec

Bạn có thể chỉnh sửa file [`main.spec`](main.spec) để tùy biến sâu hơn, sau đó build bằng:

```powershell
pyinstaller .\main.spec
```

## Một số lỗi thường gặp

- `DLL load failed`: Cài Microsoft Visual C++ Redistributable mới nhất.
- OCR không trả kết quả: Kiểm tra lại quyền truy cập và đường dẫn thư mục [`bin/Tesseract-OCR`](bin/Tesseract-OCR).
- App chạy nhưng không dịch: Kiểm tra sự tồn tại của model trong [`models/model_envit5_fast`](models/model_envit5_fast).

## Ghi chú cho developer

- Biến môi trường hiệu năng và xử lý OpenMP được cấu hình trong [`config.py`](config.py).
- Luồng dịch chạy qua `TranslationWorker` để tránh đơ UI.
- AI engine dùng singleton tại [`core/translation_engine.py`](core/translation_engine.py) và được nạp model ở bước khởi động trong [`main.py`](main.py).
- Cài đặt người dùng được lưu trong [`settings.json`](settings.json) và tự động nạp lại khi khởi động.
