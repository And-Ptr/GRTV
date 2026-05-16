#!/usr/bin/python3
import sys
import requests
import urllib.parse
import time

CLIENT_ID = "ue6666qo983tsx6so1t0vnawi233wa"
GQL_URL = "https://gql.twitch.tv/gql"

HEADERS = {
    "Client-ID": CLIENT_ID,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; GitHubActions)"
}

def get_access_token(channel):
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
            "login": channel,
            "isVod": False,
            "vodID": "",
            "playerType": "embed"
        }
    }

    for _ in range(3):
        try:
            r = requests.post(GQL_URL, json=payload, headers=HEADERS, timeout=5)
            data = r.json().get("data", {}).get("streamPlaybackAccessToken")
            if data:
                return data["value"], data["signature"]
        except:
            time.sleep(1)

    return None, None


def get_stream_url(channel):
    token, sig = get_access_token(channel)

    if not token or not sig:
        return fallback(channel)

    url = (
        f"https://usher.ttvnw.net/api/channel/hls/{channel}.m3u8"
        f"?client_id={CLIENT_ID}"
        f"&token={urllib.parse.quote(token)}"
        f"&sig={sig}"
        f"&allow_source=true"
        f"&allow_audio_only=true"
        f"&allow_spectre=true"
    )

    for _ in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=5)
            if r.ok and "#EXTM3U" in r.text:
                return clean_m3u8(r.text)
        except:
            time.sleep(1)

    return fallback(channel)


def clean_m3u8(text):
    lines = text.split("\n")
    return "\n".join(
        line for line in lines
        if not line.startswith("#EXT-X-TWITCH-INFO")
    )


def fallback(channel):
    return (
        "#EXTM3U\n"
        f"#EXTINF:-1,{channel.upper()} (offline)\n"
        "https://example.com/offline.ts\n"
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python twitch.py <channel>")
        sys.exit(1)

    print(get_stream_url(sys.argv[1]))


