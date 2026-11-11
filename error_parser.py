"""
error_parser.py - Parse tracebacks for error type, message, file, and line number.
"""

import re

# Matches Python exception line: "NameError: name 'x' is not defined"
_PY_EXCEPTION = re.compile(
    r"^((?:[A-Za-z_]\w*\.)*[A-Z]\w*(?:Error|Exception|Interrupt|Exit))\b\s*:?\s*(.*)$"
)
# Matches file and line number: File "main.py", line 12
_FILE_LINE = re.compile(r'File "([^"]+)", line (\d+)')
# Matches PowerShell error category
_PS_CATEGORY = re.compile(r"CategoryInfo\s*:\s*(\w+)")


def is_exception_line(line: str) -> bool:
    """Check if line is an exception header line (e.g. 'XxxError: ...')."""
    return bool(_PY_EXCEPTION.match(line.strip()))


def parse_error(text: str) -> dict:
    """Parse text and extract error_type, message, file, and line."""
    result = {"error_type": None, "message": "", "file": None, "line": None}

    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]

    # Scan bottom-up: error line is typically at the end
    for ln in reversed(lines):
        m = _PY_EXCEPTION.match(ln)
        if m:
            # Strip module prefix (e.g. 'json.decoder.JSONDecodeError' -> 'JSONDecodeError')
            result["error_type"] = m.group(1).split(".")[-1]
            result["message"] = m.group(2).strip()
            break

    # Fall back to PowerShell error category
    if result["error_type"] is None:
        m = _PS_CATEGORY.search(text)
        if m:
            result["error_type"] = m.group(1)

    # Extract innermost file and line location
    locations = _FILE_LINE.findall(text)
    if locations:
        result["file"], result["line"] = locations[-1][0], int(locations[-1][1])

    return result
