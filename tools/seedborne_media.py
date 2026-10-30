#!/usr/bin/env python3
"""Images for Seedborne Chronicle (no store page yet), made from captures of the current Godot build.

Captures (~/project/RandomWorldRPG-Godot, Godot 4.7.1, window parked off-screen; the window is clamped to the
screen, so shots come out about 1470x720):
    G=~/project/Godot/Godot-4.7.1/Godot.app/Contents/MacOS/Godot
    $G --path . --resolution 1920x1080 --position 3000,3000 --script res://tools/probe/world_shot.gd -- MOON-7777
        -> /tmp/rpg2_godot/world_<n>.png
    $G ... --script res://tools/probe/town_shots.gd -- /tmp/seed-shots MOON-7777:2
    $G ... --script res://tools/probe/battle_play.gd -- meadow|crypt      -> /tmp/rpg2_godot/battle_<sc>_<frame>.png
    mkdir -p /tmp/house; $G ... --fixed-fps 30 --script res://tools/probe/home_tour.gd -- 0 /tmp/house
The world-map HUD shot is docs/koinonia-20261029/hud.png in that repo.

    python3 tools/seedborne_media.py    # then python3 tools/build_content.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/games/seedborne-chronicle"
GAME = Path.home() / "project/RandomWorldRPG-Godot"
FONT = GAME / "assets/fonts/Galmuri11-Bold.ttf"

HERO = "/tmp/rpg2_godot/world_1.png"
GALLERY = [
    "/tmp/rpg2_godot/world_1.png",
    str(GAME / "docs/koinonia-20261029/hud.png"),
    "/tmp/rpg2_godot/battle_meadow_340.png",
    "/tmp/rpg2_godot/battle_crypt_410.png",
    "/tmp/house/tour_5g_after.png",
    "/tmp/house/tour_7_yard_ripe.png",
    "/tmp/seed-shots/town_MOON-7777_2.png",
    "/tmp/rpg2_godot/battle_crypt_100.png",
    "/tmp/rpg2_godot/world_0.png",
]


def logo(scale=4):
    """The title screen's logo: SEEDBORNE (gold, 36px) over CHRONICLE (cream, 24px), Galmuri bold,
    dark brown outline and a soft drop shadow, drawn at pixel size and enlarged without smoothing."""
    lines = [("SEEDBORNE", 36, (227, 169, 43)), ("CHRONICLE", 24, (248, 237, 203))]
    pad, gap = 8, 0
    fonts = [ImageFont.truetype(str(FONT), size) for _, size, _ in lines]
    boxes = [ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), t, font=f, stroke_width=3) for (t, _, _), f in zip(lines, fonts)]
    w = max(b[2] - b[0] for b in boxes) + pad * 2
    h = sum(b[3] - b[1] for b in boxes) + gap + pad * 2 + 3
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    y = pad
    for (text, _, colour), font, box in zip(lines, fonts, boxes):
        x = (w - (box[2] - box[0])) // 2 - box[0]
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.fontmode = "1"
        d.text((x, y - box[1] + 3), text, font=font, fill=(0, 0, 0, 115), stroke_width=3, stroke_fill=(0, 0, 0, 115))
        img.alpha_composite(layer)
        d = ImageDraw.Draw(img)
        d.fontmode = "1"
        d.text((x, y - box[1]), text, font=font, fill=colour, stroke_width=3, stroke_fill=(43, 29, 18))
        y += box[3] - box[1] + gap
    return img.resize((w * scale, h * scale), Image.NEAREST)


def fit(img, size, focus=(0.5, 0.5)):
    w, h = size
    s = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = round((img.width - w) * focus[0])
    y = round((img.height - h) * focus[1])
    return img.crop((x, y, x + w, y + h))


def shade(img, side, strength):
    """Darken towards one side so the logo and text stay readable."""
    w, h = img.size
    ramp = Image.new("L", (w, h))
    px = ramp.load()
    for yy in range(h):
        for xx in range(w):
            t = {"left": 1 - xx / w, "top": 1 - yy / h}[side]
            px[xx, yy] = int(255 * strength * max(0.0, t - 0.25) / 0.75)
    dark = Image.new("RGB", (w, h), (14, 22, 34))
    return Image.composite(dark, img, ramp)


def save(img, name, quality=82):
    img.convert("RGB").save(OUT / name, "WEBP", quality=quality, method=6)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    mark = logo()
    mark.save(OUT / "logo.webp", "WEBP", lossless=True)

    hero = Image.open(HERO).convert("RGB")
    save(fit(hero, (1600, 727), (0.5, 0.5)), "hero.webp", 82)

    cover = shade(fit(hero, (1232, 693)), "left", 0.75)
    m = mark.resize((560, round(mark.height * 560 / mark.width)), Image.NEAREST)
    cover.paste(m, (60, (693 - m.height) // 2), m)
    save(cover, "cover.webp", 84)

    town = Image.open("/tmp/seed-shots/town_MOON-7777_2.png").convert("RGB")
    poster = shade(fit(town, (748, 896), (0.45, 0.5)), "top", 0.8)
    m = mark.resize((620, round(mark.height * 620 / mark.width)), Image.NEAREST)
    poster.paste(m, ((748 - m.width) // 2, 56), m)
    save(poster, "poster.webp", 84)

    for i, src in enumerate(GALLERY, 1):
        img = Image.open(src).convert("RGB")
        if img.width > 1280:
            img = img.resize((1280, round(img.height * 1280 / img.width)), Image.LANCZOS)
        save(img, f"shot-{i}.webp", 82)
    print(f"{OUT.relative_to(ROOT)}: logo, hero, cover, poster, {len(GALLERY)} shots")


if __name__ == "__main__":
    main()
