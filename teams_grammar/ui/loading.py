import tkinter as tk


class LoadingWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#1e1e2e")
        self.root.overrideredirect(True)

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"260x70+{sw - 280}+{sh - 110}")

        tk.Label(
            self.root,
            text="⏳  Đang kiểm tra grammar...",
            bg="#1e1e2e",
            fg="#cdd6f4",
            font=("Segoe UI", 10),
        ).pack(expand=True)
        self.root.update()

    def close(self) -> None:
        try:
            self.root.destroy()
        except Exception:
            pass
