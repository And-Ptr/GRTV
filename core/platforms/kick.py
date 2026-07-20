#!/usr/bin/python3
import sys
import requests
import time
import json

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

            # 1️⃣ Playback URL (το σωστό manifest)
            playback = data.get("playback_url")
            if playback:
                m3u = fetch_manifest(playback)
                if m3u:
                    return m3u

            # 2️⃣ Livestream source (παλιό API)
            livestream = data.get("livestream")
            if livestream and livestream.get("source"):
                m3u = fetch_manifest(livestream["source"])
                if m3u:
                    return m3u

        except Exception:
            time.sleep(1)

    return fallback(channel)


def fetch_manifest(url):
    """
    Kick playback_url returns a JSON manifest, NOT an M3U8.
    We must extract the real HLS URL from the manifest.
    """
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if not r.ok:
            return None

        manifest = r.json()

        # Kick manifest structure:
        # { "streams": [ { "url": "REAL_M3U8_URL" } ] }
        streams = manifest.get("streams")
        if not streams:
            return None

        real_url = streams[0].get("url")
        if not real_url:
            return None

        # Now download the REAL playlist
        r2 = requests.get(real_url, headers=HEADERS, timeout=10)
        if r2.ok:
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
