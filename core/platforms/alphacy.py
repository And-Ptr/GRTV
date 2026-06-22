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
            args=[
                "--disable-web-security",
                "--no-sandbox",
                "--autoplay-policy=no-user-gesture-required",
                "--allow-running-insecure-content",
                "--disable-features=PreloadMediaEngagementData,AutoplayIgnoreWebAudio",
                "--mute-audio=false"
            ]
        )

        # ❗ Χωρίς autoplay permission (δεν υποστηρίζεται)
        context = await browser.new_context()

        page = await context.new_page()

        ALL_STREAMS = []

        def record(url):
            if ".m3u8" in url:
                print(f"📡 HLS: {url}")
                ALL_STREAMS.append(url)

        page.on("request", lambda req: record(req.url))
        page.on("response", lambda res: record(res.url))

        print("🔍 Loading page...")
        await page.goto(SITE_URL, timeout=60000)

        # Περιμένει το video element
        try:
            await page.wait_for_selector("video", timeout=90000)
        except:
            print("⚠ Video element not found")

        # Force play + unmute
        try:
            await page.evaluate("""
                const v = document.querySelector('video');
                if (v) {
                    v.muted = false;
                    v.volume = 1.0;
                    v.play().catch(()=>{});
                }
            """)
        except:
            pass

        # Περιμένει να φορτώσουν όλα τα CDN
        await asyncio.sleep(10)

        await browser.close()

        # Επιλογή CDN με βάση προτεραιότητα
        for key in PREFERRED:
            for url in ALL_STREAMS:
                if key in url:
                    print(f"🎯 SELECTED [{key}] → {url}")
                    return url

        return None


def save_stream(url):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

    content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=3000000
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
