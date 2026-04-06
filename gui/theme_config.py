"""
Module này định nghĩa lớp ThemeConfig để quản lý cấu hình giao diện cho ứng dụng. 
Nó cung cấp các theme màu sắc khác nhau và phương thức để truy xuất chúng
Giúp tách biệt logic giao diện khỏi phần còn lại của ứng dụng.
"""
class ThemeConfig:
    """
    Quản lý cấu hình giao diện cho ứng dụng.
    """
    def __init__(self):
        self.themes = {
            "Tối": {
                "bg": "#2d2d2d",
                "text": "#e0e0e0",
                "accent": "#27ae60",
                "help_bg": "#23272b",
                "help_text": "#e0e0e0",
                "panel_bg": "#2c3e50",
                "panel_border": "white",
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
                "bg": "#fff6ea",
                "text": "#2a2018",
                "accent": "#f05a3f",
                "help_bg": "#ffe8d1",
                "help_text": "#34261b",
                "panel_bg": "#faf2e8",
                "panel_border": "#838281",
                "btn_fg": "#34261b",
                "btn_hover": "#ffd4ad",
                "button_colors": {
                    "direction": "#e079fa",
                    "direction_active": "#ff7f50",
                    "scan": "#7ee6bd",
                    "clear": "#ffbf7a",
                    "help": "#ffd767",
                    "settings": "#bfd8f7",
                    "exit": "#ff8f8f",
                },
            },
        }

    def get_theme(self, name):
        """Lấy cấu hình màu sắc cho theme đã chọn."""
        return self.themes.get(name)

    def get_available_themes(self):
        """Trả về danh sách tên các theme có sẵn."""
        return list(self.themes.keys())
