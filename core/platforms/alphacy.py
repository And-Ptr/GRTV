import requests
import re
from urllib.parse import urljoin

def fetch_m3u8_from_site(url):
    """
    Κατεβάζει HTML και εντοπίζει το πρώτο .m3u8 link.
    Υποστηρίζει query strings και protocol-relative URLs.
    """

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        html = response.text

        # Regex που πιάνει:
        # - http://...m3u8
        # - https://...m3u8
        # - //domain/...m3u8
        # - relative paths
        pattern = r'(https?:\/\/[^\s\'"]+?\.m3u8[^\s\'"]*|\/\/[^\s\'"]+?\.m3u8[^\s\'"]*|[^\s\'"]+?\.m3u8[^\s\'"]*)'
        matches = re.findall(pattern, html)

        if matches:
            stream_url = matches[0]

            # Αν ξεκινάει με //
            if stream_url.startswith("//"):
                stream_url = "https:" + stream_url

            # Αν δεν ξεκινάει με http, είναι relative
            if not stream_url.startswith("http"):
                stream_url = urljoin(url, stream_url)

            return stream_url

        return None

    except Exception as e:
        print(f"⚠️ Σφάλμα κατά το fetch: {e}")
        return None


def create_m3u8(output_file, stream_url):
    """
    Δημιουργεί νέο .m3u8 αρχείο με το stream URL.
    """
    content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=3134643,FRAME-RATE=25,RESOLUTION=1920x1080,CODECS="avc1.42c01f,mp4a.40.2"
{stream_url}
"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    site_url = "https://www.alphacyprus.com.cy/live/"
    output_file = "test.m3u8"

    stream_url = fetch_m3u8_from_site(site_url)

    if stream_url:
        create_m3u8(output_file, stream_url)
        print(f"✅ Το αρχείο δημιουργήθηκε: {output_file}")
        print(f"🔗 Stream URL: {stream_url}")
    else:
        print("❌ Δεν βρέθηκε .m3u8 στο site.")
