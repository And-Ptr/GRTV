import sys
import subprocess

def get_m3u8(channel_url):
    try:
        # Χρησιμοποιούμε το yt-dlp για να πάρουμε το URL του stream
        command = [
            'yt-dlp',
            '--quiet',
            '--no-warnings',
            '-f', 'best',
            '-g',
            channel_url
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        url = result.stdout.strip()
        if url:
            print(url)
    except Exception as e:
        pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Δέχεται το URL του καναλιού ή του live video
        channel = sys.argv[1]
        if not channel.startswith('http'):
            channel = f"https://www.youtube.com/{channel}/live"
        get_m3u8(channel)
