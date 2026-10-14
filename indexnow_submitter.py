"""
TechSeconds IndexNow Submitter
Instantly notifies search engines (Microsoft Bing, Yandex, Seznam, Naver)
when new Google AMP stories and pages are published or updated.
"""

import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Optional

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import SITE_URL, INDEXNOW_KEY, DIST_DIR, STATIC_DIR


def ensure_indexnow_key_file() -> Path:
    """Ensures the IndexNow verification key file exists in dist/ and static/."""
    key_filename = f"{INDEXNOW_KEY}.txt"
    
    # Save in static (source)
    static_key_path = STATIC_DIR / key_filename
    static_key_path.write_text(INDEXNOW_KEY, encoding="utf-8")
    
    # Save in dist (deployed root)
    dist_key_path = DIST_DIR / key_filename
    dist_key_path.write_text(INDEXNOW_KEY, encoding="utf-8")
    
    return dist_key_path


def get_all_story_urls(limit: int = 100) -> List[str]:
    """Retrieves the list of story URLs from dist/stories.json."""
    stories_json = DIST_DIR / "stories.json"
    urls = [f"{SITE_URL}/"]
    
    if stories_json.exists():
        try:
            data = json.loads(stories_json.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for item in data[:limit]:
                    slug = item.get("slug")
                    if slug:
                        urls.append(f"{SITE_URL}/stories/{slug}/")
        except Exception as e:
            print(f"[!] Warning reading stories.json for IndexNow: {e}")
            
    return urls


def submit_to_indexnow(urls: Optional[List[str]] = None, key: str = INDEXNOW_KEY) -> bool:
    """
    Submits a list of URLs to the IndexNow API.
    """
    ensure_indexnow_key_file()
    
    if urls is None:
        urls = get_all_story_urls()
        
    if not urls:
        print("[!] No URLs found to submit to IndexNow.")
        return False

    # Extract host domain
    host = SITE_URL.replace("https://", "").replace("http://", "").split("/")[0]
    key_location = f"{SITE_URL}/{key}.txt"

    payload = {
        "host": host,
        "key": key,
        "keyLocation": key_location,
        "urlList": urls,
    }

    endpoint = "https://api.indexnow.org/indexnow"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "TechSeconds-IndexNow-Agent/1.0",
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")

    print(f"\n[⚡] Submitting {len(urls)} URLs to IndexNow ({endpoint})...")
    print(f" • Host: {host}")
    print(f" • Key Location: {key_location}")

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            status = response.getcode()
            if status in (200, 202):
                print(f"[✔] IndexNow Success! HTTP {status} (URLs submitted to Bing & partners)")
                return True
            else:
                print(f"[!] IndexNow returned unexpected HTTP {status}")
                return False
    except urllib.error.HTTPError as e:
        status = e.code
        err_body = e.read().decode("utf-8", errors="replace")
        if status == 202:
            print(f"[✔] IndexNow Success: HTTP 202 Accepted (Key validation in progress)")
            return True
        elif status == 400:
            print(f"[!] IndexNow HTTP 400: Invalid format. Response: {err_body}")
        elif status == 403:
            print(f"[!] IndexNow HTTP 403: Key invalid or not found at keyLocation yet. Response: {err_body}")
        elif status == 422:
            print(f"[!] IndexNow HTTP 422: Host mismatch. Response: {err_body}")
        else:
            print(f"[!] IndexNow HTTP Error {status}: {err_body}")
        return False
    except Exception as e:
        print(f"[!] IndexNow network connection error: {e}")
        return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Submit TechSeconds URLs to IndexNow")
    parser.add_argument("--limit", type=int, default=50, help="Maximum URLs to submit (default: 50)")
    args = parser.parse_args()

    urls_to_submit = get_all_story_urls(limit=args.limit)
    success = submit_to_indexnow(urls=urls_to_submit)
    sys.exit(0 if success else 1)
