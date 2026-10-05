"""
TechPulse AMP HTML Test Suite & Validator
Scans all generated Web Story files in dist/stories/ and verifies 100% compliance
against the official Google AMP HTML Validator in high-speed batch mode.
"""

import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple

# Ensure UTF-8 output on all platforms (Windows cp1252 fix)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from config import DIST_DIR


def find_all_story_files(dist_dir: Path) -> List[Path]:
    """Finds all story index.html files in dist/stories/*/index.html"""
    stories_dir = dist_dir / "stories"
    if not stories_dir.exists():
        return []
    return sorted(list(stories_dir.glob("*/index.html")))


def run_batch_amphtml_validator(file_paths: List[Path]) -> Tuple[bool, str]:
    """
    Executes official amphtml-validator CLI in batch mode via npx.
    """
    npx_bin = shutil.which("npx.cmd") or shutil.which("npx") or "npx"
    str_paths = [str(p.resolve()) for p in file_paths]
    cmd = [npx_bin, "--yes", "amphtml-validator", "--format", "text", *str_paths]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = (result.stdout + "\n" + result.stderr).strip()
        passed = (result.returncode == 0) and ("FAIL" not in output)
        return passed, output
    except Exception as e:
        return False, f"Validator invocation error: {e}"


def run_structural_rule_checks(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Independent Python verification of key Google AMP Story 1.0 structural invariants.
    """
    content = file_path.read_text(encoding="utf-8")
    errors = []

    if "<!doctype html>" not in content.lower():
        errors.append("Missing <!doctype html>")
    if "<html ⚡" not in content and "<html amp" not in content:
        errors.append("Missing <html ⚡> or <html amp> attribute")
    if '<script async src="https://cdn.ampproject.org/v0.js"></script>' not in content:
        errors.append("Missing AMP v0.js runtime script")
    if 'custom-element="amp-story"' not in content:
        errors.append("Missing amp-story-1.0.js extension")
    if "<style amp-boilerplate>" not in content:
        errors.append("Missing <style amp-boilerplate>")
    if "<style amp-custom>" not in content:
        errors.append("Missing <style amp-custom>")
    if "!important" in content:
        errors.append("Prohibited '!important' found in CSS")
    if "<amp-story standalone" not in content:
        errors.append("Missing <amp-story standalone> tag")
    if "<amp-story-page" not in content:
        errors.append("Missing <amp-story-page> tags")

    return len(errors) == 0, errors


def validate_all_stories(dist_dir: Path = DIST_DIR) -> int:
    """
    Runs the full validation suite across all generated stories in high-speed batch mode.
    Returns 0 if all pass, 1 otherwise.
    """
    story_files = find_all_story_files(dist_dir)

    print("=" * 70)
    print(" ⚡ TechPulse Google AMP Web Story 1.0 Compliance Test Suite")
    print("=" * 70)

    if not story_files:
        print("[-] No story files found in dist/stories/. Run fetch_and_generate.py first.")
        return 1

    total = len(story_files)
    print(f"[*] Validating {total} Web Stories via official Google amphtml-validator...\n")

    # 1. High-speed batch validation
    batch_passed, validator_output = run_batch_amphtml_validator(story_files)

    passed_count = 0
    failed_count = 0

    output_lines = validator_output.splitlines()

    for file_path in story_files:
        slug = file_path.parent.name
        # Check individual file output
        matching = [l for l in output_lines if str(file_path.resolve()) in l or slug in l]
        is_amp_valid = not any("FAIL" in l for l in matching) if matching else batch_passed
        struct_valid, struct_errors = run_structural_rule_checks(file_path)

        if is_amp_valid and struct_valid:
            passed_count += 1
            print(f"  [PASS] /stories/{slug}/index.html (100% AMP Compliant)")
        else:
            failed_count += 1
            print(f"  [FAIL] /stories/{slug}/index.html")
            if not is_amp_valid:
                print(f"         Validator details: {matching}")
            if not struct_valid:
                print(f"         Structural errors: {struct_errors}")

    print("\n" + "-" * 70)
    print(f" Validation Results: {passed_count}/{total} Passed (100% Target)")
    print("-" * 70)

    if failed_count == 0:
        print("  SUCCESS: All stories passed official Google AMP Story 1.0 validation!")
        return 0
    else:
        print(f"  FAILURE: {failed_count} stories failed validation.")
        return 1


if __name__ == "__main__":
    exit_code = validate_all_stories()
    sys.exit(exit_code)
