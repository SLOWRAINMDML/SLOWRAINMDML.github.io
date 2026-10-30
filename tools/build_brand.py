#!/usr/bin/env python3
"""Brand assets: logo, cloud favicon, Open Graph image and the subset Galmuri pixel font.

    python3 tools/build_brand.py

Run again after changing text in index.html, app.js or content/games.json so the
subset font still covers every character drawn in the pixel font.
"""
import json
import re
from pathlib import Path

from fontTools import subset
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "assets" / "brand"
FONTS = ROOT / "assets" / "fonts"
LOGO_SRC = Path.home() / "ima2-work/slowrain-logo/slowrain_games_logo.png"
GALMURI = Path.home() / "project/SRPG_STD/srpg-tutorial/assets/fonts/galmuri"
NAVY = (18, 31, 66)


def cloud_box(logo):
    """Bounding box of the cloud mascot: the left block before the first empty column gap."""
    alpha = logo.getchannel("A")
    w, h = logo.size
    cols = [any(alpha.getpixel((x, y)) > 16 for y in range(0, h, 2)) for x in range(w)]
    start = cols.index(True)
    x = start
    while x < w and (cols[x] or any(cols[x:x + 6])):
        x += 1
    return (start, 0, x, h)


def square(img, size, pad=0.08, bg=None):
    box = img.getbbox()
    img = img.crop(box)
    side = round(max(img.size) * (1 + pad * 2))
    canvas = Image.new("RGBA", (side, side), bg or (0, 0, 0, 0))
    canvas.alpha_composite(img, ((side - img.width) // 2, (side - img.height) // 2))
    return canvas.resize((size, size), Image.LANCZOS)


def build_images():
    BRAND.mkdir(parents=True, exist_ok=True)
    logo = Image.open(LOGO_SRC).convert("RGBA")
    logo = logo.crop(logo.getbbox())
    small = logo.resize((700, round(logo.height * 700 / logo.width)), Image.LANCZOS)
    small.save(BRAND / "logo.webp", "WEBP", quality=92, method=6)
    small.save(BRAND / "logo.png", optimize=True)

    cloud = logo.crop(cloud_box(logo))
    cloud.resize((300, round(cloud.height * 300 / cloud.width)), Image.LANCZOS).save(BRAND / "cloud.png", optimize=True)
    square(cloud, 32).save(ROOT / "favicon-32.png")
    square(cloud, 180, 0.14, (255, 255, 255, 255)).convert("RGB").save(ROOT / "apple-touch-icon.png")
    square(cloud, 64).save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])

    # Open Graph card: navy sky, logo, a row of game covers.
    games = json.loads((ROOT / "content/games.json").read_text())["games"]
    og = Image.new("RGB", (1200, 630), NAVY)
    draw = ImageDraw.Draw(og)
    for i in range(70):  # pixel rain
        x, y = (i * 173) % 1200, (i * 97) % 300
        draw.rectangle((x, y, x + 3, y + 14), fill=(60, 110, 190))
    lg = logo.resize((640, round(logo.height * 640 / logo.width)), Image.LANCZOS)
    og.paste(lg, ((1200 - lg.width) // 2, 70), lg)
    covers = [g["cover"] for g in games[:5]]
    w, gap = 220, 12
    x0 = (1200 - (w * 5 + gap * 4)) // 2
    for i, path in enumerate(covers):
        c = Image.open(ROOT / path).convert("RGB")
        c = c.resize((w, round(c.height * w / c.width)), Image.LANCZOS).crop((0, 0, w, 124))
        mask = Image.new("L", c.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, c.width - 1, c.height - 1), 14, fill=255)
        og.paste(c, (x0 + i * (w + gap), 410), mask)
    font = ImageFont.truetype(str(GALMURI / "Galmuri11-Bold.ttf"), 26)
    text = "ROBLOX · STEAM · INDIE GAMES FROM KOREA"
    tw = draw.textlength(text, font=font)
    draw.text(((1200 - tw) / 2, 565), text, font=font, fill=(255, 246, 223))
    og.save(BRAND / "og.png", optimize=True)


def build_font():
    """Subset Galmuri to the characters the site can draw with it."""
    FONTS.mkdir(parents=True, exist_ok=True)
    text = (ROOT / "index.html").read_text() + (ROOT / "app.js").read_text()
    data = json.loads((ROOT / "content/games.json").read_text())
    for g in data["games"]:
        text += "".join(g["title"].values()) + "".join((g.get("status") or {}).values())
    text += "".join(chr(c) for c in range(0x20, 0x7F)) + "·…—↗↑←→ⅡⅠ▶"
    chars = "".join(sorted(set(re.sub(r"\s", "", text)) | {" "}))
    for weight, name in (("Regular", "Galmuri11.ttf"), ("Bold", "Galmuri11-Bold.ttf")):
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["*"]
        font = subset.load_font(str(GALMURI / name), opts)
        sub = subset.Subsetter(opts)
        sub.populate(text=chars)
        sub.subset(font)
        out = FONTS / f"galmuri11-{weight.lower()}.woff2"
        subset.save_font(font, str(out), opts)
        print(f"{out.relative_to(ROOT)}: {out.stat().st_size // 1024} KB, {len(chars)} chars")
    (FONTS / "GALMURI-LICENSE.txt").write_text((GALMURI / "LICENSE.txt").read_text())


if __name__ == "__main__":
    build_images()
    build_font()
