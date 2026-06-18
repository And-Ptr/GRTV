import asyncio
import os
from playwright.async_api import async_playwright

SITE_URL = "https://www.alphacyprus.com.cy/live"
OUTPUT_DIR = "../../streams"
OUTPUT_FILE = "alphacy.m3u8"

PREFERRED = ["am8", "eu", "edge", "us"]

async def fetch_stream():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-web-security", "--no-sandbox"]
        )
        context = await browser.new_context()
        page = await context.new_page()

        found_stream = None

        def on_request(request):
            nonlocal found_stream
            url = request.url
            if ".m3u8" in url and not found_stream:
                for key in PREFERRED:
                    if key in url:
                        found_stream = url
                        print(f"🎯 FOUND (request) [{key}] → {url}")
                        return

        async def on_response(response):
            nonlocal found_stream
            url = response.url
            if ".m3u8" in url and not found_stream:
                for key in PREFERRED:
                    if key in url:
                        found_stream = url
                        print(f"🎯 FOUND (response) [{key}] → {url}")
                        return

        page.on("request", on_request)
        page.on("response", on_response)

        print("🔍 Loading page...")
        await page.goto(SITE_URL, timeout=60000)

        for _ in range(60):
            if found_stream:
                break
            await asyncio.sleep(1)

        await browser.close()
        return found_stream


def save_stream(url):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

    # ✔️ VALID MASTER PLAYLIST (VLC compatible)
    content = f"""#EXTM3U
#EXT-X-VERSION:3

#EXT-X-STREAM-INF:BANDWIDTH=3000000,RESOLUTION=1920x1080,CODECS="avc1.640028,mp4a.40.2",FRAME-RATE=25.000,CLOSED-CAPTIONS=NONE
{url}
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"📁 Saved to: {path}")


if __name__ == "__main__":
    stream = asyncio.run(fetch_stream())

    if stream:
        save_stream(stream)
        print("✅ Completed.")
    else:
        print("❌ No tokenized HLS found.")
