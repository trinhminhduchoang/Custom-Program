"""
chat_format.py - Format chatbot text replies into styled segments for tkinter GUI.
Independent of tkinter to allow portable testing.
"""

import re

CONFIDENCE_TAGS = {
    "cao": "conf_cao",
    "trung bình": "conf_tb",
    "thấp": "conf_thap",
}

_STEP = re.compile(r"^\s+\d+\.\s")
_LABEL_WITH_TEXT = ("Nguyên nhân:", "Vị trí lỗi:")


def format_segments(reply: str, as_code: bool = False) -> list[tuple[str, str]]:
    """
    Return a list of (text, tag_name) tuples for GUI styling.
    as_code=True: format entire reply as a code block.
    """
    if as_code:
        return [(reply + "\n", "code")]

    segments: list[tuple[str, str]] = []
    for line in reply.splitlines():
        if line.startswith("=="):
            segments.append((line.strip("= ").strip() + "\n", "heading"))
        elif line.startswith("Mức độ tự tin:"):
            value = line.split(":", 1)[1].strip()
            segments.append(("Mức độ tự tin: ", "label"))
            segments.append((value + "\n", CONFIDENCE_TAGS.get(value, "normal")))
        elif line.startswith(_LABEL_WITH_TEXT):
            label, rest = line.split(":", 1)
            segments.append((label + ": ", "label"))
            segments.append((rest.strip() + "\n", "normal"))
        elif line.strip() == "Cách chữa:":
            segments.append(("Cách chữa:\n", "label"))
        elif _STEP.match(line):
            segments.append((line.strip() + "\n", "step"))
        elif line.startswith("("):
            segments.append((line + "\n", "hint"))
        elif line.startswith("Mình chưa chắc chắn"):
            segments.append((line + "\n", "warn"))
        else:
            segments.append((line + "\n", "normal"))
    return segments