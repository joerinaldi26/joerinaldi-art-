import asyncio, subprocess, time
from playwright.async_api import async_playwright
async def main():
    srv = subprocess.Popen(["python3","-m","http.server","8765","-d",__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))),"site")],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
            for w,h,tag in [(1440,900,"desk"),(390,844,"mob")]:
                pg = await b.new_page(viewport={"width":w,"height":h}); errs=[]
                pg.on("pageerror", lambda e: errs.append(str(e)))
                await pg.goto("http://localhost:8765/star-wars-chase/")
                await pg.get_by_role("button", name="View Cantina Chase! full size").click(); await pg.wait_for_timeout(900)
                sc = pg.locator(".lb-scroller")
                st = lambda: sc.evaluate("e=>({sl:Math.round(e.scrollLeft), max:e.scrollWidth-e.clientWidth, imgH:Math.round(e.querySelector('img').getBoundingClientRect().height)})")
                print(tag,"open", await st(), await pg.locator(".lb-title").inner_text(), "| focused:", await pg.evaluate("document.activeElement.getAttribute('aria-label')"))
                await pg.screenshot(path=f"shots/viewer-wide-{tag}.png")
                await pg.locator(".lb-nudge.right").click(); await pg.wait_for_timeout(800); print(tag,"nudge", await st(), await pg.locator(".lb-mini i").get_attribute("style"))
                mb = await pg.locator(".lb-mini img").bounding_box(); await pg.mouse.click(mb["x"]+mb["width"]*.98, mb["y"]+mb["height"]/2); await pg.wait_for_timeout(900); print(tag,"minimap end", await st())
                await pg.keyboard.press("ArrowRight"); await pg.wait_for_timeout(700); print(tag,"arrow at end ->", await pg.locator(".lb-title").inner_text())
                await pg.keyboard.press("Escape"); await pg.wait_for_timeout(200)
                print(tag,"closed:", await pg.locator(".lb").get_attribute("hidden") is not None, "| focus back:", await pg.evaluate("document.activeElement.getAttribute('aria-label') || document.activeElement.textContent.trim()"))
                await pg.goto("http://localhost:8765/phanatics/")
                await pg.locator(".piece-open").first.click(); await pg.wait_for_timeout(800)
                print(tag,"phan open", await pg.locator(".lb-title").inner_text(), "wide:", await pg.locator(".lb").evaluate("e=>e.classList.contains('is-wide')"))
                await pg.screenshot(path=f"shots/viewer-normal-{tag}.png")
                await pg.keyboard.press("ArrowRight"); await pg.wait_for_timeout(500); print(tag,"next ->", await pg.locator(".lb-title").inner_text())
                await pg.keyboard.press("ArrowLeft"); await pg.keyboard.press("ArrowLeft"); await pg.wait_for_timeout(500); print(tag,"wrap back ->", await pg.locator(".lb-title").inner_text())
                print(tag,"errors", errs); await pg.close()
            await b.close()
    finally: srv.terminate()
asyncio.run(main())
