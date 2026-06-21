import asyncio
import os
import re
import time
from playwright.async_api import async_playwright

SITE_URL = "https://www.alphacyprus.com.cy/live"
OUTPUT_DIR = "../../streams"
OUTPUT_FILE = "alphacy.m3u8"

PREFERRED = ["am8", "eu", "edge", "us"]


def is_master_playlist(url):
    """
    Ελέγχει αν το URL είναι το κανονικό master playlist:
    - περιέχει playlist.m3u8
    - έχει nimblesessionid με 8 ψηφία
    """
    if "playlist.m3u8" not in url:
        return False

    m = re.search(r"nimblesessionid=(\d+)", url)
    if not m:
        return False

    return len(m.group(1)) == 8


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

        # Περιμένει να φορτωθούν όλα τα CDN requests
        await asyncio.sleep(5)

        print("⏳ Waiting for master playlist...")

        timeout = time.time() + 60  # 60 seconds max wait
        master_url = None

        while time.time() < timeout:
            for url in ALL_STREAMS:
                if is_master_playlist(url):
                    master_url = url
                    break

            if master_url:
                break

            await asyncio.sleep(1)

        await browser.close()

        if not master_url:
            print("❌ Master playlist not found (8-digit session missing)")
            return None

        print(f"🎯 MASTER PLAYLIST FOUND → {master_url}")
        return master_url


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

    print(f"📁
