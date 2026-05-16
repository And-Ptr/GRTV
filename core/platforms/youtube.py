import yt_dlp
import sys
import requests

YOUTUBE_ID = "uWIhV9gQClg"
DAILYMOTION_ID = "x2j7kha"

def try_youtube():
    url = f"https://www.youtube.com/watch?v={YOUTUBE_ID}"
    opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "best",
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get("url")
    except:
        return None

def try_dailymotion():
    api = f"https://www.dailymotion.com/player/metadata/video/{DAILYMOTION_ID}"
    try:
        data = requests.get(api, timeout=5).json()
        return data["qualities"]["auto"][0]["url"]
    except:
        return None

def fallback():
    return (
        "#EXTM3U\n"
        "#EXTINF:-1,Euronews Greece (offline)\n"
        "https://example.com/offline.ts\n"
    )

if __name__ == "__main__":
    stream = try_youtube()
    if not stream:
        stream = try_dailymotion()
    if not stream:
        print(fallback())
    else:
        print(stream)
