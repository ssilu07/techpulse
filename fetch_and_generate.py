"""
TechPulse Autonomous Static Orchestrator Pipeline
Strictly engineered to comply with Google Search Essentials & Spam Policies:
1. Scaled Content Abuse Prevention:
   - Enforces a strict novelty limit per run (default: 4 stories).
   - Performs semantic deduplication against the persistent archive.
   - Zero spam: If no novel, high-quality tech news exists, generates 0 stories.
2. Zero Downtime & Persistent Catalog:
   - NEVER deletes previous story directories; avoids 404 crawl errors.
   - Maintains an evergreen cumulative sitemap.xml for Google Search Console.
   - Recovers missing story files automatically if running on a fresh clone.
3. 100% Google AMP Story 1.0 Compliance:
   - Verified with official amphtml-validator.
"""

import sys
import time
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Set

# Ensure UTF-8 output on all platforms (Windows cp1252 fix)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from config import DIST_DIR, STATIC_DIR, SITE_NAME
from content_engine import (
    CURATED_VIRAL_STORIES,
    fetch_all_tech_stories,
    fetch_fresh_tech_stories,
)
from synthesizer import synthesize_story
from story_builder import write_story_file
from portal_builder import build_all_portal_pages
from validator import validate_all_stories


def copy_static_assets(src_dir: Path, dist_dir: Path):
    """Copies static CSS, JS, and image assets to dist/static/"""
    target_static = dist_dir / "static"
    if target_static.exists():
        shutil.rmtree(target_static)
    shutil.copytree(src_dir, target_static)
    print(f"[+] Static assets deployed to: {target_static}")


def load_persistent_catalog(dist_dir: Path) -> List[Dict[str, Any]]:
    """
    Loads existing story catalog from dist/stories.json.
    Falls back to CURATED_VIRAL_STORIES if catalog is missing or unreadable.
    """
    stories_json = dist_dir / "stories.json"
    if stories_json.exists():
        try:
            content = stories_json.read_text(encoding="utf-8")
            data = json.loads(content)
            if isinstance(data, list) and len(data) > 0:
                print(f"[+] Loaded persistent story catalog: {len(data)} existing stories.")
                return data
        except Exception as err:
            print(f"[!] Warning reading existing stories.json: {err}")

    print(f"[*] Initializing catalog with {len(CURATED_VIRAL_STORIES)} verified baseline stories.")
    return [dict(s) for s in CURATED_VIRAL_STORIES]


def ensure_story_files_exist(stories: List[Dict[str, Any]], dist_dir: Path):
    """
    Verifies that all cataloged stories have corresponding HTML files on disk.
    Renders any missing files to prevent broken internal links or 404s.
    """
    stories_dir = dist_dir / "stories"
    stories_dir.mkdir(parents=True, exist_ok=True)
    rendered_count = 0

    for story in stories:
        slug = story.get("slug")
        if not slug:
            continue
        story_html = stories_dir / slug / "index.html"
        if not story_html.exists():
            write_story_file(story, dist_dir)
            rendered_count += 1

    if rendered_count > 0:
        print(f"[+] Restored {rendered_count} missing story HTML files to prevent 404s.")


def run_pipeline(
    max_new: int = 4,
    skip_validation: bool = False,
    force_all: bool = False,
) -> int:
    """
    Executes the autonomous static generation lifecycle.
    
    Safe by design:
    - Never deletes existing stories from disk (eliminates 404s).
    - Capped at max_new fresh stories per run (prevents Google Scaled Content Abuse).
    - Merges new stories into cumulative catalog.
    """
    start_time = time.time()
    print("=" * 70)
    print(f" ⚡ {SITE_NAME} Autonomous Static Generation Pipeline (Google Compliant)")
    print("=" * 70)

    # 1. Prepare dist directory and persistent story directory
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    stories_dir = DIST_DIR / "stories"
    stories_dir.mkdir(parents=True, exist_ok=True)

    # 2. Load existing persistent catalog
    catalog = load_persistent_catalog(DIST_DIR)

    new_synthesized_stories: List[Dict[str, Any]] = []
    new_story_paths: List[Path] = []

    if force_all:
        print(f"[*] --force-all flag detected: Re-fetching full {max_new} feed items from scratch...")
        raw_articles = fetch_all_tech_stories(target_count=max_new)
        for idx, article in enumerate(raw_articles):
            synthesized = synthesize_story(article, index=idx)
            path = write_story_file(synthesized, DIST_DIR)
            new_synthesized_stories.append(synthesized)
            new_story_paths.append(path)
        final_catalog = new_synthesized_stories
    else:
        # 3. Novelty-checked, spam-free ingestion
        print(f"[*] Scanning feeds for up to {max_new} genuinely novel tech stories...")
        fresh_articles = fetch_fresh_tech_stories(catalog, max_new=max_new)

        if not fresh_articles:
            print("[+] Zero novel stories discovered. Feeds are up to date.")
            print("[+] Spam Prevention Protocol: Skipping redundant generation.")
        else:
            print(f"\n[*] Synthesizing {len(fresh_articles)} fresh breaking stories via Gemini / NLP engine...")
            for idx, article in enumerate(fresh_articles):
                synthesized = synthesize_story(article, index=idx)
                path = write_story_file(synthesized, DIST_DIR)
                print(f"    -> Rendered: {path.relative_to(DIST_DIR.parent)}")
                new_synthesized_stories.append(synthesized)
                new_story_paths.append(path)
                # Rate-limit safety pause
                time.sleep(1.2)

        # 4. Merge fresh stories at the top of the catalog
        # Deduplicate by slug preserving order (newest first)
        seen_slugs: Set[str] = set()
        merged_catalog: List[Dict[str, Any]] = []
        for s in new_synthesized_stories + catalog:
            s_slug = s.get("slug")
            if s_slug and s_slug not in seen_slugs:
                seen_slugs.add(s_slug)
                merged_catalog.append(s)

        final_catalog = merged_catalog

    # 5. Ensure every cataloged story has its HTML file rendered on disk
    ensure_story_files_exist(final_catalog, DIST_DIR)

    # 6. Build Portal homepage, legal pages, dynamic sitemap, robots, manifest
    print(f"\n[*] Building portal homepage, legal pages, and cumulative sitemap ({len(final_catalog)} stories)...")
    build_all_portal_pages(final_catalog, DIST_DIR)

    # 7. Copy static assets (CSS, JS, images, logos)
    copy_static_assets(STATIC_DIR, DIST_DIR)

    # 8. Run AMP validation test suite
    validation_code = 0
    if not skip_validation:
        print(f"\n[*] Running AMP validation test suite...")
        if new_story_paths:
            # Validate newly generated stories
            validation_code = validate_all_stories(DIST_DIR, specific_files=new_story_paths)
        else:
            # Validate existing stories
            validation_code = validate_all_stories(DIST_DIR)
    else:
        print(f"\n[*] Skipping AMP validation as requested.")

    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 70)
    if validation_code == 0:
        print(
            f" 🚀 PIPELINE SUCCESS! Catalog contains {len(final_catalog)} stories "
            f"({len(new_synthesized_stories)} added) in {elapsed}s"
        )
        print(f" Output ready for instant Vercel deployment: {DIST_DIR}")
    else:
        print(f" [!] PIPELINE COMPLETED WITH VALIDATION ISSUES ({elapsed}s)")
    print("=" * 70)

    return validation_code


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="TechPulse Static Story Generator (Google Compliant)")
    parser.add_argument(
        "--max-new",
        type=int,
        default=4,
        help="Maximum novel stories to ingest & synthesize per run (default: 4, prevents spam)"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Legacy alias for max-new. Clamped to 6 max to prevent automated spam unless --force-all."
    )
    parser.add_argument(
        "--force-all",
        action="store_true",
        help="Force re-fetching and full rebuild from scratch"
    )
    parser.add_argument(
        "--skip-val",
        "--skip-validation",
        dest="skip_val",
        action="store_true",
        help="Skip AMP HTML validation"
    )
    args, unknown = parser.parse_known_args()

    # Determine safe novel limit
    if args.count is not None and not args.force_all:
        # Clamp legacy --count to safe non-spam threshold
        effective_max_new = min(args.count, 6)
        print(f"[*] Note: Legacy --count {args.count} safely clamped to {effective_max_new} to comply with Google Spam policies.")
    else:
        effective_max_new = args.max_new

    code = run_pipeline(
        max_new=effective_max_new,
        skip_validation=args.skip_val,
        force_all=args.force_all,
    )
    sys.exit(code)
