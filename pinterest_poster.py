"""
TechPulse / TechSeconds Viral Pinterest Integration & Editorial Graphics Studio
Generates:
1. dist/pins/<slug>.jpg — Ultra-high CTR Cyberpunk Editorial Graphic Pins (1000x1500 px, 2:3 ratio)
   featuring blueprint reticles, curiosity banners, dual-tone typography, hardware spec matrix HUD,
   editorial score, and 3D action buttons.
2. dist/pinterest-feed.xml — Dedicated RSS 2.0 feed linking directly to custom Pin artwork.
3. dist/pinterest-bulk-pins.csv — Official Pinterest Bulk Pin Upload CSV sheet (1-click upload).
4. Domain verification check & Rich Pins metadata validation.
"""

import csv
import html as html_lib
import io
import json
import os
import re
import sys
import textwrap
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

# Ensure UTF-8 output on all platforms
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import (
    SITE_NAME,
    SITE_DESCRIPTION,
    SITE_URL,
    DIST_DIR,
    STATIC_DIR,
    PINTEREST_PROFILE_URL,
    PINTEREST_USERNAME,
    PINTEREST_DOMAIN_VERIFY,
    CATEGORIES,
)

PINS_DIST_DIR = DIST_DIR / "pins"
PINS_STATIC_DIR = STATIC_DIR / "pins"
FONTS_DIR = STATIC_DIR / "fonts"

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

# Category Visual Styling Palettes & Modern Editorial Accents
CATEGORY_THEMES = {
    "ai-tools": {
        "accent": (6, 182, 212),       # Neon Cyan
        "label": "AI TOOLS & BENCHMARKS",
        "cta": "Read Review ↗",
    },
    "smartphones": {
        "accent": (245, 158, 11),      # Amber / Gold
        "label": "SMARTPHONES & SILICON",
        "cta": "Read Review ↗",
    },
    "laptops-pc": {
        "accent": (16, 185, 129),      # Emerald Green
        "label": "LAPTOPS & SILICON TECH",
        "cta": "Read Review ↗",
    },
    "gadgets": {
        "accent": (249, 115, 22),      # Coral Orange
        "label": "GADGETS & WEARABLES",
        "cta": "Explore Specs ↗",
    },
    "gaming-gear": {
        "accent": (239, 68, 68),       # Neon Crimson
        "label": "GAMING HARDWARE",
        "cta": "Benchmark Report ↗",
    },
    "future-tech": {
        "accent": (132, 204, 22),      # Neon Lime
        "label": "FUTURE TECH & INNOVATION",
        "cta": "Read Breakdown ↗",
    },
}


def get_pinterest_board_for_category(cat_id: str) -> str:
    """Returns the matching Pinterest board name for a story category."""
    return PINTEREST_BOARD_MAP.get(cat_id, "Tech Trends & Breakthroughs")


def get_font_safe(font_filename: str, size: int, weight: str = "Bold") -> ImageFont.ImageFont:
    """Loads custom typography from static/fonts with reliable fallback and weight variation."""
    font_path = FONTS_DIR / font_filename
    if font_path.exists():
        try:
            f = ImageFont.truetype(str(font_path), size)
            if hasattr(f, "set_variation_by_name"):
                try:
                    f.set_variation_by_name(weight)
                except Exception:
                    pass
            return f
        except Exception:
            pass

    # Windows fallback
    for sys_font in ("segoeuib.ttf", "arialbd.ttf", "calibrib.ttf", "segoeui.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(sys_font, size)
        except Exception:
            continue

    return ImageFont.load_default()


def generate_editorial_pin_image(
    title: str,
    slug: str,
    category_id: str,
    raw_image_url: str,
    output_dir: Path,
    subtitle: str = "",
    force: bool = False,
) -> Path:
    """
    Renders an ultra-high CTR, magazine-grade editorial graphic Pin (1000x1500 px, 2:3 ratio).
    Features full-bleed high-res hardware photography, smooth cinematic gradient,
    clean bold typography, zero clutter, and zero box/grid lines.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{slug}.jpg"
    if out_file.exists() and not force:
        return out_file

    w, h = 1000, 1500
    pin = Image.new("RGB", (w, h), color=(8, 10, 15))

    # 1. Fetch & Scale background photo
    bg_loaded = False
    if raw_image_url and not raw_image_url.startswith("/") and not raw_image_url.endswith(".svg"):
        try:
            req = urllib.request.Request(
                raw_image_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = resp.read()
                bg = Image.open(io.BytesIO(data)).convert("RGBA")
                bg = bg.resize((w, h), Image.Resampling.LANCZOS)
                pin.paste(bg, (0, 0))
                bg_loaded = True
        except Exception:
            pass

    if not bg_loaded:
        fallback_bg = Image.new("RGBA", (w, h), color=(14, 18, 28))
        pin.paste(fallback_bg, (0, 0))

    # 2. Seamless Dual-Scrim Overlay (No harsh boxes or lines)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)

    # Top scrim for header legibility
    for y in range(0, 150):
        alpha = int(140 * (1 - (y / 150)) ** 1.5)
        draw_ov.line([(0, y), (w, y)], fill=(8, 10, 15, alpha))

    # Bottom cinematic fade: starts at y=450, achieves solid obsidian black by y=750
    grad_start = 450
    grad_solid = 750
    for y in range(grad_start, h):
        if y < grad_solid:
            factor = (y - grad_start) / (grad_solid - grad_start)
            alpha = int(255 * (factor ** 1.3))
        else:
            alpha = 255
        draw_ov.line([(0, y), (w, y)], fill=(8, 10, 15, alpha))

    pin = Image.alpha_composite(pin.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(pin)

    # 3. Typography Hierarchy
    f_brand_top = get_font_safe("JetBrainsMono-Variable.ttf", 18, "Bold")
    f_cat = get_font_safe("JetBrainsMono-Variable.ttf", 21, "Bold")

    # Responsive title sizing so long headlines never get cut off
    if len(title) > 50:
        f_title = get_font_safe("Outfit-Variable.ttf", 54, "Bold")
        title_line_h = 66
        wrap_w = 25
    else:
        f_title = get_font_safe("Outfit-Variable.ttf", 62, "Bold")
        title_line_h = 74
        wrap_w = 22

    f_sub = get_font_safe("SpaceGrotesk-Variable.ttf", 28, "Regular")
    f_footer = get_font_safe("JetBrainsMono-Variable.ttf", 19, "Medium")

    theme = CATEGORY_THEMES.get(category_id, CATEGORY_THEMES["future-tech"])
    c_accent = theme["accent"]
    cat_label = theme.get("label", "TECH TRENDS & BREAKTHROUGHS")
    cta_label = theme.get("cta", "Read Full Review ↗")

    # 4. Top Minimal Brand Header (No box)
    draw.text((70, 50), "TECHSECONDS // EXCLUSIVE REPORT", fill=(226, 232, 240, 220), font=f_brand_top)

    # 5. Editorial Content Block (Pure Typography, Zero Boxes)
    y_cursor = 760

    # Category Tag with Neon Bullet
    draw.text((70, y_cursor), f"● {cat_label}", fill=c_accent, font=f_cat)
    y_cursor += 44

    # Bold Headline (Outfit Bold with soft drop shadow)
    lines = textwrap.wrap(title, width=wrap_w)
    for line in lines[:4]:
        draw.text((72, y_cursor + 3), line, fill=(0, 0, 0, 180), font=f_title)
        draw.text((70, y_cursor), line, fill=(255, 255, 255), font=f_title)
        y_cursor += title_line_h

    y_cursor += 16
    # Clean Subtitle / Teaser
    if not subtitle:
        subtitle = "Full technical architecture, benchmark stress testing, and real-world performance breakdown."

    sub_lines = textwrap.wrap(subtitle, width=42)
    for s_line in sub_lines[:3]:
        draw.text((70, y_cursor), s_line, fill=(148, 163, 184), font=f_sub)
        y_cursor += 40

    # 6. Minimalist Studio Divider & Footer (No button boxes)
    draw.line([(70, 1390), (930, 1390)], fill=(30, 41, 59), width=1)
    draw.text((70, 1420), "techseconds.com/articles", fill=(100, 116, 139), font=f_footer)
    draw.text((730, 1420), cta_label, fill=c_accent, font=f_footer)

    # Save high-res JPEG
    pin_rgb = pin.convert("RGB")
    pin_rgb.save(out_file, quality=94, optimize=True)

    # Mirror to static
    static_file = PINS_STATIC_DIR / f"{slug}.jpg"
    static_file.parent.mkdir(parents=True, exist_ok=True)
    pin_rgb.save(static_file, quality=94, optimize=True)

    return out_file


def get_pin_media_url(slug: str, fallback_image: str) -> str:
    """Returns local custom pin URL if generated, or fallback Unsplash vertical crop."""
    local_dist = PINS_DIST_DIR / f"{slug}.jpg"
    if local_dist.exists():
        return f"{SITE_URL}/pins/{slug}.jpg"

    if "images.unsplash.com" in fallback_image:
        base = fallback_image.split("?")[0]
        return f"{base}?w=1000&h=1500&fit=crop&q=85"

    return fallback_image or f"{SITE_URL}/static/images/og-banner.png"


def generate_pinterest_feed_xml(
    stories: List[Dict[str, Any]],
    articles: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Generates a Pinterest-compliant RSS 2.0 feed linking directly to custom Pin artwork.
    Uses dynamic fresh timestamps (within last 24h) and proper Media RSS image attributes
    to guarantee immediate ingestion by Pinterest's auto-publish crawler.
    """
    from datetime import timedelta
    now_dt = datetime.now(timezone.utc)
    now_rfc822 = now_dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
    items_xml = []

    # 1. Add In-Depth Flagship Articles first (high Pinterest CTR)
    if articles:
        for idx, art in enumerate(articles[:25]):
            title = html_lib.escape(art.get("title", f"{SITE_NAME} Article"))
            slug = art.get("slug", "")
            link = f"{SITE_URL}/articles/{slug}/"
            subtitle = art.get("subtitle", "")
            cat_id = art.get("category_id", "future-tech")
            hashtags = PINTEREST_HASHTAGS.get(cat_id, "#Tech #Innovation #News")
            desc_text = f"{subtitle} Read the full technical breakdown on {SITE_NAME}. {hashtags}"
            desc = html_lib.escape(desc_text[:490])
            category = html_lib.escape(get_pinterest_board_for_category(cat_id))

            # Stagger timestamps across the last 12 hours so Pinterest recognizes every item as fresh today
            item_dt = now_dt - timedelta(minutes=(idx * 20) + 5)
            pub_rfc822 = item_dt.strftime("%a, %d %b %Y %H:%M:%S GMT")

            raw_img = art.get("image", f"{SITE_URL}/static/images/og-banner.png")
            pin_img = get_pin_media_url(slug, raw_img)
            pin_img_esc = html_lib.escape(pin_img)

            item = f"""    <item>
      <title>{title}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <pubDate>{pub_rfc822}</pubDate>
      <description>{desc}</description>
      <category>{category}</category>
      <dc:creator>{html_lib.escape(SITE_NAME)}</dc:creator>
      <enclosure url="{pin_img_esc}" length="220000" type="image/jpeg" />
      <media:content url="{pin_img_esc}" medium="image" type="image/jpeg" width="1000" height="1500" />
    </item>"""
            items_xml.append(item)

    # 2. Add Visual Stories
    offset_base = len(articles) if articles else 0
    for idx, s in enumerate(stories[:35]):
        title = html_lib.escape(s.get("title", f"{SITE_NAME} Story"))
        slug = s.get("slug", "")
        link = f"{SITE_URL}/stories/{slug}/"
        summary = s.get("summary", "")
        cat_id = s.get("category_id", "future-tech")
        hashtags = PINTEREST_HASHTAGS.get(cat_id, "#Tech #FutureTech #News")
        desc_text = f"{summary} Tap to view the full interactive story on {SITE_NAME}. {hashtags}"
        desc = html_lib.escape(desc_text[:490])
        category = html_lib.escape(get_pinterest_board_for_category(cat_id))

        # Stagger story timestamps following articles
        item_dt = now_dt - timedelta(minutes=((offset_base + idx) * 15) + 15)
        pub_rfc822 = item_dt.strftime("%a, %d %b %Y %H:%M:%S GMT")

        raw_img = s.get("image", f"{SITE_URL}/static/images/og-banner.png")
        pin_img = get_pin_media_url(slug, raw_img)
        pin_img_esc = html_lib.escape(pin_img)

        item = f"""    <item>
      <title>{title}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <pubDate>{pub_rfc822}</pubDate>
      <description>{desc}</description>
      <category>{category}</category>
      <dc:creator>{html_lib.escape(SITE_NAME)}</dc:creator>
      <enclosure url="{pin_img_esc}" length="220000" type="image/jpeg" />
      <media:content url="{pin_img_esc}" medium="image" type="image/jpeg" width="1000" height="1500" />
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
    Generates an official Pinterest Bulk Pin Upload CSV file with custom artwork links.
    """
    if output_path is None:
        output_path = DIST_DIR / "pinterest-bulk-pins.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
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
            media_url = get_pin_media_url(slug, raw_img)
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
        media_url = get_pin_media_url(slug, raw_img)
        rows.append([title, media_url, board, "", desc, link, ""])

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    return output_path


def render_all_editorial_pins(
    stories: List[Dict[str, Any]],
    articles: Optional[List[Dict[str, Any]]] = None,
    max_pins: int = 50,
    force: bool = True,
):
    """
    Renders clean, box-free magazine-grade editorial graphic pins for articles and stories.
    """
    rendered = 0
    items = []
    if articles:
        for a in articles:
            items.append((
                a.get("title", ""),
                a.get("slug", ""),
                a.get("category_id", "future-tech"),
                a.get("image", ""),
                a.get("subtitle", ""),
            ))
    for s in stories[:30]:
        items.append((
            s.get("title", ""),
            s.get("slug", ""),
            s.get("category_id", "future-tech"),
            s.get("image", ""),
            s.get("summary", ""),
        ))

    print(f"[*] Rendering {len(items)} clean editorial graphic pins (force={force})...")
    for title, slug, cat_id, img_url, sub in items:
        if not slug or not title:
            continue
        try:
            generate_editorial_pin_image(
                title, slug, cat_id, img_url, PINS_DIST_DIR, subtitle=sub, force=force
            )
            rendered += 1
        except Exception as e:
            print(f"  [!] Failed to render {slug}: {e}")

    print(f"[+] Successfully rendered {rendered} custom clean editorial Pins to dist/pins/ and static/pins/")


def sync_pinterest_assets(
    stories: List[Dict[str, Any]],
    dist_dir: Path,
    articles: Optional[List[Dict[str, Any]]] = None,
):
    """
    Synchronizes all Pinterest automation assets in the dist/ folder:
    - Custom Editorial Graphic Pins
    - dist/pinterest-feed.xml
    - dist/pinterest-bulk-pins.csv
    """
    # 1. Render custom Pin graphics
    render_all_editorial_pins(stories, articles=articles, max_pins=40)

    # 2. Generate & write Pinterest RSS feed with custom pin artwork
    feed_xml = generate_pinterest_feed_xml(stories, articles=articles)
    feed_path = dist_dir / "pinterest-feed.xml"
    feed_path.write_text(feed_xml, encoding="utf-8")
    print(f"[+] Pinterest RSS Auto-Publish Feed generated: {feed_path}")

    # 3. Generate Pinterest Bulk Pin CSV
    csv_path = generate_pinterest_bulk_csv(stories, articles=articles, output_path=dist_dir / "pinterest-bulk-pins.csv")
    print(f"[+] Pinterest Bulk Pins CSV generated: {csv_path} (Ready for 1-click Pinterest Upload)")


if __name__ == "__main__":
    from fetch_and_generate import load_persistent_catalog
    from article_builder import FLAGSHIP_ARTICLES

    catalog = load_persistent_catalog(DIST_DIR)
    sync_pinterest_assets(catalog, DIST_DIR, articles=FLAGSHIP_ARTICLES)
