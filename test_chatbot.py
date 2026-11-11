"""Tests for error_parser, knowledge_base, and chatbot. Usage: python test_chatbot.py"""

import os
import tempfile

from chatbot import DoctorBot
from error_parser import parse_error, is_exception_line
from knowledge_base import load_knowledge_base, with_bigrams

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "errors.json")
KB = load_knowledge_base(DATA_PATH)


def test_parse_error_traceback():
    text = ('Traceback (most recent call last):\n'
            '  File "main.py", line 12, in <module>\n'
            '    print(total)\n'
            "NameError: name 'total' is not defined")
    p = parse_error(text)
    assert p["error_type"] == "NameError"
    assert p["message"] == "name 'total' is not defined"
    assert p["file"] == "main.py" and p["line"] == 12


def test_parse_error_edge_cases():
    assert parse_error("chương trình chạy mãi không dừng")["error_type"] is None
    assert parse_error("")["error_type"] is None
    assert parse_error("AssertionError")["error_type"] == "AssertionError"
    # Strip module prefix
    assert parse_error("json.decoder.JSONDecodeError: Expecting value")["error_type"] == "JSONDecodeError"
    # PowerShell error
    assert parse_error("CategoryInfo : ParserError: (:) []")["error_type"] == "ParserError"


def test_is_exception_line():
    assert is_exception_line("KeyError: 'x'")
    assert not is_exception_line("    print('KeyError')")
    assert not is_exception_line("Traceback (most recent call last):")


def test_with_bigrams():
    assert with_bigrams(["a", "b", "c"]) == ["a", "b", "c", "a_b", "b_c"]
    assert with_bigrams([]) == []


def test_search_orders_by_score():
    scored = KB.search("chia cho 0 bị lỗi")
    scores = [s for s, _ in scored]
    assert scores == sorted(scores, reverse=True)
    assert scored[0][1]["id"] == "zero_division"


def test_diagnose_traceback_uses_error_type():
    bot = DoctorBot(KB)
    d = bot.diagnose("ZeroDivisionError: division by zero")
    assert d.entry["id"] == "zero_division" and d.confidence == "cao"
    # Same error type with different messages map to different entries
    assert bot.diagnose("TypeError: can only concatenate str (not \"int\") to str").entry["id"] == "type_concat"
    assert bot.diagnose("TypeError: 'str' object does not support item assignment").entry["id"] == "str_immutable"


def test_diagnose_free_text_and_no_accents():
    bot = DoctorBot(KB)
    assert bot.diagnose("chương trình chạy mãi không dừng").entry["id"] == "infinite_loop"
    assert bot.diagnose("chuong trinh chay mai khong dung").entry["id"] == "infinite_loop"


def test_unknown_input_returns_none():
    bot = DoctorBot(KB)
    assert bot.diagnose("xyz qwerty asdf") is None
    assert bot.diagnose("") is None


def test_known_error_type_without_entry_is_not_guessed():
    bot = DoctorBot(KB)
    # Error type without an entry must not fall back to guessing another entry
    assert bot.diagnose("FloatingPointError: float overflow") is None
    assert "FloatingPointError" in bot.reply("FloatingPointError: float overflow")


def test_context_commands():
    bot = DoctorBot(KB)
    assert "mô tả lỗi" in bot.reply("ví dụ")                              # No prior context
    bot.reply("ZeroDivisionError: division by zero")
    assert "len(ds)" in bot.reply("ví dụ")                                # Active context -> show example
    assert bot.last.entry["id"] == "zero_division"


def test_next_candidate():
    bot = DoctorBot(KB)
    bot.reply("TypeError: can only concatenate str (not \"int\") to str")
    first = bot.last.entry["id"]
    bot.reply("cách khác")
    assert bot.last.entry["id"] != first


def test_unanswered_is_logged():
    with tempfile.TemporaryDirectory() as tmp:
        log = os.path.join(tmp, "unanswered.log")
        bot = DoctorBot(KB, log_path=log)
        reply = bot.reply("xyz qwerty asdf")
        assert "chưa có hồ sơ" in reply
        with open(log, encoding="utf-8") as f:
            assert "xyz qwerty asdf" in f.read()


def test_every_entry_is_complete():
    # Each entry must contain required fields
    for e in KB.entries:
        for key in ("id", "ten", "trieu_chung", "chan_doan", "don_thuoc"):
            assert e[key], f"{e['id']} thiếu {key}"
    ids = [e["id"] for e in KB.entries]
    assert len(ids) == len(set(ids)), "Có id bị trùng"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
    print("Tất cả test chatbot đều qua!")