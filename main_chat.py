"""
main_chat.py - Console interface for Python Error Doctor chatbot.
Usage: python main_chat.py
"""

import os
import sys

from chatbot import DoctorBot, HELP_TEXT
from error_parser import is_exception_line
from knowledge_base import load_knowledge_base

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "errors.json")
LOG_PATH = os.path.join(BASE_DIR, "unanswered.log")

# Common prefixes indicating multiline error paste
MULTILINE_STARTS = ("Traceback", 'File "', "At line:")


def read_message() -> str | None:
    """Read user message or multiline paste. Return None on exit."""
    first = input("\nBạn: ")
    stripped = first.strip()

    if stripped.lower() in ("thoát", "thoat", "exit", "quit", "/q"):
        return None

    if stripped.lower() in ("/dan", "/paste"):
        print("(Dán nội dung, kết thúc bằng một dòng chứa /xong)")
        lines = []
        while True:
            line = input()
            if line.strip().lower() == "/xong":
                break
            lines.append(line)
        return "\n".join(lines)

    if stripped.startswith(MULTILINE_STARTS):
        lines = [first]
        while True:
            try:
                line = input()
            except EOFError:
                break
            lines.append(line)
            # Stop at final exception line or empty line
            if is_exception_line(line) or "FullyQualifiedErrorId" in line or not line.strip():
                break
        return "\n".join(lines)

    return first


def main() -> None:
    bot = DoctorBot(load_knowledge_base(DATA_PATH), log_path=LOG_PATH)
    print("=" * 50)
    print("   BÁC SĨ LỖI PYTHON")
    print("=" * 50)
    print(HELP_TEXT)

    while True:
        try:
            message = read_message()
        except (EOFError, KeyboardInterrupt):
            print("\nTạm biệt!")
            break
        if message is None:
            print("Chúc bạn code ít lỗi!")
            break
        if not message.strip():
            continue
        print("\nBác sĩ:", bot.reply(message))


if __name__ == "__main__":
    main()