import io
from PIL import Image
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QPoint, QRect, QBuffer, QIODevice
from PyQt5.QtGui import QPainter, QColor, QPen

# Các import từ dự án (giữ nguyên)
from gui.ui_components import SettingsDialog, HelpDialog, SmartTranslatorUI, OverlayManager
from config import DEFAULT_SETTINGS
from gui.theme_config import ThemeConfig
from core.translation_service import TranslationService
# ================================================================
# 1. LỚP ĐIỀU KHIỂN CHÍNH (CONTROLLER)
# ================================================================
class SmartTranslator(QWidget):
    """Lớp điều phối chính - Kết nối UI, Chụp màn hình và Dịch thuật."""
    def __init__(self):
        super().__init__()
        # 1. Khởi tạo dữ liệu & Cấu hình
        self._trans_settings = DEFAULT_SETTINGS.copy()
        self.theme_manager = ThemeConfig()
        
        # 2. Khởi tạo các thành phần chuyên biệt
        self.overlay_manager = OverlayManager(self, self.theme_manager)
        self.trans_service = TranslationService(self._trans_settings)
        
        # 3. Trạng thái giao diện
        self._is_scanning_mode = False
        self._is_selecting = False
        self._start_pt = QPoint()
        self._end_pt = QPoint()
        self._snapshot = None
        self._drag_offset = None

        # 4. Setup UI (Sử dụng builder cũ của bạn)
        self.ui_builder = SmartTranslatorUI()
        self.ui_builder.setup_ui(self)
        self.setFocusPolicy(Qt.StrongFocus)
        self._connect_signals()
        
        self._set_compact_mode()
        self.show()

    def _connect_signals(self):
        self._btn_quet_toggle.clicked.connect(self._toggle_scan_mode)
        self._btn_clear.clicked.connect(self.overlay_manager.clear_all)
        self._btn_direction.clicked.connect(self._switch_direction)
        self._btn_help.clicked.connect(self._open_help)
        self._btn_settings.clicked.connect(self._open_settings)
        self._btn_exit.clicked.connect(QApplication.quit)

    def _switch_direction(self):
        btn_colors = self.theme_manager.get_theme(self._trans_settings.get('theme', 'Tối'))['button_colors']
        if self._trans_settings.get('direction') == 'en-vi':
            self._trans_settings['direction'] = 'vi-en'
            self._btn_direction.setText("Vi ➔ En")
            self._btn_direction.setStyleSheet(f"background-color: {btn_colors['direction_active']}; width: 85px;")
        else:
            self._trans_settings['direction'] = 'en-vi'
            self._btn_direction.setText("En ➔ Vi")
            self._btn_direction.setStyleSheet(f"background-color: {btn_colors['direction']}; width: 85px;")

    def _open_help(self):
        dialog = HelpDialog(self)
        dialog.exec_()

    def _open_settings(self):
        dialog = SettingsDialog(self._trans_settings, self)
        if dialog.exec_():
            self._trans_settings.update(dialog.get_values())

    # --- Logic Chuyển đổi Chế độ ---
    
    def _toggle_scan_mode(self):
        if self._is_scanning_mode:
            self._set_compact_mode()
        else:
            self._set_full_scan_mode()

    def _set_full_scan_mode(self):
        self._is_scanning_mode = True
        # Chụp màn hình trước khi hiện lớp phủ
        self.setWindowOpacity(0)
        QApplication.processEvents()
        self._snapshot = QApplication.primaryScreen().grabWindow(0)
        self.setWindowOpacity(1)
        
        self.setGeometry(QApplication.primaryScreen().geometry())
        self._btn_quet_toggle.setText("🔙 Thu nhỏ (Esc)")
        self._btn_help.setVisible(False)
        self.setFocus()
        self.update()

    def _set_compact_mode(self):
        self._is_scanning_mode = False
        self._btn_quet_toggle.setText("🔍 Quét (Esc)")
        self._btn_help.setVisible(True)
        # Cập nhật trạng thái nút trước rồi mới tính lại kích thước panel để tránh lệch size.
        self.panel.adjustSize()
        self.resize(self.panel.size())
        self.move(0, 0)
        self.setFocus()
        self.update()

    # --- Xử lý Sự kiện Chuột ---

    def mousePressEvent(self, event):
        if self._is_scanning_mode and not self.panel.geometry().contains(event.pos()):
            self._is_selecting = True
            self._start_pt = event.pos()
            self._end_pt = event.pos()
        else:
            self._drag_offset = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        if self._is_selecting:
            self._end_pt = event.pos()
            self.update()
        elif self._drag_offset:
            self.move(event.globalPos() - self._drag_offset)

    def mouseReleaseEvent(self, event):
        if self._is_selecting:
            self._is_selecting = False
            self._handle_selection_done()
        self._drag_offset = None

    def _handle_selection_done(self):
        rect = QRect(self._start_pt, self._end_pt).normalized()
        if rect.width() < 10 or rect.height() < 10: return

        # 1. Cắt ảnh từ snapshot
        buffer = QBuffer()
        buffer.open(QIODevice.ReadWrite)
        self._snapshot.copy(rect).save(buffer, "PNG")
        pil_img = Image.open(io.BytesIO(buffer.data()))

        # 2. Tạo khung hiển thị qua OverlayManager
        target_label = self.overlay_manager.create_result_box(
            rect, self._trans_settings.get('font_size', 12)
        )

        # 3. Yêu cầu TranslationService xử lý
        self.trans_service.process_image(pil_img, target_label)

    # --- Vẽ giao diện ---

    def paintEvent(self, event):
        if not self._is_scanning_mode: return
        
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120)) # Lớp phủ mờ
        
        if self._is_selecting:
            pen = QPen(QColor("#2ecc71"), 2, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRoundedRect(QRect(self._start_pt, self._end_pt).normalized(), 10, 10)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self._toggle_scan_mode()
            event.accept()
            return

        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.overlay_manager.clear_all()
            event.accept()
            return

        super().keyPressEvent(event)