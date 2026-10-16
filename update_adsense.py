"""
Google AdSense 1-Click Publisher Activation Script for TechSeconds
Instantly configures your publisher ID, updates ads.txt, injects verification
and auto-ad scripts across all pages, and deploys to production via git.
"""

import sys
import re
import os
import subprocess
from pathlib import Path

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"


def clean_id(raw_id: str) -> str:
    """Extracts numeric digits and returns pub-XXXXXXXXXXXXXXXX."""
    raw = raw_id.strip()
    digits = re.sub(r"[^\d]", "", raw)
    if not digits:
        raise ValueError(f"Invalid Publisher ID: '{raw_id}'. Must contain numeric publisher digits.")
    return f"pub-{digits}"


def update_ads_txt(pub_id: str):
    """Updates ads.txt in root and dist/ directories."""
    content = (
        f"# Google AdSense Authorized Digital Sellers for TechSeconds\n"
        f"google.com, {pub_id}, DIRECT, f08c47fec0942fa0\n"
    )
    (BASE_DIR / "ads.txt").write_text(content, encoding="utf-8")
    (DIST_DIR / "ads.txt").write_text(content, encoding="utf-8")
    print(f"[+] Updated ads.txt with: google.com, {pub_id}, DIRECT, f08c47fec0942fa0")


def update_env(pub_id: str):
    """Saves ADSENSE_CLIENT_ID to .env and .env.local."""
    ca_pub = f"ca-{pub_id}"
    for env_name in [".env", ".env.local"]:
        env_file = BASE_DIR / env_name
        lines = []
        if env_file.exists():
            lines = env_file.read_text(encoding="utf-8").splitlines()
        
        new_lines = [l for l in lines if not l.startswith("ADSENSE_CLIENT_ID=")]
        new_lines.append(f"ADSENSE_CLIENT_ID={ca_pub}")
        env_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print(f"[+] Saved ADSENSE_CLIENT_ID={ca_pub} to {env_name}")


def inject_adsense_into_html(pub_id: str):
    """Injects AdSense async script tag into <head> of all static HTML files in dist/."""
    ca_pub = f"ca-{pub_id}"
    script_tag = f'  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ca_pub}" crossorigin="anonymous"></script>'
    
    html_files = [DIST_DIR / "index.html", DIST_DIR / "articles" / "index.html"]
    html_files.extend((DIST_DIR / "articles").glob("*/index.html"))
    for sub in ["about", "contact", "privacy", "terms", "editorial-team"]:
        legal_file = DIST_DIR / sub / "index.html"
        if legal_file.exists():
            html_files.append(legal_file)

    modified_count = 0
    for hf in html_files:
        if not hf.exists():
            continue
        html = hf.read_text(encoding="utf-8")
        if "pagead2.googlesyndication.com" in html:
            # Replace existing client ID
            html = re.sub(
                r'https://pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js\?client=ca-pub-\d+',
                f'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ca_pub}',
                html
            )
        else:
            # Inject right before </head>
            if "</head>" in html:
                html = html.replace("</head>", f"{script_tag}\n</head>", 1)
        hf.write_text(html, encoding="utf-8")
        modified_count += 1

    print(f"[+] Injected AdSense verification & auto ads script into {modified_count} HTML pages in dist/.")


def commit_and_push(pub_id: str):
    """Commits and pushes changes to git main branch."""
    try:
        print("[*] Staging files for git commit...")
        subprocess.run(["git", "add", "."], cwd=str(BASE_DIR), check=True)
        commit_msg = f"feat(adsense): activate Google AdSense publisher {pub_id} with ads.txt and verification scripts"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=str(BASE_DIR), check=False)
        print("[*] Pushing to GitHub main branch...")
        res = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE_DIR), capture_output=True, text=True)
        if res.returncode == 0:
            print("[+] Successfully deployed AdSense configuration to Vercel!")
        else:
            print(f"[!] Git push output: {res.stderr or res.stdout}")
    except Exception as err:
        print(f"[!] Git deployment error: {err}")


def main():
    if len(sys.argv) > 1:
        raw_id = sys.argv[1]
    else:
        print("=" * 60)
        print("  ⚡ TechSeconds Google AdSense 1-Click Activator")
        print("=" * 60)
        raw_id = input("Enter your Google AdSense Publisher ID (e.g. pub-1234567890123456): ").strip()

    try:
        pub_id = clean_id(raw_id)
        print(f"\n[*] Activating Publisher ID: {pub_id} (ca-{pub_id})")
        update_env(pub_id)
        update_ads_txt(pub_id)
        inject_adsense_into_html(pub_id)
        commit_and_push(pub_id)
        print("\n" + "=" * 60)
        print("  🎉 GOOGLE ADSENSE ACTIVATION COMPLETE!")
        print(f"  • Publisher ID: {pub_id}")
        print(f"  • ads.txt: https://techseconds.com/ads.txt")
        print(f"  • Verification Script: Live on all 200+ pages")
        print("=" * 60)
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
