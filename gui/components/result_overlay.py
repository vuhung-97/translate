"""
ResultOverlayManager quản lý các khung QLabel/QScrollArea hiển thị bản dịch nổi trên màn hình.
"""

from typing import List, Optional
from PyQt6.QtWidgets import QScrollArea, QLabel, QWidget, QApplication
from PyQt6.QtCore import Qt, QRect

from gui.theme import theme_manager
from utils.logger import logger


class ResultOverlayManager:
    """
    Quản lý tập hợp các khung hiển thị kết quả dịch thuật trên màn hình.
    """

    _MIN_RESULT_WIDTH = 150
    _MIN_RESULT_HEIGHT = 50

    def __init__(self, parent_widget: Optional[QWidget] = None):
        self.parent = parent_widget
        self.results: List[QScrollArea] = []

    def create_result_box(self, rect: QRect, font_size: int = 14, theme_name: str = "Sáng") -> QLabel:
        """
        Tạo khung cuộn QScrollArea tại tọa độ chọn và trả về QLabel bên trong để cập nhật văn bản.
        """
        colors = theme_manager.get_theme(theme_name)
        normalized_rect = rect.normalized()
        width = max(normalized_rect.width(), self._MIN_RESULT_WIDTH)
        height = max(normalized_rect.height(), self._MIN_RESULT_HEIGHT)

        scroll = QScrollArea(self.parent)
        scroll.setGeometry(normalized_rect.x(), normalized_rect.y(), width, height)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Thiết lập QSS cho ScrollArea
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 2px solid {colors['accent']};
                border-radius: 10px;
                background: {colors['bg']};
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {colors['accent']};
                border-radius: 2px;
            }}
        """)

        label = QLabel("⌛ Đang dịch...", scroll)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setMinimumSize(self._MIN_RESULT_WIDTH, self._MIN_RESULT_HEIGHT)
        label.setStyleSheet(f"""
            color: {colors['text']};
            font-size: {font_size}px;
            padding: 8px;
            background: transparent;
        """)

        scroll.setWidget(label)
        scroll.show()
        self.results.append(scroll)
        logger.info(f"Đã tạo Result Box tại position=({normalized_rect.x()}, {normalized_rect.y()}), size=({width}x{height})")
        return label

    def clear_all(self):
        """Xóa tất cả các khung hiển thị kết quả hiện có."""
        for item in self.results:
            try:
                item.close()
            except Exception:
                pass
        self.results.clear()
        logger.info("Đã xóa tất cảResult Overlay Boxes.")
