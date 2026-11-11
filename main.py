"""
main.py - Console interface for text analysis toolkit.
Usage: python main.py
"""

import os
import sys
from analyzer import (top_words, basic_stats, tfidf_keywords,
                      jaccard_similarity, cosine_similarity)

# Resolve path relative to script directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILE = os.path.join(BASE_DIR, "samples", "quy_che_hoc_vu.txt")

# Ensure UTF-8 output on Windows terminal
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass


def read_file(path: str) -> str | None:
    """Read UTF-8 text file. Return None on failure."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"  Không tìm thấy file: {path}")
    except UnicodeDecodeError:
        print("  File không phải UTF-8. Hãy lưu lại file với mã hóa UTF-8.")
    except OSError as err:
        print(f"  Không đọc được file: {err}")
    return None


def ask_text(prompt: str) -> str | None:
    """Prompt user for file path (Enter = default sample file). Return file contents."""
    path = input(f"{prompt} [Enter = file mẫu quy_che_hoc_vu.txt]: ").strip().strip('"')
    text = read_file(path or DEFAULT_FILE)
    if text is not None and not text.strip():
        print("  File rỗng.")
        return None
    return text


def show_stats(text: str) -> None:
    print("\n--- Thống kê cơ bản ---")
    labels = {
        "so_tu": "Số từ",
        "so_cau": "Số câu",
        "so_tu_khac_nhau": "Số từ khác nhau",
        "do_dai_cau_tb": "Độ dài câu trung bình (từ)",
        "do_da_dang_tu": "Độ đa dạng từ vựng",
    }
    for key, value in basic_stats(text).items():
        print(f"  {labels[key]:<30}: {value}")

    print("\n--- 10 từ xuất hiện nhiều nhất ---")
    for word, count in top_words(text, 10):
        print(f"  {word:<15} {'#' * count} ({count})")


def show_keywords(text: str) -> None:
    print("\n--- 8 từ khóa quan trọng nhất (TF-IDF) ---")
    for word, score in tfidf_keywords(text, 8):
        print(f"  {word:<15} {score}")


def compare_texts() -> None:
    t1 = ask_text("File thứ nhất")
    if t1 is None:
        return
    path2 = input("File thứ hai: ").strip().strip('"')
    t2 = read_file(path2)
    if t2 is None or not t2.strip():
        return
    print("\n--- Độ giống nhau (0 = khác hẳn, 1 = giống hệt) ---")
    print(f"  Jaccard (theo tập từ)      : {jaccard_similarity(t1, t2):.3f}")
    print(f"  Cosine  (theo tần suất từ) : {cosine_similarity(t1, t2):.3f}")


def main() -> None:
    menu = (
        "\n===== PHÂN TÍCH VĂN BẢN =====\n"
        "1. Thống kê một file văn bản\n"
        "2. Tìm từ khóa (TF-IDF) của một file\n"
        "3. So sánh độ giống nhau giữa hai file\n"
        "4. Phân tích đoạn văn bản gõ trực tiếp\n"
        "0. Thoát\n"
        "Chọn: "
    )
    while True:
        choice = input(menu).strip()
        if choice == "1":
            text = ask_text("Đường dẫn file")
            if text:
                show_stats(text)
        elif choice == "2":
            text = ask_text("Đường dẫn file")
            if text:
                show_keywords(text)
        elif choice == "3":
            compare_texts()
        elif choice == "4":
            text = input("Nhập đoạn văn bản: ").strip()
            if text:
                show_stats(text)
                show_keywords(text)
            else:
                print("  Bạn chưa nhập gì.")
        elif choice == "0":
            print("Tạm biệt!")
            break
        else:
            print("  Lựa chọn không hợp lệ, hãy nhập 0-4.")


if __name__ == "__main__":
    main()