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
from article_builder import build_all_articles, FLAGSHIP_ARTICLES, resolve_article_author
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
    sorted_stories = list(stories)

    # For homepage visual stories shelf, display up to 12 curated companion stories
    display_limit = max_cards if max_cards is not None else 12
    display_stories = sorted_stories[:display_limit]
    story_count = len(display_stories)
    current_year = datetime.now(timezone.utc).year

    # 1. Lead Featured Article Showcase
    lead_article = active_articles[0] if active_articles else None
    lead_feature_markup = ""
    if lead_article:
        lead_slug = lead_article.get("slug", "")
        lead_title = html_lib.escape(lead_article.get("title", ""))
        lead_sub = html_lib.escape(lead_article.get("subtitle", ""))
        lead_cat = lead_article.get("category_id", "gaming-gear")
        lead_thumb = lead_article.get("image") or get_category_fallback_image(lead_cat)
        lead_time = lead_article.get("read_time", "8 min read")
        lead_author = resolve_article_author(lead_article)
        lead_feature_markup = f"""
    <!-- Featured Lead Editorial Investigation -->
    <section class="lead-feature-container" aria-label="Lead Investigation">
      <article class="lead-feature-card">
        <div class="lead-feature-media">
          <img src="{lead_thumb}" alt="{lead_title}" class="lead-feature-img" loading="eager" fetchpriority="high">
          <span class="lead-feature-badge">★ FEATURED DEEP DIVE • {lead_cat.upper()}</span>
        </div>
        <div class="lead-feature-content">
          <div class="lead-feature-eyebrow">
            <span>📘</span> INDEPENDENT TECHNICAL ANALYSIS
          </div>
          <h2 class="lead-feature-title">
            <a href="/articles/{lead_slug}/">{lead_title}</a>
          </h2>
          <p class="lead-feature-excerpt">{lead_sub}</p>
          <div class="lead-feature-byline">
            <div class="lead-author-avatar" style="background: {lead_author['gradient']};">
              {lead_author['initials']}
            </div>
            <div class="lead-author-meta">
              <span class="lead-author-name"><a href="/editorial-team/#{lead_author['slug']}">{html_lib.escape(lead_author['name'])}</a></span>
              <span class="lead-author-role">{html_lib.escape(lead_author['role'])}</span>
            </div>
          </div>
          <div class="lead-feature-footer">
            <a href="/articles/{lead_slug}/" class="lead-cta-btn">Read Full Investigation →</a>
            <span class="lead-time-pill">⏱️ {lead_time}</span>
            <span class="lead-time-pill">📊 Verified Benchmarks</span>
          </div>
        </div>
      </article>
    </section>"""

    # 2. In-Depth Editorial Grid (Showcase 15 top articles with author bylines)
    deepdive_cards_html = []
    grid_articles = active_articles[1:16] if len(active_articles) > 1 else active_articles
    for art in grid_articles:
        art_slug = art.get("slug", "")
        art_title = html_lib.escape(art.get("title", ""))
        art_sub = html_lib.escape(art.get("subtitle", "")[:130] + "...")
        art_cat = art.get("category_id", "future-tech")
        art_thumb = art.get("image") or get_category_fallback_image(art_cat)
        art_time = art.get("read_time", "7 min read")
        art_author = resolve_article_author(art)
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
              <span style="color: var(--neon-cyan);">IN-DEPTH REVIEW</span>
            </div>
            <h3 class="deepdive-card-title">
              <a href="/articles/{art_slug}/" style="color: inherit; text-decoration: none;">{art_title}</a>
            </h3>
            <p class="deepdive-excerpt">{art_sub}</p>
            <div class="deepdive-footer">
              <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 24px; height: 24px; border-radius: 50%; background: {art_author['gradient']}; color: #fff; font-size: 0.65rem; font-weight: 700; display: flex; align-items: center; justify-content: center;">
                  {art_author['initials']}
                </div>
                <span style="font-size: 0.8rem; color: var(--text-dim);">{art_author['name']}</span>
              </div>
              <a href="/articles/{art_slug}/" class="deepdive-read-btn">Read Deep Dive →</a>
            </div>
          </div>
        </article>""")
    deepdives_markup = "\n        ".join(deepdive_cards_html)

    # 3. Editorial Standards & E-E-A-T Verification Protocol Strip
    editorial_trust_markup = f"""
    <!-- Editorial Standards & Methodology (E-E-A-T Compliance) -->
    <section class="editorial-trust-strip" aria-label="Editorial Standards & Verification Protocol">
      <div class="trust-strip-inner">
        <div class="trust-item">
          <div class="trust-icon">📘</div>
          <div>
            <h4>Specification-Grounded Research</h4>
            <p>Every guide is cross-referenced against official manufacturer whitepapers, SDK documentation, and published benchmarks.</p>
          </div>
        </div>
        <div class="trust-item">
          <div class="trust-icon">🛡️</div>
          <div>
            <h4>Zero Sponsored Bias</h4>
            <p>100% independent editorial coverage. We never accept paid placements or vendor influence over buyer verdicts.</p>
          </div>
        </div>
        <div class="trust-item">
          <div class="trust-icon">✍️</div>
          <div>
            <h4>Human-Reviewed Guides</h4>
            <p>Original long-form explainers, pros &amp; cons matrices, and practical upgrade advice written for real users.</p>
          </div>
        </div>
        <div class="trust-item">
          <div class="trust-icon">📋</div>
          <div>
            <h4>Transparent Corrections</h4>
            <p>Specifications and product details are updated promptly whenever manufacturers revise official disclosures.</p>
          </div>
        </div>
      </div>
    </section>"""

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

        # Category-tailored editorial labels if card_hook is not explicitly defined
        cat_hook_fallbacks = {
            "ai-tools": "🤖 AI BRIEFING",
            "smartphones": "📱 MOBILE ARCHITECTURE",
            "laptops-pc": "💻 SILICON & PC",
            "gadgets": "🎧 HARDWARE BRIEF",
            "future-tech": "🚀 EMERGING TECH",
            "gaming-gear": "🎮 GAMING HARDWARE",
        }
        card_hook = s.get("card_hook") or cat_hook_fallbacks.get(cat_id, "⚡ TECH BRIEF")

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
              <span class="story-source">{SITE_NAME} Visual Brief</span>
              <a href="/stories/{slug}/" class="tap-to-view-cta" aria-label="Read story: {escaped_display_title}"><span class="play-arrow">▶</span> View Visual Brief</a>
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
  <!-- PWA & Mobile Web App Meta -->
  <link rel="manifest" href="/manifest.webmanifest">
  <meta name="theme-color" content="#06b6d4">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="TechSeconds">
  <link rel="apple-touch-icon" href="/static/images/publisher-logo.png">

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
        <span>INDEPENDENT TECH EDITORIAL</span>
      </div>
    </div>
  </header>

  <!-- Hero Section -->
  <main>
    <section class="hero-section">
      <div class="hero-glow-aura"></div>
      <div class="hero-eyebrow">
        <span>⚡</span> INDEPENDENT TECH ANALYSIS &amp; BUYER GUIDES
      </div>
      <h1 class="hero-title">
        Clear Technology Analysis in <span class="gradient-text">In-Depth Guides &amp; Visual Briefs</span>
      </h1>
      <p class="hero-subtitle">
        Specification-grounded hardware breakdowns, AI workflow guides, and concise visual companions designed for developers and everyday tech buyers.
      </p>
    </section>

    {lead_feature_markup}

    <!-- In-Depth Editorial Deep Dives & Articles Section -->
    <section class="deepdives-section" aria-label="In-Depth Editorial Deep Dives">
      <div class="deepdives-header">
        <div>
          <div style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--neon-cyan); text-transform: uppercase; margin-bottom: 0.35rem;">
            ⚡ 800–1400+ WORD EDITORIAL DEEP DIVES
          </div>
          <h2 class="deepdives-title">Featured <span class="gradient-text">Tech Investigations & Reviews</span></h2>
          <p class="deepdives-subtitle">Exhaustive architectural breakdowns, silicon micro-benchmarks, and comparative buying advice.</p>
        </div>
        <a href="/articles/" class="deepdives-view-all">View All 30 Articles ({len(active_articles)}) →</a>
      </div>
      <div class="deepdives-grid">
        {deepdives_markup}
      </div>
    </section>

    {editorial_trust_markup}

    <!-- Interactive Visual Stories Shelf (Google AMP Companion) -->
    <section class="visual-stories-shelf-header" style="max-width: 1300px; margin: 4rem auto 1rem; padding: 0 1.5rem;">
      <div style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--neon-cyan); text-transform: uppercase; margin-bottom: 0.35rem;">
        ⚡ 60-SECOND MOBILE-FIRST BRIEFINGS
      </div>
      <h2 style="font-family: var(--font-heading); font-size: 1.85rem; font-weight: 800; color: #ffffff;">
        Visual Web Stories <span class="gradient-text">(Google AMP)</span>
      </h2>
      <p style="color: var(--text-muted); font-size: 0.95rem; margin-top: 0.3rem;">
        Interactive, binge-optimized visual slides covering breaking hardware news, leaks, and gadget teardowns.
      </p>
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
        <span>Displaying <strong id="visible-count">{story_count}</strong> curated stories</span>
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
          {SITE_NAME} is an independent technology publication delivering in-depth hardware breakdowns, practical software and AI workflow guides, comparative buyer advice, and concise visual companions across computing, mobile tech, and consumer electronics.
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
      <div>© {current_year} {SITE_NAME}. All rights reserved.</div>
      <div>{SITE_NAME} — Independent Technology Analysis &amp; Buyer Guides.</div>
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
  <!-- Note: AdSense script intentionally omitted on policy/utility pages for strict AdSense policy compliance -->

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
        <span>INDEPENDENT TECH EDITORIAL</span>
      </div>
    </div>
  </header>

  <main class="legal-container">
    <article class="legal-card">
      <header class="legal-header">
        <h1 class="legal-title">{title}</h1>
        <div class="legal-last-updated">LAST UPDATED: NOVEMBER 2026 // EDITORIAL STANDARDS</div>
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
          {SITE_NAME} is an independent technology publication delivering in-depth hardware breakdowns, practical software and AI workflow guides, comparative buyer advice, and concise visual companions across computing, mobile tech, and consumer electronics.
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
      <div>© {current_year} {SITE_NAME}. All rights reserved.</div>
      <div>{SITE_NAME} — Independent Technology Analysis &amp; Buyer Guides.</div>
    </div>
  </footer>


  <!-- PWA Service Worker Registration -->
  <script>if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js');</script>
</body>
</html>"""
    return html


def get_editorial_team_page_content() -> str:
    return f"""
    <div class="team-page-intro">
      <h2>Meet the {SITE_NAME} Editorial Desk</h2>
      <p class="lead-text">
        At <strong>{SITE_NAME}</strong>, we believe readers deserve transparent, grounded technology journalism without hype or anonymous clickbait. Every guide, hardware comparison, and software tutorial is researched and edited with clear attribution and verifiable sources.
      </p>
    </div>

    <div class="editorial-team-grid">

      <!-- Founder & Chief Editor: Sumit Singh -->
      <div class="team-card" id="sumit-singh">
        <div class="team-card-header">
          <div class="team-avatar-initials" style="background: linear-gradient(135deg, #06b6d4, #3b82f6);">SS</div>
          <div class="team-member-title-block">
            <h3 class="team-member-name">Sumit Singh</h3>
            <div class="team-member-role">Founder &amp; Chief Editor</div>
            <div class="team-member-beats">Focus: Consumer Hardware · AI Workflows · Mobile Optimization · Open-Source Software</div>
          </div>
        </div>
        <div class="team-bio">
          Sumit Singh is an independent software developer, technology writer, and hardware researcher who founded {SITE_NAME}. He focuses on translating complex silicon specifications, local AI workflows, smartphone architectures, and PC hardware trade-offs into clear, practical buying guides and step-by-step explainers for everyday users and developers.
        </div>
        <div class="team-footer">
          <span class="team-credential">Founder &amp; Lead Author</span>
          <a href="mailto:{CONTACT_EMAIL}" class="team-contact-btn">✉ Contact Sumit</a>
        </div>
      </div>

      <!-- Research Desk -->
      <div class="team-card" id="editorial-desk">
        <div class="team-card-header">
          <div class="team-avatar-initials" style="background: linear-gradient(135deg, #10b981, #06b6d4);">TS</div>
          <div class="team-member-title-block">
            <h3 class="team-member-name">{SITE_NAME} Editorial Desk</h3>
            <div class="team-member-role">Technical Research &amp; Fact-Checking Desk</div>
            <div class="team-member-beats">Focus: Specification Audits · Comparative Buyer Matrices · Benchmark Aggregation · Corrections</div>
          </div>
        </div>
        <div class="team-bio">
          Our editorial research desk compiles and cross-checks manufacturer technical sheets, official SDK changelogs, published third-party benchmarks, and real-world software behavior to ensure every comparative table, pros &amp; cons matrix, and FAQ reflects accurate, current information.
        </div>
        <div class="team-footer">
          <span class="team-credential">Editorial Research &amp; QA</span>
          <a href="/contact/" class="team-contact-btn">✉ Submit a Correction</a>
        </div>
      </div>

    </div>

    <div class="methodology-section" style="margin-top: 3rem;">
      <h2>Our 5-Stage Editorial &amp; Verification Process</h2>
      <p>
        Every guide and comparative breakdown published on {SITE_NAME} follows a consistent five-stage editorial checklist:
      </p>
      <div class="protocol-steps">
        <div class="protocol-step-card">
          <div class="step-num">01</div>
          <div class="step-content">
            <h4>Primary Documentation &amp; Spec Verification</h4>
            <p>Technical specifications, architecture details, and software features are cross-checked directly against manufacturer documentation, official release notes, and public technical disclosures.</p>
          </div>
        </div>
        <div class="protocol-step-card">
          <div class="step-num">02</div>
          <div class="step-content">
            <h4>Structured Side-by-Side Comparison</h4>
            <p>Each device, processor, or AI tool is evaluated in context against direct alternatives and previous generations so readers understand practical differences rather than isolated marketing numbers.</p>
          </div>
        </div>
        <div class="protocol-step-card">
          <div class="step-num">03</div>
          <div class="step-content">
            <h4>Actionable Buyer Verdicts</h4>
            <p>Every long-form article concludes with a clear "{SITE_NAME} Verdict", a balanced Pros &amp; Cons breakdown, and practical "Recommended For / Consider Waiting If" guidance.</p>
          </div>
        </div>
        <div class="protocol-step-card">
          <div class="step-num">04</div>
          <div class="step-content">
            <h4>Editorial Independence</h4>
            <p>{SITE_NAME} does not publish paid reviews disguised as editorial content or allow hardware vendors to dictate our scores, pros, or cons.</p>
          </div>
        </div>
        <div class="protocol-step-card">
          <div class="step-num">05</div>
          <div class="step-content">
            <h4>Prompt Corrections &amp; Updates</h4>
            <p>Technology moves quickly. When specifications change or readers spot an inaccuracy, we review the report and update the article promptly.</p>
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

    <h2 id="ai-disclosure">Editorial Standards &amp; Technology Use Policy</h2>
    <p>
      Transparency is the foundation of reader trust. At {SITE_NAME}, software tools are used strictly for research organization, grammar verification, and accessibility checks. All published guides, comparative matrices, pros &amp; cons evaluations, and buyer verdicts are edited and reviewed by our editorial desk before publication.
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
    <h2>Official Editorial &amp; Press Desk</h2>
    <p>
      Have a technical correction, product tip, software question, or editorial inquiry? Reach out directly to the {SITE_NAME} team below.
    </p>

    <div class="contact-highlight-box" style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 1rem;">
      <div>
        <div style="font-size: 0.85rem; color: var(--text-dim); text-transform: uppercase;">Direct Editorial Inquiries</div>
        <a href="mailto:{CONTACT_EMAIL}" class="contact-email-link" id="editorial-email-link">✉ {CONTACT_EMAIL}</a>
      </div>
      <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
        <button type="button" id="copy-email-btn" onclick="copyEditorialEmail()" style="background: rgba(6, 182, 212, 0.14); border: 1px solid rgba(6, 182, 212, 0.4); border-radius: var(--radius-full); padding: 0.45rem 1rem; color: var(--neon-cyan); font-weight: 700; font-size: 0.82rem; cursor: pointer;">
          Copy Email
        </button>
        <span style="font-family: var(--font-mono); font-size: 0.82rem; color: var(--tech-emerald);">
          Response: &lt; 24–48 Hours
        </span>
      </div>
    </div>

    <h2>Inquiry Categories</h2>
    <ul>
      <li><strong>Technical Corrections</strong>: Spot an outdated specification or broken link in any guide? Send us the article URL and source details for prompt review and correction.</li>
      <li><strong>Press Releases &amp; Review Units</strong>: Share official product documentation, press kits, or review hardware inquiries.</li>
      <li><strong>Reader Suggestions</strong>: Suggest hardware comparisons, AI workflow tutorials, or troubleshooting guides you want covered next.</li>
      <li><strong>DMCA &amp; Rights Inquiries</strong>: Contact our compliance desk with full attribution details for rapid review.</li>
    </ul>

    <h2>Compose a Message</h2>
    <form id="techseconds-contact-form" onsubmit="handleContactSubmit(event)" style="margin-top: 1.5rem; display: flex; flex-direction: column; gap: 1rem;">
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem;">
        <div>
          <label for="contact-name" style="display: block; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.4rem;">Your Name</label>
          <input id="contact-name" type="text" name="name" required style="width: 100%; padding: 0.75rem 1rem; background: rgba(13, 17, 23, 0.8); border: 1px solid var(--border-glass); border-radius: var(--radius-sm); color: #fff; outline: none;">
        </div>
        <div>
          <label for="contact-email" style="display: block; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.4rem;">Email Address</label>
          <input id="contact-email" type="email" name="email" required style="width: 100%; padding: 0.75rem 1rem; background: rgba(13, 17, 23, 0.8); border: 1px solid var(--border-glass); border-radius: var(--radius-sm); color: #fff; outline: none;">
        </div>
      </div>
      <div>
        <label for="contact-subject" style="display: block; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.4rem;">Inquiry Subject</label>
        <input id="contact-subject" type="text" name="subject" placeholder="e.g. Technical Correction or Article Suggestion" required style="width: 100%; padding: 0.75rem 1rem; background: rgba(13, 17, 23, 0.8); border: 1px solid var(--border-glass); border-radius: var(--radius-sm); color: #fff; outline: none;">
      </div>
      <div>
        <label for="contact-message" style="display: block; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.4rem;">Message</label>
        <textarea id="contact-message" name="message" rows="5" placeholder="Include article URLs, specification details, or your question..." required style="width: 100%; padding: 0.75rem 1rem; background: rgba(13, 17, 23, 0.8); border: 1px solid var(--border-glass); border-radius: var(--radius-sm); color: #fff; outline: none; font-family: inherit;"></textarea>
      </div>
      <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
        <button type="submit" style="background: linear-gradient(135deg, var(--neon-cyan), var(--tech-emerald)); border: none; border-radius: var(--radius-full); padding: 0.75rem 2rem; color: #08090d; font-weight: 800; font-family: var(--font-heading); cursor: pointer; font-size: 0.95rem; box-shadow: 0 0 15px var(--neon-cyan-glow);">
          Open in Email Client →
        </button>
        <span id="contact-status" role="status" aria-live="polite" style="font-size: 0.85rem; color: var(--tech-emerald);"></span>
      </div>
    </form>
    <script>
      function copyEditorialEmail() {{
        navigator.clipboard.writeText("{CONTACT_EMAIL}").then(function() {{
          var btn = document.getElementById("copy-email-btn");
          btn.textContent = "Copied ✓";
          setTimeout(function() {{ btn.textContent = "Copy Email"; }}, 2200);
        }});
      }}
      function handleContactSubmit(e) {{
        e.preventDefault();
        var name = document.getElementById("contact-name").value.trim();
        var email = document.getElementById("contact-email").value.trim();
        var subject = document.getElementById("contact-subject").value.trim();
        var message = document.getElementById("contact-message").value.trim();
        var body = "From: " + name + " (" + email + ")\\n\\n" + message;
        var mailtoUrl = "mailto:{CONTACT_EMAIL}?subject=" + encodeURIComponent("[{SITE_NAME}] " + subject) + "&body=" + encodeURIComponent(body);
        document.getElementById("contact-status").textContent = "Opening your default email app with your message pre-filled...";
        window.location.href = mailtoUrl;
      }}
    </script>
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

    # Note: Short companion AMP Web Stories are intentionally excluded from sitemap.xml
    # (and marked noindex, follow) so Google Search & AdSense evaluate 100% full-length
    # original editorial articles without thin-page dilution.

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


def build_404_html() -> str:
    """
    Renders a custom 404 error page matching TechSeconds' cyber-dark aesthetic.
    Features navigation to home (/), in-depth articles (/articles/), editorial lab (/editorial-team/),
    and popular reviews to gracefully redirect lost visitors and search crawlers.
    """
    current_year = datetime.now(timezone.utc).year
    canonical_url = f"{SITE_URL}/404.html"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>404 - Page Relocated or Not Found | {SITE_NAME}</title>
  <meta name="description" content="The requested tech report or story has been relocated or archived into our In-Depth Articles Library. Explore our authentic hardware benchmarks and Google AMP Web Stories.">
  <meta name="robots" content="noindex, follow">
  <link rel="canonical" href="{canonical_url}">
  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="manifest" href="/manifest.webmanifest">
  <meta name="theme-color" content="#06b6d4">

  <!-- Verification & Analytics -->
  <meta name="google-site-verification" content="{GOOGLE_SITE_VERIFICATION}">
{get_pinterest_verify_tag()}
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GA_MEASUREMENT_ID}');
  </script>
  <!-- Note: AdSense script strictly omitted on 404 error page per Google Publisher Policies -->

  <!-- Google Fonts Whitelist -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">

  <style>
    :root {{
      --bg-dark: #08090d;
      --bg-card: rgba(13, 17, 23, 0.75);
      --border-glass: rgba(255, 255, 255, 0.08);
      --neon-cyan: #06b6d4;
      --tech-emerald: #10b981;
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --text-dim: #6b7280;
      --font-heading: 'Outfit', -apple-system, sans-serif;
      --font-body: 'Space Grotesk', -apple-system, sans-serif;
      --radius-md: 16px;
      --radius-sm: 8px;
      --radius-full: 9999px;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background: var(--bg-dark);
      color: var(--text-main);
      font-family: var(--font-body);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      line-height: 1.6;
      background-image: 
        radial-gradient(circle at 50% 0%, rgba(6, 182, 212, 0.12) 0%, transparent 60%),
        radial-gradient(circle at 100% 100%, rgba(16, 185, 129, 0.08) 0%, transparent 50%);
    }}

    /* Global Header */
    .site-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1.25rem 2rem;
      border-bottom: 1px solid var(--border-glass);
      background: rgba(8, 9, 13, 0.85);
      backdrop-filter: blur(12px);
      position: sticky;
      top: 0;
      z-index: 100;
    }}

    .site-logo {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      text-decoration: none;
      color: #fff;
      font-family: var(--font-heading);
      font-weight: 900;
      font-size: 1.4rem;
      letter-spacing: -0.5px;
    }}

    .site-logo-icon {{
      width: 36px;
      height: 36px;
      background: linear-gradient(135deg, var(--neon-cyan), var(--tech-emerald));
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
    }}

    .site-nav {{
      display: flex;
      gap: 1.5rem;
      align-items: center;
    }}

    .nav-link {{
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.95rem;
      font-weight: 600;
      transition: color 0.2s ease;
    }}

    .nav-link:hover, .nav-link.active {{
      color: var(--neon-cyan);
    }}

    .nav-cta-btn {{
      background: linear-gradient(135deg, var(--neon-cyan), var(--tech-emerald));
      color: #08090d;
      padding: 0.5rem 1.25rem;
      border-radius: var(--radius-full);
      font-weight: 800;
      text-decoration: none;
      font-size: 0.9rem;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}

    .nav-cta-btn:hover {{
      transform: translateY(-2px);
      box-shadow: 0 0 15px rgba(6, 182, 212, 0.4);
    }}

    /* 404 Hero Container */
    .error-container {{
      max-width: 900px;
      margin: 4rem auto;
      padding: 0 1.5rem;
      text-align: center;
      flex: 1;
    }}

    .error-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.4rem 1.2rem;
      background: rgba(6, 182, 212, 0.1);
      border: 1px solid rgba(6, 182, 212, 0.3);
      border-radius: var(--radius-full);
      color: var(--neon-cyan);
      font-size: 0.85rem;
      font-weight: 700;
      letter-spacing: 1px;
      text-transform: uppercase;
      margin-bottom: 1.5rem;
    }}

    .error-code {{
      font-family: var(--font-heading);
      font-size: clamp(5rem, 15vw, 8.5rem);
      font-weight: 900;
      line-height: 1;
      background: linear-gradient(135deg, #ffffff 30%, var(--neon-cyan) 70%, var(--tech-emerald) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 1rem;
      letter-spacing: -2px;
    }}

    .error-title {{
      font-family: var(--font-heading);
      font-size: clamp(1.5rem, 4vw, 2.2rem);
      font-weight: 800;
      color: #fff;
      margin-bottom: 1.2rem;
    }}

    .error-desc {{
      color: var(--text-muted);
      font-size: 1.1rem;
      max-width: 650px;
      margin: 0 auto 2.5rem;
      line-height: 1.7;
    }}

    /* Fast Action Nav Grid */
    .action-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 1.25rem;
      margin-bottom: 3.5rem;
      text-align: left;
    }}

    .action-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-glass);
      border-radius: var(--radius-md);
      padding: 1.5rem;
      text-decoration: none;
      color: inherit;
      transition: all 0.25s ease;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .action-card:hover {{
      transform: translateY(-4px);
      border-color: var(--neon-cyan);
      box-shadow: 0 10px 30px rgba(6, 182, 212, 0.15);
    }}

    .action-icon {{
      font-size: 1.8rem;
      margin-bottom: 0.75rem;
    }}

    .action-card-title {{
      font-family: var(--font-heading);
      font-size: 1.15rem;
      font-weight: 700;
      color: #fff;
      margin-bottom: 0.4rem;
    }}

    .action-card-desc {{
      font-size: 0.9rem;
      color: var(--text-muted);
      line-height: 1.5;
    }}

    .action-arrow {{
      color: var(--neon-cyan);
      font-weight: 700;
      margin-top: 1rem;
      display: flex;
      align-items: center;
      gap: 0.3rem;
    }}

    /* Curated Flagships Section */
    .curated-section {{
      background: rgba(13, 17, 23, 0.5);
      border: 1px solid var(--border-glass);
      border-radius: var(--radius-md);
      padding: 2rem;
      text-align: left;
    }}

    .curated-heading {{
      font-family: var(--font-heading);
      font-size: 1.25rem;
      font-weight: 800;
      color: #fff;
      margin-bottom: 1.25rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .curated-list {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1rem;
      list-style: none;
    }}

    .curated-item a {{
      color: var(--text-main);
      text-decoration: none;
      font-size: 0.95rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.6rem 0.8rem;
      background: rgba(255, 255, 255, 0.03);
      border-radius: var(--radius-sm);
      border: 1px solid transparent;
      transition: all 0.2s ease;
    }}

    .curated-item a:hover {{
      border-color: var(--neon-cyan);
      background: rgba(6, 182, 212, 0.08);
      color: var(--neon-cyan);
    }}

    /* Footer */
    .site-footer {{
      border-top: 1px solid var(--border-glass);
      padding: 3rem 2rem 2rem;
      background: rgba(8, 9, 13, 0.95);
      margin-top: auto;
    }}

    .footer-inner {{
      max-width: 1200px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: 2fr 1fr 1fr;
      gap: 2rem;
      margin-bottom: 2rem;
    }}

    @media (max-width: 768px) {{
      .site-header {{
        padding: 1rem;
      }}
      .site-nav {{
        gap: 0.75rem;
      }}
      .footer-inner {{
        grid-template-columns: 1fr;
      }}
    }}

    .footer-col-title {{
      font-family: var(--font-heading);
      font-size: 1rem;
      color: #fff;
      margin-bottom: 1rem;
    }}

    .footer-links {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }}

    .footer-links a {{
      color: var(--text-dim);
      text-decoration: none;
      font-size: 0.88rem;
      transition: color 0.2s;
    }}

    .footer-links a:hover {{
      color: var(--neon-cyan);
    }}

    .footer-bottom {{
      border-top: 1px solid rgba(255, 255, 255, 0.05);
      padding-top: 1.5rem;
      text-align: center;
      font-size: 0.82rem;
      color: var(--text-dim);
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 1rem;
    }}
  </style>
</head>
<body>

  <!-- Site Navigation Header -->
  <header class="site-header">
    <a href="/" class="site-logo">
      <div class="site-logo-icon">⚡</div>
      <span>TECH<span style="color: var(--neon-cyan);">SECONDS</span></span>
    </a>
    <nav class="site-nav">
      <a href="/" class="nav-link">Visual Stories</a>
      <a href="/articles/" class="nav-link">In-Depth Reviews</a>
      <a href="/editorial-team/" class="nav-link">Editorial Lab</a>
      <a href="/about/" class="nav-link">About</a>
      <a href="/articles/" class="nav-cta-btn">Explore Reviews →</a>
    </nav>
  </header>

  <!-- 404 Hero Section -->
  <main class="error-container">
    <div class="error-badge">
      <span>●</span> Signal Relocated // Error 404
    </div>
    <div class="error-code">404</div>
    <h1 class="error-title">Page Relocated or Archived</h1>
    <p class="error-desc">
      The technical analysis, article, or story URL you were attempting to reach does not exist or has been restructured into our In-Depth Magazine Library. Browse our verified hardware benchmarks and Google AMP Web Stories below.
    </p>

    <!-- Fast Action Hubs -->
    <div class="action-grid">
      <a href="/" class="action-card">
        <div>
          <div class="action-icon">⚡</div>
          <h3 class="action-card-title">Visual Web Stories</h3>
          <p class="action-card-desc">Bite-sized, 45-second swipeable Google AMP visual stories covering breaking mobile, AI, and hardware disclosures.</p>
        </div>
        <div class="action-arrow">Launch Portal →</div>
      </a>

      <a href="/articles/" class="action-card">
        <div>
          <div class="action-icon">📖</div>
          <h3 class="action-card-title">In-Depth Magazine Reviews</h3>
          <p class="action-card-desc">800 to 1,500+ word comprehensive technical teardowns, silicon architecture benchmarks, and buyer scorecards.</p>
        </div>
        <div class="action-arrow">Browse 30+ Reviews →</div>
      </a>

      <a href="/editorial-team/" class="action-card">
        <div>
          <div class="action-icon">🔬</div>
          <h3 class="action-card-title">Editorial Testing Lab</h3>
          <p class="action-card-desc">Meet our verified hardware analysts, Ph.D. semiconductor specialists, and review our 5-stage testing methodology.</p>
        </div>
        <div class="action-arrow">Inspect Lab Standards →</div>
      </a>
    </div>

    <!-- Curated In-Depth Reviews -->
    <div class="curated-section">
      <div class="curated-heading">
        <span>★</span> Popular Flagship Editorial Analyses
      </div>
      <ul class="curated-list">
        <li class="curated-item">
          <a href="/articles/razer-blade-18-rtx-5090-blackwell-4k-oled/">
            <span>💻</span> Razer Blade 18 RTX 5090 Blackwell Lab Review
          </a>
        </li>
        <li class="curated-item">
          <a href="/articles/best-local-llm-hardware-guide-mac-pc/">
            <span>🧠</span> Local LLM Hardware Buying Guide (Mac vs PC)
          </a>
        </li>
        <li class="curated-item">
          <a href="/articles/sora-2-gen-3-alpha-4k-cinema-sound-models/">
            <span>🎬</span> Sora 2 vs Gen-3 Alpha 4K Cinema Benchmark
          </a>
        </li>
        <li class="curated-item">
          <a href="/articles/snapdragon-x-elite-2-laptops-28-hour-battery-desktop-arm/">
            <span>🔋</span> Snapdragon X Elite 2 vs Apple M4 Battery Analysis
          </a>
        </li>
        <li class="curated-item">
          <a href="/articles/galaxy-s26-ultra-vs-iphone-18-pro-max-camera-war/">
            <span>📸</span> Galaxy S26 Ultra vs iPhone 18 Pro Max Camera Shootout
          </a>
        </li>
        <li class="curated-item">
          <a href="/articles/5-free-ai-tools-better-than-chatgpt-plus/">
            <span>⚡</span> 5 Free AI Tools Better Than ChatGPT Plus
          </a>
        </li>
      </ul>
    </div>
  </main>

  <!-- Site Footer -->
  <footer class="site-footer">
    <div class="footer-inner">
      <div>
        <div class="site-logo" style="margin-bottom: 0.8rem;">
          <div class="site-logo-icon">⚡</div>
          <span>TECH<span style="color: var(--neon-cyan);">SECONDS</span></span>
        </div>
        <p style="color: var(--text-dim); font-size: 0.88rem; max-width: 400px; line-height: 1.6;">
          Independent technology intelligence desk delivering verified microprocessor benchmarks, mobile hardware teardowns, and Google AMP Web Stories.
        </p>
      </div>

      <div>
        <h4 class="footer-col-title">Navigation</h4>
        <ul class="footer-links">
          <li><a href="/">⚡ Visual Stories Portal</a></li>
          <li><a href="/articles/">📖 In-Depth Articles</a></li>
          <li><a href="/editorial-team/">🔬 Editorial Team & Testing</a></li>
          <li><a href="/about/">About Us</a></li>
          <li><a href="/contact/">Contact Editorial Desk</a></li>
        </ul>
      </div>

      <div>
        <h4 class="footer-col-title">Policies & Trust</h4>
        <ul class="footer-links">
          <li><a href="/privacy/">Privacy Policy (AdSense & GDPR)</a></li>
          <li><a href="/terms/">Terms of Service & Fair Use</a></li>
          <li><a href="/about/#ai-disclosure">Editorial Standards</a></li>
          <li><a href="/sitemap.xml">XML Sitemap</a></li>
        </ul>
      </div>
    </div>

    <div class="footer-bottom">
      <div>© {current_year} {SITE_NAME}. All rights reserved. Google AMP & AdSense Compliant.</div>
      <div>TechSeconds Editorial Lab & Independent Hardware Benchmarks.</div>
    </div>
  </footer>

</body>
</html>"""


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

    # 2b. Branded 404 Error Page
    not_found_html = build_404_html()
    (dist_dir / "404.html").write_text(not_found_html, encoding="utf-8")
    print(f"[+] Generated 404 error page: dist/404.html")

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

    # 6. RSS 2.0 Feed for Google News & Aggregators (Article-First Full Editorial Feed)
    rss_xml = generate_rss_xml(stories, articles=articles)
    (dist_dir / "rss.xml").write_text(rss_xml, encoding="utf-8")
    (dist_dir / "feed.xml").write_text(rss_xml, encoding="utf-8")
    print(f"[+] Generated article-first RSS feeds: dist/rss.xml & dist/feed.xml")

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


def generate_rss_xml(stories: List[Dict[str, Any]], articles: Optional[List[Dict[str, Any]]] = None) -> str:
    """Generates standard RSS 2.0 with Media RSS tags prioritizing full-length original editorial articles."""
    now_rfc822 = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    items_xml = []
    source_items = articles if articles else stories[:30]
    is_article_feed = bool(articles)
    for item_obj in source_items:
        title = html_lib.escape(item_obj.get("title", f"{SITE_NAME} Guide"))
        slug = item_obj.get("slug", "")
        link = f"{SITE_URL}/articles/{slug}/" if is_article_feed else f"{SITE_URL}/stories/{slug}/"
        summary = html_lib.escape(item_obj.get("subtitle") or item_obj.get("summary", ""))
        category = html_lib.escape(item_obj.get("category_name") or item_obj.get("category_id", "Technology"))
        pub_date = item_obj.get("published", "")
        if pub_date:
            try:
                dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                pub_rfc822 = dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
            except Exception:
                pub_rfc822 = now_rfc822
        else:
            pub_rfc822 = now_rfc822

        image_url = item_obj.get("image", f"{SITE_URL}/static/images/og-banner.png")
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

