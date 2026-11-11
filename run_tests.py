"""Run all test suites. Usage: python run_tests.py"""

import test_text_processor
import test_analyzer
import test_chatbot

suites = [test_text_processor, test_analyzer, test_chatbot]
failed = 0

for suite in suites:
    # Run all functions starting with test_
    for name in sorted(dir(suite)):
        if name.startswith("test_"):
            try:
                getattr(suite, name)()
                print(f"  OK    {suite.__name__}.{name}")
            except AssertionError:
                failed += 1
                print(f"  LỖI   {suite.__name__}.{name}")

print()
print("Tất cả test đều qua!" if failed == 0 else f"Có {failed} test bị lỗi.")
