import sys
import requests

def get_dailymotion_stream(video_id: str):
    api_url = f"https://www.dailymotion.com/player/metadata/video/{video_id}"

    try:
        r = requests.get(api_url, timeout=5)

        if not r.ok:
            return fallback(video_id)

        data = r.json()

        if "qualities" not in data:
            return fallback(video_id)

        if "auto" in data["qualities"]:
            return data["qualities"]["auto"][0]["url"]

        qualities = data["qualities"]
        for q in ["1080", "720", "480", "380", "240"]:
            if q in qualities:
                return qualities[q][0]["url"]

        return fallback(video_id)

    except Exception:
        return fallback(video_id)


def fallback(video_id: str):
    return (
        "#EXTM3U\n"
        f"#EXTINF:-1,Dailymotion {video_id} (offline)\n"
        "https://example.com/offline.ts\n"
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: python dailymotion.py <video_id>")
        sys.exit(1)

    video_id = sys.argv[1]
    print(get_dailymotion_stream(video_id))


if __name__ == "__main__":
    main()

