import asyncio
import os
import datetime
from playwright.async_api import async_playwright

SITE_URL = "https://www.alphacyprus.com.cy/live"
OUTPUT_DIR = "../../streams"
OUTPUT_FILE = "alphacy.m3u8"
LOG_FILE = "alphacy.log"

PREFERRED = ["am8", "eu", "edge", "us"]
RETRIES = 3


def log(msg):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{timestamp} {msg}"
    print(line)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


async def attempt_fetch(attempt):
    log(f"🔄 Attempt {attempt} loading page...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-web-security", "--no-sandbox"]
        )
        context = await browser.new_context()
        page = await context.new_page()

        ALL_STREAMS = []

        def record(url):
            if ".m3u8" in url:
                log(f"📡 HLS: {url}")
                ALL_STREAMS.append(url)

        page.on("request", lambda req: record(req.url))
        page.on("response", lambda res: record(res.url))

        try:
            await page.goto(SITE_URL, timeout=60000)
        except Exception as e:
            log(f"❌ Page load error: {e}")
            await browser.close()
            return None

        # Περιμένει το video
        try:
            await page.wait_for_selector("video", timeout=30000)
        except:
            log("⚠ Video element not found")

        # Πατάει play
        try:
            await page.click("video")
        except:
            pass

        # Περιμένει 5 δευτερόλεπτα για ΟΛΑ τα CDN
        await asyncio.sleep(5)

        await browser.close()

        # Επιλογή CDN με βάση προτεραιότητα
        for key in PREFERRED:
            for url in ALL_STREAMS:
                if key in url:
                    log(f"🎯 SELECTED [{key}] → {url}")
                    return url

        log("⚠ No preferred CDN found in this attempt")
        return None


async def fetch_stream():
    for attempt in range(1, RETRIES + 1):
        result = await attempt_fetch(attempt)
        if result:
            return result
        log("⏳ Retrying...\n")
        await asyncio.sleep(2)

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

    log(f"📁 Saved to: {path}")


if __name__ == "__main__":
    log("\n================= NEW RUN =================")

    stream = asyncio.run(fetch_stream())

    if stream:
        save_stream(stream)
        log("✅ Completed.")
    else:
        log("❌ No tokenized HLS found after retries.")
