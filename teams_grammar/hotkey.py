import queue
import threading

import keyboard

from .checker import check_grammar
from .clipboard import get_selected_text
from .config import HOTKEY

_in_progress = threading.Event()


def register(ui_queue: queue.Queue) -> None:
    keyboard.add_hotkey(HOTKEY, lambda: _trigger(ui_queue), suppress=False)


def _trigger(ui_queue: queue.Queue) -> None:
    if _in_progress.is_set():
        return
    _in_progress.set()
    threading.Thread(target=_run_check, args=(ui_queue,), daemon=True).start()


def _run_check(ui_queue: queue.Queue) -> None:
    try:
        original = get_selected_text()
        if not original or not original.strip():
            print("  [!] Không có text được bôi đen")
            return

        print(f"  [→] Text: {original[:60]}...")
        ui_queue.put(("loading", None))

        corrected = check_grammar(original)
        print(f"  [←] Corrected: {corrected[:60]}...")
        ui_queue.put(("result", (original, corrected)))
    finally:
        _in_progress.clear()
