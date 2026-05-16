#!/usr/bin/python3
import requests
import sys
import time

def get_dailymotion_streams(video_id):
    meta_url = f"https://www.dailymotion.com/player/metadata/video/{video_id}"

    for _ in range(3):
        try:
            meta = requests.get(meta_url, timeout=5).json()
            break
        except:
            time.sleep(1)
    else:
        return offline(video_id)

    try:
        stream_url = meta["qualities"]["auto"][0]["url"]
    except:
        return offline(video_id)

    try:
        m3u = requests.get(stream_url, timeout=5).text
        if "#EXTM3U" not in m3u:
            return offline(video_id)
        return m3u
    except:
        return offline(video_id)


def offline(video_id):
    return (
        "#EXTM3U\n"
        f"#EXTINF:-1,Dailymotion {video_id} (offline)\n"
        "https://example.com/offline.ts\n"
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dailymotion.py <id>")
        sys.exit(1)

    print(get_dailymotion_streams(sys.argv[1]))


