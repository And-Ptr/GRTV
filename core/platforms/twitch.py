import sys
import requests
import urllib.parse

CLIENT_ID = "ue6666qo983tsx6so1t0vnawi233wa"
GQL_URL = "https://gql.twitch.tv/gql"

def get_access_token(channel_name: str):
    payload = {
        "operationName": "PlaybackAccessToken",
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "0828119ded1c13477966434e15800ff57ddacf13ba1911c129dc2200705b0712"
            }
        },
        "variables": {
            "isLive": True,
            "login": channel_name,
            "isVod": False,
            "vodID": "",
            "playerType": "embed"
        }
    }

    headers = {
        "Client-ID": CLIENT_ID,
        "Content-Type": "application/json"
    }

    try:
        r = requests.post(GQL_URL, json=payload, headers=headers)
        data = r.json()
        token_data = data.get("data", {}).get("streamPlaybackAccessToken")
        if not token_data:
            return None, None
        return token_data["value"], token_data["signature"]
    except:
        return None, None


def get_stream_url(channel_name: str):
    token, sig = get_access_token(channel_name)

    if not token or not sig:
        return fallback(channel_name)

    token_encoded = urllib.parse.quote(token)

    url = (
        f"https://usher.ttvnw.net/api/channel/hls/{channel_name}.m3u8"
        f"?client_id={CLIENT_ID}"
        f"&token={token_encoded}"
        f"&sig={sig}"
        f"&allow_source=true"
        f"&allow_audio_only=true"
        f"&allow_spectre=true"
    )

    try:
        r = requests.get(url)
        if not r.ok or "#EXTM3U" not in r.text:
            return fallback(channel_name)
        return clean_m3u8(r.text)
    except:
        return fallback(channel_name)


def clean_m3u8(text: str):
    lines = text.split("\n")
    return "\n".join(
        line for line in lines
        if not line.startswith("#EXT-X-TWITCH-INFO")
        and not line.startswith("#EXT-X-MEDIA")
    )


def fallback(channel_name: str):
    return (
        "#EXTM3U\n"
        f"#EXTINF:-1,{channel_name.upper()} (offline)\n"
        "https://example.com/offline.ts\n"
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: python twitch.py <channel>")
        sys.exit(1)

    channel = sys.argv[1]
    print(get_stream_url(channel))


if __name__ == "__main__":
    main()

