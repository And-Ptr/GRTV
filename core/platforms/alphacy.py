import asyncio
import os
import re
from playwright.async_api import async_playwright

SITE_URL = "https://www.alphacyprus.com.cy/live"
OUTPUT_DIR = "streams"
OUTPUT_FILE = "playlist.m3u8"  # Το μετονόμασα σε playlist.m3u8 όπως ζήτησες

async def fetch_stream():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-web-security", "--no-sandbox"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        ALL_STREAMS = set()  # Χρήση set για αυτόματη αφαίρεση διπλότυπων

        def record(url):
            if ".m3u8" in url:
                # Φίλτρο: Απορρίπτουμε κομμάτια (chunks) και κρατάμε το Master/Index Playlist
                # Συνήθως τα chunks περιέχουν λέξεις όπως chunk, segment, fragment ή index_X_X
                if not any(x in url.lower() for x in ["chunk", "segment", "fragment", "tracks-v", "tracks-a"]):
                    print(f"📡 Found Master HLS: {url}")
                    ALL_STREAMS.add(url)

        # Ακούμε μόνο τα Requests (είναι πιο γρήγορο από το Response)
        page.on("request", lambda req: record(req.url))

        print("🔍 Loading page...")
        try:
            # Περιμένουμε να φορτώσει το δίκτυο
            await page.goto(SITE_URL, timeout=60000, wait_until="networkidle")
        except Exception as e:
            print(f"⚠ Timeout or Page Load Issue: {e}")

        # Προσπάθεια αλληλεπίδρασης για να ξεκινήσει ο player (Bypass Autoplay Block)
        try:
            await page.wait_for_selector("video", timeout=15000)
            # Κάνουμε click στο κέντρο της σελίδας ή στο video για να ξεκινήσει η ροή
            await page.click("video", force=True)
            print("👆 Clicked video to trigger stream...")
        except:
            print("⚠ Video element not ready or click failed")

        # Δίνουμε 8 δευτερόλεπτα στον player να κάνει τα requests του
        await asyncio.sleep(8)
        await browser.close()

        if not ALL_STREAMS:
            return None

        # Επιλογή του καταλληλότερου URL
        # Προτιμάμε URL που περιέχει "master" ή "index" ή "playlist"
        for url in ALL_STREAMS:
            if any(k in url.lower() for k in ["master", "index", "playlist", "live"]):
                return url
        
        # Αν δεν βρει κάποιο με τα tags, επιστρέφει το πρώτο έγκυρο m3u8 που βρήκε
        return list(ALL_STREAMS)[0]


def save_stream(url):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

    # Κατασκευή σωστού M3U αρχείου (όπως το παράγει το Stream Detector)
    content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXTINF:-1 tvg-name="Alpha CY" tvg-logo="https://alphacyprus.com.cy" group-title="Cyprus",Alpha TV Cyprus Live
{url}
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"📁 Saved to: {path}")
    print("ABS PATH:", os.path.abspath(path))


if __name__ == "__main__":
    stream = asyncio.run(fetch_stream())

    if stream:
        save_stream(stream)
        print("✅ Completed successfully.")
    else:
        print("❌ No master HLS found. Check if the site changed its player.")
