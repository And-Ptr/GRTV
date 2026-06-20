BEST = None
ALL_STREAMS = []

async def fetch_stream():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-web-security", "--no-sandbox"]
        )
        context = await browser.new_context()
        page = await context.new_page()

        def check(url):
            nonlocal BEST
            ALL_STREAMS.append(url)

            for key in PREFERRED:
                if key in url:
                    BEST = url
                    print(f"🎯 MATCH [{key}] → {url}")
                    break

        page.on("request", lambda req: ".m3u8" in req.url and check(req.url))
        page.on("response", lambda res: ".m3u8" in res.url and check(res.url))

        print("🔍 Loading page...")
        await page.goto(SITE_URL, timeout=60000)

        # Περιμένει να εμφανιστεί το video
        await page.wait_for_selector("video", timeout=30000)

        # Πατάει play
        try:
            await page.click("video")
        except:
            pass

        # Περιμένει 5 δευτερόλεπτα για ΟΛΑ τα CDN
        await asyncio.sleep(5)

        await browser.close()

        # Προτεραιότητα: am8 → eu → edge → us
        for key in PREFERRED:
            for url in ALL_STREAMS:
                if key in url:
                    return url

        return None
