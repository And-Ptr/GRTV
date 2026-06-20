import asyncio
import os
import datetime
import re
from playwright.async_api import async_playwright

SITE_URL = "https://www.alphacyprus.com.cy/live"
OUTPUT_DIR = "../../streams"
OUTPUT_FILE = "alphacy.m3u8"
LOG_FILE = "alphacy.log"

# ΜΟΝΟ το σωστό CDN
TARGET_CDN = "am8"

# Πόσες προσπάθειες να κάνει
RETRIES = 3


# -----------------------------
# LOGGING
# -----------------------------
def log(msg):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{timestamp} {msg}"
    print(line)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# -----------------------------
# VALIDATION: sessionid >= 8 digits
# -----------------------------
def is_valid_session(url):
    m = re.search(r"nimblesessionid=(\d+)", url)
    if not m:
        return False
    return len(m.group(1)) >= 8


# -----------------------------
# ΜΙΑ ΠΡΟΣΠΑΘΕΙΑ FETCH
# -----------------------------
async def attempt_fetch(attempt):
    log(f"🔄 Attempt {attempt} starting...")

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

        # Φόρτωση σελίδας
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

        # Περιμένει αρκετά ώστε να εμφανιστεί το am8
        await asyncio.sleep(8)

        await browser.close()

        # Φιλτράρει ΜΟΝΟ am8 + valid sessionid
        valid = [u for u in ALL_STREAMS if TARGET_CDN in u and is_valid_session(u)]

        if valid:
            best = valid[-1]  # το τελευταίο είναι πάντα το σωστό
            log(f"🎯 SELECTED VALID STREAM → {best}")
            return best

        log("⚠ No valid am8 stream found in this attempt")
        return None


# -----------------------------
# AUTO‑RETRY WRAPPER
# -----------------------------
async def fetch_stream():
    for attempt in range(1, RETRIES + 1):
        result = await attempt_fetch(attempt)
        if result:
            return result
        log("⏳ Retrying...\n")
        await asyncio.sleep(2)

    return None


# -----------------------------
# SAVE OUTPUT
# -----------------------------
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


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    log("\n================= NEW RUN =================")

    stream = asyncio.run(fetch_stream())

    if stream:
        save_stream(stream)
        log("✅ Completed.")
    else:
        log("❌ No valid am8 HLS found after retries.")
