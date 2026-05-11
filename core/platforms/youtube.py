import yt_dlp
import sys

def get_youtube_stream(video_id):
    # Κατασκευή του πλήρους URL
    video_url = f"https://youtube.com{video_id}"
    
    # Ρυθμίσεις για να πάρουμε μόνο το link του stream (m3u8 αν είναι live)
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            # Εκτύπωση μόνο του URL για να το πιάσει το GitHub Action
            print(info['url'])
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        get_youtube_stream(sys.argv[1])