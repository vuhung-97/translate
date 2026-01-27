# engine.py
from typing import Dict, Any, List

class EnViT5Engine:
    """
    Lõi xử lý dịch thuật sử dụng mô hình EnViT5 và thư viện CTranslate2.
    Hỗ trợ dịch song phương Anh-Việt và Việt-Anh.
    """

    def __init__(self):
        # Đối tượng dịch và mã hóa sẽ được nạp từ Main Thread
        self.translator = None
        self.tokenizer = None

    def set_models(self, translator: Any, tokenizer: Any):
        """
        Thiết lập bộ nạp mô hình từ tiến trình chính.
        """
        self.translator = translator
        self.tokenizer = tokenizer

    def translate_text(self, text: str, settings: Dict[str, Any]) -> str:
        """
        Hàm điều phối dịch thuật chính.
        Args:
            text: Văn bản nguồn cần dịch.
            settings: Từ điển cấu hình (direction, beam_size, ...).
        Returns:
            Văn bản đã được dịch và xử lý hậu kỳ.
        """
        # 1. Kiểm tra trạng thái nạp mô hình
        if not self.translator or not self.tokenizer:
            return "Lỗi: Hệ thống AI chưa sẵn sàng. Vui lòng kiểm tra lại quá trình khởi tạo!"

        # 2. Xử lý logic chiều dịch (Prompt Engineering)
        direction = settings.get('direction', 'en-vi')
        
        if direction == 'vi-en':
            prompt = f"vi: {text}"
            target_prefix = "en: "
        else:
            prompt = f"en: {text}"
            target_prefix = "vi: "

        # 3. Mã hóa đầu vào (Tokenization)
        # Thêm token kết thúc </s> nếu chưa có để AI biết điểm dừng
        source_tokens = self.tokenizer.encode(prompt, out_type=str)
        if not source_tokens or source_tokens[-1] != "</s>":
            source_tokens.append("</s>")

        # 4. Thực hiện dịch thuật (Inference)
        # Tùy chỉnh các tham số kỹ thuật để cân bằng tốc độ/chất lượng
        results = self.translator.translate_batch(
            [source_tokens], 
            beam_size=settings.get('beam_size', 2),
            repetition_penalty=settings.get('repetition_penalty', 1.5),
            no_repeat_ngram_size=settings.get('no_repeat_ngram_size', 3),
            max_decoding_length=settings.get('max_decoding_length', 256)
        )
        
        # 5. Giải mã và Hậu xử lý (Post-processing)
        raw_output = results[0].hypotheses[0]
        decoded_text = self.tokenizer.decode(raw_output)
        
        # Loại bỏ tiền tố ngôn ngữ (vi: hoặc en:) khỏi kết quả trả về
        clean_translated = decoded_text.replace(target_prefix, "").strip()
        
        # 6. Logic lọc trùng và định dạng câu
        return self._clean_and_deduplicate(clean_translated)

    def _clean_and_deduplicate(self, text: str) -> str:
        """
        Hàm nội bộ giúp loại bỏ các câu trùng lặp và chuẩn hóa dấu câu.
        """
        if not text:
            return ""

        # Tách văn bản thành danh sách các câu dựa trên dấu chấm
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        # Sử dụng Set để giữ lại các câu duy nhất theo thứ tự xuất hiện
        unique_sentences = []
        seen = set()
        for sentence in sentences:
            if sentence.lower() not in seen:
                unique_sentences.append(sentence)
                seen.add(sentence.lower())
        
        # Ghép lại thành đoạn văn và đảm bảo kết thúc bằng dấu chấm
        final_text = ". ".join(unique_sentences)
        if final_text and not final_text.endswith('.'):
            final_text += '.'
            
        return final_text

# Khởi tạo instance duy nhất để sử dụng toàn cục trong ứng dụng
ai_engine = EnViT5Engine()