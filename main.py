"""
Teams Grammar Checker
Bôi đen text → Alt+Shift+G → suggestion popup xuất hiện ở góc dưới phải.
Requires: pip install -r requirements.txt  (chạy với quyền admin trên Windows)
"""

import queue
import tkinter as tk

from teams_grammar import __version__
from teams_grammar.config import HOTKEY, OLLAMA_MODEL, POLL_INTERVAL_MS
from teams_grammar.hotkey import register
from teams_grammar.tray import start_tray
from teams_grammar.ui.loading import LoadingWindow
from teams_grammar.ui.suggestion import SuggestionWindow


def main() -> None:
    ui_queue: queue.Queue = queue.Queue()
    register(ui_queue)

    root = tk.Tk()
    root.withdraw()

    def quit_app() -> None:
        tray.stop()
        root.after(0, root.destroy)

    tray = start_tray(hotkey=HOTKEY, on_quit=quit_app)

    loader: LoadingWindow | None = None

    def poll() -> None:
        nonlocal loader
        try:
            msg, data = ui_queue.get_nowait()
            if msg == "loading":
                loader = LoadingWindow()
            elif msg == "result":
                if loader:
                    loader.close()
                    loader = None
                original, corrected = data
                SuggestionWindow(original, corrected)
        except queue.Empty:
            pass
        root.after(POLL_INTERVAL_MS, poll)

    root.after(POLL_INTERVAL_MS, poll)
    root.mainloop()


if __name__ == "__main__":
    main()
