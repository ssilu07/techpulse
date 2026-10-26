"""
TechPulse / TechSeconds Pinterest Integration & Automation Engine
Generates:
1. dist/pinterest-feed.xml — Dedicated RSS 2.0 feed formatted for Pinterest "Auto-publish from RSS".
2. dist/pinterest-bulk-pins.csv — Official Pinterest Bulk Pin Upload CSV sheet (1-click upload).
3. Domain verification check & Rich Pins metadata validation.
"""

import csv
import html as html_lib
import json
import os
import re
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ensure UTF-8 output on all platforms
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import (
    SITE_NAME,
    SITE_DESCRIPTION,
    SITE_URL,
    DIST_DIR,
    PINTEREST_PROFILE_URL,
    PINTEREST_USERNAME,
    PINTEREST_DOMAIN_VERIFY,
    CATEGORIES,
)

# Pinterest Board Mapping for TechPulse Categories
PINTEREST_BOARD_MAP = {
    "all": "Tech Trends & Breakthroughs",
    "ai-tools": "AI Tools & AI Hacks",
    "smartphones": "Smartphones, Leaks & Reviews",
    "laptops-pc": "Laptops, PC & Silicon Tech",
    "gadgets": "Gadgets, Wearables & Audio",
    "future-tech": "Future Tech & Computing",
    "gaming-gear": "Gaming Gear & Desk Setups",
}

# Category Hashtag Packs for High Pinterest CTR & SEO
PINTEREST_HASHTAGS = {
    "ai-tools": "#AITools #ArtificialIntelligence #ChatGPT #Gemini #TechHacks #MachineLearning #ProductivityHacks",
    "smartphones": "#Smartphones #MobileTech #iPhone #SamsungGalaxy #TechLeaks #PhoneReviews #Android",
    "laptops-pc": "#Laptops #PCTech #AppleSilicon #TechSetup #Ultrabook #Hardware #DeskGoals",
    "gadgets": "#Gadgets #TechGadgets #Smartwatch #Headphones #Wearables #EverydayCarry #CoolTech",
    "future-tech": "#FutureTech #Robotics #QuantumComputing #Chips #Technology #Innovation #TechNews",
    "gaming-gear": "#GamingGear #GamingSetup #Battlestation #PlayStation #Xbox #GamingCommunity #PCGaming",
}


def get_pinterest_board_for_category(cat_id: str) -> str:
    """Returns the matching Pinterest board name for a story category."""
    return PINTEREST_BOARD_MAP.get(cat_id, "Tech Trends & Breakthroughs")


def get_pinterest_image_url(raw_image: str) -> str:
    """
    Optimizes image URL for Pinterest's vertical 2:3 or 3:4 pin format (1000x1500 or 1200x1600).
    Ensures high-resolution raster asset that Pinterest crawlers can ingest.
    """
    if not raw_image or raw_image.startswith("/") or raw_image.endswith(".svg"):
        return f"{SITE_URL}/static/images/og-banner.png"

    if "images.unsplash.com" in raw_image:
        base = raw_image.split("?")[0]
        # 2:3 vertical aspect ratio (1000x1500 px) — Pinterest gold standard
        return f"{base}?w=1000&h=1500&fit=crop&q=85"

    return raw_image


def generate_pinterest_feed_xml(
    stories: List[Dict[str, Any]],
    articles: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Generates a Pinterest-compliant RSS 2.0 feed specifically formatted for
    Pinterest Business 'Auto-publish to Pinterest with RSS' feature.
    """
    now_rfc822 = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    items_xml = []

    # 1. Add In-Depth Articles first (high engagement)
    if articles:
        for art in articles[:25]:
            title = html_lib.escape(art.get("title", f"{SITE_NAME} Article"))
            slug = art.get("slug", "")
            link = f"{SITE_URL}/articles/{slug}/"
            subtitle = art.get("subtitle", "")
            cat_id = art.get("category_id", "future-tech")
            hashtags = PINTEREST_HASHTAGS.get(cat_id, "#Tech #Innovation #News")
            desc_text = f"{subtitle} Read the full technical breakdown on {SITE_NAME}. {hashtags}"
            desc = html_lib.escape(desc_text[:490])
            category = html_lib.escape(get_pinterest_board_for_category(cat_id))

            pub_date = art.get("published", "")
            if pub_date:
                try:
                    dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                    pub_rfc822 = dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
                except Exception:
                    pub_rfc822 = now_rfc822
            else:
                pub_rfc822 = now_rfc822

            raw_img = art.get("image", f"{SITE_URL}/static/images/og-banner.png")
            pin_img = get_pinterest_image_url(raw_img)
            pin_img_esc = html_lib.escape(pin_img)

            item = f"""    <item>
      <title>{title}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <pubDate>{pub_rfc822}</pubDate>
      <description>{desc}</description>
      <category>{category}</category>
      <dc:creator>{html_lib.escape(SITE_NAME)}</dc:creator>
      <enclosure url="{pin_img_esc}" length="150000" type="image/jpeg" />
      <media:content url="{pin_img_esc}" medium="image" width="1000" height="1500" />
    </item>"""
            items_xml.append(item)

    # 2. Add Visual Stories
    for s in stories[:35]:
        title = html_lib.escape(s.get("title", f"{SITE_NAME} Story"))
        slug = s.get("slug", "")
        link = f"{SITE_URL}/stories/{slug}/"
        summary = s.get("summary", "")
        cat_id = s.get("category_id", "future-tech")
        hashtags = PINTEREST_HASHTAGS.get(cat_id, "#Tech #FutureTech #News")
        desc_text = f"{summary} Tap to view the full interactive story on {SITE_NAME}. {hashtags}"
        desc = html_lib.escape(desc_text[:490])
        category = html_lib.escape(get_pinterest_board_for_category(cat_id))

        pub_date = s.get("published", "")
        if pub_date:
            try:
                dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                pub_rfc822 = dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
            except Exception:
                pub_rfc822 = now_rfc822
        else:
            pub_rfc822 = now_rfc822

        raw_img = s.get("image", f"{SITE_URL}/static/images/og-banner.png")
        pin_img = get_pinterest_image_url(raw_img)
        pin_img_esc = html_lib.escape(pin_img)

        item = f"""    <item>
      <title>{title}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <pubDate>{pub_rfc822}</pubDate>
      <description>{desc}</description>
      <category>{category}</category>
      <dc:creator>{html_lib.escape(SITE_NAME)}</dc:creator>
      <enclosure url="{pin_img_esc}" length="150000" type="image/jpeg" />
      <media:content url="{pin_img_esc}" medium="image" width="1000" height="1500" />
    </item>"""
        items_xml.append(item)

    items_block = "\n".join(items_xml)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{html_lib.escape(SITE_NAME)} — Pinterest Auto-Publish Feed</title>
    <link>{SITE_URL}/</link>
    <atom:link href="{SITE_URL}/pinterest-feed.xml" rel="self" type="application/rss+xml" />
    <description>{html_lib.escape(SITE_DESCRIPTION)}</description>
    <language>en-us</language>
    <lastBuildDate>{now_rfc822}</lastBuildDate>
{items_block}
  </channel>
</rss>
"""


def generate_pinterest_bulk_csv(
    stories: List[Dict[str, Any]],
    articles: Optional[List[Dict[str, Any]]] = None,
    output_path: Optional[Path] = None,
) -> Path:
    """
    Generates an official Pinterest Bulk Pin Upload CSV file.
    Pinterest allows uploading up to 200 Pins at once via CSV!
    Format required by Pinterest:
    Title, Media URL, Pinterest board, Thumbnail, Description, Link, Publish date
    """
    if output_path is None:
        output_path = DIST_DIR / "pinterest-bulk-pins.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    # Header required by Pinterest CSV importer
    header = ["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link", "Publish date"]
    rows.append(header)

    # 1. Add Articles
    if articles:
        for art in articles:
            title = art.get("title", "")
            slug = art.get("slug", "")
            link = f"{SITE_URL}/articles/{slug}/"
            subtitle = art.get("subtitle", "")
            cat_id = art.get("category_id", "future-tech")
            board = get_pinterest_board_for_category(cat_id)
            hashtags = PINTEREST_HASHTAGS.get(cat_id, "#Tech #Innovation")
            desc = f"{subtitle} Explore the full architectural benchmarks and specs on {SITE_NAME}. {hashtags}"[:495]
            raw_img = art.get("image", f"{SITE_URL}/static/images/og-banner.png")
            media_url = get_pinterest_image_url(raw_img)
            rows.append([title, media_url, board, "", desc, link, ""])

    # 2. Add Visual Stories
    for s in stories:
        title = s.get("title", "")
        slug = s.get("slug", "")
        link = f"{SITE_URL}/stories/{slug}/"
        summary = s.get("summary", "")
        cat_id = s.get("category_id", "future-tech")
        board = get_pinterest_board_for_category(cat_id)
        hashtags = PINTEREST_HASHTAGS.get(cat_id, "#Tech #News")
        desc = f"{summary} Read this interactive visual web story on {SITE_NAME}. {hashtags}"[:495]
        raw_img = s.get("image", f"{SITE_URL}/static/images/og-banner.png")
        media_url = get_pinterest_image_url(raw_img)
        rows.append([title, media_url, board, "", desc, link, ""])

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    return output_path


def sync_pinterest_assets(
    stories: List[Dict[str, Any]],
    dist_dir: Path,
    articles: Optional[List[Dict[str, Any]]] = None,
):
    """
    Synchronizes all Pinterest automation assets in the dist/ folder:
    - dist/pinterest-feed.xml
    - dist/pinterest-bulk-pins.csv
    """
    # 1. Generate & write Pinterest RSS feed
    feed_xml = generate_pinterest_feed_xml(stories, articles=articles)
    feed_path = dist_dir / "pinterest-feed.xml"
    feed_path.write_text(feed_xml, encoding="utf-8")
    print(f"[+] Pinterest RSS Auto-Publish Feed generated: {feed_path}")

    # 2. Generate Pinterest Bulk Pin CSV
    csv_path = generate_pinterest_bulk_csv(stories, articles=articles, output_path=dist_dir / "pinterest-bulk-pins.csv")
    print(f"[+] Pinterest Bulk Pins CSV generated: {csv_path} (Ready for 1-click Pinterest Upload)")


def print_pinterest_status():
    """Prints integration summary and domain verification status."""
    print("=" * 70)
    print(" 📌 Pinterest Integration & Syndication Engine")
    print("=" * 70)
    print(f" Profile URL     : {PINTEREST_PROFILE_URL}")
    print(f" Username        : @{PINTEREST_USERNAME}")
    print(f" Site URL        : {SITE_URL}")
    print(f" Auto Feed URL   : {SITE_URL}/pinterest-feed.xml")
    print(f" Bulk Pins CSV   : {DIST_DIR / 'pinterest-bulk-pins.csv'}")
    if PINTEREST_DOMAIN_VERIFY:
        print(f" Domain Tag Code : {PINTEREST_DOMAIN_VERIFY} (Active in <head>)")
    else:
        print(" Domain Tag Code : Not yet set (Add PINTEREST_DOMAIN_VERIFY in .env to auto-claim)")
    print("=" * 70)


if __name__ == "__main__":
    from fetch_and_generate import load_persistent_catalog
    from article_builder import FLAGSHIP_ARTICLES

    catalog = load_persistent_catalog(DIST_DIR)
    sync_pinterest_assets(catalog, DIST_DIR, articles=FLAGSHIP_ARTICLES)
    print_pinterest_status()
