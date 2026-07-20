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

            # NEW: Kick now uses playback_url instead of livestream.source
            playback = data.get("playback_url")

            if playback:
                return fetch_m3u8(playback)

            # fallback if playback_url missing
            livestream = data.get("livestream")
            if livestream and livestream.get("source"):
                return fetch_m3u8(livestream["source"])

        except Exception:
            time.sleep(1)

    return fallback(channel)


def fetch_m3u8(url):
    for _ in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=5)
            if r.ok and "#EXTM3U" in r.text:
                return r.text
        except Exception:
            time.sleep(1)

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
