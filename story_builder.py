"""
TechPulse AMP Web Story Builder
Generates 100% Google AMP Story 1.0 compliant stories with zero validator errors.
Features Outfit & Space Grotesk typography, cyber-dark glassmorphism, responsive posters, and SEO schema.
"""

import html
import json
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Dict, Any, List

from config import (
    SITE_NAME,
    SITE_URL,
    PUBLISHER_NAME,
    PUBLISHER_LOGO_URL,
    AMP_PUBLISHER_LOGO_URL,
    GOOGLE_SITE_VERIFICATION,
    GA_MEASUREMENT_ID,
    ADSENSE_CLIENT_ID,
    get_category_fallback_image,
)


def to_iso8601(date_str: str) -> str:
    """Safely converts any date string to standard ISO 8601 for Schema.org JSON-LD."""
    if not date_str:
        return datetime.now(timezone.utc).isoformat()
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.isoformat()
    except Exception:
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.isoformat()
        except Exception:
            return date_str


def get_image_variants(url: str, fallback_url: str) -> Dict[str, Any]:
    """
    Returns image variants fulfilling Google's strict AMP, Article, and Web Story specifications:
    - Minimum 1200px width for Article structured data & Discover eligibility (Google Search guideline)
    - Aspect ratio triad (16x9, 4x3, 1x1) for Schema.org image array
    - 3:4 portrait (1200x1600) for amp-story poster-portrait-src (Google minimum: 640x853)
    - 1:1 square (1200x1200) for amp-story poster-square-src (Google minimum: 960x960)
    - 4:3 landscape (1200x900) for amp-story poster-landscape-src (Google minimum: 960x720)
    - 9:16 vertical (1080x1920) for slide background amp-img
    - 16:9 landscape (1280x720) for OpenGraph and Twitter cards
    """
    default_raster_fallback = "https://images.unsplash.com/photo-1518770660439-4636190af475"

    target_url = url
    if not target_url or target_url.startswith("/") or target_url.endswith(".svg"):
        if fallback_url and not fallback_url.startswith("/") and not fallback_url.endswith(".svg"):
            target_url = fallback_url
        else:
            target_url = default_raster_fallback

    if "images.unsplash.com" in target_url:
        base = target_url.split("?")[0]
        return {
            # Google Search Article structured data: 16x9, 4x3, 1x1 all >= 1200px wide and >= 800,000px
            "schema_images": [
                f"{base}?w=1280&h=720&fit=crop&q=85",
                f"{base}?w=1200&h=900&fit=crop&q=85",
                f"{base}?w=1200&h=1200&fit=crop&q=85",
            ],
            "poster_portrait": f"{base}?w=1200&h=1600&fit=crop&q=85",
            "poster_square": f"{base}?w=1200&h=1200&fit=crop&q=85",
            "poster_landscape": f"{base}?w=1200&h=900&fit=crop&q=85",
            "og_image": f"{base}?w=1280&h=720&fit=crop&q=85",
            "slide_image": f"{base}?w=1080&h=1920&fit=crop&q=85",
        }

    # For other remote raster URLs, ensure high-res queries and fallback triad
    high_res = re.sub(r"w=\d+", "w=1280", target_url)
    fb_base = default_raster_fallback
    return {
        "schema_images": [
            high_res,
            f"{fb_base}?w=1200&h=900&fit=crop&q=85",
            f"{fb_base}?w=1200&h=1200&fit=crop&q=85",
        ],
        "poster_portrait": f"{fb_base}?w=1200&h=1600&fit=crop&q=85",
        "poster_square": f"{fb_base}?w=1200&h=1200&fit=crop&q=85",
        "poster_landscape": high_res,
        "og_image": high_res,
        "slide_image": high_res,
    }


# High-CTR hand-crafted title overrides for top-ranking & trending stories
HIGH_CTR_TITLE_OVERRIDES: Dict[str, str] = {
    "nikon-microscopic-video-competition-winner-disqualified-for-using-gene": (
        "Why Nikon Disqualified Its AI Video Winner: Shocking Truth"
    ),
    "pure-insanity-mathematicians-will-need-years-to-make-sense-of-openais": (
        "OpenAI's Math Proof Stuns Top Researchers: Full Details"
    ),
    "silicon-valleys-ai-wunderkind-launches-underdog-the-most-private-insti": (
        "Silicon Valley AI Prodigy Launches Underdog: Key Details"
    ),
    "chatgpts-intelligent-ui-update-fills-its-responses-with-pictures-chart": (
        "ChatGPT's New UI Update: Interactive Visuals & Live Charts"
    ),
    "ankers-100w-universal-charger-is-a-great-travel-gadget-for-64": (
        "Anker 100W Travel Charger: Is It Really Worth $64?"
    ),
    "amd-will-bring-fsr-4-to-handhelds-by-the-end-of-2026": (
        "AMD FSR 4 Coming to Handhelds by 2026: What to Expect"
    ),
    "spacex-announces-plan-to-become-a-major-mobile-carrier": (
        "SpaceX's Plan to Become a Major Mobile Carrier: Details"
    ),
    "danu-robotics-fight-to-build-a-better-recycling-robot": (
        "Danu Robotics: Inside the Battle for Smart Recycling"
    ),
    "google-is-launching-a-one-stop-gemini-agent-for-your-work-tasks": (
        "Google Gemini Work Agent: One-Stop Autonomous Assistant"
    ),
    "nous-research-confirms-it-hit-15b-valuation-launches-ai-agents-for-bus": (
        "Nous Research Hits $1.5B Valuation: New AI Agents Live"
    ),
    "asos-confirms-breach-of-customer-data-after-hackers-send-rogue-app-not": (
        "ASOS Confirms Major Data Breach: Rogue App Alerts Sent"
    ),
    "reflection-debuts-beam-an-open-weight-ai-model-to-rival-chinese-models": (
        "Reflection Unveils Beam: Open-Weight AI Model Powerhouse"
    ),
    "apple-discloses-deal-to-hire-team-and-license-tech-from-personalized-p": (
        "Apple Inks Big AI Tech Deal: Key Details & Strategy"
    ),
    "while-vcs-crowd-into-san-francisco-endeavor-catalyst-raises-320m-for-f": (
        "Endeavor Catalyst Raises $320M: Global Tech VC Shift"
    ),
    "our-first-five-impressions-of-googlebooks-exciting-but-underbaked": (
        "Google Books Review: Exciting Features But Needs Work"
    ),
}

TRAILING_STOPWORDS = {
    "the", "a", "an", "and", "or", "by", "for", "with", "in", "on", "at",
    "to", "from", "its", "than", "of", "is", "it", "as", "that"
}


def optimize_seo_title(raw_title: str, slug: str = "") -> str:
    """
    Transforms long journalistic headlines into punchy, high-CTR titles (45-58 characters).
    Guarantees titles never get truncated by Google Search SERP snippets or Google Discover.
    """
    if slug and slug in HIGH_CTR_TITLE_OVERRIDES:
        return HIGH_CTR_TITLE_OVERRIDES[slug]

    clean = raw_title.strip()
    clean = re.sub(r"\s*\|\s*.*$", "", clean)
    clean = re.sub(r"^(The founder's guide to |Everything you need to know about |Report:\s*|Watch:\s*|Exclusive:\s*)", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"^(A new report suggests that |Reports suggest that |Leaked:\s*)", "", clean, flags=re.IGNORECASE)

    if len(clean) <= 56:
        return clean

    if ":" in clean:
        parts = clean.split(":", 1)
        prefix, suffix = parts[0].strip(), parts[1].strip()
        if 20 <= len(prefix) <= 56:
            return prefix
        if 20 <= len(suffix) <= 56:
            return suffix

    words = clean.split()
    short = []
    for w in words:
        if len(" ".join(short + [w])) <= 54:
            short.append(w)
        else:
            break
    while short and short[-1].lower() in TRAILING_STOPWORDS:
        short.pop()

    result = " ".join(short).rstrip(":, -")
    return result if len(result) >= 15 else clean[:55].rstrip(":, -")


def get_story_poll(story: Dict[str, Any]) -> Dict[str, str]:
    """Generates an engaging, topic-relevant interactive poll for the story."""
    if story.get("poll_prompt") and story.get("poll_option_1") and story.get("poll_option_2"):
        return {
            "prompt": story["poll_prompt"],
            "opt1": story["poll_option_1"],
            "opt2": story["poll_option_2"],
        }
    
    title = (story.get("title") or "").lower()
    category = story.get("category_id", "future-tech")

    # Keyword-specific high-engagement polls
    if any(k in title for k in ["apple", "iphone", "macbook", "ipad", "ios", "vision"]):
        return {
            "prompt": "Will you buy or upgrade to this Apple device?",
            "opt1": "🔥 Yes, Day-One Upgrade",
            "opt2": "❌ Pass / Sticking with Current",
        }
    if any(k in title for k in ["openai", "chatgpt", "gpt-4", "gpt-5", "claude", "gemini", "anthropic", "ai "]):
        return {
            "prompt": "Will this AI breakthrough replace human workflows?",
            "opt1": "🤖 Definitely Yes",
            "opt2": "🛡️ Needs Human Oversight",
        }
    if any(k in title for k in ["nvidia", "gpu", "rtx", "intel", "amd", "snapdragon", "chip"]):
        return {
            "prompt": "Is this silicon performance leap worth the cost?",
            "opt1": "⚡ Massive Upgrade",
            "opt2": "🛑 Diminishing Returns",
        }
    if any(k in title for k in ["samsung", "galaxy", "pixel", "android", "xiaomi", "oneplus"]):
        return {
            "prompt": "Does this beat current flagship competition?",
            "opt1": "📱 Clear Winner",
            "opt2": "🤔 Overpriced / Minor Boost",
        }
    if any(k in title for k in ["tesla", "robotaxi", "ev", "robot", "humanoid", "waymo"]):
        return {
            "prompt": "Are you ready to trust autonomous tech daily?",
            "opt1": "🚗 Ready Right Now",
            "opt2": "🛑 Still Too Risky",
        }
    if any(k in title for k in ["ps5", "xbox", "nintendo", "switch", "gta", "steam", "game"]):
        return {
            "prompt": "Will you play this on launch day?",
            "opt1": "🎮 Day-One Must Play",
            "opt2": "🕹️ Wait for Sale / Reviews",
        }
    if any(k in title for k in ["hack", "breach", "security", "leak", "spy", "ban"]):
        return {
            "prompt": "Are you concerned about your digital privacy here?",
            "opt1": "⚠️ Very Concerned",
            "opt2": "🛡️ Already Secured",
        }

    # Category defaults
    cat_defaults = {
        "smartphones": {
            "prompt": "Would you buy this flagship device?",
            "opt1": "🔥 Worth The Price",
            "opt2": "❌ Pass / Skip It",
        },
        "ai-tools": {
            "prompt": "Will this tool change your daily productivity?",
            "opt1": "🚀 Major Productivity Boost",
            "opt2": "🤔 Overhyped Feature",
        },
        "laptops-pc": {
            "prompt": "Is this laptop hardware a game-changer?",
            "opt1": "💻 Instant Buy",
            "opt2": "🛑 Too Expensive",
        },
        "gaming": {
            "prompt": "Are you excited for this hardware/game release?",
            "opt1": "🎮 Super Hyped",
            "opt2": "😐 Not Interested",
        },
        "cybersecurity": {
            "prompt": "Does this privacy issue worry you?",
            "opt1": "⚠️ High Concern",
            "opt2": "🛡️ Low Risk",
        },
    }
    return cat_defaults.get(category, {
        "prompt": "Will this tech breakthrough become mainstream?",
        "opt1": "🚀 Next Big Thing",
        "opt2": "🤔 Fleeting Hype",
    })


def build_story_html(story: Dict[str, Any]) -> str:
    """
    Renders an AMP Web Story HTML document according to AMP Story 1.0 specification.
    """
    title = story.get("title", f"{SITE_NAME} Story")
    slug = story.get("slug", "story")
    summary = story.get("summary", "")
    category_id = story.get("category_id", "future-tech")
    source_link = story.get("link", f"{SITE_URL}/")
    source_name = story.get("source", SITE_NAME)
    published = story.get("published", "2026-10-05T00:00:00Z")
    fallback_img = f"{SITE_URL}{get_category_fallback_image(category_id)}"
    poster_image = story.get("image", fallback_img)
    slides = story.get("slides", [])

    canonical_url = f"{SITE_URL}/stories/{slug}/"
    iso_published = to_iso8601(published)
    poster_variants = get_image_variants(poster_image, fallback_img)
    seo_title = story.get("seo_title") or optimize_seo_title(title, slug)

    # Schema.org JSON-LD (NewsArticle specification compliant with Google News & Discover guidelines)
    schema_data = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": canonical_url,
        },
        "headline": seo_title,
        "alternativeHeadline": title,
        "image": poster_variants["schema_images"],
        "datePublished": iso_published,
        "dateModified": iso_published,
        "author": {
            "@type": "Organization",
            "name": PUBLISHER_NAME,
            "url": SITE_URL,
        },
        "publisher": {
            "@type": "Organization",
            "name": PUBLISHER_NAME,
            "url": SITE_URL,
            "logo": {
                "@type": "ImageObject",
                "url": AMP_PUBLISHER_LOGO_URL,
                "width": 600,
                "height": 60,
            },
        },
        "description": summary,
    }
    schema_json = json.dumps(schema_data, ensure_ascii=False)

    # Generate slides HTML
    slides_html = []
    for idx, slide in enumerate(slides):
        page_id = f"page-{idx + 1}"
        slide_title = slide.get("title", "")
        escaped_title = html.escape(slide_title, quote=True)
        slide_hook = slide.get("hook", "")
        slide_badge = slide.get("badge", f"⚡ {SITE_NAME.upper()}")
        bullet1 = slide.get("bullet1", "")
        bullet2 = slide.get("bullet2", "")
        slide_img = slide.get("image", poster_image)
        slide_variants = get_image_variants(slide_img, fallback_img)
        slide_img_url = slide_variants["slide_image"]

        outlink_html = ""
        poll_layer_html = ""
        final_actions_html = ""

        # On Slide 4, embed interactive community poll to maximize dwell time & engagements
        if idx == 3:
            poll_info = get_story_poll(story)
            safe_poll_id = re.sub(r"[^a-zA-Z0-9_-]", "-", slug)[:24].strip("-") or "poll"
            escaped_prompt = html.escape(poll_info["prompt"], quote=True)
            escaped_opt1 = html.escape(poll_info["opt1"], quote=True)
            escaped_opt2 = html.escape(poll_info["opt2"], quote=True)
            poll_layer_html = f"""
        <amp-story-grid-layer template="vertical" class="poll-grid-layer">
          <amp-story-interactive-poll
            id="poll-{safe_poll_id}"
            theme="dark"
            endpoint="{SITE_URL}/api/poll"
            prompt-text="{escaped_prompt}"
            option-1-text="{escaped_opt1}"
            option-2-text="{escaped_opt2}">
          </amp-story-interactive-poll>
        </amp-story-grid-layer>"""

        # On Slide 5 (final slide), wire the continuous next-story binge loop & in-depth article panel
        if idx == len(slides) - 1:
            next_url = story.get("next_story_url") or f"{SITE_URL}/"
            next_title = story.get("next_story_title") or "Next Tech Breakthrough"
            short_next_title = next_title[:45] + ("..." if len(next_title) > 45 else "")
            escaped_next_title = html.escape(short_next_title, quote=True)
            article_url = f"{SITE_URL}/articles/{slug}/"

            outlink_html = f"""
        <amp-story-page-outlink layout="nodisplay">
          <a href="{next_url}">⚡ Next Story: {escaped_next_title}</a>
        </amp-story-page-outlink>"""

            final_actions_html = f"""
            <div class="final-actions-panel">
              <a href="{article_url}" class="final-action-btn deepdive-action-btn">
                <span>📖 Read Full Analysis (800+ Words)</span>
                <span class="action-arr">→</span>
              </a>
              <a href="{next_url}" class="final-action-btn next-story-action-btn">
                <span>⚡ Next Story: {escaped_next_title}</span>
                <span class="action-arr">→</span>
              </a>
            </div>"""

        slide_markup = f"""
      <amp-story-page id="{page_id}">
        <amp-story-grid-layer template="fill">
          <amp-img src="{slide_img_url}"
            width="720" height="1280"
            layout="responsive"
            alt="{escaped_title}">
            <amp-img fallback src="{fallback_img}"
              width="720" height="1280"
              layout="responsive"
              alt="{escaped_title}">
            </amp-img>
          </amp-img>
        </amp-story-grid-layer>
        <amp-story-grid-layer template="fill">
          <div class="story-scrim"></div>
        </amp-story-grid-layer>
        <amp-story-grid-layer template="vertical">
          <div class="top-bar">
            <div class="brand-pill">⚡ {SITE_NAME}</div>
            <a href="/" class="amp-close-btn" aria-label="Close story and return home">✕</a>
          </div>
          <div class="content-box">
            <div class="hook-tag">{slide_hook}</div>
            <h2 class="slide-title">{slide_title}</h2>
            <div class="tech-badge">{slide_badge}</div>
            <div class="bullet-card">
              <p class="bullet-p">● {bullet1}</p>
              <p class="bullet-p">● {bullet2}</p>
            </div>{final_actions_html}
          </div>
        </amp-story-grid-layer>{poll_layer_html}{outlink_html}
      </amp-story-page>"""
        slides_html.append(slide_markup)

    all_slides_markup = "\n".join(slides_html)

    auto_ads_html = ""
    if ADSENSE_CLIENT_ID:
        ads_config_json = json.dumps({
            "ad-attributes": {
                "type": "adsense",
                "data-ad-client": ADSENSE_CLIENT_ID
            }
        }, indent=2)
        indented_ads_json = "\n".join("        " + line for line in ads_config_json.splitlines())
        auto_ads_html = f"""
      <!-- Google AdSense AMP Story Auto Ads -->
      <amp-story-auto-ads>
        <script type="application/json">
{indented_ads_json}
        </script>
      </amp-story-auto-ads>"""

    escaped_story_title = html.escape(title, quote=True)
    escaped_seo_title = html.escape(seo_title, quote=True)
    escaped_summary = html.escape(summary, quote=True)
    
    # If seo_title is <= 44 characters, append site branding; otherwise keep hook unclipped
    page_title_tag = f"{escaped_seo_title} | {SITE_NAME}" if len(seo_title) <= 44 else escaped_seo_title

    # 100% Compliant AMP Document
    html_output = f"""<!doctype html>
<html ⚡ lang="en">
  <head>
    <meta charset="utf-8">
    <title>{page_title_tag}</title>
    <link rel="canonical" href="{canonical_url}">
    <meta name="viewport" content="width=device-width,minimum-scale=1,initial-scale=1">
    <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
    <meta name="google-site-verification" content="{GOOGLE_SITE_VERIFICATION}">
    <meta name="google-site-verification" content="XMDt3lDT2kpdjLlHlxQCSn5EcJcH2yw8f6nLjhLgN7g">
    
    <!-- OpenGraph & Twitter Meta -->
    <meta property="og:title" content="{escaped_seo_title}">
    <meta property="og:description" content="{escaped_summary}">
    <meta property="og:image" content="{poster_variants['og_image']}">
    <meta property="og:image:width" content="1280">
    <meta property="og:image:height" content="720">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="{SITE_NAME}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{escaped_seo_title}">
    <meta name="twitter:description" content="{escaped_summary}">
    <meta name="twitter:image" content="{poster_variants['og_image']}">

    <!-- Fonts (Google Fonts whitelist in AMP) -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@600;700;800;900&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">

    <!-- AMP Scripts -->
    <script async src="https://cdn.ampproject.org/v0.js"></script>
    <script async custom-element="amp-story" src="https://cdn.ampproject.org/v0/amp-story-1.0.js"></script>
    <script async custom-element="amp-analytics" src="https://cdn.ampproject.org/v0/amp-analytics-0.1.js"></script>
    <script async custom-element="amp-story-interactive" src="https://cdn.ampproject.org/v0/amp-story-interactive-0.1.js"></script>
    <script async custom-element="amp-story-auto-ads" src="https://cdn.ampproject.org/v0/amp-story-auto-ads-0.1.js"></script>

    <!-- Schema.org JSON-LD -->
    <script type="application/ld+json">
    {schema_json}
    </script>

    <!-- AMP Boilerplate -->
    <style amp-boilerplate>body{{-webkit-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-moz-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-ms-animation:-amp-start 8s steps(1,end) 0s 1 normal both;animation:-amp-start 8s steps(1,end) 0s 1 normal both}}@-webkit-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@-moz-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@-ms-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@-o-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}</style><noscript><style amp-boilerplate>body{{-webkit-animation:none;-moz-animation:none;-ms-animation:none;animation:none}}</style></noscript>

    <!-- AMP Custom CSS -->
    <style amp-custom>
      amp-story {{
        font-family: 'Space Grotesk', -apple-system, sans-serif;
        color: #ffffff;
      }}
      
      .story-scrim {{
        position: absolute;
        inset: 0;
        background: linear-gradient(
          180deg,
          rgba(8, 9, 13, 0.25) 0%,
          rgba(8, 9, 13, 0.55) 35%,
          rgba(8, 9, 13, 0.88) 70%,
          #08090d 100%
        );
      }}

      .top-bar {{
        position: absolute;
        top: 24px;
        left: 20px;
        right: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        z-index: 10;
      }}

      .brand-pill {{
        background: rgba(8, 9, 13, 0.85);
        border: 1px solid rgba(6, 182, 212, 0.4);
        border-radius: 999px;
        padding: 5px 14px;
        font-family: 'Outfit', sans-serif;
        font-size: 11px;
        font-weight: 800;
        color: #06b6d4;
        letter-spacing: 0.5px;
      }}

      .amp-close-btn {{
        background: rgba(8, 9, 13, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 50%;
        width: 34px;
        height: 34px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        text-decoration: none;
        font-size: 16px;
      }}

      .content-box {{
        position: absolute;
        bottom: 34px;
        left: 20px;
        right: 20px;
      }}

      .hook-tag {{
        font-family: 'Outfit', sans-serif;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1.5px;
        color: #22d3ee;
        margin-bottom: 8px;
        text-transform: uppercase;
      }}

      .slide-title {{
        font-family: 'Outfit', sans-serif;
        font-size: 23px;
        font-weight: 900;
        line-height: 1.25;
        margin-bottom: 12px;
        color: #ffffff;
      }}

      .tech-badge {{
        display: inline-block;
        background: rgba(6, 182, 212, 0.15);
        border: 1px solid rgba(6, 182, 212, 0.5);
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 11px;
        font-weight: 700;
        color: #22d3ee;
        margin-bottom: 14px;
        letter-spacing: 0.5px;
      }}

      .bullet-card {{
        background: rgba(8, 9, 13, 0.88);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 14px 16px;
      }}

      .bullet-p {{
        font-size: 13.5px;
        line-height: 1.45;
        color: #e2e8f0;
        margin-bottom: 8px;
      }}

      .bullet-p:last-child {{
        margin-bottom: 0;
      }}

      /* Interactive Community Poll Component */
      amp-story-interactive-poll {{
        --interactive-accent-color: #06b6d4;
        --interactive-prompt-background: rgba(8, 9, 13, 0.94);
        --interactive-prompt-text-color: #ffffff;
        --interactive-option-background: rgba(255, 255, 255, 0.08);
        --interactive-option-text-color: #e2e8f0;
        font-family: 'Space Grotesk', -apple-system, sans-serif;
        justify-self: center;
        align-self: end;
        margin-bottom: 24px;
        width: calc(100% - 40px);
        max-width: 420px;
      }}

      .poll-grid-layer {{
        pointer-events: none;
      }}

      .poll-grid-layer amp-story-interactive-poll {{
        pointer-events: auto;
      }}

      /* Final Slide Dual-Action Binge Panel */
      .final-actions-panel {{
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-top: 12px;
      }}

      .final-action-btn {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 14px;
        border-radius: 10px;
        font-family: 'Outfit', sans-serif;
        font-size: 13px;
        font-weight: 700;
        text-decoration: none;
      }}

      .deepdive-action-btn {{
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.25) 0%, rgba(16, 185, 129, 0.2) 100%);
        border: 1px solid rgba(6, 182, 212, 0.5);
        color: #22d3ee;
      }}

      .next-story-action-btn {{
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: #ffffff;
      }}

      .action-arr {{
        font-size: 15px;
        margin-left: 6px;
      }}
    </style>
  </head>
  <body>
    <amp-story standalone
      title="{escaped_seo_title}"
      publisher="{PUBLISHER_NAME}"
      publisher-logo-src="{PUBLISHER_LOGO_URL}"
      poster-portrait-src="{poster_variants['poster_portrait']}"
      poster-square-src="{poster_variants['poster_square']}"
      poster-landscape-src="{poster_variants['poster_landscape']}">
      <!-- Google Analytics 4 (GA4) -->
      <amp-analytics type="gtag">
        <script type="application/json">
        {{
          "vars": {{
            "gtag_id": "{GA_MEASUREMENT_ID}",
            "config": {{
              "{GA_MEASUREMENT_ID}": {{ "groups": "default" }}
            }}
          }}
        }}
        </script>
      </amp-analytics>{auto_ads_html}
{all_slides_markup}
    </amp-story>
  </body>
</html>"""
    return html_output


def write_story_file(story: Dict[str, Any], dist_dir: Path) -> Path:
    """
    Renders and writes an AMP story into dist/stories/<slug>/index.html
    """
    slug = story.get("slug", "story")
    story_dir = dist_dir / "stories" / slug
    story_dir.mkdir(parents=True, exist_ok=True)

    file_path = story_dir / "index.html"
    content = build_story_html(story)
    file_path.write_text(content, encoding="utf-8")
    return file_path
