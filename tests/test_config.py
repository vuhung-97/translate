"""
Unit tests cho ConfigManager và TranslationSettings.
"""

import unittest
import os
from config.config_manager import ConfigManager, TranslationSettings


class TestConfig(unittest.TestCase):

    def test_translation_settings_defaults(self):
        settings = TranslationSettings()
        self.assertEqual(settings.direction, "en-vi")
        self.assertEqual(settings.beam_size, 5)
        self.assertEqual(settings.repetition_penalty, 1.5)
        self.assertEqual(settings.theme, "Sáng")

    def test_translation_settings_to_from_dict(self):
        data = {
            "direction": "vi-en",
            "ocr_engine": "easyocr",
            "beam_size": 3,
            "font_size": 20,
            "theme": "Tối"
        }
        settings = TranslationSettings.from_dict(data)
        self.assertEqual(settings.direction, "vi-en")
        self.assertEqual(settings.ocr_engine, "easyocr")
        self.assertEqual(settings.beam_size, 3)
        self.assertEqual(settings.font_size, 20)
        self.assertEqual(settings.theme, "Tối")

        dict_out = settings.to_dict()
        self.assertEqual(dict_out["ocr_engine"], "easyocr")
        self.assertEqual(dict_out["direction"], "vi-en")

    def test_config_manager_singleton(self):
        c1 = ConfigManager()
        c2 = ConfigManager()
        self.assertIs(c1, c2)
        self.assertTrue(os.path.exists(c1.SETTINGS_JSON_PATH))


if __name__ == "__main__":
    unittest.main()
