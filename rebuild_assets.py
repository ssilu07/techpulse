"""
Comprehensive Rebuild & AdSense Quality Remediation Script
Purges all scraped/boilerplate RSS stories and orphan directories, rebuilds ONLY
the 30 original flagship editorial articles and 40 handcrafted companion Web Stories,
and deploys an article-first sitemap, clean E-E-A-T trust pages, and AdSense-compliant layout.
"""

import sys
import json
import shutil
from pathlib import Path

# Set up paths dynamically relative to this script
REPO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_DIR))

from config import DIST_DIR, STATIC_DIR, SITE_URL, get_adsense_pub_id
from content_engine import CURATED_VIRAL_STORIES
from article_builder import FLAGSHIP_ARTICLES, build_all_articles
from story_builder import write_story_file, optimize_seo_title
from portal_builder import build_all_portal_pages
from fetch_and_generate import copy_static_assets


def main():
    print("=" * 70)
    print("⚡ TechSeconds Clean Editorial Rebuild & AdSense Compliance Remediation")
    print("=" * 70)

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    stories_dir = DIST_DIR / "stories"
    stories_dir.mkdir(parents=True, exist_ok=True)

    # 1. Strictly use ONLY handcrafted original curated companion stories
    #    (Eliminates 100% of scraped Verge/TechCrunch/Engadget RSS boilerplate!)
    catalog = [dict(s) for s in CURATED_VIRAL_STORIES]
    valid_story_slugs = {s.get("slug") for s in catalog if s.get("slug")}
    valid_article_slugs = {a.get("slug") for a in FLAGSHIP_ARTICLES if a.get("slug")}
    print(f"[*] Loaded {len(catalog)} handcrafted companion stories & {len(FLAGSHIP_ARTICLES)} flagship articles.")

    # 2. Wire sequential next-story navigation across curated companion stories
    catalog_len = len(catalog)
    for i, st in enumerate(catalog):
        next_st = catalog[(i + 1) % catalog_len]
        st["next_story_url"] = f"/stories/{next_st.get('slug', '')}/"
        st["next_story_title"] = next_st.get("seo_title") or next_st.get("title", "")
        if not st.get("seo_title"):
            st["seo_title"] = optimize_seo_title(st.get("title", ""), st.get("slug", ""))

    # 3. Purge ALL scraped / boilerplate / orphan story directories from dist/stories/
    purged_stories = 0
    for s_dir in list(stories_dir.iterdir()):
        if s_dir.is_dir() and s_dir.name not in valid_story_slugs:
            shutil.rmtree(s_dir, ignore_errors=True)
            purged_stories += 1
    print(f"[+] Purged {purged_stories} scraped/orphan story directories from dist/stories/.")

    # 4. Purge stale scraped Pinterest pin images from dist/pins/
    pins_dir = DIST_DIR / "pins"
    if pins_dir.exists():
        keep_pins = valid_story_slugs | valid_article_slugs
        purged_pins = 0
        for p_file in list(pins_dir.iterdir()):
            if p_file.is_file() and p_file.stem not in keep_pins:
                try:
                    p_file.unlink()
                    purged_pins += 1
                except Exception:
                    pass
        if purged_pins > 0:
            print(f"[+] Purged {purged_pins} stale scraped pin graphics from dist/pins/.")

    # 5. Re-render all 40 handcrafted companion stories with noindex, follow & clean links
    rendered_catalog = 0
    for st in catalog:
        slug = st.get("slug")
        if not slug:
            continue
        write_story_file(st, DIST_DIR)
        rendered_catalog += 1
    print(f"[+] Rendered {rendered_catalog} clean companion Web Stories (noindex, follow).")

    # 6. Rebuild all 30 flagship articles, portal homepage, legal pages, 404, article-first sitemap & RSS
    print(f"[*] Rebuilding portal homepage, {len(FLAGSHIP_ARTICLES)} articles, trust pages, 404, sitemap & RSS...")
    build_all_portal_pages(catalog, DIST_DIR)
    print(f"[+] Portal, articles, legal pages, 404.html, sitemap.xml, and RSS feeds generated successfully.")

    # 7. Copy static assets, PWA files, favicon, and ads.txt
    print(f"[*] Deploying static assets, favicon.ico, and ads.txt...")
    copy_static_assets(STATIC_DIR, DIST_DIR)

    # 8. Final check of ads.txt
    ads_txt_path = DIST_DIR / "ads.txt"
    pub_id = get_adsense_pub_id()
    if ads_txt_path.exists() and pub_id in ads_txt_path.read_text(encoding="utf-8"):
        print(f"[+] ads.txt verified: contains {pub_id}")
    else:
        print(f"[!] Warning: ads.txt check failed or missing pub_id {pub_id}")

    print("=" * 70)
    print("✅ Clean Editorial Rebuild & AdSense Remediation Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
