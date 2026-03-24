import io
from PIL import Image
from PyQt5.QtWidgets import (QWidget, QScrollArea, QLabel, QApplication)
from PyQt5.QtCore import Qt, QPoint, QRect, QBuffer, QIODevice
from PyQt5.QtGui import QPainter, QColor, QPen

# Import các tiện ích hỗ trợ từ dự án
from core.ocr_utils import clean_image_for_ocr, perform_ocr
from gui.ui_components import SettingsDialog, HelpDialog, SmartTranslatorUI
from config import DEFAULT_SETTINGS
from gui.theme_config import ThemeConfig
from core.engine import TranslationWorker

# ================================================================
# 2. GIAO DIỆN CHÍNH (MAIN WINDOW)
# ================================================================
class SmartTranslator(QWidget):
    """Ứng dụng chính điều khiển việc quét và dịch thuật màn hình."""
    def __init__(self):
        super().__init__()
        self._trans_settings = DEFAULT_SETTINGS.copy()
        self._theme_config = ThemeConfig()
        
        # 1. Gọi lớp giao diện để dựng khung
        self.ui_builder = SmartTranslatorUI()
        self.ui_builder.setup_ui(self)
        
        # 2. Kết nối logic xử lý (Signals & Slots)
        self._connect_signals()
        
        # 3. Trạng thái ban đầu
        self._is_enlarged = False
        self._selecting = False      # Trạng thái đang giữ chuột kéo vùng chọnself._start_point = QPoint()
        self._end_point = QPoint()
        self._result_labels = []     # Danh sách quản lý các khung kết quả
        self._drag_pos = None        # Vị trí để di chuyển thanh công cụ

        self._shrink_ui()
        self.show()

    def _connect_signals(self):
        """Tách riêng việc kết nối nút bấm với hàm xử lý."""
        self._btn_direction.clicked.connect(self._switch_direction)
        self._btn_quet_toggle.clicked.connect(self._toggle_mode)
        self._btn_clear.clicked.connect(self._clear_results)
        self._btn_help.clicked.connect(self._open_help)
        self._btn_settings.clicked.connect(self._open_settings)
        self._btn_exit.clicked.connect(QApplication.quit)

    # ================================================================
    # XỬ LÝ SỰ KIỆN & CHỨC NĂNG
    # ================================================================

    def _switch_direction(self):
        """Đổi chiều dịch nhanh giữa Anh-Việt và Việt-Anh."""
        btn_colors = self._get_theme_config()['button_colors']
        if self._trans_settings['direction'] == 'en-vi':
            self._trans_settings['direction'] = 'vi-en'
            self._btn_direction.setText("Vi ➔ En")
            self._btn_direction.setStyleSheet(f"background-color: {btn_colors['direction_active']}; width: 85px;")
        else:
            self._trans_settings['direction'] = 'en-vi'
            self._btn_direction.setText("En ➔ Vi")
            self._btn_direction.setStyleSheet(f"background-color: {btn_colors['direction']}; width: 85px;")

    def _open_help(self):
        """Mở cửa sổ hướng dẫn sử dụng HTML."""
        dialog = HelpDialog(self)
        dialog.exec_()

    def _open_settings(self):
        """Mở cửa sổ cấu hình thông số AI."""
        dialog = SettingsDialog(self._trans_settings, self)
        if dialog.exec_(): 
            new_settings = dialog.get_values()
            self._trans_settings.update(new_settings) # Cập nhật settings mới

    def _clear_results(self):
        """Xóa toàn bộ các khung dịch trên màn hình."""
        for label in self._result_labels:
            label.deleteLater()
        self._result_labels = []

    # ================================================================
    # QUẢN LÝ CHẾ ĐỘ QUÉT (SCREENSHOT LOGIC)
    # ================================================================

    def _toggle_mode(self):
        """Chuyển đổi giữa chế độ điều khiển và chế độ quét màn hình."""
        if not self._is_enlarged:
            self._enlarge_ui()
        else:
            self._shrink_ui()

    def _update_ui_state(self, is_enlarged):
        """Extract Method: Cập nhật toàn bộ văn bản và trạng thái các nút."""
        text = "🔙 Thu nhỏ (Esc)" if is_enlarged else "🔍 Quét (Esc)"
        self._btn_quet_toggle.setText(text)
        self._btn_help.setVisible(not is_enlarged)

    def _enlarge_ui(self):
        """Refactored: Chuyển sang chế độ quét toàn màn hình."""
        self._is_enlarged = True
        self._update_ui_state(True)
        self._full_screen_snapshot = self._capture_clean_screen()
        self.setGeometry(QApplication.primaryScreen().geometry())
        self.setFocus()
        self.update()

    def _shrink_ui(self):
        """Refactored: Thu nhỏ về thanh công cụ."""
        self._is_enlarged = False
        self._update_ui_state(False)
        self.panel.adjustSize()
        self.setGeometry(self.x(), self.y(), self.panel.width(), self.panel.height())
        self.update()

    def _capture_clean_screen(self):
        """Extract Method: Logic chụp màn hình không dính thanh công cụ."""
        self.setWindowOpacity(0)
        QApplication.processEvents() # Đảm bảo cửa sổ kịp ẩn đi
        screen = QApplication.primaryScreen()
        snapshot = screen.grabWindow(0)
        self.setWindowOpacity(1)
        return snapshot

    # ================================================================
    # XỬ LÝ CHUỘT & VẼ VÙNG CHỌN
    # ================================================================

    def mousePressEvent(self, event):
        if self._is_enlarged and event.button() == Qt.LeftButton:
            if not self.panel.geometry().contains(event.pos()):
                self._selecting = True
                self._start_point = event.pos()
                self._end_point = event.pos()
            else:
                self._drag_pos = event.globalPos() - self.pos()
        else:
            self._drag_pos = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        if self._selecting: 
            self._end_point = event.pos()
            self.update() # Vẽ lại vùng chọn xanh
        elif self._drag_pos: 
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        if self._selecting:
            self._selecting = False
            self._prepare_translation() # Thực hiện dịch
        self._drag_pos = None

    def paintEvent(self, event):
        """Hàm gốc giờ chỉ đóng vai trò điều phối việc vẽ lớp phủ và vùng chọn, tách riêng logic vẽ ra các hàm chuyên biệt."""
        if not self._is_enlarged:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self._draw_overlay(painter)
        if self._selecting:
            self._draw_selection_rectangle(painter)

    def _draw_overlay(self, painter):
        """Tách riêng logic vẽ lớp phủ mờ."""
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

    def _draw_selection_rectangle(self, painter):
        """Tách riêng logic vẽ khung chọn vùng (Dashed line & Rounded)."""
        pen = QPen(QColor(46, 204, 113), 2, Qt.DashLine)
        painter.setPen(pen)
        rect = QRect(self._start_point, self._end_point).normalized()
        painter.drawRoundedRect(rect, 8, 8)

    def keyPressEvent(self, event):
        """Xử lý phím tắt nhanh."""
        if event.key() == Qt.Key_Escape:
            self._toggle_mode()
        elif event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            self._clear_results()

    # ================================================================
    # CORE: XỬ LÝ DỊCH THUẬT (TRANSLATION LOGIC)
    # ================================================================

    def _prepare_translation(self):
        """Điều phối luồng dữ liệu từ Ảnh -> Chữ -> Bản dịch."""
        rect = QRect(self._start_point, self._end_point).normalized()
        if rect.width() < 10 or rect.height() < 10: 
            return
        pil_img = self._capture_region_to_pil(rect)
        clean_text = self._get_text_from_image(pil_img)
        if clean_text:
            self._start_translation_worker(clean_text, rect)

    def _capture_region_to_pil(self, rect):
        """Chuyển đổi vùng chụp màn hình sang định dạng PIL Image."""
        crop_pixmap = self._full_screen_snapshot.copy(rect)
        buffer = QBuffer()
        buffer.open(QIODevice.ReadWrite)
        crop_pixmap.save(buffer, "PNG")
        return Image.open(io.BytesIO(buffer.data()))

    def _get_text_from_image(self, pil_img):
        """Xử lý hậu kỳ ảnh và gọi OCR."""
        processed_img = clean_image_for_ocr(pil_img)
        ocr_lang = 'vie' if self._trans_settings.get('direction') == 'vi-en' else 'eng'
        return perform_ocr(processed_img, lang=ocr_lang)

    def _start_translation_worker(self, text, rect):
        """Khởi tạo và quản lý luồng dịch ngầm."""
        label = self._add_result_label(rect.x(), rect.y(), rect.width(), rect.height(), "⏳ Đang dịch...") 
        self._worker = TranslationWorker(text, rect.x(), rect.y(), rect.width(), self._trans_settings)
        self._worker.finished.connect(lambda result: label.setText(result))
        self._worker.start()

    def _get_theme_config(self):
        theme = self._trans_settings.get('theme', 'Tối')
        return self._theme_config.get_theme(theme) or self._theme_config.get_theme('Tối')

    def _apply_result_style(self, widget, colors):
        """Extract Method: Chuyên biệt hóa việc định dạng CSS cho khung kết quả."""
        widget.setStyleSheet(f"""
            QScrollArea {{ 
                border: 2px solid {colors['accent']}; 
                border-radius: 12px; 
                background-color: {colors['bg']};
            }}
            QScrollBar:vertical {{
                border: none; background: transparent; width: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {colors['accent']}; border-radius: 2px;
            }}
        """)

    def _add_result_label(self, x, y, w, h, text):
        """
        Refactored: Hàm chính giờ chỉ điều phối việc tạo và hiển thị.
        """
        colors = self._get_theme_config()
        scroll = QScrollArea(self)
        scroll.setGeometry(x, y, max(w, 160), max(h, 60))
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._apply_result_style(scroll, colors)
        label = self._create_result_content(text, colors)
        scroll.setWidget(label)
        scroll.show()
        self._result_labels.append(scroll)
        return label

    def _create_result_content(self, text, colors):
        """Extract Method: Tập trung vào việc tạo và định dạng Label văn bản."""
        label = QLabel(text)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        font_size = self._trans_settings.get('font_size', 12)
        
        label.setStyleSheet(f"""
            padding: 10px; 
            color: {colors['text']}; 
            font-size: {font_size}px; 
            background-color: transparent; 
            border: none;
        """)
        return label