# pylint: disable=no-name-in-module, import-error

"""
Module này định nghĩa lớp EnViT5Engine, đóng vai trò là lõi xử lý 
dịch thuật của ứng dụng. Nó được thiết kế để tách biệt hoàn toàn
logic dịch thuật khỏi phần còn lại của ứng dụng, giúp tăng tính
modular và dễ bảo trì.EnViT5Engine sử dụng mô hình CTranslate2 và
SentencePiece để thực hiện dịch thuật giữa tiếng Anh và tiếng Việt.
"""

from typing import Dict, Any, List
from config import DEFAULT_SETTINGS

class EnViT5Engine:
    """
    Lõi xử lý dịch thuật.
    """

    # Extract Constants: Gom các chuỗi cố định để dễ quản lý
    _TOKEN_EOS = "</s>"
    _PREFIX_VI = "vi: "
    _PREFIX_EN = "en: "
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("--- Khởi tạo bộ não AI duy nhất (Nạp mô hình vào VRAM) ---")
            cls._instance = super(EnViT5Engine, cls).__new__(cls)
            # Khởi tạo các thuộc tính thực sự ở đây
            cls._instance._translator = None
            cls._instance._tokenizer = None
        return cls._instance

    def __init__(self):
        # Encapsulate Field:
        self._translator = None
        self._tokenizer = None

    def set_models(self, translator: Any, tokenizer: Any):
        """Thiết lập bộ nạp mô hình (Public API)."""
        self._translator = translator
        self._tokenizer = tokenizer

    def translate_text(self, text: str, settings: Dict[str, Any]) -> str:
        """
        Hàm điều phối chính đóng vai trò như một Orchestrator 
        thay vì tự làm mọi thứ.
        """
        # 1. Kiểm tra tiền điều kiện (Guard Clause)
        if not self._is_ready():
            return "Lỗi: Hệ thống AI chưa sẵn sàng!"

        # 2. Xử lý Prompt (Extract Method)
        prompt, target_prefix = self._prepare_prompt(text, settings.get('direction', 'en-vi'))

        # 3. Mã hóa (Extract Method)
        source_tokens = self._encode_text(prompt)

        # 4. Thực hiện dịch (Extract Method)
        raw_output = self._perform_inference(source_tokens, settings)

        # 5. Giải mã và Hậu xử lý (Extract Method)
        return self._post_process(raw_output, target_prefix)

    def _is_ready(self) -> bool:
        """Kiểm tra trạng thái engine."""
        return self._translator is not None and self._tokenizer is not None

    def _prepare_prompt(self, text: str, direction: str):
        """Logic xử lý Prompt Engineering."""
        if direction == 'vi-en':
            return f"{self._PREFIX_VI}{text}", self._PREFIX_EN
        return f"{self._PREFIX_EN}{text}", self._PREFIX_VI

    def _encode_text(self, prompt: str) -> List[str]:
        """Logic Tokenization."""
        tokens = self._tokenizer.encode(prompt, out_type=str)
        if not tokens or tokens[-1] != self._TOKEN_EOS:
            tokens.append(self._TOKEN_EOS)
        return tokens

    def _perform_inference(self, tokens: List[str], settings: Dict[str, Any]):
        """Logic gọi mô hình AI."""
        results = self._translator.translate_batch(
            [tokens],
            beam_size=settings.get(
                'beam_size',
                DEFAULT_SETTINGS['beam_size']
            ),

            repetition_penalty=settings.get(
                'repetition_penalty',
                DEFAULT_SETTINGS['repetition_penalty']
            ),

            no_repeat_ngram_size=settings.get(
                'no_repeat_ngram_size',
                DEFAULT_SETTINGS['no_repeat_ngram_size']
            ),

            max_decoding_length=settings.get(
                'max_decoding_length',
                DEFAULT_SETTINGS['max_decoding_length']
            ),
        )
        return results[0].hypotheses[0]

    def _post_process(self, raw_output, target_prefix: str) -> str:
        """Logic giải mã và làm sạch văn bản."""
        decoded_text = self._tokenizer.decode(raw_output)
        clean_text = decoded_text.replace(target_prefix, "").strip()
        return self.clean_and_deduplicate(clean_text)

    def clean_and_deduplicate(self, text: str) -> str:
        """Loại bỏ câu trùng lặp và chuẩn hóa dấu câu."""
        if not text:
            return ""

        sentences = [s.strip() for s in text.split('.') if s.strip()]
        unique_sentences = []
        seen = set()
        for sentence in sentences:
            if sentence.lower() not in seen:
                unique_sentences.append(sentence)
                seen.add(sentence.lower())

        final_text = ". ".join(unique_sentences)
        if final_text and not final_text.endswith('.'):
            final_text += '.'

        return final_text

# Khởi tạo instance duy nhất
ai_engine = EnViT5Engine()
