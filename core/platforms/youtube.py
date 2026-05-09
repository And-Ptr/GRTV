import subprocess
import json
import sys

def get_youtube_streams(video_id: str):
    url = f"https://youtube.com{video_id}"
    
    try:
        # Χρησιμοποιούμε το yt-dlp για να πάρουμε τα metadata σε JSON
        result = subprocess.run(
            ["yt-dlp", "-j", url],
            capture_output=True,
            text=True,
            check=True
        )
        
        video_data = json.loads(result.stdout)
        
        # Εκτύπωση των διαθέσιμων formats (URL και ποιότητα)
        for f in video_data.get('formats', []):
            print(f"Quality: {f.get('format_note')} - URL: {f.get('url')}\n")
            
    except Exception as e:
        print(f"Σφάλμα: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Χρήση: python script.py <video_id>")
    else:
        get_youtube_streams(sys.argv[1])
