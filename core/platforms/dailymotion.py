#!/usr/bin/python3
import sys
import subprocess
import requests

def get_stream_url(video_id):
    url = f"https://www.dailymotion.com/video/{video_id}"

    try:
        # Get direct stream URL (HLS or DASH)
        result = subprocess.check_output(
            ["yt-dlp", "-g", url],
            stderr=subprocess.DEVNULL
        ).decode().strip().split("\n")

        # Usually the last URL is the best quality
        stream_url = result[-1]

        # Fetch playlist/manifest
        m3u = requests.get(stream_url, timeout=5).text

        # If it's DASH (.mpd), convert to pseudo-M3U8
        if "<MPD" in m3u or "Representation" in m3u:
            return dash_fallback(video_id)

        # Valid HLS
        if "#EXTM3U" in m3u:
            return m3u

        return dash_fallback(video_id)

    except Exception:
        return dash_fallback(video_id)


def dash_fallback(video_id):
    return (
        "#EXTM3U\n"
        f"#EXTINF:-1,Dailymotion {video_id} (no HLS available)\n"
        "https://example.com/offline.ts\n"
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dailymotion_yt.py <video_id>")
        sys.exit(1)

    print(get_stream_url(sys.argv[1]))

