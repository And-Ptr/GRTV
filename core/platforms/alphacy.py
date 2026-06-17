import asyncio
import os
import re
from playwright.async_api import async_playwright

SITE_URL = "https://www.alphacyprus.com.cy/live"
OUTPUT_DIR = "../../streams"
OUTPUT_FILE = "alphacy.m3u8"
FORCED_DOMAIN = "am8.cloudskep.com"

PROFILE_DIR = "./alphacy_profile"  # persistent browser profile

async def fetch_stream():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,  # σημαντικό για μεγάλο TTL
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="el-GR",
            timezone_id="Europe/Athens"
        )

        page = await browser.new_page()

        print("🔍 Φόρτωση σελίδας...")
        await page.goto(SITE_URL, timeout=60000)

        found_stream = None

        def handle_request(request):
            nonlocal found_stream
            url = request.url

            if ".m3u8" in url:
                found_stream = url
                print(f"\n🎯 Βρέθηκε tokenized HLS:\n{url}\n")

        page.on("request", handle_request)

        print("⏳ Περιμένω 25 δευτερόλεπτα για να φορτωθεί ο player...")
        await page.wait_for_timeout(25000)

        await browser.close()
        return found_stream


def force_domain(url):
    return re.sub(r"https://[^/]+/", f"https://{FORCED_DOMAIN}/", url)


def save_stream(url):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

    fixed_url = force_domain(url)

    content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=3000000
{fixed_url}
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"📁 Το αρχείο γράφτηκε στο: {path}")
    print(f"🔗 Τελικό URL: {fixed_url}")


if __name__ == "__main__":
    stream = asyncio.run(fetch_stream())

    if stream:
        save_stream(stream)
        print("✅ Ολοκληρώθηκε.")
    else:
        print("❌ Δεν βρέθηκε tokenized HLS.")
