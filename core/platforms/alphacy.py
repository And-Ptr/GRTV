import asyncio
import os
import re
from playwright.async_api import async_playwright

SITE_URL = "https://www.alphacyprus.com.cy/live"
OUTPUT_DIR = "streams"
OUTPUT_FILE = "ALPHA_CY.m3u8"  # Αρχείο εξόδου

async def fetch_stream():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-web-security", "--no-sandbox"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        ALL_STREAMS = set()

        def record(url):
            if ".m3u8" in url:
                if not any(x in url.lower() for x in ["chunk", "segment", "fragment", "tracks-v", "tracks-a"]):
                    print(f"Found Master HLS: {url}")
                    ALL_STREAMS.add(url)

        page.on("request", lambda req: record(req.url))

        print("Loading page...")
        try:
            await page.goto(SITE_URL, timeout=60000, wait_until="networkidle")
        except Exception as e:
            print(f"Timeout or Page Load Issue: {e}")

        try:
            await page.wait_for_selector("video", timeout=15000)
            await page.click("video", force=True)
            print("Clicked video to trigger stream...")
        except:
            print("Video element not ready or click failed")

        await asyncio.sleep(8)
        await browser.close()

        if not ALL_STREAMS:
            return None

        for url in ALL_STREAMS:
            if any(k in url.lower() for k in ["master", "index", "playlist", "live"]):
                return url

        return list(ALL_STREAMS)[0]


def save_stream(url):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

    # Χωρίς logo
    content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXTINF:-1 tvg-name="Alpha CY" group-title="Cyprus",Alpha TV Cyprus Live
{url}
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Saved to: {path}")
    print("ABS PATH:", os.path.abspath(path))


if __name__ == "__main__":
    stream = asyncio.run(fetch_stream())

    if stream:
        save_stream(stream)
        print("Completed successfully.")
    else:
        print("No master HLS found. Check if the site changed its player.")
