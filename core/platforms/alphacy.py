import asyncio
from playwright.async_api import async_playwright

TARGET_URL = "https://www.alphacyprus.com.cy/live"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("🔍 Φόρτωση σελίδας...")
        await page.goto(TARGET_URL, timeout=60000)

        found_stream = None

        # Καταγραφή network requests
        def handle_request(request):
            url = request.url
            if ".m3u8" in url:
                nonlocal found_stream
                found_stream = url
                print(f"\n🎯 Βρέθηκε stream:\n{url}\n")

        page.on("request", handle_request)

        print("⏳ Περιμένω 10 δευτερόλεπτα να φορτώσει ο player...")
        await page.wait_for_timeout(10000)

        if found_stream:
            print("✅ ΤΕΛΟΣ — Stream URL εντοπίστηκε.")
        else:
            print("❌ Δεν βρέθηκε .m3u8 — πιθανό DRM ή tokenized stream.")

        await browser.close()

asyncio.run(run())
