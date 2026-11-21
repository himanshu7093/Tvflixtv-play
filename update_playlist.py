import requests
import sys

SOURCE_URL = "https://df6d.short.gy/sspjio.m3u"
OUTPUT_FILE = "playlist.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

def fetch_and_save_playlist():
    try:
        print(f"Fetching playlist from {SOURCE_URL}...")
        response = requests.get(SOURCE_URL, headers=HEADERS, allow_redirects=True, timeout=30)
        response.raise_for_status()

        content = response.text.strip()
        if not content:
            print("Error: Fetched playlist is empty.")
            sys.exit(1)

        if not content.startswith("#EXTM3U"):
            content = "#EXTM3U\n" + content

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(content + "\n")

        channel_count = content.count("#EXTINF")
        print(f"Success! Saved {channel_count} channels to {OUTPUT_FILE}.")

    except requests.RequestException as e:
        print(f"Failed to fetch playlist: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_and_save_playlist()
