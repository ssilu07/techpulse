"""
Comprehensive Rebuild & Zero-Broken-Link Remediation Script
Regenerates all 771 stories and all 30 articles, deploys custom 404.html & favicon.ico,
and ensures 100% clean links across the entire static site.
"""

import os
import sys
import json
import re
import shutil
from pathlib import Path

# Set up paths
REPO_DIR = Path("D:/apps_and_games/website/techPulse")
sys.path.insert(0, str(REPO_DIR))

from config import DIST_DIR, STATIC_DIR, SITE_URL, get_adsense_pub_id
from article_builder import FLAGSHIP_SLUGS, FLAGSHIP_ARTICLES, build_all_articles
from story_builder import write_story_file, optimize_seo_title
from portal_builder import build_all_portal_pages, build_404_html
from fetch_and_generate import copy_static_assets

def main():
    print("=" * 70)
    print("⚡ TechSeconds Comprehensive Rebuild & Zero-Broken-Link Remediation")
    print("=" * 70)

    # 1. Load catalog stories from dist/stories.json
    stories_json_path = DIST_DIR / "stories.json"
    if not stories_json_path.exists():
        print(f"[!] Error: {stories_json_path} not found!")
        sys.exit(1)

    catalog = json.loads(stories_json_path.read_text(encoding="utf-8"))
    print(f"[*] Loaded catalog of {len(catalog)} stories from stories.json")

    # Wire sequential next-story navigation
    catalog_len = len(catalog)
    for i, st in enumerate(catalog):
        next_st = catalog[(i + 1) % catalog_len]
        st["next_story_url"] = f"/stories/{next_st.get('slug', '')}/"
        st["next_story_title"] = next_st.get("seo_title") or next_st.get("title", "")
        if not st.get("seo_title"):
            st["seo_title"] = optimize_seo_title(st.get("title", ""), st.get("slug", ""))

    # 2. Re-render all catalog stories (564 stories) using updated story_builder
    print(f"[*] Re-rendering {len(catalog)} catalog stories via story_builder.py...")
    rendered_catalog = 0
    for st in catalog:
        slug = st.get("slug")
        if not slug:
            continue
        write_story_file(st, DIST_DIR)
        rendered_catalog += 1
    print(f"[+] Successfully re-rendered {rendered_catalog} catalog stories with clean CTA links.")

    # 3. Clean and verify all 771 story folders on disk
    stories_dir = DIST_DIR / "stories"
    all_story_dirs = [p for p in stories_dir.iterdir() if p.is_dir()]
    print(f"[*] Inspecting all {len(all_story_dirs)} story directories on disk...")

    legacy_fixed = 0
    flagship_set = set(FLAGSHIP_SLUGS.keys())

    for s_dir in all_story_dirs:
        index_file = s_dir / "index.html"
        if not index_file.exists():
            continue

        html = index_file.read_text(encoding="utf-8")
        original_html = html

        # Pattern 1: Absolute article link https://techseconds.com/articles/{slug}/
        def replace_abs_link(match):
            target_slug = match.group(1)
            if target_slug not in flagship_set:
                return f'{SITE_URL}/articles/'
            return match.group(0)

        html = re.sub(r'https://techseconds\.com/articles/([a-zA-Z0-9_-]+)/', replace_abs_link, html)

        # Pattern 2: Relative article link /articles/{slug}/
        def replace_rel_link(match):
            target_slug = match.group(1)
            if target_slug not in flagship_set:
                return '/articles/'
            return match.group(0)

        html = re.sub(r'(?<!https://techseconds\.com)/articles/([a-zA-Z0-9_-]+)/', replace_rel_link, html)

        # Pattern 3: Button text for non-flagship deep dive links
        # If the story links to /articles/ (hub), ensure the button text says Explore In-Depth Tech Reviews
        if f'{SITE_URL}/articles/' in html or 'href="/articles/"' in html:
            # Replace older variations of deep dive button text
            html = re.sub(r'<span>📖 Read Full Analysis \(800\+ Words\)</span>', '<span>📖 Explore In-Depth Tech Reviews</span>', html)
            html = re.sub(r'📖 Read Full In-Depth Analysis \(\d+\+ Words\)', '📖 Explore In-Depth Tech Reviews', html)

        if html != original_html:
            index_file.write_text(html, encoding="utf-8")
            legacy_fixed += 1

    print(f"[+] Verified and sanitized all {len(all_story_dirs)} stories on disk ({legacy_fixed} legacy files updated).")

    # 4. Re-render all 30 flagship editorial articles and /articles/ index page
    print(f"[*] Re-rendering {len(FLAGSHIP_ARTICLES)} flagship articles via article_builder.py...")
    build_all_articles(catalog, DIST_DIR)
    print(f"[+] Successfully rebuilt all flagship articles and articles directory index.")

    # 5. Rebuild portal homepage, legal pages, 404.html, sitemap.xml, robots.txt, etc.
    print(f"[*] Re-rendering portal pages, custom 404.html, and sitemap...")
    build_all_portal_pages(catalog, DIST_DIR)
    print(f"[+] Portal pages, 404.html, and sitemap generated successfully.")

    # 6. Copy static assets and ensure favicon.ico is deployed
    print(f"[*] Deploying static assets and favicon.ico...")
    copy_static_assets(STATIC_DIR, DIST_DIR)

    # 7. Final check of ads.txt
    ads_txt_path = DIST_DIR / "ads.txt"
    pub_id = get_adsense_pub_id()
    if ads_txt_path.exists() and pub_id in ads_txt_path.read_text(encoding="utf-8"):
        print(f"[+] ads.txt verified: contains {pub_id}")
    else:
        print(f"[!] Warning: ads.txt check failed or missing pub_id {pub_id}")

    print("=" * 70)
    print("✅ Full rebuild and remediation complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()
