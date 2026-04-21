import time
import tkinter as tk

import pyperclip

from ..clipboard import simulate_paste


class SuggestionWindow:
    def __init__(self, original: str, corrected: str):
        self.root = tk.Tk()
        self.root.title("✏️ Grammar Suggestion")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#1e1e2e")

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"520x280+{sw - 540}+{sh - 320}")

        self._build_ui(original, corrected)
        self.root.wait_window()

    def _build_ui(self, original: str, corrected: str) -> None:
        root = self.root

        header = tk.Frame(root, bg="#313244", height=36)
        header.pack(fill="x")
        tk.Label(
            header, text="✏️  Grammar Checker",
            bg="#313244", fg="#cdd6f4",
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", padx=12, pady=8)

        body = tk.Frame(root, bg="#1e1e2e")
        body.pack(fill="both", expand=True, padx=14, pady=8)

        tk.Label(body, text="Bản gốc:", bg="#1e1e2e", fg="#6c7086",
                 font=("Segoe UI", 8)).pack(anchor="w")
        orig_box = tk.Text(
            body, height=3, wrap="word",
            bg="#313244", fg="#a6adc8", relief="flat",
            font=("Segoe UI", 9), padx=6, pady=4,
        )
        orig_box.insert("1.0", original)
        orig_box.configure(state="disabled")
        orig_box.pack(fill="x", pady=(2, 8))

        tk.Label(body, text="Đề xuất sửa:", bg="#1e1e2e", fg="#a6e3a1",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self._corr_box = tk.Text(
            body, height=3, wrap="word",
            bg="#313244", fg="#a6e3a1", relief="flat",
            font=("Segoe UI", 9, "bold"), padx=6, pady=4,
        )
        self._corr_box.insert("1.0", corrected)
        self._corr_box.pack(fill="x", pady=(2, 8))

        btn_frame = tk.Frame(root, bg="#1e1e2e")
        btn_frame.pack(fill="x", padx=14, pady=(0, 12))

        tk.Button(
            btn_frame, text="✅  Apply & Copy",
            bg="#a6e3a1", fg="#1e1e2e", activebackground="#94e2a1",
            font=("Segoe UI", 9, "bold"), relief="flat",
            padx=14, pady=6, cursor="hand2",
            command=self._apply,
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_frame, text="✖  Dismiss",
            bg="#45475a", fg="#cdd6f4", activebackground="#585b70",
            font=("Segoe UI", 9), relief="flat",
            padx=14, pady=6, cursor="hand2",
            command=root.destroy,
        ).pack(side="left")

        if original.strip() == corrected.strip():
            tk.Label(
                btn_frame, text="✓ Không có lỗi nào!",
                bg="#1e1e2e", fg="#a6e3a1",
                font=("Segoe UI", 9),
            ).pack(side="right")

    def _apply(self) -> None:
        corrected = self._corr_box.get("1.0", "end-1c")
        pyperclip.copy(corrected)
        self.root.destroy()
        time.sleep(0.2)
        simulate_paste()
