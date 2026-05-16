#!/usr/bin/python3
import sys
import requests

def get_dailymotion_master(video_id: str):
    api_url = f"https://www.dailymotion.com/player/metadata/video/{video_id}"

    try:
        r = requests.get(api_url, timeout=5)
        if not r.ok:
            return None

        data = r.json()
        if "qualities" not in data:
            return None

        qualities = data["qualities"]

        # Dailymotion qualities → resolution map
        resolution_map = {
            "1080": "1920x1080",
            "720": "1280x720",
            "480": "854x480",
            "380": "512x288",
            "240": "320x180"
        }

        # Dailymotion qualities → bandwidth map (approx)
        bandwidth_map = {
            "1080": 6000000,
            "720": 4000000,
            "480": 2000000,
            "380": 800000,
            "240": 500000
        }

        # Dailymotion qualities → codecs map
        codecs_map = {
            "1080": 'avc1.4D4028,mp4a.40.5',
            "720":  'avc1.4D401F,mp4a.40.5',
            "480":  'avc1.4D401E,mp4a.40.5',
            "380":  'avc1.420015,mp4a.40.5',
            "240":  'avc1.42000c,mp4a.40.5'
        }

        playlist = ["#EXTM3U"]

        # Order of qualities
        order = ["380", "240", "480", "720", "1080"]

        for q in order:
            if q in qualities:
                url = qualities[q][0]["url"]
                res = resolution_map[q]
                bw = bandwidth_map[q]
                codecs = codecs_map[q]

                playlist.append(
                    f'#EXT-X-STREAM-INF:RESOLUTION={res},FRAME-RATE=25.000000,BANDWIDTH={bw},CODECS="{codecs}",NAME="{q}"'
                )
                playlist.append(url)

        return "\n".join(playlist)

    except Exception:
        return None


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
    playlist = get_dailymotion_master(video_id)

    if playlist:
        print(playlist)
    else:
        print(fallback(video_id))


if __name__ == "__main__":
    main()
