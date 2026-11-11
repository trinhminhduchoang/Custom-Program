"""
gui_chat.py - Tkinter GUI for Python Error Doctor chatbot.
Usage: python gui_chat.py
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont

from chat_format import format_segments
from chatbot import DoctorBot
from knowledge_base import load_knowledge_base

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "errors.json")
LOG_PATH = os.path.join(BASE_DIR, "unanswered.log")

COLORS = {
    "header_bg": "#1a5fb4",
    "header_fg": "#ffffff",
    "header_sub": "#dbe7ff",
    "chat_bg": "#ffffff",
    "user_bg": "#e8f0fe",
    "code_bg": "#f1f1f1",
    "who_user": "#1a5fb4",
    "who_bot": "#26a269",
    "heading": "#1a5fb4",
    "conf_cao": "#26a269",
    "conf_tb": "#b5770a",
    "conf_thap": "#c01c28",
    "hint": "#77767b",
    "status_bg": "#f0f0f0",
}

WELCOME = (
    "Chào bạn! Mình là Bác sĩ lỗi Python.\n"
    "- Dán thông báo lỗi (cả Traceback nhiều dòng) hoặc mô tả triệu chứng vào ô bên dưới, "
    "rồi nhấn Ctrl+Enter hoặc nút Chẩn đoán.\n"
    "- Nút 'Ví dụ' để xem code minh họa, 'Cách khác' nếu chẩn đoán chưa đúng.\n"
    "- Nút 'Mở file...' để nạp thông báo lỗi từ một file .txt."
)


class DoctorApp:
    def __init__(self, root, bot: DoctorBot):
        self.root = root
        self.bot = bot
        root.title("Bác sĩ lỗi Python")
        root.geometry("980x720")
        root.minsize(760, 560)
        self._pick_fonts()
        self._build_ui()
        self._configure_tags()
        self._show_welcome()
        self.input.focus_set()

    # ------------------------------------------------------------------ UI setup
    def _pick_fonts(self) -> None:
        families = set(tkfont.families(self.root))
        self.ui_font = next((f for f in ("Segoe UI", "Arial", "Helvetica") if f in families), "Helvetica")
        self.code_font = next((f for f in ("Consolas", "Courier New", "Courier") if f in families), "Courier")

    def _build_ui(self) -> None:
        c, ui = COLORS, self.ui_font

        # Header
        header = tk.Frame(self.root, bg=c["header_bg"])
        header.pack(side="top", fill="x")
        tk.Label(header, text="Bác sĩ lỗi Python", font=(ui, 18, "bold"),
                 bg=c["header_bg"], fg=c["header_fg"]).pack(anchor="w", padx=16, pady=(10, 0))
        tk.Label(header, text="Dán thông báo lỗi hoặc mô tả triệu chứng, mình sẽ chẩn đoán và gợi ý cách sửa",
                 font=(ui, 10), bg=c["header_bg"], fg=c["header_sub"]).pack(anchor="w", padx=16, pady=(0, 10))

        # Status bar (packed at bottom)
        self.status = tk.StringVar(
            value=f"Đã nạp {len(self.bot.kb.entries)} hồ sơ lỗi  |  Câu hỏi chưa trả lời được sẽ ghi vào unanswered.log")
        tk.Label(self.root, textvariable=self.status, anchor="w", bg=c["status_bg"],
                 font=(ui, 9), padx=12, pady=3).pack(side="bottom", fill="x")

        # Input area
        input_frame = ttk.Frame(self.root)
        input_frame.pack(side="bottom", fill="x", padx=12, pady=(6, 10))
        ttk.Label(input_frame, text="Dán lỗi hoặc mô tả ở đây (Ctrl+Enter để gửi):").pack(anchor="w")

        box = ttk.Frame(input_frame)
        box.pack(fill="x", pady=(2, 6))
        self.input = tk.Text(box, height=6, wrap="word", font=(self.code_font, 10),
                             relief="solid", borderwidth=1, undo=True)
        in_scroll = ttk.Scrollbar(box, command=self.input.yview)
        self.input.configure(yscrollcommand=in_scroll.set)
        in_scroll.pack(side="right", fill="y")
        self.input.pack(side="left", fill="x", expand=True)
        self.input.bind("<Control-Return>", self._on_send)
        self.root.bind("<Control-l>", lambda event: self._clear())

        buttons = ttk.Frame(input_frame)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Chẩn đoán", command=self._on_send).pack(side="left")
        ttk.Button(buttons, text="Ví dụ", command=lambda: self._quick("ví dụ")).pack(side="left", padx=(8, 0))
        ttk.Button(buttons, text="Cách khác", command=lambda: self._quick("cách khác")).pack(side="left", padx=(8, 0))
        ttk.Button(buttons, text="Mở file...", command=self._open_file).pack(side="left", padx=(8, 0))
        ttk.Button(buttons, text="Xóa hội thoại", command=self._clear).pack(side="right")

        # Chat display area
        chat_frame = ttk.Frame(self.root)
        chat_frame.pack(side="top", fill="both", expand=True, padx=12, pady=(10, 0))
        self.output = tk.Text(chat_frame, wrap="word", state="disabled", relief="flat",
                              bg=c["chat_bg"], padx=12, pady=8, font=(ui, 11))
        out_scroll = ttk.Scrollbar(chat_frame, command=self.output.yview)
        self.output.configure(yscrollcommand=out_scroll.set)
        out_scroll.pack(side="right", fill="y")
        self.output.pack(side="left", fill="both", expand=True)

    def _configure_tags(self) -> None:
        c, ui, code = COLORS, self.ui_font, self.code_font
        tag = self.output.tag_configure
        tag("who_user", font=(ui, 10, "bold"), foreground=c["who_user"], spacing1=12)
        tag("who_bot", font=(ui, 10, "bold"), foreground=c["who_bot"], spacing1=12)
        tag("user", background=c["user_bg"], lmargin1=12, lmargin2=12, rmargin=12)
        tag("user_code", background=c["user_bg"], font=(code, 10), lmargin1=12, lmargin2=12, rmargin=12)
        tag("heading", font=(ui, 13, "bold"), foreground=c["heading"], spacing1=4, spacing3=4)
        tag("label", font=(ui, 11, "bold"))
        tag("conf_cao", font=(ui, 11, "bold"), foreground=c["conf_cao"])
        tag("conf_tb", font=(ui, 11, "bold"), foreground=c["conf_tb"])
        tag("conf_thap", font=(ui, 11, "bold"), foreground=c["conf_thap"])
        tag("step", lmargin1=24, lmargin2=44)
        tag("hint", font=(ui, 9, "italic"), foreground=c["hint"])
        tag("warn", font=(ui, 10, "italic"), foreground=c["conf_tb"])
        tag("code", font=(code, 10), background=c["code_bg"], lmargin1=12, lmargin2=12, rmargin=12)

    # ------------------------------------------------------------------- Display
    def _add_message(self, who: str, who_tag: str, segments: list[tuple[str, str]]) -> None:
        self.output.configure(state="normal")
        self.output.insert("end", who + "\n", who_tag)
        for text, tag in segments:
            self.output.insert("end", text, tag)
        self.output.insert("end", "\n")
        self.output.configure(state="disabled")
        self.output.see("end")

    def _show_welcome(self) -> None:
        self._add_message("Bác sĩ", "who_bot", format_segments(WELCOME))

    # ------------------------------------------------------------------- Actions
    def _safe_reply(self, text: str) -> str:
        try:
            return self.bot.reply(text)
        except Exception as err:   # Prevent crashes on unexpected errors
            return f"Có lỗi nội bộ khi xử lý: {err}"

    def _respond(self, text: str) -> None:
        reply = self._safe_reply(text)
        # Format as code block if reply matches example code
        last = self.bot.last
        as_code = last is not None and reply == last.entry.get("vi_du")
        self._add_message("Bác sĩ", "who_bot", format_segments(reply, as_code=as_code))

    def _on_send(self, event=None):
        text = self.input.get("1.0", "end").strip()
        if not text:
            return "break"
        tag = "user_code" if "\n" in text else "user"
        self._add_message("Bạn", "who_user", [(text + "\n", tag)])
        self.input.delete("1.0", "end")
        self._respond(text)
        return "break"          # Prevent Tkinter from inserting newline on Ctrl+Enter

    def _quick(self, command: str) -> None:
        self._add_message("Bạn", "who_user", [(command + "\n", "user")])
        self._respond(command)

    def _open_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Chọn file chứa thông báo lỗi",
            filetypes=[("Văn bản", "*.txt *.log"), ("Tất cả", "*.*")])
        if not path:
            return
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError as err:
            messagebox.showerror("Không mở được file", str(err))
            return
        self.input.delete("1.0", "end")
        self.input.insert("1.0", content.strip())

    def _clear(self) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")
        self.bot.last = None
        self._show_welcome()


def _enable_dpi_awareness() -> None:
    """Enable DPI awareness on Windows for crisp fonts."""
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


def main() -> None:
    _enable_dpi_awareness()
    root = tk.Tk()
    try:
        kb = load_knowledge_base(DATA_PATH)
    except (OSError, ValueError) as err:     # ValueError includes JSON decoding errors
        root.withdraw()
        messagebox.showerror("Không nạp được hồ sơ lỗi", f"{DATA_PATH}\n\n{err}")
        return
    DoctorApp(root, DoctorBot(kb, log_path=LOG_PATH))
    root.mainloop()


if __name__ == "__main__":
    main()