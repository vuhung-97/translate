"""
Cửa sổ cấu hình các thông số AI, OCR Engine và Giao diện.
"""

from typing import Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QSpinBox, QDoubleSpinBox,
    QComboBox, QPushButton, QHBoxLayout, QDialogButtonBox
)
from config import config_manager, DEFAULT_SETTINGS
from utils.logger import logger


class SettingsDialog(QDialog):
    """Cửa sổ cài đặt hệ thống SmartTranslator."""

    def __init__(self, current_settings: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.settings = current_settings
        self.default_values = DEFAULT_SETTINGS

        self.setWindowTitle("Cấu hình AI & Giao diện")
        self.setFixedSize(460, 390)
        self.controls = {}
        self._apply_styles()
        self._init_ui()

    def _apply_styles(self):
        self.setStyleSheet("""
            QLabel { 
                font-size: 14px; 
                color: #2c3e50; 
            }
            QSpinBox, QDoubleSpinBox, QComboBox { 
                font-size: 14px; 
                padding: 4px; 
                border: 1px solid #bdc3c7; 
                border-radius: 4px;
            }
            QPushButton { 
                font-weight: bold; 
                min-height: 30px; 
            }
        """)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        # 1. OCR Engine Choice
        self.controls["ocr_engine"] = QComboBox()
        self.controls["ocr_engine"].addItems(["tesseract", "easyocr"])
        current_ocr = self.settings.get("ocr_engine", "tesseract")
        self.controls["ocr_engine"].setCurrentText(current_ocr.lower())
        self.controls["ocr_engine"].setToolTip("Lựa chọn công cụ nhận diện chữ (Tesseract hoặc EasyOCR).")
        form_layout.addRow("OCR Engine:", self.controls["ocr_engine"])

        # 2. AI Parameters
        self.controls["beam_size"] = QSpinBox()
        self.controls["beam_size"].setRange(1, 10)
        self.controls["beam_size"].setToolTip("Giá trị cao giúp dịch tốt hơn nhưng chậm hơn.")
        self.controls["beam_size"].setValue(int(self.settings.get("beam_size", 5)))
        form_layout.addRow("Beam Size:", self.controls["beam_size"])

        self.controls["repetition_penalty"] = QDoubleSpinBox()
        self.controls["repetition_penalty"].setRange(1.0, 3.0)
        self.controls["repetition_penalty"].setSingleStep(0.1)
        self.controls["repetition_penalty"].setToolTip("Phạt lặp từ giúp giảm lặp từ trong câu.")
        self.controls["repetition_penalty"].setValue(float(self.settings.get("repetition_penalty", 1.5)))
        form_layout.addRow("Phạt lặp từ:", self.controls["repetition_penalty"])

        self.controls["no_repeat_ngram_size"] = QSpinBox()
        self.controls["no_repeat_ngram_size"].setRange(0, 5)
        self.controls["no_repeat_ngram_size"].setValue(int(self.settings.get("no_repeat_ngram_size", 3)))
        form_layout.addRow("Chặn lặp cụm (ngram):", self.controls["no_repeat_ngram_size"])

        self.controls["max_decoding_length"] = QSpinBox()
        self.controls["max_decoding_length"].setRange(50, 512)
        self.controls["max_decoding_length"].setValue(int(self.settings.get("max_decoding_length", 256)))
        form_layout.addRow("Độ dài tối đa:", self.controls["max_decoding_length"])

        # 3. UI Display Parameters
        self.controls["font_size"] = QSpinBox()
        self.controls["font_size"].setRange(8, 40)
        self.controls["font_size"].setValue(int(self.settings.get("font_size", 17)))
        form_layout.addRow("Cỡ chữ hiển thị:", self.controls["font_size"])

        self.controls["theme"] = QComboBox()
        self.controls["theme"].addItems(["Sáng", "Tối"])
        self.controls["theme"].setCurrentText(self.settings.get("theme", "Sáng"))
        form_layout.addRow("Chủ đề (Theme):", self.controls["theme"])

        main_layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.btn_reset = QPushButton("Khôi phục mặc định")
        self.btn_reset.setStyleSheet("background-color: #e67e22; color: white;")
        self.btn_reset.clicked.connect(self.reset_to_defaults)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.save_and_accept)
        self.button_box.rejected.connect(self.reject)

        button_layout.addWidget(self.btn_reset)
        button_layout.addWidget(self.button_box)
        main_layout.addLayout(button_layout)

    def save_and_accept(self):
        new_values = self.get_values()
        config_manager.save_settings(new_values)
        logger.info("Đã lưu cấu hình mới từ SettingsDialog.")
        self.accept()

    def reset_to_defaults(self):
        for key, widget in self.controls.items():
            if key in self.default_values:
                if isinstance(widget, QComboBox):
                    widget.setCurrentText(str(self.default_values[key]))
                else:
                    widget.setValue(self.default_values[key])

    def get_values(self) -> Dict[str, Any]:
        result = {}
        for key, widget in self.controls.items():
            if isinstance(widget, QComboBox):
                result[key] = widget.currentText()
            else:
                result[key] = widget.value()
        return result
