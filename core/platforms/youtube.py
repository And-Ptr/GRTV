import sys
import subprocess

def get_youtube_stream(video_id):
    try:
        # Χρησιμοποιούμε το yt-dlp για να πάρουμε το URL του live stream
        # Το format "best" ή "95" συνήθως δίνει το HLS (m3u8) stream
        command = [
            'yt-dlp',
            '--quiet',
            '--no-warnings',
            '-g',
            f'https://youtube.com{video_id}'
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        stream_url = result.stdout.strip()
        
        if stream_url:
            print(stream_url)
        else:
            sys.exit(1)
            
    except subprocess.CalledProcessError:
        # Αν το βίντεο δεν είναι live ή υπάρχει σφάλμα
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_id = sys.argv[1]
        get_youtube_stream(video_id)
    else:
        sys.exit(1)
