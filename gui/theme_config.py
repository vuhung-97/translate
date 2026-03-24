class ThemeConfig:
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
                    "direction": "#8e44ad",
                    "direction_active": "#2980b9",
                    "scan": "#27ae60",
                    "clear": "#e67e22",
                    "help": "#675820",
                    "settings": "#7f8c8d",
                    "exit": "#c0392b"
                }
            },
            "Sáng": {
                "bg": "#ffffff",
                "text": "#1a1a1a",
                "accent": "#27ae60",
                "help_bg": "#f8f8f8",
                "help_text": "#1a1a1a",
                "panel_bg": "#f5f6fa",
                "panel_border": "#cccccc",
                "btn_fg": "#1a1a1a",
                "btn_hover": "#e0e0e0",
                "button_colors": {
                    "direction": "#8e44ad",
                    "direction_active": "#2980b9",
                    "scan": "#27ae60",
                    "clear": "#e67e22",
                    "help": "#f1c40f",
                    "settings": "#7f8c8d",
                    "exit": "#c0392b"
                }
            }
        }

    def get_theme(self, name):
        return self.themes.get(name)

    def get_available_themes(self):
        return list(self.themes.keys())
