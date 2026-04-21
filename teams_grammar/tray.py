import pystray
from PIL import Image, ImageDraw, ImageFont


def _make_icon() -> Image.Image:
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background circle
    draw.ellipse([2, 2, size - 2, size - 2], fill="#1e1e2e")

    # Green ring
    draw.ellipse([2, 2, size - 2, size - 2], outline="#a6e3a1", width=4)

    # Letter "G" — try a truetype font, fall back to default
    letter = "G"
    try:
        font = ImageFont.truetype("segoeui.ttf", 36)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1]),
              letter, fill="#a6e3a1", font=font)

    return img


def start_tray(hotkey: str, on_quit) -> pystray.Icon:
    icon = pystray.Icon(
        name="teams_grammar",
        icon=_make_icon(),
        title="Teams Grammar Checker",
        menu=pystray.Menu(
            pystray.MenuItem("Teams Grammar Checker", None, enabled=False),
            pystray.MenuItem(f"Hotkey: {hotkey.upper()}", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", lambda icon, item: on_quit()),
        ),
    )
    icon.run_detached()
    return icon
