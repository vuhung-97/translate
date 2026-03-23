# ui_components.py
from typing import Dict, Any
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QSpinBox, 
    QDoubleSpinBox, QDialogButtonBox, QComboBox, 
    QPushButton, QHBoxLayout
)
from PyQt5.QtCore import QThread, pyqtSignal

# Import thực thể AI đã được khởi tạo từ engine
from engine import ai_engine
from config import DEFAULT_SETTINGS

# ================================================================
# 1. CẤU HÌNH MẶC ĐỊNH (IMMUTABLE SETTINGS)
# ================================================================
# Sử dụng MappingProxyType để đảm bảo các giá trị mặc định không bị thay đổi trong quá trình chạy
DEFAULT_SETTINGS = DEFAULT_SETTINGS

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
# 3. LUỒNG XỬ LÝ DỊCH THUẬT (BACKGROUND WORKER)
# ================================================================
class TranslationWorker(QThread):
    """
    Luồng xử lý riêng biệt để thực hiện dịch thuật mà không gây treo giao diện chính (UI).
    """
    # Tín hiệu phát ra khi dịch xong: (kết quả, x, y, width)
    finished = pyqtSignal(str, int, int, int)

    def __init__(self, text: str, x: int, y: int, w: int, settings: Dict[str, Any]):
        super().__init__()
        self.text = text
        self.x, self.y, self.w = x, y, w
        self.settings = settings

    def run(self):
        """Thực thi tác vụ dịch thuật trong luồng phụ."""
        try:
            # Gọi hàm dịch từ engine trung tâm
            result = ai_engine.translate_text(self.text, self.settings)
            self.finished.emit(result, self.x, self.y, self.w)
        except Exception as e:
            # Trả về thông báo lỗi nếu quá trình dịch thất bại
            self.finished.emit(f"⚠️ Lỗi AI: {str(e)}", self.x, self.y, self.w)