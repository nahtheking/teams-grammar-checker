import time

import pyperclip
from pynput import keyboard as pynput_kb


def get_selected_text() -> str:
    ctrl = pynput_kb.Controller()
    for key in (
        pynput_kb.Key.alt_l, pynput_kb.Key.alt_r,
        pynput_kb.Key.shift, pynput_kb.Key.shift_l, pynput_kb.Key.shift_r,
    ):
        ctrl.release(key)
    time.sleep(0.2)

    pyperclip.copy("")
    time.sleep(0.1)
    with ctrl.pressed(pynput_kb.Key.ctrl_l):
        ctrl.tap("c")
    time.sleep(0.3)
    return pyperclip.paste()


def simulate_paste() -> None:
    ctrl = pynput_kb.Controller()
    with ctrl.pressed(pynput_kb.Key.ctrl_l):
        ctrl.tap("v")
