#!/usr/bin/python3
import sys
import requests
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; KickScraper)"
}

def get_kick_stream(channel):
    api_url = f"https://kick.com/api/v2/channels/{channel}"

    for _ in range(3):
        try:
            r = requests.get(api_url, headers=HEADERS, timeout=5)
            if not r.ok:
                time.sleep(1)
                continue

            data = r.json()

            # 1️⃣ Playback URL (το σωστό HLS)
            playback = data.get("playback_url")
            if playback:
                m3u = fetch_m3u8_follow_redirect(playback)
                if m3u:
                    return m3u

            # 2️⃣ Livestream source (παλιό API)
            livestream = data.get("livestream")
            if livestream and livestream.get("source"):
                m3u = fetch_m3u8_follow_redirect(livestream["source"])
                if m3u:
                    return m3u

        except Exception:
            time.sleep(1)

    return fallback(channel)


def fetch_m3u8_follow_redirect(url):
    """
    Kick playback_url is NOT a playlist.
    It redirects to the REAL .m3u8.
    We must follow redirects manually.
    """
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        final_url = r.url  # the real playlist URL

        r2 = requests.get(final_url, headers=HEADERS, timeout=10)
        if r2.ok and "#EXTM3U" in r2.text:
            return r2.text

    except Exception:
        return None

    return None


def fallback(channel):
    return (
        "#EXTM3U\n"
        f"#EXTINF:-1,{channel.upper()} (offline)\n"
        "https://static.kick.com/offline.mp4\n"
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python kick.py <channel>")
        sys.exit(1)

    print(get_kick_stream(sys.argv[1]))
