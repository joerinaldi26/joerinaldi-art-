#!/usr/bin/env python3
"""Builds joerinaldi.art into ./site from content.json.

Edit content.json (titles, captions, Etsy links, copy), then run:  python3 build.py
Images live in site/img/<series>/<NN>-800.webp, -1600.webp and -full.webp.
"""
import json, html, os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "site")
C = json.load(open(os.path.join(ROOT, "content.json"), encoding="utf-8"))
S = C["site"]
SERIES = C["series"]
BY = {s["slug"]: s for s in SERIES}
GROUPS = {g["id"]: g for g in C["groups"]}
DOMAIN = "https://joerinaldi.art"
e = lambda t: html.escape(t or "", quote=True)

EXT = '<svg class="ext" aria-hidden="true" width="11" height="11" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 2h6v6M10 2 3 9"/></svg>'
EXPAND = '<svg aria-hidden="true" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10 2h4v4M6 14H2v-4M14 2 9.5 6.5M2 14l4.5-4.5"/></svg>'

def img(slug, f, size="800"):
    return f"/img/{slug}/{f}-{size}.webp"

def srcset(slug, p):
    return f'src="{img(slug, p["file"])}" srcset="{img(slug, p["file"])} 800w, {img(slug, p["file"], "1600")} 1600w"'

def dims(p, maxw=800):
    w, h = p["w"], p["h"]
    if w > maxw:
        h, w = round(h * maxw / w), maxw
    return f'width="{w}" height="{h}"'

def lb_attrs(slug, p):
    return (f'data-lb data-full="{img(slug, p["file"], "full")}" data-thumb="{img(slug, p["file"])}" '
            f'data-w="{p["w"]}" data-h="{p["h"]}" data-title="{e(p["title"])}"')

def page(title, desc, body, path, active="Work", og=None):
    og = og or "/img/phanatics/00-1600.webp"
    nav = "".join(
        f'<a href="{href}"{" aria-current=\"page\"" if label == active else ""}>{label}</a>'
        for label, href in [("Work", "/"), ("About", "/#about")])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{DOMAIN}{path}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{DOMAIN}{og}">
<meta property="og:url" content="{DOMAIN}{path}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/fonts/libre-franklin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/big-shoulders-display.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="topbar" aria-hidden="true"></div>
<header class="wrap">
<div class="masthead">
<a class="wordmark" href="/">Joe Rinaldi</a>
<nav class="nav cap" aria-label="Main">{nav}<a class="shop" href="{S['shop']}" target="_blank" rel="noopener">Shop{EXT}</a></nav>
</div>
</header>
<main id="main">
{body}
</main>
{footer()}
<script src="/assets/viewer.js" defer></script>
</body>
</html>
"""

def footer():
    return f"""<footer class="footer">
<div class="wrap">
<div class="footer-top">
<div>
<p class="kick">{e(S['shop_name'])} on Etsy</p>
<p class="head">Tell your friends to <span style="color: var(--pink)">tell their dads.</span></p>
</div>
<a class="btn" href="{S['shop']}" target="_blank" rel="noopener">Shop on Etsy{EXT}</a>
</div>
<div class="footer-base">
<span>&#169; Joe Rinaldi, Philadelphia. Semipro tee-ball coach.</span>
<nav aria-label="Elsewhere">
<a href="mailto:{S['email']}">{S['email']}</a>
<a href="{S['instagram']}">Instagram</a>
<a href="{S['shop']}" target="_blank" rel="noopener">Etsy shop {EXT}</a>
</nav>
</div>
</div>
</footer>"""

def capbar(left, right="", right_cls="count"):
    return f'<div class="capbar"><span class="cap">{e(left)}</span><span class="cap {right_cls}">{e(right)}</span></div>'

def visible(s):
    return [p for p in s["pieces"] if not p.get("hidden")]

# ---------------- homepage ----------------
def home():
    cast = [("phanatics-03", 220, "The Phanatic at bat"), ("sports-02", 240, "Joel Embiid"), ("star-wars-chase-08", 160, "Ponda Baba"),
            ("superheroes-02", 210, "Dr. Doom"), ("kids-00", 190, "A birthday pirate"), ("sports-16", 230, "Jalen Hurts"), ("phanatics-12", 215, "The Phanatic")]
    lineup = "\n".join(f'<img src="/img/cast/{n}.webp" alt="{e(a)}" style="height: min({h}px, {h / 11:.2f}vw); z-index: {i % 3 + 1}">' for i, (n, h, a) in enumerate(cast))

    def tile(slug):
        s = BY[slug]; t = C["tiles"][slug]; p = s["pieces"][t["image"]]
        return f"""<a class="tile" href="/{slug}/">
<div class="tile-img"><img class="art" {srcset(slug, p)} sizes="(max-width: 700px) 90vw, 400px" {dims(p)} alt="" loading="lazy"></div>
{capbar(s['title'], f"{len(visible(s))} pieces")}
<p>{e(t['line'])}</p>
</a>"""

    def shelf(gid, n):
        g = GROUPS[gid]; slugs = [s["slug"] for s in SERIES if s["group"] == gid]
        two = " two" if len(slugs) == 2 else ""
        return f"""<section class="shelf" aria-labelledby="g-{gid}">
<div class="shelf-head"><div><p class="kick">Section {n:02d}</p><h2 class="head" id="g-{gid}">{e(g['name'])}</h2></div><p class="shelf-line">{e(g['line'])}</p></div>
<div class="grid{two}">
{''.join(tile(s) for s in slugs)}
</div>
</section>"""

    stickers = "".join(f'<img class="art" src="{img("phanatics", BY["phanatics"]["pieces"][i]["file"])}" alt="{e(BY["phanatics"]["pieces"][i]["title"])} sticker" loading="lazy">' for i in [0, 13, 9, 15])
    shop = f"""<section class="shop-band" aria-labelledby="shop-h">
<div>
<p class="kick">{e(S['shop_name'])} on Etsy</p>
<h2 class="head" id="shop-h" style="margin-bottom: 14px">Stickers, magnets and shirts</h2>
<p>The Phanatics and a few of the Philly sports pieces are for sale in my Etsy shop. Tell your friends to tell their dads.</p>
<a class="btn" href="{S['shop']}" target="_blank" rel="noopener">Shop on Etsy{EXT}</a>
</div>
<div class="stickers">{stickers}</div>
</section>"""

    board = ""
    if C.get("drawing_board"):
        cards = []
        for d in C["drawing_board"]:
            s = BY[d["series"]]; p = s["pieces"][d["image"]]
            cards.append(f"""<a class="tile" href="/{s['slug']}/">
<div class="tile-img"><img class="art" {srcset(s['slug'], p)} sizes="(max-width: 700px) 90vw, 400px" {dims(p)} alt="" loading="lazy"></div>
{capbar(d['title'], 'In progress')}
<p>{e(d['line'])}</p>
</a>""")
        board = f"""<section class="shelf" aria-labelledby="g-board">
<div class="shelf-head"><div><p class="kick">Section {len(C['groups']) + 1:02d}</p><h2 class="head" id="g-board">On the Drawing Board</h2></div><p class="shelf-line">New projects and works in progress, posted before they are finished.</p></div>
<div class="grid">{''.join(cards)}</div>
</section>"""

    tag_a, tag_b = S["tagline"].rsplit(". ", 1)
    about = "".join(f"<p>{'<span class=\"dropcap\" aria-hidden=\"true\">' + e(t[0]) + '</span><span class=\"sr-only\">' + e(t[0]) + '</span>' + e(t[1:]) if i == 0 else e(t)}</p>" for i, t in enumerate(S["about"]))
    body = f"""<div class="wrap">
<section class="hero">
<p class="kick">Illustration &#183; Philadelphia</p>
<h1 class="disp">{e(tag_a)}. <span>{e(tag_b)}</span></h1>
<div class="byline"><p class="cap" style="font-size: 13px">By Joe Rinaldi</p><p class="intro">{e(S['intro'])}</p></div>
<div class="lineup" role="img" aria-label="A lineup of characters from the work below">
{lineup}
</div>
</section>
{shelf('home-team', 1)}
{shop}
{shelf('multiverse', 2)}
{shelf('for-hire', 3)}
{board}
<section class="about" id="about" aria-labelledby="about-h">
<div><p class="kick">About</p><h2 class="head" id="about-h">Joe Rinaldi</h2></div>
<div class="body">{about}<p>Say hi: <a href="mailto:{S['email']}">{S['email']}</a></p></div>
</section>
</div>"""
    return page(f"Joe Rinaldi: {S['tagline']}", S["intro"], body, "/")

# ---------------- series pages ----------------
def series_page(s, prev, nxt):
    slug = s["slug"]
    pieces = visible(s)
    li = s["lead"]["index"]; lead = s["pieces"][li]
    rest = [p for p in pieces if p is not lead]
    if s.get("wide_first"):
        rest = [p for p in rest if p["w"] / p["h"] > 2.2] + [p for p in rest if p["w"] / p["h"] <= 2.2]
    pieces = [lead] + rest
    n_total = len(pieces)
    wide = lead["w"] / lead["h"] > 2.2
    tone = s["lead"]["tone"]
    num_of = {id(p): i + 1 for i, p in enumerate(pieces)}

    buy_lead = f'<a class="buy" href="{lead["etsy"]}" target="_blank" rel="noopener">Buy on Etsy{EXT}</a>' if lead.get("etsy") else ""
    cap_lead = f'<span class="cap" style="font-size: 15px">{e(lead["title"])}</span>&#160; {e(s["lead"]["caption"])}' if s["lead"]["caption"] else f'<span class="cap" style="font-size: 15px">{e(lead["title"])}</span>'
    if wide:
        leadoff = f"""<section class="leadoff wide {'light' if tone == 'light' else ''}" aria-label="Leading off">
<div class="leadoff-inner">
<p class="kick">Leading Off</p>
<button type="button" class="leadoff-art" {lb_attrs(slug, lead)} aria-label="View {e(lead['title'])} full size"><img src="{img(slug, lead['file'], 'full')}" {dims(lead, 2500)} alt="{e(lead['title'])}"></button>
<div class="leadoff-text"><p>{cap_lead} <span class="lo-num">{num_of[id(lead)]:02d} / {n_total}</span></p>
<button type="button" class="btn-line" {lb_attrs(slug, lead)}>{EXPAND}View full size</button></div>
</div>
</section>"""
    else:
        leadoff = f"""<section class="leadoff {'light' if tone == 'light' else ''}" aria-label="Leading off">
<div class="leadoff-inner">
<button type="button" class="leadoff-art" {lb_attrs(slug, lead)} aria-label="View {e(lead['title'])} full size"><img {srcset(slug, lead)} sizes="(max-width: 700px) 92vw, 760px" {dims(lead, 1600)} alt="{e(lead['title'])}"></button>
<div class="leadoff-text"><p class="kick">Leading Off</p><p>{cap_lead}</p>{buy_lead}</div>
</div>
</section>"""

    figs = []
    for p in rest:
        is_wide = p["w"] / p["h"] > 2.2
        right = (f'<a class="buy" href="{p["etsy"]}" target="_blank" rel="noopener">Buy on Etsy{EXT}</a>' if p.get("etsy")
                 else (f'<button type="button" class="btn-line" {lb_attrs(slug, p)}>{EXPAND}View full size</button>' if is_wide else ""))
        num = f' <span class="num">{num_of[id(p)]:02d} / {n_total}</span>' if is_wide else ""
        sizes = "(max-width: 1360px) 100vw, 1264px" if is_wide else "(max-width: 700px) 92vw, 420px"
        src = f'src="{img(slug, p["file"], "1600")}" srcset="{img(slug, p["file"])} 800w, {img(slug, p["file"], "1600")} 1600w, {img(slug, p["file"], "full")} 2500w"' if is_wide else srcset(slug, p)
        figs.append(f"""<figure class="piece{' wide' if is_wide else ''}">
<button type="button" class="piece-open" {lb_attrs(slug, p)} aria-label="View {e(p['title'] or 'this piece')} full size"><img class="art" {src} sizes="{sizes}" {dims(p, 1600 if is_wide else 800)} alt="{e(p['title'])}" loading="lazy"></button>
<figcaption><span class="cap">{e(p['title'])}{num}</span>{right}</figcaption>
</figure>""")

    g = GROUPS[s["group"]]
    shopbox = ""
    if slug in ("phanatics", "sports"):
        label = "Shop the Phanatics" if slug == "phanatics" else "Shop stickers"
        shopbox = f'<div class="shopbox"><a class="btn" href="{S["shop"]}" target="_blank" rel="noopener">{label}{EXT}</a><span>At {e(S["shop_name"])}, my Etsy shop</span></div>'
    point = ""
    if s.get("point_after"):
        point = f"""<section class="point-after" aria-label="Point after">
<div><p class="kick">Point After</p><h2 class="head" style="font-size: 36px">How it started</h2></div>
<div class="body"><p>{e(s['point_after'])}</p></div>
</section>"""
    nav = '<nav class="series-nav" aria-label="More series">'
    if prev: nav += f'<a href="/{prev["slug"]}/"><span class="kick">Previous</span><span class="head">{e(prev["title"])}</span></a>'
    if nxt: nav += f'<a class="next" href="/{nxt["slug"]}/"><span class="kick">Next</span><span class="head">{e(nxt["title"])}</span></a>'
    nav += "</nav>"
    body = f"""<div class="wrap">
<div class="series-head">
<div>
<p class="kick"><a href="/">Work</a> / {e(g['name'])}</p>
<h1 class="disp">{e(s['title'])}</h1>
<p class="deck">{e(s['deck'])}</p>
</div>
{shopbox}
</div>
</div>
{leadoff}
<div class="wrap">
<div class="pieces">
{''.join(figs)}
</div>
{point}
{nav}
</div>"""
    og = img(slug, lead["file"], "1600")
    return page(f"{s['title']}: Joe Rinaldi", s["deck"], body, f"/{slug}/", og=og)

def not_found():
    body = f"""<div class="wrap"><div class="series-head"><div>
<p class="kick">404</p><h1 class="disp">Foul ball.</h1>
<p class="deck">That page isn't here. Head back to <a href="/">the work</a>.</p>
</div></div></div>"""
    return page("Page not found: Joe Rinaldi", "Page not found", body, "/404")

def write(rel, text):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    assert chr(0x2014) not in text, f"em dash in {rel}"
    open(path, "w", encoding="utf-8").write(text)

if __name__ == "__main__":
    write("index.html", home())
    for i, s in enumerate(SERIES):
        write(f"{s['slug']}/index.html", series_page(s, SERIES[i - 1] if i else None, SERIES[i + 1] if i + 1 < len(SERIES) else None))
    write("404.html", not_found())
    write("_redirects", "/about /#about 301\n/contact /#about 301\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    urls = ["/"] + [f"/{s['slug']}/" for s in SERIES]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"<url><loc>{DOMAIN}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    write("favicon.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#141414"/>'
          '<text x="32" y="44" text-anchor="middle" font-family="Arial Black, Arial, sans-serif" font-weight="900" font-size="30" fill="#fff">JR</text></svg>')
    print("built", len(SERIES) + 2, "pages")
