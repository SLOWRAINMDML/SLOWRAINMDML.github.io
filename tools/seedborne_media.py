#!/usr/bin/env python3
"""Images for Seedborne Chronicle from its official store art.

- STOVE (released 2026-11, https://store.onstove.com/ko/games/106576): the key art (book and sprout logo) and the
  Korean screenshots, read straight from the store page. The key art is the card cover and the portrait card.
- Steam (coming 2026-12-08, https://store.steampowered.com/app/5578430/): the main capsule from the store page, and
  from the Steam kit (~/project/RandomWorldRPG-Godot/marketing/steam_20261106/art) the text-free library hero and the
  logo for the top banner, plus a few 1920x1080 screenshots for the gallery.

    python3 tools/seedborne_media.py    # then python3 tools/build_content.py
"""
import io
import re
import time
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/games/seedborne-chronicle"
STOVE_PAGE = "https://store.onstove.com/ko/games/106576"
STEAM_PAGE = "https://store.steampowered.com/app/5578430/?l=koreana"
STOVE_IMAGES = r"https://d2x8kymwjom7h7\.cloudfront\.net/live/member_no/83974014/application_no/SGS0104044/images/[^\"\\ ]+\.(?:png|jpg|jpeg|webp)"
KIT = Path.home() / "project/RandomWorldRPG-Godot/marketing/steam_20261106/art"
KIT_SHOTS = ["09_sailing.png", "07_labyrinth.png", "04_all_out_attack.png", "03_whirlwind_strike.png"]


def get(url, tries=4):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (slowrain-games-site)", "Cookie": "birthtime=0; wants_mature_content=1"})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except OSError:
            if attempt == tries - 1:
                raise
            time.sleep(2 ** attempt)


def save(img, name, width=None, quality=84):
    img = img.convert("RGB")
    if width and img.width > width:
        img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    img.save(OUT / name, "WEBP", quality=quality, method=6)


def crop_ratio(img, ratio, focus_x=0.5):
    w, h = img.size
    if w / h > ratio:
        nw = round(h * ratio)
        left = min(max(round(w * focus_x - nw / 2), 0), w - nw)
        return img.crop((left, 0, left + nw, h))
    nh = round(w / ratio)
    return img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    page = get(STOVE_PAGE).decode("utf-8", "replace")
    urls = list(dict.fromkeys(re.findall(STOVE_IMAGES, page)))  # page order, no repeats
    key_url = next(u for u in urls if "store-key-art" in u)
    key = Image.open(io.BytesIO(get(key_url)))

    steam = get(STEAM_PAGE).decode("utf-8", "replace")
    capsule = re.search(r"https://[^\"' ]+/apps/5578430/[0-9a-f]+/capsule_616x353\.jpg", steam).group(0)
    shots = [Image.open(io.BytesIO(get(capsule.replace(".jpg", "_2x.jpg"))))]  # the Steam main capsule
    shots += [Image.open(io.BytesIO(get(u))) for u in urls if u != key_url]
    shots += [Image.open(KIT / "screenshots" / name) for name in KIT_SHOTS]

    for old in OUT.glob("*.webp"):  # only now that every download worked
        old.unlink()
    save(key, "cover.webp", quality=90)
    save(crop_ratio(key, 748 / 896), "poster.webp", quality=90)
    for i, shot in enumerate(shots, 1):
        save(shot, f"shot-{i}.webp", 1280, 82)

    hero = crop_ratio(Image.open(KIT / "library_hero_3840x1240.png"), 2.2, 0.55)
    save(hero, "hero.webp", 1920, 82)
    Image.open(KIT / "library_logo_1280x720.png").convert("RGBA").crop(
        Image.open(KIT / "library_logo_1280x720.png").getbbox()).save(OUT / "logo.webp", "WEBP", lossless=True)
    print(f"{OUT.relative_to(ROOT)}: cover, poster, hero, logo, {len(shots)} shots (1 Steam capsule, {len(urls) - 1} from STOVE)")


if __name__ == "__main__":
    main()
