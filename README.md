# EnViT5 Smart Translator

Ứng dụng dịch màn hình offline dùng PyQt5 + Tesseract OCR + EnViT5 (CTranslate2).

Mục tiêu của dự án là quét văn bản trên màn hình, OCR theo vùng chọn, sau đó dịch nhanh giữa Anh-Việt hoặc Việt-Anh ngay trên máy cục bộ.

## Tính năng chính

- Dịch hoàn toàn offline, không cần Internet.
- Quét vùng màn hình bằng chuột, hiển thị bản dịch trực tiếp trên giao diện.
- Hỗ trợ 2 chiều dịch: `en-vi` và `vi-en`.
- Có hộp cài đặt để tinh chỉnh các tham số suy luận: `beam_size`, `repetition_penalty`, `no_repeat_ngram_size`, `max_decoding_length`, `font_size`, giao diện chủ đề.
- OCR nội bộ bằng Tesseract, model OCR đặt sẵn trong thư mục dự án.

## Công nghệ sử dụng

- Python 3.13
- PyQt5
- CTranslate2
- sentencepiece
- pytesseract + OpenCV + Pillow

## Yêu cầu hệ thống

- Windows 10/11 (đã kiểm thử chính trên Windows).
- CPU chạy tốt với thiết lập mặc định của dự án.
- Cần giữ nguyên thư mục model và OCR đi kèm khi chạy app.

## Chạy dự án ở chế độ dev

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
3. Ứng dụng OCR và dịch, kết quả hiển thị ngay trên vùng vừa chọn.
4. Nhấn `Enter` để xóa toàn bộ kết quả hiện có.
5. Nhấn `Esc` lần nữa để thu nhỏ giao diện về thanh công cụ.

## Cấu hình dịch

Trong cửa sổ Cài đặt có các tham số chính:

- `beam_size`: tăng chất lượng tìm kiếm, đổi lại chậm hơn.
- `repetition_penalty`: giảm lặp từ/cụm từ.
- `no_repeat_ngram_size`: chặn lặp cụm theo n-gram.
- `max_decoding_length`: giới hạn độ dài đầu ra.
- `font_size`: cỡ chữ vùng kết quả.

Cấu hình mặc định được khai báo trong `config.py` tại `DEFAULT_SETTINGS`.

## Cấu trúc thư mục

```text
translate2/
├── main.py
├── config.py
├── main.spec
├── requirements.txt
├── core/
│   ├── engine.py
│   └── ocr_utils.py
├── gui/
│   ├── main_window.py
│   ├── ui_components.py
│   ├── theme_config.py
│   └── help.html
├── models/
│   └── model_envit5_fast/
└── bin/
        └── Tesseract-OCR/
```

## Đóng gói bằng PyInstaller

Có thể build theo file spec sẵn có:

```powershell
pyinstaller .\main.spec
```

Nếu build thủ công bằng CLI, cần đảm bảo thêm đúng dữ liệu theo cấu trúc hiện tại:

```powershell
pyinstaller --noconfirm --onedir --windowed --name "SmartTranslator_EnViT5" ^
    --add-data "models\model_envit5_fast;models\model_envit5_fast" ^
    --add-data "bin\Tesseract-OCR;bin\Tesseract-OCR" ^
    main.py
```

Sau khi đóng gói, file thực thi phải đi cùng các thư mục dữ liệu đã add ở trên để OCR và model dịch hoạt động.

## Một số lỗi thường gặp

- `DLL load failed`: cài Microsoft Visual C++ Redistributable mới nhất.
- OCR không trả kết quả: kiểm tra lại quyền truy cập và đường dẫn thư mục `bin/Tesseract-OCR`.
- App chạy nhưng không dịch: kiểm tra sự tồn tại của model trong `models/model_envit5_fast`.

## Ghi chú cho developer

- Biến môi trường hiệu năng và xử lý OpenMP được cấu hình trong `config.py`.
- Luồng dịch chạy qua `TranslationWorker` để tránh đơ UI.
- AI engine dùng singleton tại `core/engine.py` và được nạp model ở bước khởi động trong `main.py`.
