# 🚀 EnViT5 Smart Translator - Bản Siêu Tốc (Offline)

> **EnViT5 Smart Translator** là công cụ dịch thuật màn hình mạnh mẽ, sử dụng trí tuệ nhân tạo (AI) để dịch trực tiếp từ hình ảnh sang tiếng Việt. Phần mềm được tối ưu hóa đặc biệt cho dòng chip Intel Core i7 Thế hệ 12, đảm bảo tốc độ phản hồi tức thì mà không cần kết nối Internet.

---

## 🌟 Tính năng nổi bật

- **Dịch Offline 100%**: Không gửi dữ liệu lên mây, bảo mật tuyệt đối thông tin.
- **Cốt lõi VietAI**: Sử dụng mô hình EnViT5 chuyên sâu cho cặp ngôn ngữ Anh - Việt.
- **Tốc độ i7 Gen 12**: Tận dụng nhân P-cores và định dạng INT8 Quantization để dịch trong chưa đầy 1 giây.
- **Chống lặp thông minh**: Tích hợp bộ phạt lặp (Repetition Penalty) và tự động chuẩn hóa dấu câu đầu vào.

---

## 📦 Hướng dẫn cài đặt (Bản Portable)

> Nếu bạn sử dụng bộ máy đã đóng gói (thư mục `dist\EnViT5_Portable`), **không cần cài đặt Python hay bất cứ thư viện nào**.

1. **Giải nén**: Giải nén tệp tin `.zip` vào một thư mục trên ổ cứng (ưu tiên SSD).
2. **Khởi chạy**: Tìm và nhấp đúp vào file `EnViT5_Portable.exe`.
3. **Cấp quyền**: Nếu Windows Defender hiện cảnh báo, chọn **More info** → **Run anyway**.

> ⚠️ **Lưu ý:**
> Toàn bộ dữ liệu quan trọng như bộ não AI và động cơ OCR nằm trong thư mục `_internal`. Vui lòng không xóa hoặc di chuyển thư mục này.

---

## 📖 Hướng dẫn sử dụng

### Giao diện phần mềm

Phần mềm có 4 nút chính:

- **Quét / Thu nhỏ (Esc):** Phóng to màn hình để bắt đầu chế độ dịch hoặc thu nhỏ để thoát.
- **Xóa (Enter):** Xóa vùng đã chọn và reset màn hình.
- **Cài đặt:** Mở cửa sổ cài đặt với các thông số: - `Beams Size`: Số lượng beam trong quá trình tìm kiếm, ảnh hưởng đến chất lượng bản dịch (giá trị cao hơn có thể cải thiện chất lượng nhưng làm chậm tốc độ). - `Phạt lặp`: Hệ số phạt lặp từ, giúp giảm khả năng lặp lại từ trong bản dịch. - `Chặn lặp cụm`: Kích thước n-gram không được lặp lại, ngăn chặn việc lặp lại cụm từ trong bản dịch. - `Độ dài tối đa`: Độ dài tối đa của bản dịch đầu ra. - `Cỡ chữ`: Kích thước chữ hiển thị trong bản dịch.
- **Thoát (X):** Đóng phần mềm.

### Các bước dịch nhanh

1. Chọn nút **Quét** (hoặc nhấn Esc nếu đang ở chế độ thu nhỏ).
2. Màn hình chuyển sang chế độ mờ.
3. Chọn vùng cần dịch bằng chuột (nên chọn theo câu hoặc đoạn văn, tránh chọn theo danh mục hoặc menu để dịch tốt nhất).
4. Nếu muốn reset màn hình, nhấn nút **Xóa** hoặc Enter.
5. Thu nhỏ phần mềm bằng nút **Thu nhỏ** hoặc Esc.
6. Thoát phần mềm bằng nút **X**.

---

## 👨‍💻 Dev Guide

Ứng dụng dịch thuật màn hình sử dụng bộ não EnViT5 (CTranslate2), Tesseract OCR và giao diện PyQt5.

### 1. Thiết lập Môi trường (Venv)

Để tránh xung đột thư viện và lỗi đường dẫn tuyệt đối, hãy luôn khởi tạo môi trường ảo mới:

```powershell
python -m venv venv
# Kích hoạt:
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Cài đặt Thư viện

Sau khi kích hoạt venv, tiến hành cài đặt các phụ thuộc chính:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> **Lưu ý:** Nếu gặp lỗi DLL load failed khi chạy OpenCV hoặc CTranslate2, hãy cài đặt Microsoft Visual C++ Redistributable.

### 3. Quản lý Phụ thuộc với pipreqs

Khi bạn thêm module mới vào code, hãy dùng pipreqs để cập nhật `requirements.txt`. Do dự án chứa ký tự tiếng Việt, bắt buộc dùng flag encoding:

```powershell
# Tạo lại file requirements (ép kiểu UTF-8)
pipreqs . --force --encoding=utf-8
```

### 4. Đóng gói phần mềm (Packaging)

Sử dụng PyInstaller để đóng gói thành file `.exe`. Vì ứng dụng cần các folder tài nguyên, hãy dùng tham số `--add-data`.

**Lệnh đóng gói chuẩn:**

```powershell
pyinstaller --noconfirm --onedir --windowed --name "EnViT5_Translator" \
    --add-data "model_envit5_fast;model_envit5_fast" \
    --add-data "Tesseract-OCR;Tesseract-OCR" \
    --add-data ".env;." main.py
```

- `--onedir`: Tạo thư mục chứa file chạy (khuyên dùng để dễ quản lý folder model).
- `--windowed`: Tắt màn hình console đen khi mở app.

---

### 5. Lưu ý quan trọng sau khi đóng gói

- **Cấu trúc thư mục:** Đảm bảo folder `model_envit5_fast` và `Tesseract-OCR` nằm cùng cấp với file `.exe`.
- **Quyền truy cập:** Nếu ứng dụng không thực hiện được OCR, hãy thử chạy với quyền Administrator để Tesseract có quyền đọc bộ nhớ tạm.
- **i7 Gen 12 (Hybrid CPU):** Code đã được ép `intra_threads=1` và `OMP_NUM_THREADS=1` để tránh hiện tượng treo (Deadlock) trên kiến trúc nhân P và E của Intel. Đừng tăng thông số này lên trừ khi bạn đã test kỹ trên các dòng chip khác.
- **Tesseract Path:** Trong code, hàm `get_resource_path()` sẽ tự động tìm đường dẫn trong thư mục tạm `_MEIPASS` của PyInstaller, hãy giữ nguyên logic này để app hoạt động trên mọi máy.

---

### 6. Cấu trúc Project

```plaintext
EnViT5_Project/
├── main.py                # File chạy duy nhất
├── model_envit5_fast/     # Chứa model.bin, spiece.model
├── Tesseract-OCR/         # Chứa tesseract.exe và tessdata/
├── .env                   # Chứa HF_TOKEN (nếu cần)
└── requirements.txt       # Danh sách thư viện
```
