import asyncio
import os
import datetime
import re
from playwright.async_api import async_playwright

SITE_URL = "https://www.alphacyprus.com.cy/live"
OUTPUT_DIR = "../../streams"
OUTPUT_FILE = "alphacy.m3u8"
LOG_FILE = "alphacy.log"

TARGET_CDN = "am8"
RETRIES = 3


def log(msg: str):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{timestamp} {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def is_valid_session(url: str) -> bool:
    m = re.search(r"nimblesessionid=(\d+)", url)
    if not m:
        return False
    return len(m.group(1)) >= 8


async def attempt_fetch(attempt: int):
    log(f"🔄 Attempt {attempt} starting...")

    FINAL_STREAMS = []
    RAW_STREAMS = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-web-security", "--no-sandbox"]
        )
        context = await browser.new_context()
        page = await context.new_page()

        async def on_response(response):
            url = response.url
            if ".m3u8" not in url:
                return

            # Καταγραφή raw URL
            RAW_STREAMS.append(url)
            log(f"📡 RAW HLS: {url}")

            # Προσπάθεια ανάγνωσης body για redirect / final URL
            try:
                body = await response.text()
            except Exception:
                return

            # Βρες οποιοδήποτε πλήρες HLS URL μέσα στο body
            m = re.search(r"https://[^\s\"']+\.m3u8[^\s\"']*", body)
            if m:
                final_url = m.group(0)
                log(f"📡 BODY HLS CANDIDATE: {final_url}")
                if TARGET_CDN in final_url and is_valid_session(final_url):
                    log(f"🎯 FINAL REDIRECT URL (valid) → {final_url}")
                    FINAL_STREAMS.append(final_url)
                    return

            # Αν δεν βρέθηκε final μέσα στο body, δοκίμασε το ίδιο το response URL
            if TARGET_CDN in url and is_valid_session(url):
                log(f"🎯 RESPONSE URL (valid) → {url}")
                FINAL_STREAMS.append(url)

        page.on("response", on_response)

        try:
            await page.goto(SITE_URL, timeout=60000)
        except Exception as e:
            log(f"❌ Page load error: {e}")
            await browser.close()
            return None

        try:
            await page.wait_for_selector("video", timeout=30000)
        except Exception:
            log("⚠ Video element not found")

        try:
            await page.click("video")
        except Exception:
            pass

        # Δώσε χρόνο να γίνουν όλα τα HLS / redirects
        await asyncio.sleep(10)

        await browser.close()

        # Αν βρήκαμε final streams από body/redirect, πάρε το τελευταίο
        if FINAL_STREAMS:
            best = FINAL_STREAMS[-1]
            log(f"✅ SELECTED FINAL STREAM → {best}")
            return best

        # Fallback: ψάξε στα RAW μόνο am8 + valid session
        fallback = [u for u in RAW_STREAMS if TARGET_CDN in u and is_valid_session(u)]
        if fallback:
            best = fallback[-1]
            log(f"✅ FALLBACK RAW STREAM → {best}")
            return best

        log("⚠ No valid am8 stream found in this attempt")
        return None


async def fetch_stream():
    for attempt in range(1, RETRIES + 1):
        result = await attempt_fetch(attempt)
        if result:
            return result
        log("⏳ Retrying...\n")
        await asyncio.sleep(2)
    return None


def save_stream(url: str):
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
        log("❌ No valid am8 HLS found after retries.")
