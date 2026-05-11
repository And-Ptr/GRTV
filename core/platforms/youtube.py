import sys
import subprocess

def get_youtube_stream(video_id):
    try:
        command = [
            'yt-dlp',
            '--quiet',
            '--no-warnings',
            '--impersonate', 'chrome',  
            '--cookies-from-browser', 'chrome', 
            '-f', 'b',
            '-g',
            f'https://www.youtube.com/watch?v={video_id}'
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        stream_url = result.stdout.strip().split('\n')
        
        if stream_url:
            print(stream_url[0])
    except subprocess.CalledProcessError:
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        get_youtube_stream(sys.argv[1])