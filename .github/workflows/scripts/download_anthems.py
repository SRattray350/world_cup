from pathlib import Path
import re
import time
import urllib.request
from urllib.parse import urljoin

OUT_DIR = Path("audio/anthems")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# page code on NationalAnthems.info -> filename your wheel.html expects
ANTHEMS = {
    "mx": "mexico.mp3",
    "za": "south-africa.mp3",
    "kr": "korea.mp3",
    "cz": "czechia.mp3",
    "ca": "canada.mp3",
    "ba": "bosnia.mp3",
    "qa": "qatar.mp3",
    "ch": "switzerland.mp3",
    "br": "brazil.mp3",
    "ma": "morocco.mp3",
    "ht": "haiti.mp3",
    "sct": "scotland.mp3",
    "us": "usa.mp3",
    "py": "paraguay.mp3",
    "au": "australia.mp3",
    "tr": "turkiye.mp3",
    "de": "germany.mp3",
    "cw": "curacao.mp3",
    "ci": "ivory-coast.mp3",
    "ec": "ecuador.mp3",
    "nl": "netherlands.mp3",
    "jp": "japan.mp3",
    "se": "sweden.mp3",
    "tn": "tunisia.mp3",
    "be": "belgium.mp3",
    "eg": "egypt.mp3",
    "ir": "iran.mp3",
    "nz": "new-zealand.mp3",
    "es": "spain.mp3",
    "cv": "cape-verde.mp3",
    "sa": "saudi-arabia.mp3",
    "uy": "uruguay.mp3",
    "fr": "france.mp3",
    "sn": "senegal.mp3",
    "iq": "iraq.mp3",
    "no": "norway.mp3",
    "ar": "argentina.mp3",
    "dz": "algeria.mp3",
    "at": "austria.mp3",
    "jo": "jordan.mp3",
    "pt": "portugal.mp3",
    "cd": "dr-congo.mp3",
    "uz": "uzbekistan.mp3",
    "co": "colombia.mp3",
    "gb": "england.mp3",
    "hr": "croatia.mp3",
    "gh": "ghana.mp3",
    "pa": "panama.mp3",
}

BASE = "https://nationalanthems.info/"

def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Applied-Sciences-Sweepstake/1.0"
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()

def find_mp3_url(page_code: str) -> str | None:
    page_url = f"{BASE}{page_code}.htm"
    html = fetch(page_url).decode("utf-8", errors="ignore")

    # Look for any direct MP3 link in the page.
    matches = re.findall(r'(?:href|src)=["\']([^"\']+\.mp3[^"\']*)["\']', html, flags=re.I)
    if matches:
        return urljoin(page_url, matches[0])

    # Fallback guesses in case the site uses predictable direct paths.
    candidates = [
        f"{BASE}{page_code}.mp3",
        f"{BASE}audio/{page_code}.mp3",
        f"{BASE}mp3/{page_code}.mp3",
        f"{BASE}music/{page_code}.mp3",
    ]

    for candidate in candidates:
        try:
            data = fetch(candidate)
            if data[:3] == b"ID3" or b"mpeg" in data[:100].lower() or len(data) > 50_000:
                return candidate
        except Exception:
            continue

    return None

def main() -> None:
    missing = []

    for page_code, filename in ANTHEMS.items():
        output_path = OUT_DIR / filename

        if output_path.exists() and output_path.stat().st_size > 10_000:
            print(f"Already exists: {filename}")
            continue

        print(f"Finding anthem for {page_code} -> {filename}")

        try:
            mp3_url = find_mp3_url(page_code)
            if not mp3_url:
                print(f"Could not find MP3 for {page_code}")
                missing.append(page_code)
                continue

            print(f"Downloading {mp3_url}")
            output_path.write_bytes(fetch(mp3_url))
            print(f"Saved {output_path}")

        except Exception as error:
            print(f"Failed {page_code}: {error}")
            missing.append(page_code)

        # Be polite to the source site.
        time.sleep(1)

    if missing:
        print("\nMissing or failed:")
        for code in missing:
            print(f"- {code}")
    else:
        print("\nAll anthem files downloaded.")

if __name__ == "__main__":
    main()
