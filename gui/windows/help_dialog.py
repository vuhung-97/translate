"""
Dialog hiển thị hướng dẫn sử dụng chi tiết bằng HTML.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QDialogButtonBox
from config import HELP_DIALOG_HTML
from utils.logger import logger


class HelpDialog(QDialog):
    """Cửa sổ Hướng dẫn sử dụng ứng dụng."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hướng dẫn sử dụng SmartTranslator")
        self.setFixedSize(520, 620)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        self.text_browser = QTextBrowser()
        
        try:
            with open(HELP_DIALOG_HTML, encoding="utf-8") as f:
                html_content = f.read()
        except FileNotFoundError:
            logger.error(f"Không tìm thấy file hướng dẫn {HELP_DIALOG_HTML}")
            html_content = "<b>Lỗi: Không tìm thấy file hướng dẫn help.html</b>"

        self.text_browser.setHtml(html_content)
        layout.addWidget(self.text_browser)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
