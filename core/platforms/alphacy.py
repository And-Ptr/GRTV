import asyncio
import os
from playwright.async_api import async_playwright

SITE_URL = "https://www.alphacyprus.com.cy/live"
OUTPUT_DIR = "streams"
OUTPUT_FILE = "alphacy.m3u8"

PREFERRED = ["am8", "eu", "edge", "us", "playlist.m3u8"]


async def fetch_stream():
    async with async_playwright() as p:
        # Ορίζουμε ένα πραγματικό User-Agent για να μοιάζει με κανονικό browser
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-web-security", "--no-sandbox"]
        )
        
        # Περνάμε το User-Agent στο context
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()

        ALL_STREAMS = []

        # Συνάρτηση που καταγράφει το URL ΚΑΙ τα Headers
        async def record(request):
            url = request.url
            if ".m3u8" in url:
                try:
                    headers = await request.all_headers()
                    # Παίρνουμε το referer αν υπάρχει, αλλιώς βάζουμε το default SITE_URL
                    referer = headers.get("referer", SITE_URL)
                    user_req_agent = headers.get("user-agent", user_agent)
                    
                    print(f"📡 Found HLS: {url}")
                    ALL_STREAMS.append({
                        "url": url,
                        "referer": referer,
                        "user_agent": user_req_agent
                    })
                except Exception as e:
                    # Σε περίπτωση που το request έχει κλείσει
                    pass

        # Ακούμε τα requests
        page.on("request", lambda req: asyncio.create_task(record(req)))

        print("🔍 Loading page...")
        # Περνάμε και το referer κατά την πλοήγηση
        await page.goto(SITE_URL, timeout=60000, referer=SITE_URL)

        try:
            await page.wait_for_selector("video", timeout=30000)
        except:
            print("⚠ Video element not found")

        try:
            await page.click("video")
        except:
            pass

        await asyncio.sleep(7) # Λίγος παραπάνω χρόνος για να προλάβει να κάνει load το master playlist
        await browser.close()

        # Φιλτράρισμα με βάση τις προτιμήσεις
        for key in PREFERRED:
            for stream_data in ALL_STREAMS:
                if key in stream_data["url"]:
                    print(f"🎯 SELECTED [{key}] → {stream_data['url']}")
                    return stream_data

        # Αν δεν βρει με βάση τα preferred, αλλά βρήκε έστω και ένα m3u8, δώσε το πρώτο
        if ALL_STREAMS:
            print(f"🎯 SELECTED [First Available] → {ALL_STREAMS[0]['url']}")
            return ALL_STREAMS[0]

        return None


def save_stream(stream_data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

    url = stream_data["url"]
    referer = stream_data["referer"]
    ua = stream_data["user_agent"]

    # Format συμβατό με VLC, Kodi και IPTV Players που υποστηρίζουν HTTP Headers
    content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXTINF:-1,Alpha Cyprus Live
#EXTVLCOPT:http-user-agent={ua}
#EXTVLCOPT:http-referer={referer}
{url}|User-Agent={ua}&Referer={referer}
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"📁 Saved to: {path}")
    print("ABS PATH:", os.path.abspath(path))


if __name__ == "__main__":
    stream_data = asyncio.run(fetch_stream())

    if stream_data:
        save_stream(stream_data)
        print("✅ Completed.")
    else:
        print("❌ No tokenized HLS found.")
