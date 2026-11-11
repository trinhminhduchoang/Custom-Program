"""
chatbot.py - Python Error Doctor chatbot combining rule-based traceback parsing and TF-IDF search.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime

from error_parser import parse_error
from knowledge_base import KnowledgeBase
from text_processor import normalize

# Cosine score thresholds
MIN_SCORE = 0.10      # Below this threshold: treat as unrecognized
HIGH_SCORE = 0.30     # At or above: high confidence

HELP_TEXT = (
    "Mình là Bác sĩ lỗi Python. Bạn có thể:\n"
    "  - Dán thông báo lỗi (Traceback...) hoặc chỉ dòng cuối, ví dụ: NameError: name 'x' is not defined\n"
    "  - Hoặc mô tả triệu chứng, ví dụ: \"chương trình chạy mãi không dừng\"\n"
    "  - Gõ 'ví dụ' để xem ví dụ, 'cách khác' nếu chẩn đoán chưa đúng\n"
    "  - Gõ /dan để dán nhiều dòng, /xong để kết thúc; 'thoát' để ra"
)

DISCLAIMER = "(Chẩn đoán dựa trên bộ hồ sơ có sẵn, hãy kiểm tra lại với code của bạn.)"


@dataclass
class Diagnosis:
    candidates: list[dict]                 # Candidate entries sorted by relevance
    scores: list[float]
    confidence: str                        # 'cao' | 'trung bình' | 'thấp'
    parsed: dict = field(default_factory=dict)
    index: int = 0                         # Index of currently displayed candidate

    @property
    def entry(self) -> dict:
        return self.candidates[self.index]


class DoctorBot:
    def __init__(self, kb: KnowledgeBase, log_path: str | None = None):
        self.kb = kb
        self.log_path = log_path
        self.last: Diagnosis | None = None      # Last diagnosis for conversational context

    # ---------------------------------------------------------------- Diagnosis
    def diagnose(self, text: str) -> Diagnosis | None:
        parsed = parse_error(text)
        etype = parsed["error_type"]

        # Traceback present: query by error type and message only
        query = f"{etype} {parsed['message']}" if etype else text
        ranked = self.kb.search(query)

        # Rule 1: filter candidates matching parsed error type
        if etype:
            typed = [(s, e) for s, e in ranked
                     if etype.lower() in [t.lower() for t in e["error_type"]]]
            if typed:
                scores = [s for s, _ in typed]
                if len(typed) == 1 or scores[0] >= HIGH_SCORE:
                    conf = "cao"
                else:
                    conf = "trung bình"
                return Diagnosis([e for _, e in typed], scores, conf, parsed)

        # Error type recognized but not in database: do not guess across error types
        if etype:
            return None

        # Rule 2: no traceback; rank purely by text similarity
        best_score = ranked[0][0]
        if best_score < MIN_SCORE:
            return None
        top = [(s, e) for s, e in ranked[:3] if s >= MIN_SCORE]
        conf = "trung bình" if best_score >= HIGH_SCORE else "thấp"
        return Diagnosis([e for _, e in top], [s for s, _ in top], conf, parsed)

    # -------------------------------------------------------------------- Reply
    def reply(self, text: str) -> str:
        cmd = normalize(text, keep_accents=False)

        if cmd in ("help", "huong dan", "tro giup", "?"):
            return HELP_TEXT
        if cmd in ("xin chao", "chao", "hello", "hi", "chao bac si"):
            return "Chào bạn! Bạn đang gặp lỗi gì vậy? (Gõ 'help' để xem hướng dẫn)"

        # Context commands based on last diagnosis
        if cmd in ("vi du", "cho vi du", "xem vi du"):
            return self._show_example()
        if cmd in ("cach khac", "khong dung", "chua dung", "con gi nua", "con khong"):
            return self._next_candidate()

        diagnosis = self.diagnose(text)
        if diagnosis is None:
            self.last = None
            self._log_unanswered(text)
            etype = parse_error(text)["error_type"]
            if etype:
                return (f"Mình nhận ra đây là lỗi {etype}, nhưng chưa có hồ sơ cho loại lỗi này.\n"
                        "Mình đã ghi lại để bổ sung sau. Bạn thử tra tên lỗi này trong tài liệu Python nhé.")
            return ("Mình chưa có hồ sơ phù hợp với trường hợp này.\n"
                    "Bạn thử dán đúng dòng cuối của thông báo lỗi (dạng 'XxxError: ...') "
                    "hoặc mô tả triệu chứng chi tiết hơn nhé.")
        self.last = diagnosis
        return self._format(diagnosis)

    # --------------------------------------------------------------- Formatting
    def _format(self, d: Diagnosis) -> str:
        e = d.entry
        lines = []
        if d.confidence == "thấp":
            lines.append("Mình chưa chắc chắn, nhưng có thể là:")
        lines.append(f"== CHẨN ĐOÁN: {e['ten']} ==")
        if d.parsed.get("file"):
            name = re.split(r"[\\/]", d.parsed["file"])[-1]   # Extract filename for both \ and /
            lines.append(f"Vị trí lỗi: {name}, dòng {d.parsed['line']}")
        lines.append(f"Mức độ tự tin: {d.confidence}")
        lines.append(f"\nNguyên nhân: {e['chan_doan']}")
        lines.append("\nCách chữa:")
        for i, step in enumerate(e["don_thuoc"], 1):
            lines.append(f"  {i}. {step}")
        hints = []
        if e.get("vi_du"):
            hints.append("'ví dụ' để xem ví dụ")
        if len(d.candidates) > 1:
            hints.append("'cách khác' nếu chưa đúng bệnh")
        if hints:
            lines.append("\n(Gõ " + ", ".join(hints) + ".)")
        lines.append(DISCLAIMER)
        return "\n".join(lines)

    def _show_example(self) -> str:
        if self.last is None:
            return "Bạn hãy mô tả lỗi trước, mình sẽ đưa ví dụ sau nhé."
        example = self.last.entry.get("vi_du")
        return example if example else "Hồ sơ này chưa có ví dụ."

    def _next_candidate(self) -> str:
        if self.last is None:
            return "Bạn hãy mô tả lỗi trước nhé."
        if self.last.index + 1 >= len(self.last.candidates):
            return "Mình hết ứng viên rồi. Bạn mô tả chi tiết hơn giúp mình nhé."
        self.last.index += 1
        self.last.confidence = "thấp"
        return self._format(self.last)

    # ------------------------------------------------------------------ Logging
    def _log_unanswered(self, text: str) -> None:
        """Log unanswered queries for future knowledge base expansion."""
        if not self.log_path:
            return
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        one_line = text.replace("\n", " / ")
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"{stamp}\t{one_line}\n")