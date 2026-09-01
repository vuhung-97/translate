"""
Quản lý theme giao diện (Sáng/Tối) cho toàn bộ ứng dụng SmartTranslator.
"""

from typing import Dict, Any, List

class ThemeConfig:
    """
    Quản lý bảng màu và phong cách giao diện của ứng dụng.
    """

    def __init__(self):
        self.themes: Dict[str, Dict[str, Any]] = {
            "Tối": {
                "bg": "#2d2d2d",
                "text": "#e9dfdf",
                "accent": "#27ae60",
                "help_bg": "#23272b",
                "help_text": "#e0e0e0",
                "panel_bg": "#3D5A77",
                "panel_border": "#080808",
                "btn_fg": "white",
                "btn_hover": "#34495e",
                "button_colors": {
                    "direction": "#8b33b1",
                    "direction_active": "#3396d8",
                    "scan": "#2bc76c",
                    "clear": "#e98c3c",
                    "help": "#99822D",
                    "settings": "#4db2b9",
                    "exit": "#c92311",
                },
            },
            "Sáng": {
                "bg": "#ffffff",
                "text": "#2a2018",
                "accent": "#27ae60",
                "help_bg": "#23272b",
                "help_text": "#e0e0e0",
                "panel_bg": "#3D5A77",
                "panel_border": "#080808",
                "btn_fg": "white",
                "btn_hover": "#34495e",
                "button_colors": {
                    "direction": "#8b33b1",
                    "direction_active": "#3396d8",
                    "scan": "#2bc76c",
                    "clear": "#e98c3c",
                    "help": "#99822D",
                    "settings": "#4db2b9",
                    "exit": "#c92311",
                },
            },
        }

    def get_theme(self, name: str) -> Dict[str, Any]:
        """Lấy bảng màu theo tên theme."""
        return self.themes.get(name, self.themes["Sáng"])

    def get_available_themes(self) -> List[str]:
        """Trả về danh sách các theme có sẵn."""
        return list(self.themes.keys())

theme_manager = ThemeConfig()
