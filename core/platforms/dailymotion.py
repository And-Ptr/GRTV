import sys
import requests

def get_dailymotion_stream(video_id: str):
    api_url = f"https://www.dailymotion.com/player/metadata/video/{video_id}"

    try:
        r = requests.get(api_url, timeout=5)

        if not r.ok:
            return None

        data = r.json()

        if "qualities" not in data:
            return None

        # Προτιμάμε HLS adaptive (auto)
        if "auto" in data["qualities"]:
            return data["qualities"]["auto"][0]["url"]

        # Εναλλακτικά, παίρνουμε την καλύτερη διαθέσιμη ποιότητα
        qualities = data["qualities"]
        for q in ["1080", "720", "480", "380", "240"]:
            if q in qualities:
                return qualities[q][0]["url"]

        return None

    except Exception:
        return None


def generate_m3u8(title: str, stream_url: str):
    return (
        "#EXTM3U\n"
        f"#EXTINF:-1,{title}\n"
        f"{stream_url}\n"
    )


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
    stream = get_dailymotion_stream(video_id)

    if stream:
        print(generate_m3u8(f"Dailymotion {video_id}", stream))
    else:
        print(fallback(video_id))


if __name__ == "__main__":
    main()


