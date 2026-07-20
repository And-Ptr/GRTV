#!/usr/bin/python3
import sys
import requests
import time
import re

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

            playback = data.get("playback_url")
            if playback:
                m3u = resolve_master_playlist(playback)
                if m3u:
                    return m3u

        except Exception:
            time.sleep(1)

    return fallback(channel)


def resolve_master_playlist(url):
    """
    Kick playback_url returns a MediaPackage master playlist.
    We must extract variant playlists and return the best one.
    """

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if not r.ok:
            return None

        master = r.text

        # Find variant playlists inside master
        variants = re.findall(r'(https?://[^\s]+\.m3u8)', master)

        if not variants:
            return None

        # Pick the highest quality playlist (usually last)
        best = variants[-1]

        r2 = requests.get(best, headers=HEADERS, timeout=10)
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
