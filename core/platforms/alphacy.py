async def fetch_stream():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        found_stream = None

        async def handle_response(response):
            nonlocal found_stream
            url = response.url

            if ".m3u8" in url:
                print(f"📡 HLS response: {url}")

                # Προτεραιότητα CDN
                for key in PREFERRED:
                    if key in url:
                        found_stream = url
                        print(f"\n🎯 Βρέθηκε HLS ({key}):\n{url}\n")
                        return

        page.on("response", handle_response)

        print("🔍 Φόρτωση σελίδας...")
        await page.goto(SITE_URL, timeout=60000)

        # Περιμένει μέχρι 60 δευτερόλεπτα για το stream
        for _ in range(60):
            if found_stream:
                break
            await asyncio.sleep(1)

        await browser.close()
        return found_stream
