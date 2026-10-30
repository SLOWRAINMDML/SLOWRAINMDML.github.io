#!/usr/bin/env python3
"""Build content/games.json and game images from content/catalog.json.

Roblox games: names and store descriptions (ko/en) come from the public Roblox
APIs, as do the icon and every store thumbnail. Featured Roblox games also get a
1920px hero picked from the private game repo (assets/store/thumb_*.png), when a
GitHub token is available from `git credential fill`.

The Steam game takes its capsule, screenshots and clips from the live store page, and its
banner/poster from the same in-game renders as the store header (SRPG_STD tools, local only).

    python3 tools/build_content.py            # everything
    python3 tools/build_content.py --no-hero  # skip the GitHub hero step
"""
import importlib.util
import io
import json
import re
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
SRPG = Path.home() / "project/SRPG_STD"
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


def steam_ingame_art(folder):
    """Banner, poster and logo from the same in-game renders as the live Steam header/main capsule.

    Uses SRPG_STD's tools/build_steam_header_ingame_20261014.py (voxel castle backdrop + Adrian/Sarah
    render, night grade, pixel logo). No painted key art."""
    spec = importlib.util.spec_from_file_location("ingame", SRPG / "tools/build_steam_header_ingame_20261014.py")
    ingame = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ingame)
    renders = SRPG / "output/release/2026-10-14-steam-capsules/render/header_noai"
    castle = Image.open(renders / "castle_backdrop.png").convert("RGB")
    party = Image.open(renders / "party_h2.png").convert("RGBA")
    party = ingame.night_grade(party.crop(party.getbbox()))

    place_logo = ingame.caps.place_logo
    ingame.caps.place_logo = lambda img, *args, **kwargs: img.convert("RGB")  # the page draws its own title
    try:
        hero = ingame.header(castle, party, size=(1920, 872), castle_cx=1560, party_h=760, party_cx=1300, cut=0.12)
    finally:
        ingame.caps.place_logo = place_logo
    poster = ingame.header(castle, party, size=(748, 896), castle_cx=470, party_h=640, party_cx=390, cut=0.1,
                           logo_box=(0.07, 0.05, 0.93, 0.3))
    logo = ingame.caps.logo("pixel", 1100)
    logo.save(folder / "logo.webp", "WEBP", quality=92, method=6)
    return (save_webp(hero, folder / "hero.webp", 1920, 82), save_webp(poster, folder / "poster.webp", 748, 86),
            (folder / "logo.webp").relative_to(ROOT).as_posix())


def build_steam(g):
    """Steam game: capsule, screenshots and description clips straight from the live store page."""
    print(g["id"])
    folder = MEDIA / g["id"]
    for old in folder.glob("*"):
        old.unlink()
    folder.mkdir(parents=True, exist_ok=True)
    app = g["steamAppId"]
    details = {}
    for lang, code in (("ko", "korean"), ("en", "english")):
        details[lang] = get(f"https://store.steampowered.com/api/appdetails?appids={app}&l={code}")[str(app)]["data"]
    page = get(f"https://store.steampowered.com/app/{app}/?l=english",
               {"Cookie": "birthtime=0; wants_mature_content=1"}, raw=True).decode("utf-8", "replace")

    capsule = re.search(r'https://[^"\' ]+/apps/%d/[0-9a-f]+/capsule_616x353\.jpg' % app, page).group(0)
    cover = save_webp(Image.open(io.BytesIO(get(capsule.replace(".jpg", "_2x.jpg"), raw=True))), folder / "cover.webp", 1232, 84)
    gallery = [save_webp(Image.open(io.BytesIO(get(s["path_full"], raw=True))), folder / f"shot-{i}.webp", 1280, 82)
               for i, s in enumerate(details["en"]["screenshots"], 1)]
    videos = []
    for i, url in enumerate(dict.fromkeys(re.findall(r'https://[^"\' ]+/apps/%d/extras/[0-9a-f]+\.mp4' % app, page)), 1):
        dst = folder / f"clip-{i}.mp4"
        dst.write_bytes(get(url, raw=True))
        poster = dst.with_suffix(".webp")
        frame = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", "1", "-i", str(dst), "-frames:v", "1",
                                "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True).stdout
        save_webp(Image.open(io.BytesIO(frame)), poster, 640, 80)
        videos.append({"src": dst.relative_to(ROOT).as_posix(), "poster": poster.relative_to(ROOT).as_posix()})
    hero, poster, logo = steam_ingame_art(folder)

    return {
        "id": g["id"],
        "platform": "pc",
        "platforms": g["platforms"],
        "title": g["title"],
        "tagline": g["tagline"],
        "description": {lang: details[lang]["short_description"] for lang in ("ko", "en")},
        "highlights": g.get("highlights"),
        "tags": g["tags"],
        "status": g["status"],
        "facts": g["facts"],
        "url": f"https://store.steampowered.com/app/{app}/",
        "icon": None,
        "logo": logo,
        "cover": cover,
        "poster": poster,
        "hero": hero,
        "heroFocus": "80% 50%",
        "gallery": gallery,
        "videos": videos,
    }


def build_unreleased(g):
    """PC game without a store page yet: images already made in assets/games/<id>/ (see tools/seedborne_media.py)."""
    print(g["id"])
    folder = MEDIA / g["id"]
    rel = lambda p: p.relative_to(ROOT).as_posix()
    return {
        "id": g["id"],
        "platform": "pc",
        "platforms": g["platforms"],
        "title": g["title"],
        "tagline": g["tagline"],
        "description": g["description"],
        "highlights": g.get("highlights"),
        "tags": g["tags"],
        "status": g["status"],
        "facts": g["facts"],
        "url": None,
        "icon": None,
        "logo": rel(folder / "logo.webp"),
        "cover": rel(folder / "cover.webp"),
        "poster": rel(folder / "poster.webp"),
        "hero": rel(folder / "hero.webp"),
        "gallery": [rel(p) for p in sorted(folder.glob("shot-*.webp"), key=lambda p: int(p.stem.split("-")[1]))],
        "videos": [],
    }


def main():
    catalog = json.loads(CATALOG.read_text())
    token = None if "--no-hero" in sys.argv else github_token()
    featured = set(catalog["featured"])
    roblox = [g for g in catalog["games"] if g["platform"] == "roblox"]
    built = {g["id"]: g for g in build_roblox(roblox, featured, token)}
    for g in catalog["games"]:
        if g["platform"] == "pc":
            built[g["id"]] = build_steam(g) if g.get("steamAppId") else build_unreleased(g)
    games = [built[g["id"]] for g in catalog["games"]]
    OUT.write_text(json.dumps({"featured": catalog["featured"], "games": games}, ensure_ascii=False, indent=1) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(games)} games")


if __name__ == "__main__":
    main()
