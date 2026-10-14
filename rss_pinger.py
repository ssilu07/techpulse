"""
TechSeconds RSS & WebSub Syndication Pinger
Notifies Google WebSub / PubSubHubbub hub and global RSS aggregators
(Feedly, Flipboard, Bing News) whenever fresh tech stories are generated.
"""

import sys
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import SITE_URL, SITE_NAME


def ping_websub_hub(feed_url: str = f"{SITE_URL}/rss.xml") -> bool:
    """
    Pings the official Google WebSub hub (pubsubhubbub.appspot.com)
    to notify search engines that new content has been published.
    """
    hub_url = "https://pubsubhubbub.appspot.com/"
    post_data = urllib.parse.urlencode({
        "hub.mode": "publish",
        "hub.url": feed_url,
    }).encode("utf-8")

    req = urllib.request.Request(
        hub_url,
        data=post_data,
        headers={
            "User-Agent": "TechSeconds-WebSub-Publisher/1.0",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            if status in (200, 204):
                print(f"[✔] WebSub Hub Success (HTTP {status}) for: {feed_url}")
                return True
            else:
                print(f"[!] WebSub Hub HTTP {status} for: {feed_url}")
                return False
    except Exception as e:
        print(f"[!] WebSub Hub ping notice for {feed_url}: {e}")
        return False


def ping_pingomatic() -> bool:
    """
    Pings Ping-O-Matic to broadcast new updates to aggregators and search services.
    """
    endpoint = "http://pingomatic.com/ping/"
    params = {
        "title": SITE_NAME,
        "blogurl": f"{SITE_URL}/",
        "rssurl": f"{SITE_URL}/rss.xml",
        "chk_weblogscom": "on",
        "chk_blogs": "on",
        "chk_feedburner": "on",
        "chk_syndic8": "on",
        "chk_newsgator": "on",
        "chk_myyahoo": "on",
        "chk_pubsubcom": "on",
        "chk_blogdigger": "on",
    }
    url = f"{endpoint}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "TechSeconds-RSS-Agent/1.0"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            if status == 200:
                print(f"[✔] Ping-O-Matic Syndication Success (HTTP 200)")
                return True
            return False
    except Exception as e:
        print(f"[!] Ping-O-Matic ping notice: {e}")
        return False


def ping_rss_hubs():
    """Pings both Google WebSub and syndication hubs."""
    print("\n[⚡] Broadcasting RSS updates to Google WebSub & Aggregators...")
    ping_websub_hub(f"{SITE_URL}/rss.xml")
    ping_websub_hub(f"{SITE_URL}/feed.xml")
    ping_pingomatic()


if __name__ == "__main__":
    ping_rss_hubs()
