"""
Lõi xử lý dịch thuật EnViT5 Engine (CTranslate2 + SentencePiece).
Áp dụng Singleton Pattern và tách bạch quy trình Tokenization -> Inference -> Post-processing.
"""

import time
from typing import Dict, Any, List, Optional, Tuple

from config import SETTINGS
from utils.logger import logger
from utils.exceptions import TranslationError, AIModelLoadError


class EnViT5Engine:
    """
    Singleton Class xử lý dịch thuật bằng CTranslate2 và SentencePiece.
    """

    _TOKEN_EOS = "</s>"
    _PREFIX_VI = "vi: "
    _PREFIX_EN = "en: "
    _instance: Optional["EnViT5Engine"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EnViT5Engine, cls).__new__(cls)
            cls._instance._translator = None
            cls._instance._tokenizer = None
            cls._instance._is_loaded = False
        return cls._instance

    def set_models(self, translator: Any, tokenizer: Any):
        """Thiết lập các instance của mô hình CTranslate2 và SentencePiece."""
        if translator is None or tokenizer is None:
            logger.error("set_models nhận tham số None!")
            raise AIModelLoadError("Translator hoặc Tokenizer không thể là None")
        self._translator = translator
        self._tokenizer = tokenizer
        self._is_loaded = True
        logger.info("EnViT5Engine đã nạp mô hình thành công.")

    def is_ready(self) -> bool:
        """Kiểm tra xem mô hình AI đã sẵn sàng chưa."""
        return self._is_loaded and self._translator is not None and self._tokenizer is not None

    def translate_text(self, text: str, settings: Optional[Dict[str, Any]] = None) -> str:
        """
        Phương thức điều phối chính để thực hiện dịch câu.
        """
        if not text or not text.strip():
            return ""

        if not self.is_ready():
            logger.error("Dịch thất bại: Hệ thống AI chưa được nạp mô hình!")
            return "Lỗi: Hệ thống AI chưa sẵn sàng!"

        if settings is None:
            settings = SETTINGS.settings.to_dict() if hasattr(SETTINGS, 'settings') else SETTINGS

        start_time = time.time()
        direction = settings.get("direction", "en-vi")

        try:
            # 1. Prepare Prompt
            prompt, target_prefix = self._prepare_prompt(text, direction)

            # 2. Tokenize / Encode
            source_tokens = self._encode_text(prompt)

            # 3. Perform AI Inference
            raw_output = self._perform_inference(source_tokens, settings)

            # 4. Decode & Post-process
            result = self._post_process(raw_output, target_prefix)
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Dịch hoàn tất trong {elapsed:.1f}ms [{direction}]")
            return result

        except Exception as e:
            logger.error(f"Lỗi trong quá trình dịch thuật AI: {e}", exc_info=True)
            return f"⚠️ Lỗi AI: {str(e)}"

    def _prepare_prompt(self, text: str, direction: str) -> Tuple[str, str]:
        """Tạo prompt chuẩn hóa cho mô hình EnViT5."""
        if direction == "vi-en":
            return f"{self._PREFIX_VI}{text}", self._PREFIX_EN
        return f"{self._PREFIX_EN}{text}", self._PREFIX_VI

    def _encode_text(self, prompt: str) -> List[str]:
        """Mã hóa chuỗi văn bản thành danh sách tokens với EOS token."""
        tokens = self._tokenizer.encode(prompt, out_type=str)
        if not tokens or tokens[-1] != self._TOKEN_EOS:
            tokens.append(self._TOKEN_EOS)
        return tokens

    def _perform_inference(self, tokens: List[str], settings: Dict[str, Any]) -> List[str]:
        """Chạy suy luận batch với CTranslate2."""
        beam_size = settings.get("beam_size", 5)
        repetition_penalty = settings.get("repetition_penalty", 1.5)
        no_repeat_ngram_size = settings.get("no_repeat_ngram_size", 3)
        max_decoding_length = settings.get("max_decoding_length", 256)

        results = self._translator.translate_batch(
            [tokens],
            beam_size=beam_size,
            repetition_penalty=repetition_penalty,
            no_repeat_ngram_size=no_repeat_ngram_size,
            max_decoding_length=max_decoding_length,
        )
        return results[0].hypotheses[0]

    def _post_process(self, raw_output: List[str], target_prefix: str) -> str:
        """Giải mã tokens thành chuỗi và làm sạch kết quả."""
        decoded_text = self._tokenizer.decode(raw_output)
        clean_text = decoded_text.replace(target_prefix, "").strip()
        return self.clean_and_deduplicate(clean_text)

    def clean_and_deduplicate(self, text: str) -> str:
        """Loại bỏ câu trùng lặp và chuẩn hóa dấu chấm kết thúc."""
        if not text:
            return ""

        sentences = [s.strip() for s in text.split(".") if s.strip()]
        unique_sentences = []
        seen = set()
        for sentence in sentences:
            if sentence.lower() not in seen:
                unique_sentences.append(sentence)
                seen.add(sentence.lower())

        final_text = ". ".join(unique_sentences)
        if final_text and not final_text.endswith("."):
            final_text += "."

        return final_text


# Single global instance
ai_engine = EnViT5Engine()
