import requests
import sys

SOURCE_URL = "https://df6d.short.gy/sspjio.m3u"
OUTPUT_FILE = "playlist.m3u"

# IPTV links often block browsers and require a media player User-Agent
USER_AGENTS = [
    "TiviMate/4.7.0 (Linux; Android 11)",
    "OTT Navigator/1.6.9.4 (Linux; Android 11)",
    "VLC/3.0.18 LibVLC/3.0.18",
    "Dalvik/2.1.0 (Linux; U; Android 12; Pixel 6 Build/SD1A.210817.023)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
]

def is_valid_m3u(text):
    lower = text.lstrip().lower()
    if lower.startswith("<!doctype html") or lower.startswith("<html"):
        return False
    return "#EXTINF" in text

def clean_and_preserve_m3u(raw_text):
    """
    Normalizes line endings while preserving ALL tags:
    - #EXTM3U
    - #EXTINF (logos, groups, tvg-id)
    - #KODIPROP (DRM: ClearKey, Widevine, license_type, license_key, inputstream)
    - #EXTVLCOPT (http-user-agent, http-referrer)
    - #EXTHTTP (custom JSON headers/cookies)
    - Stream URLs (m3u8, mpd, ts, php, etc.)
    """
    lines = [line.strip() for line in raw_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    cleaned = []
    has_header = False

    for line in lines:
        if not line:
            continue
        if line.startswith("#EXTM3U"):
            if not has_header:
                cleaned.append(line)
                has_header = True
            continue
        cleaned.append(line)

    if not has_header:
        cleaned.insert(0, "#EXTM3U")

    return "\n".join(cleaned) + "\n"

def fetch_and_save_playlist():
    for ua in USER_AGENTS:
        print(f"Trying User-Agent: {ua[:35]}...")
        try:
            response = requests.get(
                SOURCE_URL,
                headers={"User-Agent": ua, "Accept": "*/*"},
                allow_redirects=True,
                timeout=30
            )
            response.raise_for_status()
            text = response.text

            if is_valid_m3u(text):
                final_m3u = clean_and_preserve_m3u(text)
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    f.write(final_m3u)

                total = final_m3u.count("#EXTINF")
                drm_count = final_m3u.count("#KODIPROP")
                print(f"\nSUCCESS! Saved {total} channels ({drm_count} DRM tags) to {OUTPUT_FILE}.")
                print("\n--- Preview (First 10 lines) ---")
                print("\n".join(final_m3u.splitlines()[:10]))
                print("--------------------------------")
                return
            else:
                print("  -> Response was not a valid M3U (got HTML or empty). Trying next...")

        except requests.RequestException as e:
            print(f"  -> Request failed: {e}")

    print("\nERROR: Could not fetch a valid M3U playlist from the source URL.")
    print("The source link may be geo-blocked (India-only) or offline.")
    sys.exit(1)

if __name__ == "__main__":
    fetch_and_save_playlist()
