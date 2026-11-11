"""Tests for text_processor.py. Usage: python test_text_processor.py"""

from text_processor import (remove_diacritics, normalize, normalize_money,
                            split_sentences, tokenize)


def test_remove_diacritics():
    assert remove_diacritics("Quy chế thi cử") == "Quy che thi cu"
    assert remove_diacritics("Đại học Đà Nẵng") == "Dai hoc Da Nang"


def test_remove_diacritics_uppercase():
    assert remove_diacritics("ĐẠI HỌC") == "DAI HOC"


def test_normalize():
    assert normalize("  Xin   CHÀO,  các bạn!  ") == "xin chào các bạn"
    assert normalize("Học phí?", keep_accents=False) == "hoc phi"


def test_split_sentences():
    text = "Hôm nay trời đẹp. Bạn đi học chưa? Tôi đi rồi!"
    assert split_sentences(text) == ["Hôm nay trời đẹp.", "Bạn đi học chưa?", "Tôi đi rồi!"]


def test_split_sentences_with_numbers():
    # Dots within numbers should not split sentences
    text = "Học phí 12.000.000 đồng. Hạn nộp là ngày 5."
    assert split_sentences(text) == ["Học phí 12.000.000 đồng.", "Hạn nộp là ngày 5."]


def test_normalize_numbers():
    # Remove thousand-separator dots
    assert normalize("Học phí 12.000.000 đồng") == "học phí 12000000 đồng"
    # Separate currency unit from number
    assert normalize("Giá 12.000đ!") == "giá 12000 đ"
    assert normalize("Giá 12.000đ!", keep_accents=False) == "gia 12000 d"
    # Preserve decimals, dates, and phone numbers
    assert normalize("Điểm GPA là 3.5/4.0") == "điểm gpa là 3.5/4.0"
    assert normalize("Hạn nộp: 20/10/2026") == "hạn nộp 20/10/2026"
    assert normalize("Gọi 0123-456-789 để hỏi") == "gọi 0123-456-789 để hỏi"
    # Strip trailing sentence period
    assert normalize("Giá 12.000.") == "giá 12000"


def test_normalize_money_shorthand():
    assert normalize_money("12tr") == "12000000"
    assert normalize_money("12 triệu") == "12000000"
    assert normalize_money("500k") == "500000"
    assert normalize_money("500 nghìn") == "500000"
    assert normalize_money("500 ngàn") == "500000"
    assert normalize_money("2 tỷ") == "2000000000"
    assert normalize_money("12 trieu") == "12000000"          # Unaccented input


def test_normalize_money_decimal_and_compound():
    assert normalize_money("1.5tr") == "1500000"
    assert normalize_money("1,5 triệu") == "1500000"
    assert normalize_money("2,5 tỷ") == "2500000000"
    assert normalize_money("2tr5") == "2500000"               # 2.5 million
    assert normalize_money("1tr500") == "1500000"
    assert normalize_money("12 triệu 500 nghìn") == "12500000"


def test_normalize_money_not_money():
    # Non-currency expressions remain unchanged
    assert normalize_money("10km") == "10km"
    assert normalize_money("12 trường") == "12 trường"
    assert normalize_money("lớp 10a1") == "lớp 10a1"


def test_money_all_forms_match():
    # Normalize varied currency notations consistently
    for text in ["học phí 12tr", "học phí 12 triệu", "học phí 12.000.000 đồng"]:
        assert "12000000" in tokenize(text)
    assert normalize("Học phí 12 triệu", keep_accents=False) == "hoc phi 12000000"


def test_normalize_underscore():
    assert normalize("hello_world 123") == "hello world 123"


def test_tokenize_numbers():
    assert tokenize("Học phí 12.000.000 đồng") == ["học", "phí", "12000000", "đồng"]


def test_tokenize():
    assert tokenize("Học phí của trường là bao nhiêu?") == ["học", "phí", "trường", "bao", "nhiêu"]
    # Remove stopwords for unaccented input
    assert tokenize("Hoc phi cua truong la bao nhieu", keep_accents=False) == \
        ["hoc", "phi", "truong", "bao", "nhieu"]


def test_tokenize_edge_cases():
    assert tokenize("") == []
    assert tokenize("của và là") == []
    assert tokenize("HỌC   PHÍ!!!   ???") == ["học", "phí"]


if __name__ == "__main__":
    test_remove_diacritics()
    test_remove_diacritics_uppercase()
    test_normalize()
    test_normalize_numbers()
    test_normalize_underscore()
    test_normalize_money_shorthand()
    test_normalize_money_decimal_and_compound()
    test_normalize_money_not_money()
    test_money_all_forms_match()
    test_split_sentences()
    test_split_sentences_with_numbers()
    test_tokenize()
    test_tokenize_numbers()
    test_tokenize_edge_cases()
    print("Tất cả test đều qua!")