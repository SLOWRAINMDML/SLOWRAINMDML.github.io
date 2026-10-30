#!/usr/bin/env python3
"""Build content/games.json and game images from content/catalog.json.

Roblox games: names and store descriptions (ko/en) come from the public Roblox
APIs, as do the icon and every store thumbnail. Featured Roblox games also get a
1920px hero picked from the private game repo (assets/store/thumb_*.png), when a
GitHub token is available from `git credential fill`.

The Steam game uses the local store media in SRPG_STD (see STEAM_MEDIA below).

    python3 tools/build_content.py            # everything
    python3 tools/build_content.py --no-hero  # skip the GitHub hero step
"""
import io
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "content" / "catalog.json"
OUT = ROOT / "content" / "games.json"
MEDIA = ROOT / "assets" / "games"
STEAM_MEDIA = Path.home() / "project/SRPG_STD/output/release/2026-10-13-steam-media"
UA = {"User-Agent": "slowrain-games-site/1.0"}


def get(url, headers=None, raw=False, tries=4):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            break
        except (OSError, urllib.error.URLError):
            if attempt == tries - 1:
                raise
            time.sleep(2 ** attempt)
    return data if raw else json.loads(data)


def save_webp(img, path, width, quality=82):
    img = img.convert("RGB")
    if img.width > width:
        img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "WEBP", quality=quality, method=6)
    return path.relative_to(ROOT).as_posix()


def crop_ratio(img, ratio, focus_x=0.5):
    """Crop to width/height = ratio, keeping focus_x (0..1) of the width in view."""
    w, h = img.size
    if w / h > ratio:
        nw = round(h * ratio)
        left = min(max(round(w * focus_x - nw / 2), 0), w - nw)
        return img.crop((left, 0, left + nw, h))
    nh = round(w / ratio)
    top = (h - nh) // 2
    return img.crop((0, top, w, top + nh))


def github_token():
    try:
        out = subprocess.run(["git", "credential", "fill"], input="protocol=https\nhost=github.com\n\n",
                             capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return None
    for line in out.splitlines():
        if line.startswith("password="):
            return line[len("password="):]
    return None


def split_name(name):
    """'곰팡이펫 연구소 | MOLDY PETS LAB' -> ('곰팡이펫 연구소', 'MOLDY PETS LAB')."""
    if name and " | " in name:
        a, b = name.split(" | ", 1)
        return a.strip(), b.strip()
    return name, None


def fingerprint(img):
    return list(img.convert("L").resize((32, 18), Image.BILINEAR).getdata())


def distance(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def repo_text(token, repo, path):
    url = f"https://api.github.com/repos/SLOWRAINMDML/ROBLOX-{repo}/contents/{path}"
    try:
        return get(url, {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.raw"}, raw=True).decode()
    except Exception:
        return None


def hero_from_repo(token, game, first_thumb):
    """Find the repo's 1920px store thumbnail that matches Roblox's first thumbnail."""
    auth = {"Authorization": f"Bearer {token}"}
    url = f"https://api.github.com/repos/SLOWRAINMDML/ROBLOX-{game['repo']}/contents/assets/store"
    try:
        files = [f for f in get(url, auth) if f["name"].startswith("thumb") and f["name"].endswith(".png")]
    except Exception as exc:
        print(f"  hero: no assets/store ({exc})")
        return None
    target = fingerprint(first_thumb)
    best = None
    for f in files:
        img = Image.open(io.BytesIO(get(f["url"], {**auth, "Accept": "application/vnd.github.raw"}, raw=True)))
        score = distance(fingerprint(img), target)
        if best is None or score < best[0]:
            best = (score, f["name"], img)
    if not best:
        return None
    print(f"  hero: {best[1]} (distance {best[0]})")
    return best[2]


def build_roblox(games, featured, token):
    ids = ",".join(str(g["universeId"]) for g in games)
    info = {d["id"]: d for d in get(f"https://games.roblox.com/v1/games?universeIds={ids}")["data"]}
    icons = {d["targetId"]: d["imageUrl"] for d in get(
        f"https://thumbnails.roblox.com/v1/games/icons?universeIds={ids}&returnPolicy=PlaceHolder"
        "&size=512x512&format=Png&isCircular=false")["data"]}
    thumbs = {d["universeId"]: [t["imageUrl"] for t in d["thumbnails"] if t["state"] == "Completed"] for d in get(
        f"https://thumbnails.roblox.com/v1/games/multiget/thumbnails?universeIds={ids}&countPerUniverse=10"
        "&defaults=true&size=768x432&format=Png&isCircular=false")["data"]}

    out = []
    for g in games:
        uid = g["universeId"]
        print(g["id"])
        names = {d["languageCode"]: d for d in get(
            f"https://gameinternationalization.roblox.com/v1/name-description/games/{uid}")["data"]}
        ko, en = names.get("ko", {}), names.get("en", {})
        ko_title, en_from_ko = split_name(ko.get("name"))
        en_title = (en.get("name") and split_name(en["name"])[0]) or en_from_ko or info[uid]["name"]
        title = {"ko": ko_title or en_title, "en": en_title, **g.get("title", {})}

        desc_ko = ko.get("description") or info[uid]["description"]
        desc_en = en.get("description")
        if not desc_en and token:
            desc_en = repo_text(token, g["repo"], "docs/description_en.txt")
        description = {"ko": desc_ko.strip(), "en": (desc_en or desc_ko).strip(), **g.get("description", {})}

        folder = MEDIA / g["id"]
        icon = save_webp(Image.open(io.BytesIO(get(icons[uid], raw=True))), folder / "icon.webp", 256, 85)
        gallery = []
        first = None
        for i, url in enumerate(thumbs.get(uid, []), 1):
            img = Image.open(io.BytesIO(get(url, raw=True)))
            first = first or img
            gallery.append(save_webp(img, folder / f"shot-{i}.webp", 768))
        hero = None
        if g["id"] in featured and token and first is not None:
            big = hero_from_repo(token, g, first)
            if big is not None:
                hero = save_webp(crop_ratio(big, 16 / 9), folder / "hero.webp", 1600, 80)
        if hero is None and g["id"] in featured and (folder / "hero.webp").exists():
            hero = (folder / "hero.webp").relative_to(ROOT).as_posix()  # kept from an earlier run

        meta = info[uid]
        out.append({
            "id": g["id"],
            "platform": "roblox",
            "title": title,
            "tagline": g["tagline"],
            "description": description,
            "tags": g["tags"],
            "players": meta.get("maxPlayers"),
            "released": meta.get("created", "")[:10],
            "url": f"https://www.roblox.com/games/{g['placeId']}",
            "icon": icon,
            "cover": gallery[0] if gallery else icon,
            "hero": hero or (gallery[0] if gallery else None),
            "gallery": gallery,
        })
    return out


def build_steam(g):
    print(g["id"])
    folder = MEDIA / g["id"]
    app = g["steamAppId"]
    details = {}
    for lang, code in (("ko", "korean"), ("en", "english")):
        details[lang] = get(f"https://store.steampowered.com/api/appdetails?appids={app}&l={code}")[str(app)]["data"]

    caps = STEAM_MEDIA / "capsules"
    hero = save_webp(crop_ratio(Image.open(caps / "library-hero.jpg"), 2.2, 0.6), folder / "hero.webp", 1920, 80)
    logo = folder / "logo.webp"
    Image.open(caps / "library-logo.png").save(logo, "WEBP", quality=90, method=6, lossless=False)
    cover = save_webp(Image.open(caps / "main.png"), folder / "cover.webp", 900, 84)
    poster = save_webp(Image.open(caps / "vertical.png"), folder / "poster.webp", 748, 84)
    gallery = [save_webp(Image.open(p), folder / f"shot-{i}.webp", 1280, 80)
               for i, p in enumerate(sorted((STEAM_MEDIA / "screenshots").glob("*.png")), 1)]
    videos = []
    for name in ("tactics-battle-action", "tactics-tactical-movement"):
        src = STEAM_MEDIA / "description" / f"{name}.mp4"
        if src.exists():
            dst = folder / f"{name}.mp4"
            dst.write_bytes(src.read_bytes())
            videos.append(dst.relative_to(ROOT).as_posix())

    return {
        "id": g["id"],
        "platform": "steam",
        "title": g["title"],
        "tagline": g["tagline"],
        "description": {lang: details[lang]["short_description"] for lang in ("ko", "en")},
        "highlights": g.get("highlights"),
        "tags": g["tags"],
        "status": g["status"],
        "facts": g["facts"],
        "url": f"https://store.steampowered.com/app/{app}/",
        "icon": None,
        "logo": logo.relative_to(ROOT).as_posix(),
        "cover": cover,
        "poster": poster,
        "hero": hero,
        "gallery": gallery,
        "videos": videos,
    }


def main():
    catalog = json.loads(CATALOG.read_text())
    token = None if "--no-hero" in sys.argv else github_token()
    featured = set(catalog["featured"])
    roblox = [g for g in catalog["games"] if g["platform"] == "roblox"]
    built = {g["id"]: g for g in build_roblox(roblox, featured, token)}
    for g in catalog["games"]:
        if g["platform"] == "steam":
            built[g["id"]] = build_steam(g)
    games = [built[g["id"]] for g in catalog["games"]]
    OUT.write_text(json.dumps({"featured": catalog["featured"], "games": games}, ensure_ascii=False, indent=1) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(games)} games")


if __name__ == "__main__":
    main()
