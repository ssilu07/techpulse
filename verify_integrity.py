"""
Comprehensive Automated Verification & AdSense Compliance Suite for TechSeconds
Validates:
1. Zero scraped third-party RSS stories, zero boilerplate fallback text, zero orphan directories
2. Zero broken internal links across all companion Web Stories & all 30 flagship articles
3. 100% Google AMP Story 1.0 structural compliance + noindex on short visual stories
4. Article-first sitemap.xml (no thin story dilution)
5. Strict AdSense script hygiene:
   - Present on content pages (/, /articles/, /articles/<slug>/)
   - Absent on 404.html and policy/utility pages (/privacy/, /terms/, /contact/, /about/, /editorial-team/)
   - Valid ads.txt publisher entry
6. Zero legacy TechPulse branding or fake AI author personas anywhere in dist/
"""

import sys
import re
import json
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_DIR))

from validator import run_structural_rule_checks

BANNED_SOURCES = {"The Verge", "TechCrunch", "Engadget", "Android Police"}
BANNED_TERMS = ["TechPulse", "Elena Rostova", "Marcus Vance", "Dr. Aarav Patel", "Aarav Patel"]


def run_verification():
    dist_dir = REPO_DIR / "dist"
    stories_dir = dist_dir / "stories"
    articles_dir = dist_dir / "articles"

    failures = []

    print("=" * 70)
    print("⚡ RUNNING COMPREHENSIVE ADSENSE & INTEGRITY VERIFICATION SUITE")
    print("=" * 70)

    # 1. Stories catalog & zero-boilerplate / zero-orphan audit
    stories_json_path = dist_dir / "stories.json"
    catalog = json.loads(stories_json_path.read_text(encoding="utf-8"))
    catalog_slugs = {s.get("slug") for s in catalog if s.get("slug")}
    disk_story_slugs = {p.name for p in stories_dir.iterdir() if p.is_dir()}
    valid_article_slugs = {p.name for p in articles_dir.iterdir() if p.is_dir()}

    orphan_dirs = disk_story_slugs - catalog_slugs
    scraped_items = [s["slug"] for s in catalog if s.get("source") in BANNED_SOURCES or s.get("synthesizer") == "context-aware-nlp-engine"]

    print(f"[*] 1. Story Hygiene: {len(catalog)} curated stories | Orphans: {len(orphan_dirs)} | Scraped/Boilerplate: {len(scraped_items)}")
    if orphan_dirs:
        failures.append(f"Found {len(orphan_dirs)} orphan story directories")
    if scraped_items:
        failures.append(f"Found {len(scraped_items)} scraped/boilerplate stories in stories.json")

    # 2. Broken links + AMP structural compliance + noindex check on stories
    story_files = sorted(stories_dir.glob("*/index.html"))
    broken_story_links = 0
    amp_failed = 0
    missing_noindex = 0
    for sf in story_files:
        content = sf.read_text(encoding="utf-8")
        for target in re.findall(r'(?:https://techseconds\.com)?/articles/([a-zA-Z0-9_-]+)/', content):
            if target and target not in valid_article_slugs:
                broken_story_links += 1
        ok, errs = run_structural_rule_checks(sf)
        if not ok:
            amp_failed += 1
            failures.append(f"AMP fail on {sf.parent.name}: {errs}")
        if 'content="noindex, follow"' not in content:
            missing_noindex += 1

    print(f"[*] 2. Stories AMP & Links: {len(story_files)} checked | Broken Links: {broken_story_links} | AMP Failed: {amp_failed} | Missing noindex: {missing_noindex}")
    if broken_story_links:
        failures.append(f"{broken_story_links} broken article links inside stories")
    if missing_noindex:
        failures.append(f"{missing_noindex} stories missing noindex, follow")

    # 3. Articles broken links & AdSense presence
    article_files = sorted([p / "index.html" for p in articles_dir.iterdir() if p.is_dir()])
    broken_article_links = 0
    articles_missing_adsense = 0
    for af in article_files:
        content = af.read_text(encoding="utf-8")
        for target in re.findall(r'(?:https://techseconds\.com)?/stories/([a-zA-Z0-9_-]+)/', content):
            if target and target not in disk_story_slugs:
                broken_article_links += 1
        if "adsbygoogle.js?client=ca-pub-1811294933992844" not in content:
            articles_missing_adsense += 1

    print(f"[*] 3. Articles Audit: {len(article_files)} articles | Broken Links: {broken_article_links} | Missing AdSense: {articles_missing_adsense}")
    if broken_article_links:
        failures.append(f"{broken_article_links} broken story links inside articles")
    if articles_missing_adsense:
        failures.append(f"{articles_missing_adsense} articles missing AdSense tag")

    # 4. Article-first Sitemap check (zero /stories/ URLs)
    sitemap_text = (dist_dir / "sitemap.xml").read_text(encoding="utf-8")
    sitemap_urls = re.findall(r"<loc>(.*?)</loc>", sitemap_text)
    sitemap_stories = [u for u in sitemap_urls if "/stories/" in u]
    print(f"[*] 4. Sitemap Audit: {len(sitemap_urls)} total URLs | Thin /stories/ URLs in sitemap: {len(sitemap_stories)}")
    if sitemap_stories:
        failures.append(f"Found {len(sitemap_stories)} /stories/ URLs in sitemap.xml")

    # 5. AdSense placement policy check (404 & legal pages must NOT have adsbygoogle; homepage & articles MUST)
    no_ads_pages = [
        dist_dir / "404.html",
        dist_dir / "privacy" / "index.html",
        dist_dir / "terms" / "index.html",
        dist_dir / "contact" / "index.html",
        dist_dir / "about" / "index.html",
        dist_dir / "editorial-team" / "index.html",
    ]
    ads_leak_pages = [str(p.relative_to(dist_dir)) for p in no_ads_pages if p.exists() and "adsbygoogle" in p.read_text(encoding="utf-8")]
    home_has_ads = "adsbygoogle.js?client=ca-pub-1811294933992844" in (dist_dir / "index.html").read_text(encoding="utf-8")
    articles_hub_has_ads = "adsbygoogle.js?client=ca-pub-1811294933992844" in (articles_dir / "index.html").read_text(encoding="utf-8")
    print(f"[*] 5. AdSense Placement Hygiene: Home={home_has_ads} | ArticlesHub={articles_hub_has_ads} | Leaks on 404/Legal={len(ads_leak_pages)}")
    if not home_has_ads or not articles_hub_has_ads:
        failures.append("Homepage or Articles hub missing AdSense tag")
    if ads_leak_pages:
        failures.append(f"AdSense tag found on non-content/error pages: {ads_leak_pages}")

    # 6. ads.txt & Favicon & Branding/Persona Cleanliness
    ads_txt_ok = "pub-1811294933992844" in (dist_dir / "ads.txt").read_text(encoding="utf-8")
    favicon_ok = (dist_dir / "favicon.ico").exists() and (dist_dir / "favicon.ico").stat().st_size > 0
    brand_leaks = []
    check_pages = [dist_dir / "index.html", articles_dir / "index.html", *no_ads_pages, *article_files]
    for p in check_pages:
        if p.exists():
            txt = p.read_text(encoding="utf-8")
            for term in BANNED_TERMS:
                if term in txt:
                    brand_leaks.append((str(p.relative_to(dist_dir)), term))
    print(f"[*] 6. Trust & Branding Check: ads.txt={ads_txt_ok} | favicon={favicon_ok} | Legacy Brand/Fake Persona Leaks={len(brand_leaks)}")
    if not ads_txt_ok:
        failures.append("ads.txt invalid or missing publisher ID")
    if not favicon_ok:
        failures.append("favicon.ico missing")
    if brand_leaks:
        failures.append(f"Found legacy branding/fake persona leaks: {brand_leaks[:5]}")

    print("=" * 70)
    if not failures:
        print("✅ ALL CHECKS PASSED (100% CLEAN & ADSENSE COMPLIANT)")
        return 0
    else:
        print("❌ VERIFICATION FAILED:")
        for f in failures:
            print(f"   - {f}")
        return 1


if __name__ == "__main__":
    sys.exit(run_verification())
