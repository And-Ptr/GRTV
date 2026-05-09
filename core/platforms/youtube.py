import sys
import subprocess

def get_m3u8(url_or_id):
    try:
        # Αν δεν είναι πλήρες URL, το φτιάχνουμε
        if not url_or_id.startswith('http'):
            if 'watch?v=' in url_or_id:
                url = f"https://www.youtube.com/{url_or_id}"
            elif url_or_id.startswith('@'):
                url = f"https://www.youtube.com/{url_or_id}/live"
            else:
                url = f"https://youtube.com{url_or_id}"
        else:
            url = url_or_id

        command = [
            'yt-dlp',
            '--quiet',
            '--no-warnings',
            '-f', 'best',
            '-g',
            url
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        print(result.stdout.strip())
    except Exception:
        pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        get_m3u8(sys.argv[1])
