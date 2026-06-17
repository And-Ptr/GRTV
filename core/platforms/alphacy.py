import asyncio
import os
from playwright.async_api import async_playwright

SITE_URL = "https://www.alphacyprus.com.cy/live"
OUTPUT_DIR = "../../streams"
OUTPUT_FILE = "alphacy.m3u8"

# Προτεραιότητα CDN
PREFERRED = ["am8", "eu", "edge", "us"]

async def fetch_stream():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        found_stream = None

        def handle_request(request):
            nonlocal found_stream
            url = request.url

            # Καταγραφή όλων των HLS για debugging
            if ".m3u8" in url:
                print(f"📡 HLS request: {url}")

            # Αν ήδη βρέθηκε stream, μην συνεχίζεις
            if found_stream:
                return

            # Έλεγχος προτεραιότητας CDN
            if ".m3u8" in url:
                for key in PREFERRED:
                    if key in url:
                        found_stream = url
                        print(f"\n🎯 Βρέθηκε HLS ({key}):\n{url}\n")
                        return

        # Listener ΠΡΙΝ το goto
        page.on("request", handle_request)

        print("🔍 Φόρτωση σελίδας...")
        await page.goto(SITE_URL, timeout=60000)

        # Περιμένει μέχρι 60 δευτερόλεπτα για το stream
        for _ in range(60):
            if found_stream:
                break
            await asyncio.sleep(1)

        await browser.close()
        return found_stream


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

    print(f"📁 Το αρχείο γράφτηκε στο: {path}")


if __name__ == "__main__":
    stream = asyncio.run(fetch_stream())

    if stream:
        save_stream(stream)
        print("✅ Ολοκληρώθηκε.")
    else:
        print("❌ Δεν βρέθηκε tokenized HLS.")
