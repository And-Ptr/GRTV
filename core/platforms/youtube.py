import sys
import subprocess

def get_youtube_stream(video_id):
    try:
        # Ορίζουμε έναν έγκυρο browser User-Agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        command = [
            'yt-dlp',
            '--quiet',
            '--no-warnings',
            '--user-agent', user_agent,
            '--referer', 'https://youtube.com',
            '-g',
            f'https://youtube.comwatch?v={video_id}' # Διορθωμένο URL
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        stream_url = result.stdout.strip()
        
        if stream_url:
            print(stream_url)
        else:
            sys.exit(1)
            
    except subprocess.CalledProcessError:
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        get_youtube_stream(sys.argv[1])
    else:
        sys.exit(1)
