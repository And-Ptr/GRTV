import sys
import requests

def get_dailymotion_stream(video_id: str):
    api_url = f"https://www.dailymotion.com/player/metadata/video/{video_id}"

    try:
        r = requests.get(api_url, timeout=5)

        # Αν το video δεν υπάρχει ή είναι private
        if not r.ok:
            return fallback(video_id)

        data = r.json()

        # Αν δεν υπάρχουν qualities → fallback
        if "qualities" not in data:
            return fallback(video_id)

        # Προτιμάμε το "auto" (HLS adaptive)
        if "auto" in data["qualities"]:
            return data["qualities"]["auto"][0]["url"]

        # Εναλλακτικά παίρνουμε το υψηλότερο διαθέσιμο
        qualities = data["qualities"]
        for quality in ["1080", "720", "480", "380", "240"]:
            if quality in qualities:
                return qualities[quality][0]["url"]

        # Αν δεν βρεθεί τίποτα → fallback
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

