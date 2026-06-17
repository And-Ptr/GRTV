import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin

SITE_URL = "https://www.alphacyprus.com.cy/live"
OUTPUT_FILE = "alphacy.m3u8"

async def fetch_stream():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("🔍 Φόρτωση σελίδας...")
        await page.goto(SITE_URL, timeout=60000)

        found_stream = None

        # Καταγραφή network requests
        def on_request(request):
            nonlocal found_stream
            url = request.url

            if ".m3u8" in url:
                found_stream = url
                print(f"\n🎯 Βρέθηκε stream:\n{url}\n")

        page.on("request", on_request)

        print("⏳ Περιμένω 10 δευτερόλεπτα να φορτώσει ο player...")
        await page.wait_for_timeout(10000)

        await browser.close()
        return found_stream


def create_m3u8_file(stream_url):
    content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=3134643,FRAME-RATE=25,RESOLUTION=1920x1080,CODECS="avc1.42c01f,mp4a.40.2"
{stream_url}
"""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"📁 Το αρχείο δημιουργήθηκε: {OUTPUT_FILE}")


if __name__ == "__main__":
    stream = asyncio.run(fetch_stream())

    if stream:
        create_m3u8_file(stream)
        print("✅ Ολοκληρώθηκε.")
    else:
        print("❌ Δεν βρέθηκε .m3u8 — πιθανό DRM ή tokenized stream.")
