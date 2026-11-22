"""Rebuild packaging/macos/AeroxLite.icns: the app mark from the window header (ui_theme.logo_image,
a mouse on a dark rounded square), on the macOS icon grid (the shape fills 824 of 1024 px, like the
other Dock icons). Usage: python packaging/macos/make_icon.py"""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import ui_theme  # noqa: E402


def main():
    canvas = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    mark = ui_theme.logo_image(824, "#18181B", "#FFFFFF")
    canvas.paste(mark, (100, 100), mark)
    out = Path(__file__).resolve().parent / "AeroxLite.icns"
    canvas.save(out, format="ICNS")
    print("written", out, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
