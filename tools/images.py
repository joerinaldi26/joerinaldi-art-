#!/usr/bin/env python3
"""Turn original artwork into the three web sizes the site uses.

Put originals in  originals/<series-slug>/<NN>.<png|jpg|webp|tif>
(NN = the piece number in content.json, e.g. 01 for Cantina Chase!), then run:

    pip install pillow
    python3 tools/images.py

Writes site/img/<slug>/<NN>-800.webp, -1600.webp and -full.webp, and updates the
piece's width/height in content.json. -full is capped at 6000px wide, so long
pieces like the Star Wars chases keep their detail in the full-size viewer.
"""
import glob, json, os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FULL_MAX = 6000
content_path = os.path.join(ROOT, "content.json")
C = json.load(open(content_path, encoding="utf-8"))
series = {s["slug"]: s for s in C["series"]}

for path in sorted(glob.glob(os.path.join(ROOT, "originals", "*", "*"))):
    slug = os.path.basename(os.path.dirname(path))
    num = os.path.splitext(os.path.basename(path))[0]
    if slug not in series:
        print("skip (unknown series):", path); continue
    im = Image.open(path)
    if getattr(im, "n_frames", 1) > 1:
        im.seek(0)
    im = im.convert("RGBA")
    if im.getchannel("A").getextrema()[0] == 255:
        im = im.convert("RGB")
    out = os.path.join(ROOT, "site", "img", slug)
    os.makedirs(out, exist_ok=True)
    full = im
    for size, maxw in (("800", 800), ("1600", 1600), ("full", FULL_MAX)):
        w, h = im.size
        r = im if w <= maxw else im.resize((maxw, round(h * maxw / w)), Image.LANCZOS)
        r.save(os.path.join(out, f"{num}-{size}.webp"), "WEBP", quality=82, method=5)
        if size == "full":
            full = r
    for p in series[slug]["pieces"]:
        if p["file"] == num:
            p["w"], p["h"] = full.size
    print("ok", slug, num, full.size)

json.dump(C, open(content_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("Now run: python3 build.py")
