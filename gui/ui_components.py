# pylint: disable=missing-function-docstring, missing-class-docstring, missing-module-docstring, too-few-public-methods, no-name-in-module, import-error
from typing import Dict, Any
from PyQt5.QtWidgets import (
    QDialog,
    QScrollArea,
    QTextBrowser,
    QVBoxLayout,
    QFormLayout,
    QSpinBox,
    QDoubleSpinBox,
    QDialogButtonBox,
    QComboBox,
    QPushButton,
    QHBoxLayout,
    QWidget,
    QLabel,
)
from PyQt5.QtCore import Qt

# Import thực thể AI đã được khởi tạo từ engine
from config import SETTINGS, HELP_DIALOG_HTML, save_settings



# ================================================================
# 1. DIALOG CÀI ĐẶT HỆ THỐNG
# ================================================================
class SettingsDialog(QDialog):
    """
    Cửa sổ cấu hình các tham số kỹ thuật cho mô hình AI và Giao diện.
    """

    def __init__(self, current_settings: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.settings = current_settings
        self.default_values = SETTINGS

        self.setWindowTitle("Cấu hình bộ não EnViT5")
        self.setFixedSize(450, 350)
        self.apply_styles()
        self.controls = {}
        self.initUI()

    def apply_styles(self):
        """Thiết lập phong cách hiển thị cho các thành phần điều khiển."""
        self.setStyleSheet("""
            QLabel { 
                font-size: 14px; 
                color: #2c3e50; }
            QSpinBox, 
            QDoubleSpinBox, 
            QComboBox { 
                font-size: 14px; 
                padding: 4px; 
                border: 1px solid #bdc3c7; 
                border-radius: 4px;
            }
            QPushButton { 
                font-weight: bold; 
                min-height: 30px; }
        """)

    def initUI(self):
        """Khởi tạo và sắp xếp các widget trong form."""
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        # --- Nhóm tham số AI ---
        self.controls["beam_size"] = QSpinBox()
        self.controls["beam_size"].setRange(1, 10)
        self.controls["beam_size"].setToolTip(
            "Giá trị cao giúp dịch hay hơn nhưng chậm hơn."
        )
        self.controls["beam_size"].setValue(self.settings.get("beam_size", 2))
        form_layout.addRow("Beam Size:", self.controls["beam_size"])

        self.controls["repetition_penalty"] = QDoubleSpinBox()
        self.controls["repetition_penalty"].setRange(1.0, 3.0)
        self.controls["repetition_penalty"].setToolTip(
            "Giá trị cao giúp giảm lặp từ nhưng có thể làm dịch cứng hơn."
        )
        self.controls["repetition_penalty"].setSingleStep(0.1)
        self.controls["repetition_penalty"].setValue(
            self.settings.get("repetition_penalty", 1.5)
        )
        form_layout.addRow("Phạt lặp từ:", self.controls["repetition_penalty"])

        self.controls["no_repeat_ngram_size"] = QSpinBox()
        self.controls["no_repeat_ngram_size"].setRange(0, 5)
        self.controls["no_repeat_ngram_size"].setToolTip(
            "Giá trị >0 giúp chặn lặp cụm từ, nhưng có thể làm dịch cứng hơn."
        )
        self.controls["no_repeat_ngram_size"].setValue(
            self.settings.get("no_repeat_ngram_size", 3)
        )
        form_layout.addRow("Chặn lặp cụm:", self.controls["no_repeat_ngram_size"])

        self.controls["max_decoding_length"] = QSpinBox()
        self.controls["max_decoding_length"].setRange(50, 512)
        self.controls["max_decoding_length"].setToolTip(
            "Độ dài tối đa của chuỗi đầu ra."
        )

        self.controls["max_decoding_length"].setValue(
            self.settings.get("max_decoding_length", 256)
        )
        form_layout.addRow("Độ dài tối đa:", self.controls["max_decoding_length"])

        # --- Nhóm hiển thị ---
        self.controls["font_size"] = QSpinBox()
        self.controls["font_size"].setRange(8, 40)
        self.controls["font_size"].setToolTip(
            "Cỡ chữ của văn bản hiển thị trong ứng dụng."
        )
        self.controls["font_size"].setValue(self.settings.get("font_size", 14))
        form_layout.addRow("Cỡ chữ hiển thị:", self.controls["font_size"])

        self.controls["theme"] = QComboBox()
        self.controls["theme"].addItems(["Sáng", "Tối"])
        self.controls["theme"].setCurrentText(self.settings.get("theme", "Tối"))
        form_layout.addRow("Chủ đề (Theme):", self.controls["theme"])

        main_layout.addLayout(form_layout)

        # --- Thanh nút điều hướng ---
        button_layout = QHBoxLayout()

        self.btn_reset = QPushButton("Khôi phục mặc định")
        self.btn_reset.setStyleSheet("background-color: #e67e22; color: white;")
        self.btn_reset.clicked.connect(self.reset_to_defaults)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.save_and_accept)
        self.button_box.rejected.connect(self.reject)

        button_layout.addWidget(self.btn_reset)
        button_layout.addWidget(self.button_box)
        main_layout.addLayout(button_layout)
        
    def save_and_accept(self):
        """Lưu cài đặt vào file JSON khi nhấn OK."""
        settings = self.get_values()
        save_settings(settings)
        self.accept()

    def reset_to_defaults(self):
        """Đặt lại tất cả các widget về giá trị trong SETTINGS."""
        for key, widget in self.controls.items():
            if key in self.default_values:
                if isinstance(widget, QComboBox):
                    widget.setCurrentText(self.default_values[key])
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


# ================================================================
# 2. CỬA SỔ HƯỚNG DẪN (HELP DIALOG)
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
        except FileNotFoundError:
            html_content = "<b>Lỗi: Không tìm thấy file hướng dẫn help.html</b>"
        self.text_browser.setHtml(html_content)
        layout.addWidget(self.text_browser)
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


# ================================================================
# 3. GIAO DIỆN CHÍNH
# ================================================================


class SmartTranslatorUI:
    """Lớp chuyên trách khởi tạo giao diện cho SmartTranslator."""

    def setup_ui(self, target):
        # target ở đây chính là đối tượng SmartTranslator (self)
        target.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        target.setAttribute(Qt.WA_TranslucentBackground)

        # 2. Lấy cấu hình màu trực tiếp từ ThemeManager của target
        # Đảm bảo target đã khởi tạo self.theme_manager trước khi gọi hàm này
        current_theme_name = target.trans_settings.get("theme", "Tối")
        colors = target.theme_manager.get_theme(current_theme_name)

        # Tạo Panel chính
        target.panel = QWidget(target)

        target.panel.setStyleSheet(f"""
            QWidget {{
                background-color: {colors['panel_bg']};
                border-radius: 8px;
                border: 1px solid {colors['panel_border']}; }}
            QPushButton {{
                color: {colors['btn_fg']};
                font-weight: bold;
                border-radius: 4px;
                padding: 6px 10px;
                border: none; }}
            QPushButton:hover {{
                background-color: {colors['btn_hover']}; }}
        """)

        layout = QHBoxLayout(target.panel)
        layout.setContentsMargins(10, 5, 10, 5)

        # Khởi tạo các nút (Gán trực tiếp vào target để file chính dễ truy cập)
        btn_colors = colors["button_colors"]

        target.btn_direction = QPushButton("En ➔ Vi")
        target.btn_direction.setStyleSheet(
            f"background-color: {btn_colors['direction']}; width: 85px;"
        )

        target.btn_quet_toggle = QPushButton("🔍 Quét (Esc)")
        target.btn_quet_toggle.setStyleSheet(f"background-color: {btn_colors['scan']};")

        target.btn_clear = QPushButton("Xóa (Enter)")
        target.btn_clear.setStyleSheet(f"background-color: {btn_colors['clear']};")

        target.btn_help = QPushButton("❓ HDSD")
        target.btn_help.setStyleSheet(f"background-color: {btn_colors['help']};")

        target.btn_settings = QPushButton("⚙️")
        target.btn_settings.setFixedWidth(40)
        target.btn_settings.setStyleSheet(
            f"background-color: {btn_colors['settings']};"
        )

        target.btn_exit = QPushButton("✕")
        target.btn_exit.setFixedWidth(40)
        target.btn_exit.setStyleSheet(f"background-color: {btn_colors['exit']};")

        # Add widgets
        widgets = [
            target.btn_direction,
            target.btn_quet_toggle,
            target.btn_clear,
            target.btn_help,
            target.btn_settings,
            target.btn_exit,
        ]
        for w in widgets:
            layout.addWidget(w)


# ================================================================
# 4. HIỂN THỊ KẾT QUẢ
# ================================================================
class OverlayManager:
    """Chuyên quản lý các khung (labels) kết quả trên màn hình."""

    _MIN_RESULT_WIDTH = 150
    _MIN_RESULT_HEIGHT = 50

    def __init__(self, parent, theme_manager):
        self.parent = parent
        self.theme_manager = theme_manager
        self.results = []

    def create_result_box(self, rect, font_size):
        colors = self.theme_manager.get_theme(
            self.parent.trans_settings.get("theme", "Tối")
        )
        normalized_rect = rect.normalized()
        width = max(normalized_rect.width(), self._MIN_RESULT_WIDTH)
        height = max(normalized_rect.height(), self._MIN_RESULT_HEIGHT)

        scroll = QScrollArea(self.parent)
        scroll.setGeometry(normalized_rect.x(), normalized_rect.y(), width, height)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setAttribute(Qt.WA_DeleteOnClose)

        # Style cho ScrollArea
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 2px solid {colors['accent']};
                border-radius: 10px;
                background: {colors['bg']}; }}
            QScrollBar:vertical {{
                background: transparent;
                width: 4px; }}
            QScrollBar::handle:vertical {{
                background: {colors['accent']};
                border-radius: 2px; }}
        """)

        label = QLabel("⌛ Đang dịch...")
        label.setWordWrap(True)
        label.setMinimumSize(self._MIN_RESULT_WIDTH, self._MIN_RESULT_HEIGHT)
        label.setStyleSheet(
            f"""color: {colors['text']};
                font-size: {font_size}px;
                padding: 8px;
                background: transparent;""")

        scroll.setWidget(label)
        scroll.show()
        self.results.append(scroll)
        return label

    def clear_all(self):
        for item in self.results:
            item.close()
        self.results.clear()
