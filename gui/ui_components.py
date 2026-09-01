"""
Wrapper tương thích ngược cho gui.ui_components.
Ủy quyền cho các module trong gui.windows, gui.components và gui.theme.
"""

from gui.windows.settings_dialog import SettingsDialog
from gui.windows.help_dialog import HelpDialog
from gui.components.result_overlay import ResultOverlayManager as OverlayManager
from gui.windows.toolbar_window import ToolbarWindow


class SmartTranslatorUI:
    """Class wrapper tương thích ngược cho SmartTranslatorUI cũ."""
    def setup_ui(self, target):
        pass
