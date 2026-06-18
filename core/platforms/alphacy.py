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
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-web-security", "--no-sandbox"]
        )
        context = await browser.new_context()
        page = await context.new_page()

        found_stream = None

        # -----------------------------
        # 1) ΠΙΑΝΕΙ ΟΛΑ ΤΑ REQUESTS
        # -----------------------------
        def on_request(request):
            nonlocal found_stream
            url = request.url

            if ".m3u8" in url:
                print(f"📡 REQUEST HLS: {url}")

                if not found_stream:
                    for key in PREFERRED:
                        if key in url:
                            found_stream = url
                            print(f"🎯 FOUND (request) [{key}] → {url}")
                            return

        page.on("request", on_request)

        # -----------------------------
        # 2) ΠΙΑΝΕΙ ΟΛΑ ΤΑ RESPONSES
        # -----------------------------
        async def on_response(response):
            nonlocal found_stream
            url = response.url

            if ".m3u8" in url:
                print(f"📡 RESPONSE HLS: {url}")

                if not found_stream:
                    for key in PREFERRED:
                        if key in url:
                            found_stream = url
                            print(f"🎯 FOUND (response) [{key}] → {url}")
                            return

        page.on("response", on_response)

        # -----------------------------
        # 3) ΦΟΡΤΩΣΗ ΣΕΛΙΔΑΣ
        # -----------------------------
        print("🔍 Loading page...")
        await page.goto(SITE_URL, timeout=60000)

        # Περιμένει μέχρι 60 δευτερόλεπτα
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

    print(f"📁 Saved to: {path}")


if __name__ == "__main__":
    stream = asyncio.run(fetch_stream())

    if stream:
        save_stream(stream)
        print("✅ Completed.")
    else:
        print("❌ No tokenized HLS found.")
