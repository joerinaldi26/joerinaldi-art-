import asyncio, subprocess, time, re, os
from playwright.async_api import async_playwright

PAGES = ["/", "/phanatics/", "/sports/", "/bat-spider/", "/team-up/", "/star-wars-chase/", "/superheroes/", "/nerdcore/", "/editorial/", "/kids/", "/nope"]
OUT = "shots"
os.makedirs(OUT, exist_ok=True)

async def main():
    srv = subprocess.Popen(["python3", "-m", "http.server", "8765", "-d", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
            for w, h, tag in [(1440, 900, "desk"), (390, 844, "mob")]:
                for path in PAGES:
                    pg = await b.new_page(viewport={"width": w, "height": h})
                    errs, bad = [], []
                    pg.on("pageerror", lambda e: errs.append(str(e)))
                    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
                    pg.on("response", lambda r: bad.append(f"{r.status} {r.url}") if r.status >= 400 and not r.url.endswith("/nope") else None)
                    await pg.goto("http://localhost:8765" + path)
                    # scroll through to trigger lazy images
                    H = await pg.evaluate("document.documentElement.scrollHeight")
                    for y in range(0, H, 700):
                        await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(40)
                    await pg.wait_for_timeout(500)
                    broken = await pg.evaluate("[...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src)")
                    overflow = await pg.evaluate("document.documentElement.scrollWidth > window.innerWidth + 1")
                    name = (path.strip("/") or "home").replace("/", "_")
                    await pg.evaluate("window.scrollTo(0,0)")
                    await pg.screenshot(path=f"{OUT}/{name}-{tag}.png", full_page=True)
                    print(f"{tag:4} {path:20} h={H:5} errs={errs[:2]} bad={bad[:3]} broken={broken[:2]} hscroll={overflow}")
                    await pg.close()
            # links
            pg = await b.new_page()
            await pg.goto("http://localhost:8765/")
            links = set()
            for path in PAGES[:-1]:
                await pg.goto("http://localhost:8765" + path)
                for href in await pg.evaluate("[...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'))"):
                    if href.startswith("/") and "#" not in href: links.add(href)
            for l in sorted(links):
                r = await pg.goto("http://localhost:8765" + l)
                if r.status != 200: print("BROKEN LINK", l, r.status)
            print("internal links checked:", len(links))
            await b.close()
    finally:
        srv.terminate()

asyncio.run(main())
