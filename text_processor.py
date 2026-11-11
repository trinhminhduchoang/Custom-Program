"""
text_processor.py - Text processing utilities: normalization, diacritics removal,
currency parsing, and sentence/word tokenization.
"""

import re
import unicodedata
from decimal import Decimal

# Common stopwords
STOPWORDS = {
    "và", "của", "là", "có", "cho", "các", "những", "một", "được", "trong",
    "với", "này", "đó", "để", "khi", "từ", "không", "như", "đã", "sẽ", "về",
    "tại", "theo", "thì", "mà", "hoặc", "cũng", "rằng", "nên", "bị", "ra",
    "vào", "lên", "còn", "nếu", "do", "bởi", "vì", "rất", "mọi",
}

# Currency units and multipliers (both accented and unaccented)
MONEY_UNITS = {
    "tr": 10**6, "triệu": 10**6, "trieu": 10**6,
    "k": 10**3, "nghìn": 10**3, "nghin": 10**3, "ngàn": 10**3, "ngan": 10**3,
    "tỷ": 10**9, "tỉ": 10**9, "ty": 10**9,
}

_MILLION = r"(?:triệu|trieu|tr)"
_THOUSAND = r"(?:nghìn|nghin|ngàn|ngan|k)"
_ANY_UNIT = r"(?:triệu|trieu|tr|nghìn|nghin|ngàn|ngan|k|tỷ|tỉ|ty)"
_NUM = r"\d+(?:[.,]\d+)*"          # 12 | 1.5 | 1,5 | 12.000.000
_START = r"(?<![\w.,])"            # Do not match within words/numbers


def remove_diacritics(text: str) -> str:
    """Remove Vietnamese diacritics: 'Quy chế thi' -> 'Quy che thi'."""
    # Decompose accented characters into base letter + combining mark
    decomposed = unicodedata.normalize("NFD", text)
    # Filter out non-spacing marks (category 'Mn')
    no_marks = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    # Replace 'đ' and 'Đ' separately as NFD does not decompose them
    return no_marks.replace("đ", "d").replace("Đ", "D")


def _parse_number(s: str) -> Decimal:
    """Parse Vietnamese numbers (handle dots as thousand separators or decimals)."""
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", s):
        return Decimal(s.replace(".", ""))
    return Decimal(s.replace(",", "."))


def normalize_money(text: str) -> str:
    """Normalize shorthand currency expressions into integer strings."""
    # 1) Compound amounts: "12 triệu 500 nghìn"
    def combined(m):
        total = _parse_number(m.group(1)) * MONEY_UNITS[m.group(2)] \
            + Decimal(m.group(3)) * MONEY_UNITS[m.group(4)]
        return str(int(total))

    text = re.sub(
        rf"{_START}({_NUM})\s*({_MILLION})\s*(\d+)\s*({_THOUSAND})(?!\w)",
        combined, text)

    # 2) Compact format: "2tr5" -> 2.5m, "1tr500" -> 1.5m, "1k5" -> 1.5k
    def attached(m):
        unit = MONEY_UNITS[m.group(2)]
        frac = Decimal(m.group(3)) / (10 ** len(m.group(3)))
        return str(int((Decimal(m.group(1)) + frac) * unit))

    text = re.sub(
        rf"{_START}(\d+)({_MILLION}|{_THOUSAND})(\d{{1,3}})(?!\w)",
        attached, text)

    # 3) Simple format: "12tr", "1,5 triệu", "500k", "2 tỷ"
    def simple(m):
        return str(int(_parse_number(m.group(1)) * MONEY_UNITS[m.group(2)]))

    return re.sub(rf"{_START}({_NUM})\s*({_ANY_UNIT})(?!\w)", simple, text)


def normalize(text: str, keep_accents: bool = True) -> str:
    """Normalize text: lowercase, parse currency, clean punctuation, collapse whitespace."""
    # Convert to NFC form and lowercase
    text = unicodedata.normalize("NFC", text).lower()

    # Normalize money before removing diacritics
    text = normalize_money(text)

    if not keep_accents:
        text = remove_diacritics(text)

    # Replace underscores with spaces
    text = text.replace("_", " ")

    # Step 1: Remove thousand-separator dots (e.g. 12.000.000 -> 12000000)
    text = re.sub(r"(?<=\d)\.(?=\d{3}(?!\d))", "", text)

    # Step 2: Remove punctuation except between digits (preserves 3.5, 20/10/2026)
    text = re.sub(r"(?<!\d)[^\w\s]|[^\w\s](?!\d)", " ", text)

    # Step 3: Separate currency symbol: 12000đ -> 12000 đ
    text = re.sub(r"(?<=\d)(?=[đd]\b)", " ", text)

    # Collapse consecutive whitespace
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text: str) -> list[str]:
    """Split text into sentences by punctuation (. ! ?)."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def tokenize(text: str, remove_stopwords: bool = True,
             keep_accents: bool = True) -> list[str]:
    """Tokenize text into words."""
    words = normalize(text, keep_accents=keep_accents).split()
    if remove_stopwords:
        # Strip diacritics from stopwords if accents are removed
        stop = STOPWORDS if keep_accents else {remove_diacritics(w) for w in STOPWORDS}
        words = [w for w in words if w not in stop]
    return words