import sys
import subprocess

def get_m3u8(video_id):
    try:
        # Αν είναι σκέτο ID, φτιάχνουμε το URL. Αν είναι ήδη URL, το αφήνουμε.
        if "youtube.com" in video_id or "youtu.be" in video_id:
            url = video_id
        else:
            url = f"https://youtube.com{video_id}"

        command = [
            'yt-dlp',
            '--quiet',
            '--no-warnings',
            '-f', 'best',
            '-g',
            url
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        link = result.stdout.strip()
        
        if link:
            print(link)
            
    except Exception:
        pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        get_m3u8(sys.argv[1])
