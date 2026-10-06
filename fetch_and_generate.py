"""
TechPulse Standalone Orchestrator Pipeline
Executes the full autonomous static generation lifecycle:
1. Fetch live tech RSS feeds & viral fallback dataset
2. Synthesize 5-slide stories via Gemini API / deterministic rule engine
3. Render 100% AMP Web Stories into dist/stories/<slug>/index.html
4. Render Cyberpunk Glassmorphic Portal homepage dist/index.html
5. Render 4 mandatory legal pages (/about/, /privacy/, /terms/, /contact/)
6. Generate dynamic sitemap.xml, robots.txt, and stories.json
7. Copy static assets to dist/static/
8. Execute built-in AMP HTML test suite validator
"""

import sys
import time
import shutil
from pathlib import Path

# Ensure UTF-8 output on all platforms (Windows cp1252 fix)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from config import DIST_DIR, STATIC_DIR, SITE_NAME
from content_engine import fetch_all_tech_stories
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


def run_pipeline(target_count: int = 12, skip_validation: bool = False) -> int:
    """Executes the end-to-end generation pipeline."""
    start_time = time.time()
    print("=" * 70)
    print(f" ⚡ {SITE_NAME} Autonomous Static Generation Pipeline")
    print("=" * 70)

    # Prepare dist directory and clean obsolete stories
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    stories_dir = DIST_DIR / "stories"
    if stories_dir.exists():
        shutil.rmtree(stories_dir)
    stories_dir.mkdir(parents=True, exist_ok=True)

    # 1. Fetch & ingest tech news
    raw_articles = fetch_all_tech_stories(target_count=target_count)
    if not raw_articles:
        print("[!] No stories retrieved. Aborting pipeline.")
        return 1

    # 2. Synthesize stories into 5 snappy slides
    print(f"\n[*] Synthesizing {len(raw_articles)} stories into 5-slide AMP stories...")
    synthesized_stories = []
    for idx, article in enumerate(raw_articles):
        synthesized = synthesize_story(article, index=idx)
        synthesized_stories.append(synthesized)

    # 3. Generate individual AMP Story pages
    print(f"\n[*] Writing AMP Web Story files into dist/stories/...")
    for story in synthesized_stories:
        path = write_story_file(story, DIST_DIR)
        print(f"    -> Rendered: {path.relative_to(DIST_DIR.parent)}")

    # 4. Generate Portal homepage, legal pages, sitemap, robots, manifest
    print(f"\n[*] Building portal homepage, legal pages, and sitemaps...")
    build_all_portal_pages(synthesized_stories, DIST_DIR)

    # 5. Copy static assets (CSS, JS, images, logos)
    copy_static_assets(STATIC_DIR, DIST_DIR)

    # 6. Run AMP validation test suite
    validation_code = 0
    if not skip_validation:
        print(f"\n[*] Running AMP validation test suite...")
        validation_code = validate_all_stories(DIST_DIR)
    else:
        print(f"\n[*] Skipping AMP validation as requested.")

    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 70)
    if validation_code == 0:
        print(f" 🚀 PIPELINE SUCCESS! Built {len(synthesized_stories)} stories in {elapsed}s")
        print(f" Output ready for instant Vercel deployment: {DIST_DIR}")
    else:
        print(f" [!] PIPELINE COMPLETED WITH VALIDATION ISSUES ({elapsed}s)")
    print("=" * 70)

    return validation_code


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="TechPulse Static Story Generator")
    parser.add_argument("--count", type=int, default=12, help="Target number of stories")
    parser.add_argument("--skip-val", "--skip-validation", dest="skip_val", action="store_true", help="Skip AMP HTML validation")
    args, unknown = parser.parse_known_args()

    code = run_pipeline(target_count=args.count, skip_validation=args.skip_val)
    sys.exit(code)
