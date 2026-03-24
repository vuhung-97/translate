from typing import Dict, Any
from PyQt5.QtWidgets import (
    QDialog, QTextBrowser, QVBoxLayout, QFormLayout, QSpinBox, 
    QDoubleSpinBox, QDialogButtonBox, QComboBox, 
    QPushButton, QHBoxLayout, QWidget
)
from PyQt5.QtCore import Qt

# Import thực thể AI đã được khởi tạo từ engine
from config import DEFAULT_SETTINGS, HELP_DIALOG_HTML

# ================================================================
# 1. CẤU HÌNH MẶC ĐỊNH (IMMUTABLE SETTINGS)
# ================================================================
# Sử dụng MappingProxyType để đảm bảo các giá trị mặc định không bị thay đổi trong quá trình chạy
DEFAULT_SETTINGS = DEFAULT_SETTINGS.copy()

# ================================================================
# 2. DIALOG CÀI ĐẶT HỆ THỐNG
# ================================================================
class SettingsDialog(QDialog):
    """
    Cửa sổ cấu hình các tham số kỹ thuật cho mô hình AI và Giao diện.
    """
    def __init__(self, current_settings: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.settings = current_settings
        self.default_values = DEFAULT_SETTINGS
        
        self.setWindowTitle("Cấu hình bộ não EnViT5")
        self.setFixedSize(450, 350)
        self.apply_styles()
        self.initUI()

    def apply_styles(self):
        """Thiết lập phong cách hiển thị cho các thành phần điều khiển."""
        self.setStyleSheet("""
            QLabel { font-size: 14px; color: #2c3e50; }
            QSpinBox, QDoubleSpinBox, QComboBox { 
                font-size: 14px; padding: 4px; border: 1px solid #bdc3c7; border-radius: 4px;
            }
            QPushButton { font-weight: bold; min-height: 30px; }
        """)

    def initUI(self):
        """Khởi tạo và sắp xếp các widget trong form."""
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        # --- Nhóm tham số AI ---
        self.sb_beam = QSpinBox()
        self.sb_beam.setRange(1, 10)
        self.sb_beam.setToolTip("Giá trị cao giúp dịch hay hơn nhưng chậm hơn.")
        self.sb_beam.setValue(self.settings.get('beam_size', 2))
        form_layout.addRow("Beam Size:", self.sb_beam)

        self.dsb_rep = QDoubleSpinBox()
        self.dsb_rep.setRange(1.0, 3.0)
        self.dsb_rep.setSingleStep(0.1)
        self.dsb_rep.setValue(self.settings.get('repetition_penalty', 1.5))
        form_layout.addRow("Phạt lặp từ:", self.dsb_rep)

        self.sb_ngram = QSpinBox()
        self.sb_ngram.setRange(0, 5)
        self.sb_ngram.setValue(self.settings.get('no_repeat_ngram_size', 3))
        form_layout.addRow("Chặn lặp cụm:", self.sb_ngram)

        self.sb_max = QSpinBox()
        self.sb_max.setRange(50, 512)
        self.sb_max.setValue(self.settings.get('max_decoding_length', 256))
        form_layout.addRow("Độ dài tối đa:", self.sb_max)

        # --- Nhóm hiển thị ---
        self.sb_font = QSpinBox()
        self.sb_font.setRange(8, 40)
        self.sb_font.setValue(self.settings.get('font_size', 14))
        form_layout.addRow("Cỡ chữ hiển thị:", self.sb_font)

        self.cb_theme = QComboBox()
        self.cb_theme.addItems(["Sáng", "Tối"])
        self.cb_theme.setCurrentText(self.settings.get('theme', 'Tối'))
        form_layout.addRow("Chủ đề (Theme):", self.cb_theme)

        main_layout.addLayout(form_layout)

        # --- Thanh nút điều hướng ---
        button_layout = QHBoxLayout()
        
        self.btn_reset = QPushButton("Khôi phục mặc định")
        self.btn_reset.setStyleSheet("background-color: #e67e22; color: white;")
        self.btn_reset.clicked.connect(self.reset_to_defaults)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        button_layout.addWidget(self.btn_reset)
        button_layout.addWidget(self.button_box)
        main_layout.addLayout(button_layout)

    def reset_to_defaults(self):
        """Đặt lại tất cả các widget về giá trị trong DEFAULT_SETTINGS."""
        self.sb_beam.setValue(self.default_values['beam_size'])
        self.dsb_rep.setValue(self.default_values['repetition_penalty'])
        self.sb_ngram.setValue(self.default_values['no_repeat_ngram_size'])
        self.sb_max.setValue(self.default_values['max_decoding_length'])
        self.sb_font.setValue(self.default_values['font_size'])
        self.cb_theme.setCurrentText(self.default_values['theme'])

    def get_values(self) -> Dict[str, Any]:
        """Thu thập dữ liệu từ các widget trả về từ điển cấu hình."""
        return {
            'beam_size': self.sb_beam.value(),
            'repetition_penalty': self.dsb_rep.value(),
            'no_repeat_ngram_size': self.sb_ngram.value(),
            'max_decoding_length': self.sb_max.value(),
            'font_size': self.sb_font.value(),
            'theme': self.cb_theme.currentText()
        }

# ================================================================
# 3. CỬA SỔ HƯỚNG DẪN (HELP DIALOG)
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
        self.text_browser = QTextBrowser()
        html_path = HELP_DIALOG_HTML
        try:
            with open(html_path, encoding="utf-8") as f:
                html_content = f.read()
        except Exception:
            html_content = "<b>Lỗi: Không tìm thấy file hướng dẫn help.html</b>"
        self.text_browser.setHtml(html_content)
        layout.addWidget(self.text_browser)
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
     
     
# ================================================================
# 4. GIAO DIỆN CHÍNH
# ================================================================

class SmartTranslatorUI:
    """Lớp chuyên trách khởi tạo giao diện cho SmartTranslator."""
    def setup_ui(self, target):
        # target ở đây chính là đối tượng SmartTranslator (self)
        target.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        target.setAttribute(Qt.WA_TranslucentBackground)

        # Tạo Panel chính
        target.panel = QWidget(target)
        colors = target._get_theme_config()
        
        target.panel.setStyleSheet(f"""
            QWidget {{ background-color: {colors['panel_bg']}; border-radius: 8px; border: 1px solid {colors['panel_border']}; }}
            QPushButton {{ color: {colors['btn_fg']}; font-weight: bold; border-radius: 4px; padding: 6px 10px; border: none; }}
            QPushButton:hover {{ background-color: {colors['btn_hover']}; }}
        """)

        layout = QHBoxLayout(target.panel)
        layout.setContentsMargins(10, 5, 10, 5)

        # Khởi tạo các nút (Gán trực tiếp vào target để file chính dễ truy cập)
        btn_colors = colors['button_colors']
        
        target._btn_direction = QPushButton("En ➔ Vi")
        target._btn_direction.setStyleSheet(f"background-color: {btn_colors['direction']}; width: 85px;")

        target._btn_quet_toggle = QPushButton("🔍 Quét (Esc)")
        target._btn_quet_toggle.setStyleSheet(f"background-color: {btn_colors['scan']};")

        target._btn_clear = QPushButton("Xóa (Enter)")
        target._btn_clear.setStyleSheet(f"background-color: {btn_colors['clear']};")

        target._btn_help = QPushButton("❓ HDSD")
        target._btn_help.setStyleSheet(f"background-color: {btn_colors['help']};")

        target._btn_settings = QPushButton("⚙️")
        target._btn_settings.setFixedWidth(40)
        target._btn_settings.setStyleSheet(f"background-color: {btn_colors['settings']};")

        target._btn_exit = QPushButton("✕")
        target._btn_exit.setFixedWidth(40)
        target._btn_exit.setStyleSheet(f"background-color: {btn_colors['exit']};")

        # Add widgets
        widgets = [target._btn_direction, target._btn_quet_toggle, 
                   target._btn_clear, target._btn_help, 
                   target._btn_settings, target._btn_exit]
        for w in widgets:
            layout.addWidget(w)