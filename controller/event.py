"""
Module controller.event hỗ trợ tương thích ngược cho các phiên bản cũ.
"""

from PyQt6.QtWidgets import QWidget

class Event(QWidget):
    pass

class MouseEvent(Event):
    pass

class UIHandler(Event):
    pass
