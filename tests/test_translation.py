"""
Unit tests cho EnViT5Engine (Prompt Engineering & Clean Deduplicate).
"""

import unittest
from core.translation_engine import EnViT5Engine


class TestTranslation(unittest.TestCase):

    def test_prepare_prompt(self):
        engine = EnViT5Engine()
        prompt_en, target_en = engine._prepare_prompt("Hello world", "en-vi")
        self.assertEqual(prompt_en, "en: Hello world")
        self.assertEqual(target_en, "vi: ")

        prompt_vi, target_vi = engine._prepare_prompt("Xin chào thế giới", "vi-en")
        self.assertEqual(prompt_vi, "vi: Xin chào thế giới")
        self.assertEqual(target_vi, "en: ")

    def test_clean_and_deduplicate(self):
        engine = EnViT5Engine()
        text = "Xin chào. Xin chào. Hôm nay trời đẹp."
        result = engine.clean_and_deduplicate(text)
        self.assertEqual(result, "Xin chào. Hôm nay trời đẹp.")


if __name__ == "__main__":
    unittest.main()
