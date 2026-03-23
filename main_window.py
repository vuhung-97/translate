import io
from PIL import Image
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QHBoxLayout, QScrollArea, QLabel, 
    QApplication, QDialog, QVBoxLayout, QTextBrowser, 
    QDialogButtonBox
)
from PyQt5.QtCore import Qt, QPoint, QRect, QBuffer, QIODevice
from PyQt5.QtGui import QPainter, QColor, QPen

# Import các tiện ích hỗ trợ từ dự án
from ocr_utils import clean_image_for_ocr, perform_ocr
from ui_components import SettingsDialog, TranslationWorker
from config import DEFAULT_SETTINGS

# ================================================================
# 1. CỬA SỔ HƯỚNG DẪN (HELP DIALOG)
# ================================================================
class HelpDialog(QDialog):
    """Hiển thị hướng dẫn sử dụng chi tiết bằng HTML."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hướng dẫn sử dụng EnViT5")
        self.setFixedSize(520, 620)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Sử dụng QTextBrowser để hiển thị nội dung có định dạng HTML
        self.text_browser = QTextBrowser()
        
        self.text_browser.setHtml("""
            <div style='font-family: Arial, sans-serif; font-size: 16px; line-height: 1.8; color: #2c3e50; padding: 10px;'>
                <h1 style='color: #27ae60; text-align: center; border-bottom: 2px solid #27ae60; padding-bottom: 10px;'>
                    🚀 Hướng dẫn Sử dụng EnViT5
                </h1>

                <p style='font-size: 18px; text-align: center; color: #7f8c8d;'>
                    <i>Giải pháp dịch thuật màn hình thông minh, tối ưu cho tiếng Việt.</i>
                </p>

                <h3 style='background-color: #ecf0f1; padding: 10px; border-left: 5px solid #2980b9; color: #2980b9;'>
                    📍 BƯỚC 1: CÁCH QUÉT DỊCH
                </h3>
                <ol style='margin-left: 20px;'>
                    <li><b>Kích hoạt:</b> Nhấn nút <span style='color: #27ae60;'><b>🔍 Quét</b></span> trên thanh công cụ hoặc nhấn phím tắt <span style='background-color: #f39c12; color: white; padding: 2px 6px; border-radius: 4px;'><b>ESC</b></span>. Màn hình sẽ tối lại và "đóng băng" để bạn chọn vùng.</li>
                    <li><b>Chọn vùng:</b> Nhấn giữ <b>Chuột Trái</b> và kéo để tạo một vùng bao quanh đoạn văn bản tiếng Anh bạn muốn dịch.</li>
                    <li><b>Kết quả:</b> Thả chuột, hệ thống sẽ tự động nhận diện chữ và hiển thị bản dịch tiếng Việt ngay tại vị trí đó sau vài giây.</li>
                    <li><b>Lưu ý:</b> Nên chọn một đoạn hoặc câu văn đầy đủ để dịch sát nghĩa nhất</li>
                </ol>

                <h3 style='background-color: #ecf0f1; padding: 10px; border-left: 5px solid #e67e22; color: #e67e22;'>
                    ⌨️ PHÍM TẮT QUAN TRỌNG
                </h3>
                <div style='margin-left: 10px; padding: 10px; border: 1px dashed #bdc3c7; border-radius: 8px;'>
                    <p>🔹 <span style='background-color: #f39c12; color: white; padding: 2px 8px; border-radius: 4px;'><b>ESC</b></span> : 
                        <b>Quét / Thu nhỏ</b> - Bật hoặc tắt chế độ đóng băng màn hình để bắt đầu chọn vùng dịch mới.</p>
                    <p>🔹 <span style='background-color: #e67e22; color: white; padding: 2px 8px; border-radius: 4px;'><b>ENTER</b></span> : 
                        <b>Xóa</b> - Xóa nhanh tất cả các khung bản dịch đang hiển thị trên màn hình để làm sạch không gian làm việc.</p>
                </div>

                <h3 style='background-color: #ecf0f1; padding: 10px; border-left: 5px solid #8e44ad; color: #8e44ad;'>
                    ⚙️ CẤU HÌNH AI (SETTINGS)
                </h3>
                <ul style='margin-left: 20px;'>
                    <li><b>Beam Size:</b> Điều chỉnh độ sâu tìm kiếm (cao = tốt hơn nhưng chậm hơn).</li>
                    <li><b>Phạt lặp:</b> Ngăn chặn tình trạng AI dịch quẩn quanh một cụm từ.</li>
                    <li><b>Cỡ chữ & Theme:</b> Tùy chỉnh hiển thị kết quả.</li>
                </ul>

                <br>
                <div style='background-color: #2ecc71; color: white; text-align: center; padding: 15px; border-radius: 10px;'>
                    <b>Mẹo:</b> Bạn có thể di chuyển thanh công cụ bằng cách kéo vùng trống của thanh đi!
                </div>
            </div>
        """)
        layout.addWidget(self.text_browser)

        # Nút đóng cửa sổ
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


# ================================================================
# 2. GIAO DIỆN CHÍNH (MAIN WINDOW)
# ================================================================
class SmartTranslator(QWidget):
    """Ứng dụng chính điều khiển việc quét và dịch thuật màn hình."""
    def __init__(self):
        super().__init__()
        
        # 1. Khởi tạo cấu hình mặc định
        self.trans_settings = DEFAULT_SETTINGS.copy()
        
        # 2. Khởi tạo trạng thái giao diện
        self.is_enlarged = False    # Chế độ đang quét toàn màn hình
        self.selecting = False      # Trạng thái đang giữ chuột kéo vùng chọn
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.result_labels = []     # Danh sách quản lý các khung kết quả
        self.drag_pos = None        # Vị trí để di chuyển thanh công cụ
        
        self.initUI()

    def initUI(self):
        """Thiết lập giao diện thanh công cụ điều khiển."""
        # Cấu hình cửa sổ: Luôn trên cùng, không viền, dạng Tool
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Tạo Panel chính chứa các nút bấm
        self.panel = QWidget(self)
        self.panel.setStyleSheet("""
            QWidget { background-color: #2c3e50; border-radius: 8px; border: 1px solid white; }
            QPushButton { color: white; font-weight: bold; border-radius: 4px; padding: 6px 10px; border: none; }
            QPushButton:hover { background-color: #34495e; }
        """)
        
        layout = QHBoxLayout(self.panel)
        layout.setContentsMargins(10, 5, 10, 5)

        # --- Danh sách các nút chức năng ---
        
        # 1. Nút chuyển đổi chiều dịch
        self.btn_direction = QPushButton("En ➔ Vi")
        self.btn_direction.setStyleSheet("background-color: #8e44ad; width: 85px;")
        self.btn_direction.clicked.connect(self.switch_direction)

        # 2. Nút kích hoạt Quét
        self.btn_quet_toggle = QPushButton("🔍 Quét (Esc)")
        self.btn_quet_toggle.setStyleSheet("background-color: #27ae60;")
        self.btn_quet_toggle.clicked.connect(self.toggle_mode)
        
        # 3. Nút Xóa nhanh kết quả
        btn_clear = QPushButton("Xóa (Enter)")
        btn_clear.setStyleSheet("background-color: #e67e22;")
        btn_clear.clicked.connect(self.clear_results)
        
        # 4. Nút Hướng dẫn sử dụng
        self.btn_help = QPushButton("❓ HDSD")
        self.btn_help.setStyleSheet("background-color: #675820;") 
        self.btn_help.clicked.connect(self.open_help)

        # 5. Nút Cài đặt (⚙️)
        btn_settings = QPushButton("⚙️")
        btn_settings.setFixedWidth(40)
        btn_settings.setStyleSheet("background-color: #7f8c8d;")
        btn_settings.clicked.connect(self.open_settings)
        
        # 6. Nút Thoát ứng dụng
        btn_exit = QPushButton("✕")
        btn_exit.setFixedWidth(40)
        btn_exit.setStyleSheet("background-color: #c0392b;")
        btn_exit.clicked.connect(QApplication.quit)
        
        # Thêm các thành phần vào Layout
        for widget in [self.btn_direction, self.btn_quet_toggle, btn_clear, self.btn_help, btn_settings, btn_exit]:
            layout.addWidget(widget)
        
        self.shrink_ui() # Bắt đầu ở trạng thái thu nhỏ
        self.show()

    # ================================================================
    # XỬ LÝ SỰ KIỆN & CHỨC NĂNG
    # ================================================================

    def switch_direction(self):
        """Đổi chiều dịch nhanh giữa Anh-Việt và Việt-Anh."""
        if self.trans_settings['direction'] == 'en-vi':
            self.trans_settings['direction'] = 'vi-en'
            self.btn_direction.setText("Vi ➔ En")
            self.btn_direction.setStyleSheet("background-color: #2980b9; width: 85px;")
        else:
            self.trans_settings['direction'] = 'en-vi'
            self.btn_direction.setText("En ➔ Vi")
            self.btn_direction.setStyleSheet("background-color: #8e44ad; width: 85px;")

    def open_help(self):
        """Mở cửa sổ hướng dẫn sử dụng HTML."""
        dialog = HelpDialog(self)
        dialog.exec_()

    def open_settings(self):
        """Mở cửa sổ cấu hình thông số AI."""
        dialog = SettingsDialog(self.trans_settings, self)
        if dialog.exec_(): 
            new_settings = dialog.get_values()
            self.trans_settings.update(new_settings) # Cập nhật settings mới

    def clear_results(self):
        """Xóa toàn bộ các khung dịch trên màn hình."""
        for label in self.result_labels:
            label.deleteLater()
        self.result_labels = []

    # ================================================================
    # QUẢN LÝ CHẾ ĐỘ QUÉT (SCREENSHOT LOGIC)
    # ================================================================

    def toggle_mode(self):
        """Chuyển đổi giữa chế độ điều khiển và chế độ quét màn hình."""
        if not self.is_enlarged:
            self.enlarge_ui()
        else:
            self.shrink_ui()

    def enlarge_ui(self):
        """Phóng to ra toàn màn hình để bắt đầu chọn vùng dịch."""
        self.is_enlarged = True
        self.btn_quet_toggle.setText("🔙 Thu nhỏ (Esc)")
        
        # Bước 1: Ẩn thanh công cụ tạm thời để chụp ảnh sạch màn hình
        self.setWindowOpacity(0)
        QApplication.processEvents()
        
        # Bước 2: Chụp toàn bộ màn hình
        screen = QApplication.primaryScreen()
        self.full_screen_snapshot = screen.grabWindow(0)
        
        # Bước 3: Hiện lại và phóng to toàn màn hình
        self.setWindowOpacity(1)
        self.setGeometry(QApplication.primaryScreen().geometry())
        self.setFocus()
        self.update()

    def shrink_ui(self):
        """Thu nhỏ về thanh công cụ điều khiển."""
        self.is_enlarged = False
        self.btn_quet_toggle.setText("🔍 Quét (Esc)")
        self.panel.adjustSize()
        self.setGeometry(self.x(), self.y(), self.panel.width(), self.panel.height())
        self.update()

    # ================================================================
    # XỬ LÝ CHUỘT & VẼ VÙNG CHỌN
    # ================================================================

    def mousePressEvent(self, event):
        if self.is_enlarged and event.button() == Qt.LeftButton:
            # Nếu không nhấn vào thanh công cụ -> Bắt đầu chọn vùng
            if not self.panel.geometry().contains(event.pos()):
                self.selecting = True
                self.start_point = event.pos()
                self.end_point = event.pos()
            else:
                self.drag_pos = event.globalPos() - self.pos()
        else:
            self.drag_pos = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        if self.selecting: 
            self.end_point = event.pos()
            self.update() # Vẽ lại vùng chọn xanh
        elif self.drag_pos: 
            self.move(event.globalPos() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        if self.selecting:
            self.selecting = False
            self.prepare_translation() # Thực hiện dịch
        self.drag_pos = None

    def paintEvent(self, event):
        """Vẽ lớp overlay tối và hình chữ nhật vùng chọn với nét đứt và bo góc."""
        if self.is_enlarged:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing) # Bật khử răng cưa để bo góc mượt hơn
            
            # Vẽ nền tối mờ cho toàn màn hình
            painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
            
            if self.selecting:
                # 1. Thiết lập bút vẽ: Màu xanh lá, độ dày 2, NÉT ĐỨT (Qt.DashLine)
                pen = QPen(QColor(46, 204, 113), 2, Qt.DashLine)
                painter.setPen(pen)
                
                # 2. Vẽ hình chữ nhật BO GÓC (Rounded Rect)
                # Tham số 8, 8 là bán kính bo góc (x_radius, y_radius)
                rect = QRect(self.start_point, self.end_point).normalized()
                painter.drawRoundedRect(rect, 8, 8)

    def keyPressEvent(self, event):
        """Xử lý phím tắt nhanh."""
        if event.key() == Qt.Key_Escape:
            self.toggle_mode()
        elif event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            self.clear_results()

    # ================================================================
    # CORE: XỬ LÝ DỊCH THUẬT (TRANSLATION LOGIC)
    # ================================================================

    def prepare_translation(self):
        """Cắt ảnh vùng chọn, xử lý OCR và gửi cho AI dịch."""
        rect = QRect(self.start_point, self.end_point).normalized()
        if rect.width() < 10 or rect.height() < 10: return

        # 1. Trích xuất ảnh từ vùng chọn
        crop_pixmap = self.full_screen_snapshot.copy(rect)
        buffer = QBuffer()
        buffer.open(QIODevice.ReadWrite)
        crop_pixmap.save(buffer, "PNG")
        pil_img = Image.open(io.BytesIO(buffer.data()))

        # 2. Tiền xử lý ảnh & OCR
        processed_img = clean_image_for_ocr(pil_img)
        
        # Xác định ngôn ngữ OCR dựa trên chiều dịch
        ocr_lang = 'vie' if self.trans_settings.get('direction') == 'vi-en' else 'eng'
        clean_text = perform_ocr(processed_img, lang=ocr_lang)

        # 3. Gửi văn bản cho luồng dịch thuật (Worker)
        if clean_text:
            label = self.add_result_label(rect.x(), rect.y(), rect.width(), rect.height(), "⏳ Đang dịch...") 
            
            # Khởi tạo Worker để dịch ngầm (không treo UI)
            self.worker = TranslationWorker(clean_text, rect.x(), rect.y(), rect.width(), self.trans_settings)
            
            # Kết nối tín hiệu khi dịch xong
            self.worker.finished.connect(lambda result, x, y, w: label.setText(result))
            self.worker.start()

    def add_result_label(self, x, y, w, h, text):
        """Tạo khung hiển thị kết quả với thiết kế bo góc và đổ bóng nhẹ."""
        theme = self.trans_settings.get('theme', 'Tối')
        bg_color = "#2d2d2d" if theme == "Tối" else "#ffffff"
        text_color = "#e0e0e0" if theme == "Tối" else "#1a1a1a"
        
        # Tạo vùng cuộn (Scroll Area)
        scroll = QScrollArea(self)
        scroll.setGeometry(x, y, max(w, 160), max(h, 60))
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Thiết kế CSS: Bo góc 12px cho khung hiển thị
        scroll.setStyleSheet(f"""
            QScrollArea {{ 
                border: 2px solid #27ae60; 
                border-radius: 12px; 
                background-color: {bg_color};
            }}
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: #27ae60;
                border-radius: 2px;
            }}
        """)
        
        # Nhãn chứa văn bản (cũng cần bo góc hoặc nền trong suốt để không đè lên khung ngoài)
        label = QLabel(text)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        label.setStyleSheet(f"""
            padding: 10px; 
            color: {text_color}; 
            font-size: {self.trans_settings['font_size']}px; 
            background-color: transparent; 
            border: none;
        """)
        
        scroll.setWidget(label)
        scroll.show()
        self.result_labels.append(scroll) 
        return label