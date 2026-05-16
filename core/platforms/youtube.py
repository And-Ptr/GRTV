import yt_dlp
import sys

def get_youtube_stream(video_id):
    # Σωστό URL για YouTube video ή live stream
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': 'best[ext=mp4]/best',  # Προτιμά MP4 ή το καλύτερο διαθέσιμο
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            # Αν είναι live, παίρνουμε HLS m3u8
            if 'url' in info:
                print(info['url'])
            elif 'formats' in info:
                # Βρίσκουμε το καλύτερο format
                best = info['formats'][-1]
                print(best['url'])
            else:
                print("Error: No stream URL found")
                sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        get_youtube_stream(sys.argv[1])
