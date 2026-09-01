"""
ResultOverlayManager quản lý các khung QLabel/QScrollArea hiển thị bản dịch nổi trực tiếp trên màn hình.
Hỗ trợ Nhấp đúp chuột (Double-Click) để xóa ô bản dịch riêng lẻ.
"""

from typing import List, Optional, Callable
from PyQt6.QtWidgets import QScrollArea, QLabel, QWidget
from PyQt6.QtCore import Qt, QRect, pyqtSignal

from gui.theme import theme_manager
from utils.logger import logger


class ResultLabel(QLabel):
    """QLabel tùy chỉnh nhận sự kiện nhấp đúp chuột."""
    double_clicked = pyqtSignal()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


class ResultScrollArea(QScrollArea):
    """QScrollArea tùy chỉnh nhận sự kiện nhấp đúp chuột."""
    double_clicked = pyqtSignal()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


class ResultOverlayManager:
    """
    Quản lý tập hợp các khung hiển thị kết quả dịch thuật nổi trực tiếp trên màn hình (Floating Frameless Overlay).
    """

    _MIN_RESULT_WIDTH = 160
    _MIN_RESULT_HEIGHT = 50

    def __init__(self, parent_widget: Optional[QWidget] = None, box_closed_callback: Optional[Callable] = None):
        self.parent = parent_widget
        self.box_closed_callback = box_closed_callback
        self.results: List[QScrollArea] = []

    def create_result_box(self, rect: QRect, font_size: int = 14, theme_name: str = "Sáng") -> QLabel:
        """
        Tạo khung cuộn QScrollArea nổi không khung viền tại tọa độ chọn và trả về QLabel bên trong.
        Nền màu đục rắn 100% không bị trong suốt.
        """
        colors = theme_manager.get_theme(theme_name)
        normalized_rect = rect.normalized()
        width = max(normalized_rect.width(), self._MIN_RESULT_WIDTH)
        height = max(normalized_rect.height(), self._MIN_RESULT_HEIGHT)

        scroll = ResultScrollArea(self.parent)
        scroll.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        # Loại bỏ WA_TranslucentBackground để không bị mất màu nền
        scroll.setGeometry(normalized_rect.x(), normalized_rect.y(), width, height)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        scroll.setToolTip("Nhấp đúp chuột để xóa ô này")

        # QSS Style với màu nền đục rắn 100%
        bg_color = colors['bg']
        text_color = colors['text']
        accent_color = colors['accent']

        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 2px solid {accent_color};
                border-radius: 10px;
                background-color: {bg_color};
            }}
            QWidget#qt_scrollarea_viewport {{
                background-color: {bg_color};
                border-radius: 8px;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {accent_color};
                border-radius: 2px;
            }}
        """)

        # Label hiển thị văn bản bản dịch với màu nền rắn
        label = ResultLabel("⌛ Đang dịch...", scroll)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setMinimumSize(self._MIN_RESULT_WIDTH - 10, self._MIN_RESULT_HEIGHT - 10)
        label.setToolTip("Nhấp đúp chuột để xóa ô này")
        label.setStyleSheet(f"""
            color: {text_color};
            font-size: {font_size}px;
            padding: 8px;
            background-color: {bg_color};
            border-radius: 8px;
        """)

        scroll.setWidget(label)

        # Xử lý sự kiện nhấp đúp chuột để xóa ô riêng lẻ
        scroll.double_clicked.connect(lambda: self.close_result_box(scroll))
        label.double_clicked.connect(lambda: self.close_result_box(scroll))

        scroll.show()
        scroll.raise_()
        self.results.append(scroll)
        logger.info(f"Đã tạo Result Box nổi tại position=({normalized_rect.x()}, {normalized_rect.y()}), size=({width}x{height})")
        return label

    def get_result_rects(self) -> List[QRect]:
        """Trả về danh sách QRect khung hình của tất cả các ô bản dịch đang hiển thị."""
        rects = []
        for scroll in self.results:
            try:
                if scroll.isVisible():
                    rects.append(scroll.frameGeometry())
            except Exception:
                pass
        return rects

    def close_result_box(self, scroll: QScrollArea):
        """Xóa một khung kết quả dịch cụ thể khi nhấp đúp chuột."""
        if scroll in self.results:
            self.results.remove(scroll)
        try:
            scroll.close()
            logger.info("Đã xóa 1 ô Result Overlay Box bằng nhấp đúp chuột.")
        except Exception as e:
            logger.warning(f"Lỗi khi xóa ô Result Box: {e}")

        # Đẩy các ô còn lại lên trên và gọi callback nếu có
        self.raise_all()
        if self.box_closed_callback:
            try:
                self.box_closed_callback()
            except Exception:
                pass

    def raise_all(self):
        """Đẩy tất cả các khung kết quả nổi lên phía trên tầng hiển thị."""
        for scroll in self.results:
            try:
                scroll.raise_()
            except Exception:
                pass

    def clear_all(self):
        """Xóa tất cả các khung hiển thị kết quả hiện có."""
        for item in self.results:
            try:
                item.close()
            except Exception:
                pass
        self.results.clear()
        logger.info("Đã xóa tất cả Result Overlay Boxes.")
