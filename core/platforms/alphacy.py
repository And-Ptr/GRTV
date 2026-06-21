import asyncio
import os
import re
import time
from playwright.async_api import async_playwright

SITE_URL = "https://www.alphacyprus.com.cy/live"

# ΣΩΣΤΟ PATH ΓΙΑ ΤΟΝ ΦΑΚΕΛΟ GRTV/streams
OUTPUT_DIR = "../streams"
OUTPUT_FILE = "alphacy.m3u8"


def is_master_playlist(url):
    if "playlist.m3u8" not in url:
        return False

    m = re.search(r"nimblesessionid=(\d+)", url)
    if not m:
        return False

    return len(m.group(1)) == 8


async def fetch_stream():
    print("Starting Playwright...")

    async with async_playwright() as p:
        print("Launching Chromium...")

        try:
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
        except Exception as e:
            print("Chromium failed to launch:", e)
            return None

        context = await browser.new_context()
        page = await context.new_page()

        ALL_STREAMS = []

        def record(url):
            if ".m3u8" in url:
                print("HLS:", url)
                ALL_STREAMS.append(url)

        page.on("request", lambda req: record(req.url))
        page.on("response", lambda res: record(res.url))

        print("Loading page:", SITE_URL)
        await page.goto(SITE_URL, timeout=60000)

        try:
            await page.wait_for_selector("video", timeout=90000)
            print("Video element found.")
        except:
            print("Video element not found.")

        try:
            await page.evaluate("""
                const v = document.querySelector('video');
                if (v) {
                    v.muted = false;
                    v.volume = 1.0;
                    v.play().catch(()=>{});
                }
            """)
            print("Video play triggered.")
        except:
            print("Failed to trigger video play.")

        print("Waiting for player to load...")
        await asyncio.sleep(15)

        print("Waiting for master playlist...")

        timeout = time.time() + 90
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
            print("Master playlist not found.")
            return None

        print("MASTER PLAYLIST FOUND:", master_url)
        return master_url


def save_stream(url):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

    content = (
        "#EXTM3U\n"
        "#EXT-X-VERSION:3\n"
        "#EXT-X-STREAM-INF:BANDWIDTH=3000000\n"
        f"{url}\n"
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print("Saved to:", path)


if __name__ == "__main__":
    stream = asyncio.run(fetch_stream())

    if stream:
        save_stream(stream)
        print("Completed.")
    else:
        print("No tokenized HLS found.")
