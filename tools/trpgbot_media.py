#!/usr/bin/env python3
"""Cover and gallery for the TRPG master bot from the phone screenshots in /tmp/trpgbot/final (see tools/trpgbot/)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/games/trpg-master-bot"
COVER = ["/tmp/trpgbot/final/3_scene.png", "/tmp/trpgbot/final/3b_roll.png", "/tmp/trpgbot/final/4_fight.png"]
SHOTS = ["/tmp/trpgbot/final/1_builder.png", "/tmp/trpgbot/final/2_party.png", "/tmp/trpgbot/final/3_scene.png",
         "/tmp/trpgbot/final/3b_roll.png", "/tmp/trpgbot/final/4_fight.png"]
BG = (28, 23, 18)  # the app's theme colour


def phone(img, height, radius=26):
    """A screenshot as a rounded phone screen with a thin bezel."""
    shot = img.resize((round(img.width * height / img.height), height), Image.LANCZOS)
    bezel = 8
    frame = Image.new("RGBA", (shot.width + bezel * 2, shot.height + bezel * 2), (0, 0, 0, 0))
    ImageDraw.Draw(frame).rounded_rectangle((0, 0, frame.width - 1, frame.height - 1), radius + bezel, fill=(12, 10, 8, 255))
    mask = Image.new("L", shot.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, shot.width - 1, shot.height - 1), radius, fill=255)
    frame.paste(shot, (bezel, bezel), mask)
    return frame


def cover(shots, size=(1232, 693)):
    w, h = size
    canvas = Image.new("RGBA", size, BG + (255,))
    # warm table-lamp glow behind the phones
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((w * 0.15, h * 0.05, w * 0.85, h * 1.1), fill=(227, 169, 43, 70))
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))
    phones = [phone(s, int(h * 0.86)) for s in shots]
    gap = 34
    total = sum(p.width for p in phones) + gap * (len(phones) - 1)
    x = (w - total) // 2
    for i, p in enumerate(phones):
        y = (h - p.height) // 2 + (0 if i == 1 else 22)
        shadow = Image.new("RGBA", size, (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle((x + 6, y + 14, x + p.width + 6, y + p.height + 14), 34, fill=(0, 0, 0, 150))
        canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14)))
        canvas.alpha_composite(p, (x, y))
        x += p.width + gap
    return canvas.convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("shot-*.webp"):
        old.unlink()
    cover([Image.open(p).convert("RGB") for p in COVER]).save(OUT / "cover.webp", "WEBP", quality=86, method=6)
    shots = [Image.open(p).convert("RGB") for p in SHOTS]
    for i, shot in enumerate(shots, 1):
        shot.resize((720, round(shot.height * 720 / shot.width)), Image.LANCZOS).save(OUT / f"shot-{i}.webp", "WEBP", quality=84, method=6)
    print(f"{OUT.relative_to(ROOT)}: cover + {len(shots)} shots")


if __name__ == "__main__":
    main()
