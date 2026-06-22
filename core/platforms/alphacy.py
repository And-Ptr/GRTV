import time
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth

SITE_URL = "https://www.alphacyprus.com.cy/live"

OUTPUT_DIR = "../streams"
OUTPUT_FILE = "alphacy.m3u8"


def is_master_playlist(url):
    if "playlist.m3u8" not in url:
        return False

    m = re.search(r"nimblesessionid=(\d+)", url)
    if not m:
        return False

    return len(m.group(1)) == 8


def fetch_stream():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)

    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    print("Loading page...")
    driver.get(SITE_URL)

    time.sleep(10)

    # Force play
    try:
        driver.execute_script("""
            const v = document.querySelector('video');
            if (v) {
                v.muted = false;
                v.volume = 1.0;
                v.play().catch(()=>{});
            }
        """)
    except:
        pass

    print("Waiting for video to load...")
    time.sleep(20)

    logs = driver.get_log("performance")
    urls = []

    for entry in logs:
        msg = entry["message"]
        if ".m3u8" in msg:
            urls.append(msg)

    driver.quit()

    # Extract URLs
    clean_urls = []
    for line in urls:
        m = re.search(r"https?://[^\s\"']+\.m3u8[^\s\"']*", line)
        if m:
            clean_urls.append(m.group(0))

    for url in clean_urls:
        if is_master_playlist(url):
            print("MASTER PLAYLIST FOUND:", url)
            return url

    print("Master playlist not found.")
    return None


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
    stream = fetch_stream()

    if stream:
        save_stream(stream)
        print("Completed.")
    else:
        print("No tokenized HLS found.")
