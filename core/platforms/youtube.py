import sys
import subprocess

def get_m3u8(video_id):
    try:
        # Διόρθωση: Καθαρίζουμε το ID
        video_id = str(video_id).strip()
        url = f"https://www.youtube.com/watch?v={video_id}"

        # Παράμετροι για να μοιάζει με κανονικό browser
        command = [
            'yt-dlp',
            '--quiet',
            '--no-warnings',
            '--no-check-certificate',
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '-f', 'best',
            '-g',
            url
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        link = result.stdout.strip()
        
        if link and link.startswith('http'):
            print(link)
    except Exception:
        pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Χρησιμοποιούμε το sys.argv[1] για να πάρουμε το ID σωστά
        get_m3u8(sys.argv[1])
