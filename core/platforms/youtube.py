import sys
import subprocess

def get_m3u8(video_id):
    try:
        # Καθαρίζουμε το video_id
        video_id = video_id.strip()
        
        # Φτιάχνουμε το σωστό URL
        if "youtube.com" in video_id or "youtu.be" in video_id:
            url = video_id
        else:
            url = f"https://youtube.com{video_id}"

        # Χρήση yt-dlp με ειδικές παραμέτρους για YouTube live
        command = [
            'yt-dlp',
            '--quiet',
            '--no-warnings',
            '--no-check-certificate',
            '-f', 'best',
            '-g',
            url
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        link = result.stdout.strip()
        
        # Εκτύπωση του link (αυτό θα γραφτεί στο m3u8 μέσω του YAML)
        if link:
            print(link)
            
    except Exception:
        pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # sys.argv[1] παίρνει το ID που δώσαμε στο workflow
        get_m3u8(sys.argv[1])
