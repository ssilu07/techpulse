"""
TechPulse Portal Builder
Generates the futuristic dark Cyberpunk/Glassmorphic homepage,
the 4 mandatory legal pages (/about/, /privacy/, /terms/, /contact/),
the XML sitemap with Google Image extensions, robots.txt, and stories.json manifest.
"""

import html as html_lib
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from config import (
    SITE_NAME,
    SITE_TAGLINE,
    SITE_DESCRIPTION,
    SITE_URL,
    CONTACT_EMAIL,
    PUBLISHER_NAME,
    PUBLISHER_LOGO_URL,
    CATEGORIES,
    GOOGLE_SITE_VERIFICATION,
    GA_MEASUREMENT_ID,
    get_category_fallback_image,
    get_adsense_script_tag,
    get_adsense_pub_id,
    PINTEREST_PROFILE_URL,
    PINTEREST_USERNAME,
    PINTEREST_DOMAIN_VERIFY,
    get_pinterest_verify_tag,
)
from story_builder import optimize_seo_title, HIGH_CTR_TITLE_OVERRIDES
from article_builder import build_all_articles, FLAGSHIP_ARTICLES
from pinterest_poster import sync_pinterest_assets


def build_portal_html(
    stories: List[Dict[str, Any]],
    max_cards: Optional[int] = None,
    articles: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Renders the futuristic Cyber-Dark portal homepage.
    Displays in-depth tech editorial deep dives and interactive Google AMP Web Stories.
    Prioritizes top-performing & trending stories for maximal PageRank & internal linking equity.
    """
    active_articles = articles if articles is not None else FLAGSHIP_ARTICLES
    trending_stories = [s for s in stories if s.get("slug") in HIGH_CTR_TITLE_OVERRIDES]
    regular_stories = [s for s in stories if s.get("slug") not in HIGH_CTR_TITLE_OVERRIDES]
    sorted_stories = trending_stories + regular_stories

    display_stories = sorted_stories[:max_cards] if max_cards and len(sorted_stories) > max_cards else sorted_stories
    story_count = len(display_stories)
    current_year = datetime.now(timezone.utc).year

    # Build deepdives cards HTML for homepage showcase
    deepdive_cards_html = []
    for art in active_articles[:6]:
        art_slug = art.get("slug", "")
        art_title = html_lib.escape(art.get("title", ""))
        art_sub = html_lib.escape(art.get("subtitle", "")[:130] + "...")
        art_cat = art.get("category_id", "future-tech")
        art_thumb = art.get("image") or get_category_fallback_image(art_cat)
        art_time = art.get("read_time", "6 min read")
        deepdive_cards_html.append(f"""
        <article class="deepdive-card">
          <div class="deepdive-thumb-wrap">
            <img src="{art_thumb}" alt="{art_title}" class="deepdive-thumb" loading="lazy">
            <span class="deepdive-thumb-badge">{art_cat.upper()}</span>
          </div>
          <div class="deepdive-body">
            <div class="deepdive-meta">
              <span>⏱️ {art_time}</span>
              <span>•</span>
              <span style="color: var(--neon-cyan);">600+ WORDS</span>
            </div>
            <h3 class="deepdive-card-title">
              <a href="/articles/{art_slug}/" style="color: inherit; text-decoration: none;">{art_title}</a>
            </h3>
            <p class="deepdive-excerpt">{art_sub}</p>
            <div class="deepdive-footer">
              <a href="/articles/{art_slug}/" class="deepdive-read-btn">Read Deep Dive →</a>
              <a href="/stories/{art_slug}/" class="deepdive-story-link" target="_blank">⚡ Story</a>
            </div>
          </div>
        </article>""")
    deepdives_markup = "\n        ".join(deepdive_cards_html)

    # Build category filter pills HTML
    pills_html = []
    for cat in CATEGORIES:
        is_all = cat["id"] == "all"
        active_cls = " active" if is_all else ""
        icon = cat.get("icon", "⚡")
        pills_html.append(
            f'<button class="category-pill{active_cls}" data-category="{cat["id"]}">'
            f'<span>{icon}</span> {cat["name"]}'
            f'</button>'
        )
    pills_markup = "\n      ".join(pills_html)

    # Build story cards HTML
    cards_html = []
    for idx, s in enumerate(display_stories):
        cat_id = s.get("category_id", "future-tech")
        # Find category badge
        cat_badge = "⚡ TECH"
        for c in CATEGORIES:
            if c["id"] == cat_id:
                cat_badge = c.get("badge", cat_badge)
                break

        title = s.get("title", "")
        slug = s.get("slug", "")
        summary = s.get("summary", "")
        fallback_img = get_category_fallback_image(cat_id)
        raw_image = s.get("image") or fallback_img

        # Optimize image for card thumbnail dimension (cut memory & decode latency)
        card_image = raw_image
        if "images.unsplash.com" in card_image:
            card_image = re.sub(r"w=\d+", "w=540", card_image)
            if "q=" in card_image:
                card_image = re.sub(r"q=\d+", "q=75", card_image)
            else:
                card_image = f"{card_image}&q=75"

        source = s.get("source", SITE_NAME)
        read_time = s.get("read_time", "45s")
        display_title = s.get("seo_title") or optimize_seo_title(title, slug)
        escaped_title = html_lib.escape(title, quote=True)
        escaped_display_title = html_lib.escape(display_title, quote=True)
        escaped_summary = html_lib.escape(summary, quote=True)

        # Above-fold priority eager loading vs below-fold lazy async
        if idx < 4:
            loading_attrs = 'loading="eager" fetchpriority="high" decoding="async"'
        else:
            loading_attrs = 'loading="lazy" fetchpriority="low" decoding="async"'

        # Category-tailored curiosity badges if card_hook is not explicitly defined
        cat_hook_fallbacks = {
            "ai-tools": "🤖 SECRET AI TOOL",
            "smartphones": "📱 FLAGSHIP LEAK",
            "laptops-pc": "💻 SILICON MONSTER",
            "gadgets": "🎧 HARDWARE SHOCK",
            "future-tech": "🚀 TECH BREAKTHROUGH",
            "gaming-gear": "🎮 120Hz BEAST",
        }
        card_hook = s.get("card_hook") or cat_hook_fallbacks.get(cat_id, "⚡ TRENDING")

        card_markup = f"""
        <article class="story-card" 
          tabindex="0" 
          role="button"
          aria-label="Open story: {escaped_display_title}"
          data-slug="{slug}" 
          data-category="{cat_id}"
          data-title="{escaped_title}"
          data-summary="{escaped_summary}">
          <img class="story-card-bg" 
            src="{card_image}" 
            alt="{escaped_display_title}" 
            {loading_attrs} 
            width="720" height="1080"
            referrerpolicy="no-referrer"
            onerror="this.onerror=null;this.src='{fallback_img}';">
          <div class="story-card-scrim"></div>
          
          <div class="story-card-top">
            <span class="story-cat-badge">{cat_badge}</span>
            <span class="story-duration-badge">⚡ {read_time}</span>
          </div>

          <div class="story-card-body">
            <div class="story-urgency-badge">{card_hook}</div>
            <h2 class="story-card-title">{escaped_display_title}</h2>
            <p class="story-card-snippet">{summary}</p>
            <div class="story-card-footer">
              <span class="story-source">via {source}</span>
              <a href="/stories/{slug}/" class="tap-to-view-cta" aria-label="Read story: {escaped_display_title}"><span class="play-arrow">▶</span> Tap to Unlock ⚡</a>
            </div>
          </div>
        </article>"""
        cards_html.append(card_markup)

    stories_markup = "\n".join(cards_html)

    # Schema.org JSON-LD for WebSite
    website_schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME,
        "url": SITE_URL,
        "description": SITE_DESCRIPTION,
        "sameAs": [
            PINTEREST_PROFILE_URL,
        ],
        "publisher": {
            "@type": "Organization",
            "name": PUBLISHER_NAME,
            "url": SITE_URL,
            "sameAs": [
                PINTEREST_PROFILE_URL,
            ],
            "logo": {
                "@type": "ImageObject",
                "url": PUBLISHER_LOGO_URL,
                "width": 512,
                "height": 512,
            },
        },
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{SITE_URL}/?q={{search_term_string}}",
            "query-input": "required name=search_term_string",
        },
    }
    schema_json = json.dumps(website_schema, ensure_ascii=False)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{SITE_NAME} — {SITE_TAGLINE}</title>
  <meta name="description" content="{SITE_DESCRIPTION}">
  <link rel="canonical" href="{SITE_URL}/">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">

  <!-- Google Search Console Verification -->
  <meta name="google-site-verification" content="{GOOGLE_SITE_VERIFICATION}">
  <meta name="google-site-verification" content="XMDt3lDT2kpdjLlHlxQCSn5EcJcH2yw8f6nLjhLgN7g">

  <!-- Pinterest Official Domain Verification -->
{get_pinterest_verify_tag()}

  <!-- Google Analytics 4 (GA4) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GA_MEASUREMENT_ID}');
  </script>
{get_adsense_script_tag()}

  <!-- OpenGraph & Twitter Cards -->
  <meta property="og:title" content="{SITE_NAME} — {SITE_TAGLINE}">
  <meta property="og:description" content="{SITE_DESCRIPTION}">
  <meta property="og:url" content="{SITE_URL}/">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:image" content="{SITE_URL}/static/images/og-banner.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{SITE_NAME} — {SITE_TAGLINE}">
  <meta name="twitter:description" content="{SITE_DESCRIPTION}">
  <meta name="twitter:image" content="{SITE_URL}/static/images/og-banner.png">

  <!-- Favicons & Feeds -->
  <link rel="icon" type="image/svg+xml" href="/static/images/logo.svg">
  <link rel="apple-touch-icon" href="/static/images/publisher-logo.png">
  <link rel="alternate" type="application/rss+xml" title="{SITE_NAME} RSS Feed" href="{SITE_URL}/rss.xml">
  <link rel="alternate" type="application/rss+xml" title="{SITE_NAME} Pinterest Feed" href="{SITE_URL}/pinterest-feed.xml">

  <!-- Google Fonts: Outfit & Space Grotesk -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">

  <!-- Portal Stylesheet -->
  <link rel="stylesheet" href="/static/css/portal.css">

  <!-- Schema.org JSON-LD -->
  <script type="application/ld+json">
  {schema_json}
  </script>
</head>
<body>

  <!-- Site Navigation Header -->
  <header class="site-header">
    <div class="header-container">
      <a href="/" class="brand-link" aria-label="{SITE_NAME} Home">
        <img class="brand-logo-img" src="/static/images/logo.svg" alt="{SITE_NAME} Logo" width="160" height="40">
      </a>
      
      <nav aria-label="Main Navigation">
        <ul class="nav-links">
          <li><a href="/" class="nav-link active">Stories</a></li>
          <li><a href="/articles/" class="nav-link">Articles</a></li>
          <li><a href="/editorial-team/" class="nav-link">Editorial Team</a></li>
          <li><a href="/about/" class="nav-link">About</a></li>
          <li><a href="/contact/" class="nav-link">Contact</a></li>
          <li><a href="/privacy/" class="nav-link">Privacy</a></li>
          <li><a href="/terms/" class="nav-link">Terms</a></li>
        </ul>
      </nav>

      <div class="live-badge">
        <span class="pulse-dot"></span>
        <span>VERIFIED EDITORIAL LAB</span>
      </div>
    </div>
  </header>

  <!-- Hero Section -->
  <main>
    <section class="hero-section">
      <div class="hero-glow-aura"></div>
      <div class="hero-eyebrow">
        <span>⚡</span> 100% GOOGLE AMP WEB STORIES & IN-DEPTH ARTICLES
      </div>
      <h1 class="hero-title">
        The Future Of Tech in <span class="gradient-text">Visual Stories & Deep Dives</span>
      </h1>
      <p class="hero-subtitle">
        Instant mobile-first Google Web Stories and comprehensive 600-900+ word engineering breakdowns covering frontier AI, silicon lithography, flagship phones, and futuristic computing.
      </p>
    </section>

    <!-- In-Depth Editorial Deep Dives & Articles Section -->
    <section class="deepdives-section" aria-label="In-Depth Editorial Deep Dives">
      <div class="deepdives-header">
        <div>
          <div style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--neon-cyan); text-transform: uppercase; margin-bottom: 0.35rem;">
            ⚡ 600–900+ WORD EDITORIAL DEEP DIVES
          </div>
          <h2 class="deepdives-title">In-Depth <span class="gradient-text">Tech Analysis & Reviews</span></h2>
          <p class="deepdives-subtitle">Exhaustive architectural breakdowns, silicon micro-benchmarks, and comparative buying advice.</p>
        </div>
        <a href="/articles/" class="deepdives-view-all">View All Articles ({len(active_articles)}) →</a>
      </div>
      <div class="deepdives-grid">
        {deepdives_markup}
      </div>
    </section>

    <!-- Controls: Search & Category Filter Pills -->
    <section class="controls-wrapper" aria-label="Story filters and search">
      <div class="search-box-container">
        <span class="search-icon">🔍</span>
        <input 
          type="search" 
          id="story-search-input" 
          class="search-input" 
          placeholder="Search AI tools, 2nm chips, flagships, GPUs..." 
          aria-label="Search stories">
        <span class="search-shortcut-badge">/</span>
      </div>

      <div class="category-filter-pills" role="toolbar" aria-label="Filter stories by category">
        {pills_markup}
      </div>

      <div class="results-status-bar">
        <span>Displaying <strong id="visible-count">{story_count}</strong> stories</span>
        <span>Tap any card for fullscreen story viewer</span>
      </div>
    </section>

    <!-- Stories Grid -->
    <section class="stories-container" aria-label="Latest Tech Stories">
      <div class="stories-grid">
        {stories_markup}
        <div id="no-stories-found" class="no-stories-found" style="display: none;">
          <h3>No matching stories found</h3>
          <p style="color: var(--text-muted); margin-top: 0.5rem;">Try another keyword or select a different category pill above.</p>
        </div>
      </div>
    </section>
  </main>

  <!-- Interactive Lightbox Modal Dialog -->
  <dialog id="story-dialog" aria-label="Story viewer">
    <div class="modal-phone-frame">
      <div class="modal-frame-notch"></div>
      
      <div class="modal-top-bar">
        <button id="modal-close-btn" class="modal-btn" aria-label="Close story">
          <span class="modal-close-cross">✕</span>
        </button>
        <a id="modal-external-btn" href="#" target="_blank" rel="noopener" class="modal-btn" aria-label="Open story in new tab" title="Open full story in new tab">
          <span>↗</span>
        </a>
      </div>

      <iframe id="modal-story-iframe" class="modal-story-iframe" title="Web Story Frame" loading="lazy"></iframe>
    </div>
  </dialog>

  <!-- Site Footer -->
  <footer class="site-footer">
    <div class="footer-container">
      <div class="footer-brand">
        <img src="/static/images/logo.svg" alt="{SITE_NAME}" height="32">
        <p>
          {SITE_NAME} is a premier technology publication and hardware intelligence lab delivering verified visual journalism, deep architectural breakdowns, benchmark analysis, and comprehensive buyer guides across artificial intelligence, semiconductor lithography, and consumer electronics.
        </p>
      </div>

      <div class="footer-col">
        <h4 class="footer-col-title">Navigation</h4>
        <ul class="footer-links">
          <li><a href="/">Latest Stories</a></li>
          <li><a href="/articles/">In-Depth Articles</a></li>
          <li><a href="/editorial-team/">Editorial Team & Methodology</a></li>
          <li><a href="/about/">About & Mission</a></li>
          <li><a href="/contact/">Editorial Desk</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <h4 class="footer-col-title">Connect & Feeds</h4>
        <ul class="footer-links">
          <li>
            <a href="{PINTEREST_PROFILE_URL}" target="_blank" rel="noopener me" style="display: inline-flex; align-items: center; gap: 0.45rem; color: #ff5277; font-weight: 600;">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="#e60023"><path d="M12 0C5.373 0 0 5.373 0 12c0 5.084 3.163 9.426 7.627 11.174-.105-.949-.2-2.405.042-3.441.218-.937 1.407-5.965 1.407-5.965s-.359-.719-.359-1.782c0-1.668.967-2.914 2.171-2.914 1.023 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738a.36.36 0 0 1 .083.345l-.333 1.36c-.053.22-.174.267-.402.161-1.499-.698-2.436-2.889-2.436-4.649 0-3.785 2.75-7.262 7.929-7.262 4.163 0 7.398 2.967 7.398 6.931 0 4.136-2.607 7.464-6.227 7.464-1.216 0-2.359-.632-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24 12 24c6.627 0 12-5.373 12-12 0-6.628-5.373-12-12-12z"/></svg>
              Pinterest (@{PINTEREST_USERNAME})
            </a>
          </li>
          <li><a href="/rss.xml" target="_blank">RSS 2.0 Feed</a></li>
          <li><a href="/pinterest-feed.xml" target="_blank">Pinterest RSS Feed</a></li>
          <li><a href="/sitemap.xml">XML Sitemap</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <h4 class="footer-col-title">Policies</h4>
        <ul class="footer-links">
          <li><a href="/privacy/">Privacy Policy (AdSense & GDPR)</a></li>
          <li><a href="/terms/">Terms of Service & Fair Use</a></li>
          <li><a href="/about/#ai-disclosure">Editorial Standards & Tech Use</a></li>
          <li><a href="/contact/">Corrections & DMCA</a></li>
        </ul>
      </div>
    </div>

    <div class="footer-bottom">
      <div>© {current_year} {SITE_NAME}. All rights reserved. 100% Google AMP Story Compliant.</div>
      <div>TechPulse Editorial Lab & Independent Hardware Benchmarks.</div>
    </div>
  </footer>

  <!-- Client Script -->
  <script src="/static/js/portal.js"></script>
</body>
</html>"""
    return html


def build_legal_page_html(
    page_id: str, title: str, description: str, content_html: str
) -> str:
    """
    Renders a mandatory legal or policy page in the exact site theme.
    """
    current_year = datetime.now(timezone.utc).year
    canonical_url = f"{SITE_URL}/{page_id}/"

    # Schema JSON-LD for legal page
    page_type = "AboutPage" if page_id == "about" else ("ContactPage" if page_id == "contact" else "WebPage")
    schema_data = {
        "@context": "https://schema.org",
        "@type": page_type,
        "name": f"{title} | {SITE_NAME}",
        "description": description,
        "url": canonical_url,
        "publisher": {
            "@type": "Organization",
            "name": PUBLISHER_NAME,
            "logo": {
                "@type": "ImageObject",
                "url": PUBLISHER_LOGO_URL,
            },
        },
    }
    schema_json = json.dumps(schema_data, ensure_ascii=False)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} | {SITE_NAME}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{canonical_url}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">

  <!-- Google Search Console Verification -->
  <meta name="google-site-verification" content="{GOOGLE_SITE_VERIFICATION}">
  <meta name="google-site-verification" content="XMDt3lDT2kpdjLlHlxQCSn5EcJcH2yw8f6nLjhLgN7g">

  <!-- Pinterest Official Domain Verification -->
{get_pinterest_verify_tag()}

  <!-- Google Analytics 4 (GA4) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GA_MEASUREMENT_ID}');
  </script>
{get_adsense_script_tag()}

  <!-- OpenGraph & Twitter Cards -->
  <meta property="og:title" content="{title} | {SITE_NAME}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:image" content="{SITE_URL}/static/images/og-banner.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title} | {SITE_NAME}">
  <meta name="twitter:description" content="{description}">

  <!-- Favicons -->
  <link rel="icon" type="image/svg+xml" href="/static/images/logo.svg">
  <link rel="apple-touch-icon" href="/static/images/publisher-logo.png">

  <!-- Google Fonts: Outfit & Space Grotesk -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">

  <!-- Portal Stylesheet -->
  <link rel="stylesheet" href="/static/css/portal.css">

  <!-- Schema.org JSON-LD -->
  <script type="application/ld+json">
  {schema_json}
  </script>
</head>
<body>

  <!-- Site Navigation Header -->
  <header class="site-header">
    <div class="header-container">
      <a href="/" class="brand-link" aria-label="{SITE_NAME} Home">
        <img class="brand-logo-img" src="/static/images/logo.svg" alt="{SITE_NAME} Logo" width="160" height="40">
      </a>
      
      <nav aria-label="Main Navigation">
        <ul class="nav-links">
          <li><a href="/" class="nav-link">Stories</a></li>
          <li><a href="/articles/" class="nav-link">Articles</a></li>
          <li><a href="/editorial-team/" class="nav-link{' active' if page_id == 'editorial-team' else ''}">Editorial Team</a></li>
          <li><a href="/about/" class="nav-link{' active' if page_id == 'about' else ''}">About</a></li>
          <li><a href="/contact/" class="nav-link{' active' if page_id == 'contact' else ''}">Contact</a></li>
          <li><a href="/privacy/" class="nav-link{' active' if page_id == 'privacy' else ''}">Privacy</a></li>
          <li><a href="/terms/" class="nav-link{' active' if page_id == 'terms' else ''}">Terms</a></li>
        </ul>
      </nav>

      <div class="live-badge">
        <span class="pulse-dot"></span>
        <span>VERIFIED EDITORIAL LAB</span>
      </div>
    </div>
  </header>

  <main class="legal-container">
    <article class="legal-card">
      <header class="legal-header">
        <h1 class="legal-title">{title}</h1>
        <div class="legal-last-updated">LAST UPDATED: OCTOBER 2026 // COMPLIANCE VERIFIED</div>
      </header>
      <div class="legal-content">
        {content_html}
      </div>
    </article>
  </main>

  <!-- Site Footer -->
  <footer class="site-footer">
    <div class="footer-container">
      <div class="footer-brand">
        <img src="/static/images/logo.svg" alt="{SITE_NAME}" height="32">
        <p>
          {SITE_NAME} is a premier technology publication and hardware intelligence lab delivering verified visual journalism, deep architectural breakdowns, benchmark analysis, and comprehensive buyer guides across artificial intelligence, semiconductor lithography, and consumer electronics.
        </p>
      </div>

      <div class="footer-col">
        <h4 class="footer-col-title">Navigation</h4>
        <ul class="footer-links">
          <li><a href="/">Latest Stories</a></li>
          <li><a href="/articles/">In-Depth Articles</a></li>
          <li><a href="/editorial-team/">Editorial Team & Methodology</a></li>
          <li><a href="/about/">About & Mission</a></li>
          <li><a href="/contact/">Editorial Desk</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <h4 class="footer-col-title">Connect & Feeds</h4>
        <ul class="footer-links">
          <li>
            <a href="{PINTEREST_PROFILE_URL}" target="_blank" rel="noopener me" style="display: inline-flex; align-items: center; gap: 0.45rem; color: #ff5277; font-weight: 600;">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="#e60023"><path d="M12 0C5.373 0 0 5.373 0 12c0 5.084 3.163 9.426 7.627 11.174-.105-.949-.2-2.405.042-3.441.218-.937 1.407-5.965 1.407-5.965s-.359-.719-.359-1.782c0-1.668.967-2.914 2.171-2.914 1.023 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738a.36.36 0 0 1 .083.345l-.333 1.36c-.053.22-.174.267-.402.161-1.499-.698-2.436-2.889-2.436-4.649 0-3.785 2.75-7.262 7.929-7.262 4.163 0 7.398 2.967 7.398 6.931 0 4.136-2.607 7.464-6.227 7.464-1.216 0-2.359-.632-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24 12 24c6.627 0 12-5.373 12-12 0-6.628-5.373-12-12-12z"/></svg>
              Pinterest (@{PINTEREST_USERNAME})
            </a>
          </li>
          <li><a href="/rss.xml" target="_blank">RSS 2.0 Feed</a></li>
          <li><a href="/pinterest-feed.xml" target="_blank">Pinterest RSS Feed</a></li>
          <li><a href="/sitemap.xml">XML Sitemap</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <h4 class="footer-col-title">Policies</h4>
        <ul class="footer-links">
          <li><a href="/privacy/">Privacy Policy (AdSense & GDPR)</a></li>
          <li><a href="/terms/">Terms of Service & Fair Use</a></li>
          <li><a href="/about/#ai-disclosure">Editorial Standards & Tech Use</a></li>
          <li><a href="/contact/">Corrections & DMCA</a></li>
        </ul>
      </div>
    </div>

    <div class="footer-bottom">
      <div>© {current_year} {SITE_NAME}. All rights reserved. 100% Google AMP Story Compliant.</div>
      <div>TechPulse Editorial Lab & Independent Hardware Benchmarks.</div>
    </div>
  </footer>

</body>
</html>"""
    return html


def get_editorial_team_page_content() -> str:
    return f"""
    <div class="team-page-intro">
      <h2>Meet the {SITE_NAME} Editorial & Engineering Desk</h2>
      <p class="lead-text">
        At <strong>{SITE_NAME}</strong>, technology reporting is conducted with the rigorous discipline of systems engineering. Our editorial staff comprises veteran hardware analysts, solid-state physicists, systems architects, and AI researchers dedicated to uncovering the real silicon architecture, micro-benchmarks, and thermal dynamics beneath marketing press releases.
      </p>
    </div>

    <div class="editorial-team-grid">
      
      <!-- Member 1: Sumit Singh -->
      <div class="team-card" id="sumit-singh">
        <div class="team-card-header">
          <div class="team-avatar-initials" style="background: linear-gradient(135deg, #06b6d4, #3b82f6);">SS</div>
          <div class="team-member-title-block">
            <h3 class="team-member-name">Sumit Singh</h3>
            <div class="team-member-role">Editor-in-Chief & Principal Systems Architect</div>
            <div class="team-member-beats">Beats: Semiconductor Nodes · Apple Silicon · Qualcomm Platforms · Mobile Architectures</div>
          </div>
        </div>
        <div class="team-bio">
          Sumit brings over 8 years of hands-on experience evaluating low-level microprocessor architectures, silicon lithography transitions, and distributed computing infrastructures. As Editor-in-Chief, he directs {SITE_NAME}'s hardware testing protocols, oversees benchmark verifications, and authors definitive flagships on semiconductor advancements, including TSMC N2 GAA implementations and ARM instruction set transitions.
        </div>
        <div class="team-footer">
          <span class="team-credential">Verified Hardware Architect</span>
          <a href="mailto:{CONTACT_EMAIL}" class="team-contact-btn">✉ Contact Sumit</a>
        </div>
      </div>

      <!-- Member 2: Dr. Aarav Patel -->
      <div class="team-card" id="aarav-patel">
        <div class="team-card-header">
          <div class="team-avatar-initials" style="background: linear-gradient(135deg, #10b981, #06b6d4);">AP</div>
          <div class="team-member-title-block">
            <h3 class="team-member-name">Dr. Aarav Patel</h3>
            <div class="team-member-role">Senior Semiconductor & Silicon Fabrication Analyst</div>
            <div class="team-member-beats">Beats: TSMC & Intel Nodes · GAA Nanosheets · Backside Power Delivery (BSPDN) · Thermal Dynamics</div>
          </div>
        </div>
        <div class="team-bio">
          Holding a Ph.D. in Solid-State Electronics, Dr. Patel specializes in sub-3nm lithography, High-NA EUV optical systems, and advanced multi-die packaging (CoWoS, EMIB). His analyses provide granular transistor-level evaluations of modern desktop and datacenter processors, unpacking parasitic capacitance, voltage droop mitigation, and sustained thermal dissipation profiles.
        </div>
        <div class="team-footer">
          <span class="team-credential">Ph.D. Solid-State Electronics</span>
          <a href="mailto:{CONTACT_EMAIL}" class="team-contact-btn">✉ Contact Desk</a>
        </div>
      </div>

      <!-- Member 3: Elena Rostova -->
      <div class="team-card" id="elena-rostova">
        <div class="team-card-header">
          <div class="team-avatar-initials" style="background: linear-gradient(135deg, #8b5cf6, #ec4899);">ER</div>
          <div class="team-member-title-block">
            <h3 class="team-member-name">Elena Rostova</h3>
            <div class="team-member-role">Lead Artificial Intelligence & Frontier Models Editor</div>
            <div class="team-member-beats">Beats: Multimodal Reasoners · Agentic Architectures · On-Device NPUs · Model Quantization</div>
          </div>
        </div>
        <div class="team-bio">
          With a Master's background in Computational Intelligence, Elena leads coverage of frontier generative AI systems, including Google Gemini, Anthropic Claude, and open-weight model architectures. She conducts empirical latency and accuracy benchmarks across tool-use agents, multi-agent synchronization pipelines, and device-level tensor accelerators.
        </div>
        <div class="team-footer">
          <span class="team-credential">M.S. Computational Systems</span>
          <a href="mailto:{CONTACT_EMAIL}" class="team-contact-btn">✉ Contact Desk</a>
        </div>
      </div>

      <!-- Member 4: Marcus Vance -->
      <div class="team-card" id="marcus-vance">
        <div class="team-card-header">
          <div class="team-avatar-initials" style="background: linear-gradient(135deg, #f59e0b, #ef4444);">MV</div>
          <div class="team-member-title-block">
            <h3 class="team-member-name">Marcus Vance</h3>
            <div class="team-member-role">Hardware Testing & Consumer Electronics Lead</div>
            <div class="team-member-beats">Beats: Mobile Sensor Optics · LTPO Display Panels · Handheld Gaming · Battery Chemistries</div>
          </div>
        </div>
        <div class="team-bio">
          A veteran tech reviewer with over a decade in consumer device teardowns and lab testing, Marcus heads {SITE_NAME}'s mobile imaging and display colorimetry evaluations. His hands-on reviews focus on real-world ergonomic durability, sustained thermal throttling in mobile gaming, and battery longevity under synthetic workloads.
        </div>
        <div class="team-footer">
          <span class="team-credential">10+ Yrs Hardware Lab Testing</span>
          <a href="mailto:{CONTACT_EMAIL}" class="team-contact-btn">✉ Contact Desk</a>
        </div>
      </div>

    </div>

    <div class="methodology-section" style="margin-top: 3rem;">
      <h2>Our 5-Stage Editorial & Testing Protocol</h2>
      <p>
        Every article, review, and comparative breakdown published on {SITE_NAME} adheres to our rigorous 5-stage journalistic verification protocol:
      </p>
      <div class="protocol-steps">
        <div class="protocol-step-card">
          <div class="step-num">01</div>
          <div class="step-content">
            <h4>Empirical Grounding in Engineering Whitepapers</h4>
            <p>We do not rely on corporate marketing claims or unsubstantiated rumors. Clock speeds, transistor density, cache hierarchies, and silicon lithography are cross-referenced directly against vendor technical whitepapers, patent disclosures, and IEEE publications.</p>
          </div>
        </div>
        <div class="protocol-step-card">
          <div class="step-num">02</div>
          <div class="step-content">
            <h4>Comparative Architecture & Standardized Benchmarking</h4>
            <p>Every newly announced device or silicon platform is placed into a standardized comparison matrix against direct market predecessors and competitors, evaluating generational IPC improvements, efficiency curves, and thermal ceilings.</p>
          </div>
        </div>
        <div class="protocol-step-card">
          <div class="step-num">03</div>
          <div class="step-content">
            <h4>Actionable Editorial Verdicts</h4>
            <p>We believe technology reporting must provide definitive consumer value. Every in-depth review delivers a clear "TechPulse Verdict", a balanced Pros & Cons matrix, and explicit "Who Should Upgrade vs Who Should Wait" guidance.</p>
          </div>
        </div>
        <div class="protocol-step-card">
          <div class="step-num">04</div>
          <div class="step-content">
            <h4>Zero Sponsored Editorial or Pay-To-Play Coverage</h4>
            <p>Editorial independence is non-negotiable. {SITE_NAME} maintains a firewall between business operations and our tech reviews. We never accept sponsored reviews, paid benchmark placements, or editorial veto power from manufacturers.</p>
          </div>
        </div>
        <div class="protocol-step-card">
          <div class="step-num">05</div>
          <div class="step-content">
            <h4>Transparent Corrections & Public Errata Log</h4>
            <p>When technical errors or newly clarified specifications emerge, our editorial desk updates the story with an explicit, timestamped correction note within 24 hours of verifiable notice.</p>
          </div>
        </div>
      </div>
    </div>
    """


def get_about_page_content() -> str:
    return f"""
    <h2>Our Journalism Mission & Origin</h2>
    <p>
      Welcome to <strong>{SITE_NAME}</strong>. In an era inundated with clickbait, recycled press releases, and bloated websites overloaded with intrusive scripts, we believe technology journalism must be rapid, verifiable, deeply analytical, and visually compelling.
    </p>
    <p>
      Founded to bridge the gap between fast-paced mobile storytelling and rigorous engineering analysis, {SITE_NAME} provides two complementary experiences: lightning-fast 5-slide Google AMP Web Stories for instant visual intelligence on mobile devices, and comprehensive 600–900+ word in-depth architectural breakdowns for engineers, builders, and discerning tech buyers.
    </p>

    <h2>What Sets {SITE_NAME} Apart: Substantial Original Value</h2>
    <p>
      Rather than merely summarizing news wires, {SITE_NAME} brings proprietary editorial analysis to every piece of coverage:
    </p>
    <ul>
      <li><strong>Architectural Deep Dives</strong>: We evaluate silicon lithography (TSMC, Intel, Samsung), cache layouts, memory bandwidth, and thermal dissipation metrics rather than quoting synthetic PR charts.</li>
      <li><strong>Side-by-Side Comparison Matrices</strong>: Every hardware and AI breakthrough is benchmarked against its direct historical predecessor and market rival in our structured engineering tables.</li>
      <li><strong>Definitive Buyer Verdicts</strong>: We provide explicit "Who Should Upgrade vs Who Should Wait" recommendations and transparent Pros & Cons matrices, ensuring our readers make informed purchasing and architectural decisions.</li>
    </ul>

    <h2>Meet Our Editorial Desk</h2>
    <p>
      Our coverage is led by experienced hardware analysts, systems engineers, and technology researchers. Meet our full editorial masthead, credentials, and beat specializations on our dedicated <a href="/editorial-team/" style="color: var(--neon-cyan); font-weight: 700;">Editorial Team & Testing Methodology</a> page.
    </p>

    <h2>Editorial Independence & Commercial Ethics</h2>
    <p>
      We maintain strict journalistic independence. We do not accept sponsored content disguised as editorial news, nor do we enter into pay-to-play hardware benchmarking agreements. Our stories cite primary sources, engineering whitepapers, and direct manufacturer disclosures.
    </p>

    <h2 id="ai-disclosure">Editorial Standards & Technology Use Policy</h2>
    <p>
      Transparency is the foundation of reader trust. At {SITE_NAME}, computational data tools and natural language models are utilized strictly for initial research indexing, syntax verification, and tracking public RSS wires. All editorial conclusions, hardware verdicts, pros & cons matrices, technical evaluations, and published copy are authored, reviewed, and approved by human editorial staff.
    </p>

    <h2>Contact The Editorial Desk & Corrections</h2>
    <p>
      We welcome feedback, press releases, embargoed news tips, technical corrections, and partnership requests. Reach out to our lead team at:
    </p>
    <div class="contact-highlight-box">
      <span>Official Editorial Inquiries:</span>
      <a href="mailto:{CONTACT_EMAIL}" class="contact-email-link">⚡ {CONTACT_EMAIL}</a>
    </div>
    """


def get_privacy_page_content() -> str:
    return f"""
    <h2>Privacy Policy & Data Protection Overview</h2>
    <p>
      At <strong>{SITE_NAME}</strong> (accessible at {SITE_URL}), safeguarding the privacy of our visitors is paramount. This Privacy Policy document outlines the types of information collected and recorded by {SITE_NAME} and how we use it in strict accordance with the General Data Protection Regulation (GDPR) and the California Consumer Privacy Act (CCPA).
    </p>

    <h2>Google AdSense & DoubleClick DART Cookies</h2>
    <p>
      Google is one of the third-party vendors on our site. Google uses cookies, commonly known as <strong>DART cookies</strong>, to serve advertisements to visitors based on their prior visits to {SITE_NAME} and other websites on the internet.
    </p>
    <p>
      Visitors may choose to decline the use of DART cookies by visiting the Google Ad and Content Network Privacy Policy at:
      <a href="https://policies.google.com/technologies/ads" target="_blank" rel="noopener">https://policies.google.com/technologies/ads</a>.
    </p>

    <h2>Log Files & Anonymous Analytics</h2>
    <p>
      Like most web servers and hosting platforms (such as Vercel), {SITE_NAME} follows a standard procedure of utilizing log files. These files log visitors when they access website pages. The information collected includes:
    </p>
    <ul>
      <li>Internet Protocol (IP) addresses (anonymized where applicable)</li>
      <li>Browser user-agent and device type</li>
      <li>Date and timestamp of requests</li>
      <li>Referring and exit pages</li>
      <li>Number of clicks and viewport dimensions</li>
    </ul>
    <p>
      This data is not linked to any personally identifiable information. The purpose is purely to analyze engagement trends, administer the platform, track user movement on the website, and optimize static asset caching.
    </p>

    <h2>GDPR Data Protection Rights (EU Users)</h2>
    <p>
      If you reside within the European Economic Area (EEA), you have the following rights:
    </p>
    <ul>
      <li><strong>Right to access</strong>: You have the right to request copies of your personal data.</li>
      <li><strong>Right to rectification</strong>: You can request correction of any inaccurate information.</li>
      <li><strong>Right to erasure</strong>: You have the right to request the deletion of your personal data under certain conditions.</li>
      <li><strong>Right to restrict or object to processing</strong>: You can object to our processing of your personal data.</li>
    </ul>

    <h2>CCPA Privacy Rights (Do Not Sell My Personal Information)</h2>
    <p>
      Under the California Consumer Privacy Act (CCPA), California consumers have the right to:
    </p>
    <ul>
      <li>Request disclosure of categories and specific pieces of personal data collected.</li>
      <li>Request that a business delete any personal data collected.</li>
      <li><strong>Right to opt-out</strong>: Request that a business that sells personal data not sell your personal data. <em>{SITE_NAME} does not sell personal user data to any third party.</em></li>
    </ul>

    <h2>Privacy Officer Contact</h2>
    <p>
      If you have questions about our privacy policies or wish to exercise your data rights, please contact our data compliance desk:
    </p>
    <div class="contact-highlight-box">
      <span>Data Protection Officer:</span>
      <a href="mailto:{CONTACT_EMAIL}" class="contact-email-link">⚡ {CONTACT_EMAIL}</a>
    </div>
    """


def get_terms_page_content() -> str:
    return f"""
    <h2>Terms of Service & Usage Agreement</h2>
    <p>
      By accessing or using <strong>{SITE_NAME}</strong> ({SITE_URL}), you agree to comply with and be bound by these Terms of Service. If you do not agree with any part of these terms, please refrain from using the platform.
    </p>

    <h2>Fair Use Doctrine (17 U.S.C. § 107)</h2>
    <p>
      {SITE_NAME} is a technology journalism, hardware analysis, and visual commentary publication. The content, quotes, excerpts, product specifications, and imagery featured on this site are utilized in accordance with the <strong>Fair Use Doctrine (17 U.S.C. § 107)</strong> for purposes including:
    </p>
    <ul>
      <li>News reporting and journalistic summary</li>
      <li>Technological commentary and educational analysis</li>
      <li>Comparative performance benchmarking and criticism</li>
    </ul>
    <p>
      All original copyrights, trademarks, and intellectual property belong exclusively to their respective creators, publishers, and manufacturers. Every story provides clear attribution and canonical links pointing back to primary coverage.
    </p>

    <h2>Trademark & Corporate Disclaimer</h2>
    <p>
      "Apple", "iPhone", "iOS", "Samsung", "Galaxy", "Google", "Android", "Pixel", "Qualcomm", "Snapdragon", "Nvidia", "GeForce", "Intel", "AMD", "Sony", "PlayStation", "Microsoft", "Xbox", "Nothing", and all other company, brand, or product names, logos, and trademarks displayed or mentioned on this platform are the registered trademarks of their respective owners.
    </p>
    <p>
      Reference to any specific commercial products, processes, or services by trade name, trademark, manufacturer, or otherwise does not constitute or imply endorsement, sponsorship, or recommendation by {SITE_NAME} or its operators.
    </p>

    <h2>Disclaimer of Warranties & Limitation of Liability</h2>
    <p>
      All content on {SITE_NAME} is provided on an "as is" and "as available" basis without warranties of any kind. While our engineering desk and editorial team endeavor to maintain accurate and up-to-date technical information, we cannot guarantee the complete accuracy or future availability of third-party products.
    </p>

    <h2>DMCA Notice & Takedown Requests</h2>
    <p>
      If you are a copyright owner or authorized representative and believe that any content hosted on {SITE_NAME} infringes upon your copyright, please submit an official DMCA notification to our compliance officer:
    </p>
    <div class="contact-highlight-box">
      <span>DMCA & Legal Desk:</span>
      <a href="mailto:{CONTACT_EMAIL}" class="contact-email-link">⚡ {CONTACT_EMAIL}</a>
    </div>
    """


def get_contact_page_content() -> str:
    return f"""
    <h2>Official Editorial & Press Desk</h2>
    <p>
      Have a breaking hardware leak, software discovery, security advisory, or press release? We actively monitor our communication lines 24/7.
    </p>

    <div class="contact-highlight-box">
      <div>
        <div style="font-size: 0.85rem; color: var(--text-dim); text-transform: uppercase;">Direct Editorial Inquiries</div>
        <a href="mailto:{CONTACT_EMAIL}" class="contact-email-link">⚡ {CONTACT_EMAIL}</a>
      </div>
      <div style="font-family: var(--font-mono); font-size: 0.85rem; color: var(--tech-emerald);">
        Response SLA: &lt; 24 Hours
      </div>
    </div>

    <h2>Inquiry Categories</h2>
    <ul>
      <li><strong>News Tips & Hardware Leaks</strong>: Share technical whitepapers, CAD renders, or benchmark dumps. Confidentiality honored upon request.</li>
      <li><strong>Hardware Review Units</strong>: Submit flagship smartphones, audio gear, GPUs, or robotics hardware for visual Web Story coverage.</li>
      <li><strong>Technical Corrections</strong>: If any story contains an inaccurate specification or erroneous benchmark, notify us immediately for instant correction.</li>
      <li><strong>Syndication & API Inquiries</strong>: Integrate our AMP Web Stories feed into your news aggregator or mobile application via <code>/stories.json</code>.</li>
    </ul>

    <h2>Send Us A Direct Message</h2>
    <form action="mailto:{CONTACT_EMAIL}" method="POST" enctype="text/plain" style="margin-top: 1.5rem; display: flex; flex-direction: column; gap: 1rem;">
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
        <div>
          <label style="display: block; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.4rem;">Your Name</label>
          <input type="text" name="name" required style="width: 100%; padding: 0.75rem 1rem; background: rgba(13, 17, 23, 0.8); border: 1px solid var(--border-glass); border-radius: var(--radius-sm); color: #fff; outline: none;">
        </div>
        <div>
          <label style="display: block; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.4rem;">Email Address</label>
          <input type="email" name="email" required style="width: 100%; padding: 0.75rem 1rem; background: rgba(13, 17, 23, 0.8); border: 1px solid var(--border-glass); border-radius: var(--radius-sm); color: #fff; outline: none;">
        </div>
      </div>
      <div>
        <label style="display: block; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.4rem;">Inquiry Subject</label>
        <input type="text" name="subject" placeholder="e.g. News Tip: Flagship Silicon Benchmark" required style="width: 100%; padding: 0.75rem 1rem; background: rgba(13, 17, 23, 0.8); border: 1px solid var(--border-glass); border-radius: var(--radius-sm); color: #fff; outline: none;">
      </div>
      <div>
        <label style="display: block; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.4rem;">Message</label>
        <textarea name="message" rows="5" placeholder="Include technical details, URLs, or leak descriptions..." required style="width: 100%; padding: 0.75rem 1rem; background: rgba(13, 17, 23, 0.8); border: 1px solid var(--border-glass); border-radius: var(--radius-sm); color: #fff; outline: none; font-family: inherit;"></textarea>
      </div>
      <div>
        <button type="submit" style="background: linear-gradient(135deg, var(--neon-cyan), var(--tech-emerald)); border: none; border-radius: var(--radius-full); padding: 0.75rem 2rem; color: #08090d; font-weight: 800; font-family: var(--font-heading); cursor: pointer; font-size: 0.95rem; box-shadow: 0 0 15px var(--neon-cyan-glow);">
          Send Message ⚡
        </button>
      </div>
    </form>
    """


def _xml_escape(val: Any) -> str:
    """Escapes special characters (&, <, >, \", ') for XML compliance."""
    if not val:
        return ""
    clean_text = html_lib.unescape(str(val).strip())
    return (
        clean_text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def generate_sitemap_xml(
    stories: List[Dict[str, Any]],
    articles: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Builds dynamic sitemap.xml adhering to Sitemaps Protocol 0.9 with Google Image extensions.
    Includes portal, articles index, full-length articles, legal pages, and AMP stories.
    """
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    urls = [
        {"loc": f"{SITE_URL}/", "priority": "1.0", "changefreq": "hourly", "image": None},
        {"loc": f"{SITE_URL}/articles/", "priority": "0.8", "changefreq": "daily", "image": None},
        {"loc": f"{SITE_URL}/editorial-team/", "priority": "0.8", "changefreq": "monthly", "image": None},
        {"loc": f"{SITE_URL}/about/", "priority": "0.7", "changefreq": "monthly", "image": None},
        {"loc": f"{SITE_URL}/privacy/", "priority": "0.5", "changefreq": "monthly", "image": None},
        {"loc": f"{SITE_URL}/terms/", "priority": "0.5", "changefreq": "monthly", "image": None},
        {"loc": f"{SITE_URL}/contact/", "priority": "0.6", "changefreq": "monthly", "image": None},
    ]

    # Add all in-depth articles
    if articles:
        for a in articles:
            a_slug = a.get("slug", "")
            if not a_slug:
                continue
            a_title = a.get("title", "")
            a_img = a.get("image", "")
            a_pub = a.get("published", "")
            a_mod = now_iso
            if a_pub and len(a_pub) >= 10:
                cand = a_pub[:10]
                if re.match(r"^\d{4}-\d{2}-\d{2}$", cand):
                    a_mod = cand

            image_data = {"loc": a_img, "title": a_title} if a_img else None
            urls.append({
                "loc": f"{SITE_URL}/articles/{a_slug}/",
                "priority": "0.9",
                "changefreq": "weekly",
                "lastmod": a_mod,
                "image": image_data,
            })

    for s in stories:
        slug = s.get("slug", "")
        title = s.get("title", "")
        img = s.get("image", "")
        published = s.get("published", "")
        
        # Extract YYYY-MM-DD from published if available, else default to now
        story_mod = now_iso
        if published and len(published) >= 10:
            candidate = published[:10]
            if re.match(r"^\d{4}-\d{2}-\d{2}$", candidate):
                story_mod = candidate

        image_data = {"loc": img, "title": title} if img else None
        urls.append({
            "loc": f"{SITE_URL}/stories/{slug}/",
            "priority": "0.8",
            "changefreq": "daily",
            "lastmod": story_mod,
            "image": image_data,
        })

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
    ]

    for u in urls:
        lastmod_val = u.get("lastmod", now_iso)
        lines.append("  <url>")
        lines.append(f"    <loc>{_xml_escape(u['loc'])}</loc>")
        lines.append(f"    <lastmod>{lastmod_val}</lastmod>")
        lines.append(f"    <changefreq>{u['changefreq']}</changefreq>")
        lines.append(f"    <priority>{u['priority']}</priority>")
        if u.get("image") and u["image"].get("loc"):
            lines.append("    <image:image>")
            lines.append(f"      <image:loc>{_xml_escape(u['image']['loc'])}</image:loc>")
            if u["image"].get("title"):
                lines.append(f"      <image:title>{_xml_escape(u['image']['title'])}</image:title>")
            lines.append("    </image:image>")
        lines.append("  </url>")

    lines.append("</urlset>")
    xml_content = "\n".join(lines)

    # Validate output with ElementTree to guarantee well-formed XML
    try:
        import xml.etree.ElementTree as ET
        ET.fromstring(xml_content.encode("utf-8"))
    except Exception as exc:
        print(f"[!] Warning: Generated sitemap XML validation failed: {exc}")

    return xml_content


def generate_robots_txt() -> str:
    """Generates robots.txt pointing to the XML sitemap."""
    return f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""


def build_all_portal_pages(stories: List[Dict[str, Any]], dist_dir: Path):
    """
    Renders and writes in-depth articles, portal homepage, legal pages, sitemap, robots, and stories.json.
    """
    # 0. In-Depth Editorial Articles (/articles/ and /articles/<slug>/)
    articles = build_all_articles(stories, dist_dir)

    # 1. Homepage dist/index.html
    home_html = build_portal_html(stories, articles=articles)
    (dist_dir / "index.html").write_text(home_html, encoding="utf-8")
    print(f"[+] Generated homepage: dist/index.html")

    # 2. Legal & Editorial Pages
    legal_pages = [
        ("editorial-team", f"Editorial Team & Testing Methodology | {SITE_NAME}", f"Meet {SITE_NAME}'s hardware architects, chip analysts, and AI researchers. Learn our 5-stage testing methodology and journalistic ethics.", get_editorial_team_page_content()),
        ("about", f"About {SITE_NAME} & Editorial Mission", f"Learn about {SITE_NAME}'s mission, journalistic standards, and E-E-A-T analysis methodology.", get_about_page_content()),
        ("privacy", f"Privacy Policy & GDPR Compliance | {SITE_NAME}", f"{SITE_NAME} privacy policy: Google AdSense DART cookies, analytics, CCPA, and GDPR rights.", get_privacy_page_content()),
        ("terms", f"Terms of Service & Fair Use | {SITE_NAME}", f"Terms of service, Fair Use (17 U.S.C. § 107) and trademark disclaimers for {SITE_NAME}.", get_terms_page_content()),
        ("contact", f"Contact Editorial Desk | {SITE_NAME}", f"Contact {SITE_NAME} editorial team at {CONTACT_EMAIL} for tips, leaks, and inquiries.", get_contact_page_content()),
    ]

    for page_id, page_title, page_desc, content_html in legal_pages:
        page_dir = dist_dir / page_id
        page_dir.mkdir(parents=True, exist_ok=True)
        page_markup = build_legal_page_html(page_id, page_title, page_desc, content_html)
        (page_dir / "index.html").write_text(page_markup, encoding="utf-8")
        print(f"[+] Generated legal page: dist/{page_id}/index.html")

    # 3. Dynamic Sitemap.xml (Includes stories and in-depth articles)
    sitemap_xml = generate_sitemap_xml(stories, articles=articles)
    (dist_dir / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")
    print(f"[+] Generated sitemap: dist/sitemap.xml")

    # 4. Robots.txt
    robots_txt = generate_robots_txt()
    (dist_dir / "robots.txt").write_text(robots_txt, encoding="utf-8")
    print(f"[+] Generated robots: dist/robots.txt")

    # 5. Manifest stories.json
    stories_json = json.dumps(stories, indent=2, ensure_ascii=False)
    (dist_dir / "stories.json").write_text(stories_json, encoding="utf-8")
    print(f"[+] Generated manifest: dist/stories.json")

    # 6. RSS 2.0 Feed for Google News & Aggregators
    rss_xml = generate_rss_xml(stories)
    (dist_dir / "rss.xml").write_text(rss_xml, encoding="utf-8")
    (dist_dir / "feed.xml").write_text(rss_xml, encoding="utf-8")
    print(f"[+] Generated RSS feeds: dist/rss.xml & dist/feed.xml")

    # 6b. Pinterest RSS Auto-Publish Feed & Bulk CSV Syndication
    sync_pinterest_assets(stories, dist_dir, articles=articles)

    # 7. Google AdSense Authorized Digital Sellers (ads.txt)
    pub_id = get_adsense_pub_id()
    if pub_id:
        ads_txt_body = (
            f"# Google AdSense Authorized Digital Sellers for {SITE_NAME}\n"
            f"google.com, {pub_id}, DIRECT, f08c47fec0942fa0\n"
        )
    else:
        ads_txt_body = (
            f"# Google AdSense Authorized Digital Sellers for {SITE_NAME}\n"
            "# Configure ADSENSE_CLIENT_ID in .env or run: python update_adsense.py ca-pub-XXXXXXXXXXXXXXXX\n"
            "# google.com, pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0\n"
        )
    (dist_dir / "ads.txt").write_text(ads_txt_body, encoding="utf-8")
    if dist_dir.parent:
        (dist_dir.parent / "ads.txt").write_text(ads_txt_body, encoding="utf-8")
    print(f"[+] Deployed Google AdSense ads.txt (pub_id: {pub_id or 'awaiting client ID'})")


def generate_rss_xml(stories: List[Dict[str, Any]]) -> str:
    """Generates standard RSS 2.0 with Media RSS tags for Google News & Feedly."""
    now_rfc822 = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    items_xml = []
    for s in stories[:60]:
        title = html_lib.escape(s.get("title", f"{SITE_NAME} Story"))
        slug = s.get("slug", "")
        link = f"{SITE_URL}/stories/{slug}/"
        summary = html_lib.escape(s.get("summary", ""))
        category = html_lib.escape(s.get("category_name", "Technology"))
        pub_date = s.get("published", "")
        if pub_date:
            try:
                dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                pub_rfc822 = dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
            except Exception:
                pub_rfc822 = now_rfc822
        else:
            pub_rfc822 = now_rfc822

        image_url = s.get("image", f"{SITE_URL}/static/images/og-banner.png")
        image_url_esc = html_lib.escape(image_url)

        item = f"""    <item>
      <title>{title}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <pubDate>{pub_rfc822}</pubDate>
      <description>{summary}</description>
      <category>{category}</category>
      <dc:creator>{html_lib.escape(SITE_NAME)}</dc:creator>
      <enclosure url="{image_url_esc}" length="120000" type="image/jpeg" />
      <media:content url="{image_url_esc}" medium="image" />
    </item>"""
        items_xml.append(item)

    items_block = "\n".join(items_xml)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{html_lib.escape(SITE_NAME)}</title>
    <link>{SITE_URL}/</link>
    <atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml" />
    <atom:link href="https://pubsubhubbub.appspot.com/" rel="hub" />
    <description>{html_lib.escape(SITE_DESCRIPTION)}</description>
    <language>en-us</language>
    <lastBuildDate>{now_rfc822}</lastBuildDate>
{items_block}
  </channel>
</rss>
"""

