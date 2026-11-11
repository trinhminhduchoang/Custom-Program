"""
evaluate.py - Evaluate chatbot accuracy on test queries.
Usage: python evaluate.py
"""

import os
import sys

from chatbot import DoctorBot
from knowledge_base import load_knowledge_base

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "errors.json")

# (query, expected_id)
TEST_CASES = [
    # --- Natural language queries (accented / unaccented) ---
    ("cài thư viện rồi mà vẫn báo không tìm thấy module", "module_not_found"),
    ("pip install xong van loi no module named", "module_not_found"),
    ("chương trình chạy mãi không dừng", "infinite_loop"),
    ("while true bi treo khong thoat duoc", "infinite_loop"),
    ("mở file bị lỗi không tìm thấy file", "file_not_found"),
    ("dòng code lệch hàng bị lỗi thụt lề", "indentation_error"),
    ("chia cho 0 bị lỗi", "zero_division"),
    ("tiếng việt hiện thành dấu hỏi trong terminal", "console_question_marks"),
    ("gõ code python vào powershell bị lỗi", "powershell_python_mix"),
    ("gõ python không chạy, báo is not recognized", "python_not_recognized"),
    ("hàm cứ gọi chính nó mãi không dừng", "recursion_error"),
    ("nhập số mà cộng bị lỗi không cộng được chuỗi với số", "type_concat"),
    ("đọc file tiếng việt bị lỗi font mã hóa", "unicode_error"),
    ("truy cập phần tử cuối list bị vượt quá chỉ số", "index_error"),
    ("tên biến chưa được định nghĩa", "name_error"),
    ("lấy giá trị từ dict không có key", "key_error"),
    ("nhập chữ thay vì số, int() báo lỗi", "value_error"),
    ("sửa một chữ cái trong chuỗi không được", "str_immutable"),
    ("sửa biến bên ngoài trong hàm bị lỗi", "unbound_local"),
    ("file của mình trùng tên với thư viện random", "module_shadow"),
    ("test bị fail vì assert sai", "assertion_error"),
    ("thiếu dấu hai chấm sau if", "syntax_error"),
    ("hàm trả về None rồi gọi append bị lỗi", "none_attribute"),
    ("gọi hàm thiếu tham số", "type_args_count"),
    ("dùng chuỗi làm chỉ số của list", "list_indices"),
    ("import tên hàm không có trong module", "import_name"),
    # --- Traceback snippets ---
    ("Traceback (most recent call last):\n  File \"a.py\", line 3, in <module>\nNameError: name 'total' is not defined", "name_error"),
    ("ModuleNotFoundError: No module named 'sentence_transformers'", "module_not_found"),
    ("TypeError: can only concatenate str (not \"int\") to str", "type_concat"),
    ("TypeError: add() takes 2 positional arguments but 3 were given", "type_args_count"),
    ("AttributeError: 'NoneType' object has no attribute 'append'", "none_attribute"),
    ("AttributeError: module 'random' has no attribute 'randint'", "module_shadow"),
    ("IndexError: list index out of range", "index_error"),
    ("KeyError: 'ten'", "key_error"),
    ("ValueError: invalid literal for int() with base 10: 'abc'", "value_error"),
    ("FileNotFoundError: [Errno 2] No such file or directory: 'samples/a.txt'", "file_not_found"),
    ("UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte", "unicode_error"),
    ("RecursionError: maximum recursion depth exceeded", "recursion_error"),
    ("TypeError: 'str' object does not support item assignment", "str_immutable"),
    ("TypeError: list indices must be integers or slices, not str", "list_indices"),
    ("UnboundLocalError: local variable 'count' referenced before assignment", "unbound_local"),
    ("ZeroDivisionError: division by zero", "zero_division"),
    ("IndentationError: expected an indented block after 'if' statement on line 2", "indentation_error"),
    ("SyntaxError: '(' was never closed", "syntax_error"),
    ("ImportError: cannot import name 'tinh' from 'utils'", "import_name"),
    ("json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)", "json_decode_error"),
    ("JSONDecodeError: Expecting property name enclosed in double quotes: line 2 column 5", "json_decode_error"),
    ("đọc file json bị lỗi không hợp lệ", "json_decode_error"),
    ("AssertionError", "assertion_error"),
    ("TabError: inconsistent use of tabs and spaces in indentation", "indentation_error"),
    ("CategoryInfo          : ParserError: (:) [], ParentContainsErrorRecordException", "powershell_python_mix"),
    ("'python' is not recognized as an internal or external command", "python_not_recognized"),
]

# Hard test set: natural phrasing with fewer exact keyword matches
HARD_CASES = [
    ("máy báo lỗi vì mình quên thụt đầu dòng", "indentation_error"),
    ("code của mình chạy hoài không ra kết quả", "infinite_loop"),
    ("sao mình import thư viện hoài không được", "module_not_found"),
    ("đọc file txt mà python bảo không thấy", "file_not_found"),
    ("khi chạy báo lỗi dòng đầu tiên sai cú pháp", "syntax_error"),
    ("mình lấy phần tử thứ 5 của list có 3 phần tử", "index_error"),
    ("trung bình điểm của danh sách rỗng bị lỗi", "zero_division"),
    ("mình in ra tên mà báo chưa tồn tại", "name_error"),
    ("code ra chữ ??? thay vì tiếng việt", "console_question_marks"),
    ("lệnh pip không dùng được", "python_not_recognized"),
    ("kết quả của sort là None", "none_attribute"),
    ("input số xong cộng với 1 báo lỗi kiểu dữ liệu", "type_concat"),
    ("đổi chữ cái đầu của chuỗi thành chữ hoa bằng cách gán", "str_immutable"),
    ("tôi gõ print vào PS D:\\ thì báo lỗi", "powershell_python_mix"),
    ("hàm đệ quy chạy hoài rồi báo lỗi", "recursion_error"),
    ("access key khong co trong dictionary", "key_error"),
    ("mình viết biến count ngoài hàm rồi tăng nó trong hàm", "unbound_local"),
    ("kiểm tra kết quả hàm bằng assert thì báo lỗi", "assertion_error"),
    ("json.load báo lỗi dù file có dữ liệu", "json_decode_error"),
]


def evaluate(cases, name: str, use_bigrams: bool = True, verbose: bool = True) -> float:
    bot = DoctorBot(load_knowledge_base(DATA_PATH, use_bigrams=use_bigrams))
    top1 = top3 = 0
    for question, expected in cases:
        d = bot.diagnose(question)
        ids = [e["id"] for e in d.candidates[:3]] if d else []
        if ids and ids[0] == expected:
            top1 += 1
        if expected in ids:
            top3 += 1
        elif verbose:
            print(f"SAI : {question[:60]!r}\n      mong đợi {expected}, nhận được {ids[:3]}")
        if verbose and ids and ids[0] != expected and expected in ids:
            print(f"Top-3 nhưng không phải top-1: {question[:60]!r} -> {ids}")
    n = len(cases)
    if verbose:
        print(f"\n[{name}] Bigram: {'có' if use_bigrams else 'không'} | "
              f"Top-1: {top1}/{n} = {top1 / n:.0%} | Top-3: {top3}/{n} = {top3 / n:.0%}")
    return top1 / n


if __name__ == "__main__":
    for label, cases in (("Bộ dễ", TEST_CASES), ("Bộ khó", HARD_CASES)):
        evaluate(cases, label, use_bigrams=True)
        evaluate(cases, label, use_bigrams=False, verbose=False)
        print()