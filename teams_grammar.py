"""
Teams Grammar Checker
- Bôi đen text trong Teams → nhấn Ctrl+Shift+G
- Tool gửi lên Ollama, hiện suggestion qua notification
- Nhấn "Apply" → tự paste text đã sửa
"""

import subprocess
import threading
import time
import json
import queue
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import ttk
import pyperclip
from pynput import keyboard

# Queue để giao tiếp từ background thread → main thread
ui_queue = queue.Queue()

# ── Config ─────────────────────────────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"   # đổi thành qwen2.5:3b nếu muốn

SYSTEM_PROMPT = """You are a grammar checker. 
The user will give you a message they want to send in Microsoft Teams (professional workplace).
Fix ONLY grammar, spelling, and tense errors. 
Do NOT change the meaning, tone, or wording unless grammatically necessary.
Reply with ONLY the corrected text. No explanation. No quotes. Just the fixed text."""

# ── Ollama call ─────────────────────────────────────────────────────────────
def check_grammar(text: str) -> str:
    payload = json.dumps({
        "model":  OLLAMA_MODEL,
        "prompt": text,
        "system": SYSTEM_PROMPT,
        "stream": False
    }).encode()

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get("response", "").strip()
    except urllib.error.URLError:
        return "❌ Không kết nối được Ollama. Hãy chắc chắn Ollama đang chạy."
    except Exception as e:
        return f"❌ Lỗi: {e}"

# ── Suggestion popup ────────────────────────────────────────────────────────
class SuggestionWindow:
    def __init__(self, original: str, corrected: str):
        self.corrected = corrected
        self.root = tk.Tk()
        self.root.title("✏️ Grammar Suggestion")
        self.root.geometry("520x280")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#1e1e2e")

        # ── Position: bottom-right corner
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"520x280+{sw-540}+{sh-320}")

        self._build_ui(original, corrected)
        self.root.wait_window()  # Block chỉ window này, không block main loop

    def _build_ui(self, original, corrected):
        root = self.root
        pad = {"padx": 14, "pady": 6}

        # Header
        header = tk.Frame(root, bg="#313244", height=36)
        header.pack(fill="x")
        tk.Label(header, text="✏️  Grammar Checker",
                 bg="#313244", fg="#cdd6f4",
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=12, pady=8)

        # Body
        body = tk.Frame(root, bg="#1e1e2e")
        body.pack(fill="both", expand=True, padx=14, pady=8)

        # Original
        tk.Label(body, text="Bản gốc:", bg="#1e1e2e", fg="#6c7086",
                 font=("Segoe UI", 8)).pack(anchor="w")
        orig_box = tk.Text(body, height=3, wrap="word",
                           bg="#313244", fg="#a6adc8", relief="flat",
                           font=("Segoe UI", 9), padx=6, pady=4)
        orig_box.insert("1.0", original)
        orig_box.configure(state="disabled")
        orig_box.pack(fill="x", pady=(2, 8))

        # Corrected
        tk.Label(body, text="Đề xuất sửa:", bg="#1e1e2e", fg="#a6e3a1",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.corr_box = tk.Text(body, height=3, wrap="word",
                                bg="#313244", fg="#a6e3a1", relief="flat",
                                font=("Segoe UI", 9, "bold"), padx=6, pady=4)
        self.corr_box.insert("1.0", corrected)
        self.corr_box.pack(fill="x", pady=(2, 8))

        # Buttons
        btn_frame = tk.Frame(root, bg="#1e1e2e")
        btn_frame.pack(fill="x", padx=14, pady=(0, 12))

        apply_btn = tk.Button(
            btn_frame, text="✅  Apply & Copy",
            bg="#a6e3a1", fg="#1e1e2e", activebackground="#94e2a1",
            font=("Segoe UI", 9, "bold"), relief="flat",
            padx=14, pady=6, cursor="hand2",
            command=self._apply
        )
        apply_btn.pack(side="left", padx=(0, 8))

        dismiss_btn = tk.Button(
            btn_frame, text="✖  Dismiss",
            bg="#45475a", fg="#cdd6f4", activebackground="#585b70",
            font=("Segoe UI", 9), relief="flat",
            padx=14, pady=6, cursor="hand2",
            command=root.destroy
        )
        dismiss_btn.pack(side="left")

        # No changes label
        if original.strip() == corrected.strip():
            tk.Label(btn_frame, text="✓ Không có lỗi nào!",
                     bg="#1e1e2e", fg="#a6e3a1",
                     font=("Segoe UI", 9)).pack(side="right")

    def _apply(self):
        corrected = self.corr_box.get("1.0", "end-1c")
        pyperclip.copy(corrected)
        self.root.destroy()
        # Paste vào Teams sau khi cửa sổ đóng
        time.sleep(0.2)
        _simulate_paste()

# ── Loading popup ────────────────────────────────────────────────────────────
class LoadingWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("")
        self.root.geometry("260x70")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#1e1e2e")
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"260x70+{sw-280}+{sh-110}")
        self.root.overrideredirect(True)

        tk.Label(self.root, text="⏳  Đang kiểm tra grammar...",
                 bg="#1e1e2e", fg="#cdd6f4",
                 font=("Segoe UI", 10)).pack(expand=True)
        self.root.update()  # Chỉ update 1 lần, KHÔNG gọi mainloop()

    def close(self):
        try:
            self.root.destroy()
        except:
            pass

# ── Helpers ──────────────────────────────────────────────────────────────────
def _simulate_paste():
    """Simulate Ctrl+V to paste into Teams"""
    ctrl = keyboard.Controller()
    with ctrl.pressed(keyboard.Key.ctrl_l):
        ctrl.tap('v')

def _get_selected_text() -> str:
    """Copy selected text — release hotkey keys trước để Teams giữ focus"""
    ctrl = keyboard.Controller()

    # Release Alt+Shift để Teams không mất focus
    ctrl.release(keyboard.Key.alt_l)
    ctrl.release(keyboard.Key.alt_r)
    ctrl.release(keyboard.Key.shift)
    ctrl.release(keyboard.Key.shift_l)
    ctrl.release(keyboard.Key.shift_r)
    time.sleep(0.2)

    # Clear clipboard rồi copy selection
    pyperclip.copy("")
    time.sleep(0.1)
    with ctrl.pressed(keyboard.Key.ctrl_l):
        ctrl.tap('c')
    time.sleep(0.3)
    return pyperclip.paste()

# ── Hotkey handler ────────────────────────────────────────────────────────────
pressed_keys = set()
_triggered = False  # chống trigger nhiều lần khi giữ phím

def _normalize(key):
    """Chuẩn hoá key để so sánh — fix pynput Windows quirk"""
    try:
        if hasattr(key, 'char') and key.char:
            if key.char == '\x07':
                return 'g'
            return key.char.lower()
    except:
        pass
    return key

def _is_hotkey():
    """Alt + Shift + G"""
    has_alt   = (keyboard.Key.alt_l   in pressed_keys or
                 keyboard.Key.alt_r   in pressed_keys or
                 keyboard.Key.alt     in pressed_keys)
    has_shift = (keyboard.Key.shift   in pressed_keys or
                 keyboard.Key.shift_l in pressed_keys or
                 keyboard.Key.shift_r in pressed_keys)
    norm      = {_normalize(k) for k in pressed_keys}
    has_g     = 'g' in norm
    return has_alt and has_shift and has_g

def on_press(key):
    global _triggered
    pressed_keys.add(key)
    # Debug: in ra phím đang nhấn
    print(f"  [key] {key} | norm={_normalize(key)} | hotkey={_is_hotkey()}")
    if _is_hotkey() and not _triggered:
        _triggered = True
        print("  [✓] Hotkey detected! Đang xử lý...")
        threading.Thread(target=_run_check, daemon=True).start()

def on_release(key):
    global _triggered
    pressed_keys.discard(key)
    _triggered = False

def _run_check():
    # 1. Lấy text đang được bôi đen
    original = _get_selected_text()
    if not original or not original.strip():
        print("  [!] Không có text được bôi đen")
        return

    print(f"  [→] Text: {original[:60]}...")

    # 2. Báo loading qua queue
    ui_queue.put(("loading", None))

    # 3. Gọi Ollama
    corrected = check_grammar(original)
    print(f"  [←] Corrected: {corrected[:60]}...")

    # 4. Gửi kết quả về main thread để hiện popup
    ui_queue.put(("result", (original, corrected)))

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  Teams Grammar Checker")
    print("  Bôi đen text → Alt+Shift+G")
    print(f"  Model: {OLLAMA_MODEL}")
    print("=" * 50)
    print("  Đang chạy ngầm... (Ctrl+C để thoát)")

    # Khởi động keyboard listener ở background thread
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    loader_win = None

    # Tạo hidden root để giữ tkinter event loop sống
    root = tk.Tk()
    root.withdraw()

    # Main loop chạy trên main thread — xử lý UI từ queue
    while True:
        try:
            # Xử lý tkinter events
            root.update()

            try:
                msg, data = ui_queue.get_nowait()
            except queue.Empty:
                time.sleep(0.05)
                continue

            if msg == "loading":
                loader_win = LoadingWindow()

            elif msg == "result":
                if loader_win:
                    loader_win.close()
                    loader_win = None
                original, corrected = data
                SuggestionWindow(original, corrected)

        except KeyboardInterrupt:
            print("\n  Đã thoát.")
            break
        except tk.TclError:
            break
