import yt_dlp
import sys

def get_youtube_stream(video_id):
    # Σωστό URL για YouTube video
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            print(info['url'])  # Επιστρέφει το direct stream URL
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        get_youtube_stream(sys.argv[1])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        get_youtube_stream(sys.argv[1])
