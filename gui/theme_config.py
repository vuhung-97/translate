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

    def get_theme(self, name):
        """Lấy cấu hình màu sắc cho theme đã chọn."""
        return self.themes.get(name)

    def get_available_themes(self):
        """Trả về danh sách tên các theme có sẵn."""
        return list(self.themes.keys())
