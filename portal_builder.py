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
from typing import List, Dict, Any
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
    get_category_fallback_image,
)


def build_portal_html(stories: List[Dict[str, Any]], max_cards: int = 48) -> str:
    """
    Renders the futuristic Cyber-Dark portal homepage.
    Caps displayed cards to max_cards to preserve mobile DOM performance.
    """
    display_stories = stories[:max_cards] if max_cards and len(stories) > max_cards else stories
    story_count = len(display_stories)
    current_year = datetime.now(timezone.utc).year

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
        escaped_title = html_lib.escape(title, quote=True)
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
          aria-label="Open story: {escaped_title}"
          data-slug="{slug}" 
          data-category="{cat_id}"
          data-title="{escaped_title}"
          data-summary="{escaped_summary}">
          <img class="story-card-bg" 
            src="{card_image}" 
            alt="{escaped_title}" 
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
            <h2 class="story-card-title">{title}</h2>
            <p class="story-card-snippet">{summary}</p>
            <div class="story-card-footer">
              <span class="story-source">via {source}</span>
              <a href="/stories/{slug}/" class="tap-to-view-cta" aria-label="Read story: {escaped_title}"><span class="play-arrow">▶</span> Tap to Unlock ⚡</a>
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
        "publisher": {
            "@type": "Organization",
            "name": PUBLISHER_NAME,
            "logo": {
                "@type": "ImageObject",
                "url": PUBLISHER_LOGO_URL,
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

  <!-- Google Search Console Verification -->
  <meta name="google-site-verification" content="{GOOGLE_SITE_VERIFICATION}">

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
          <li><a href="/" class="nav-link active">Stories</a></li>
          <li><a href="/about/" class="nav-link">About</a></li>
          <li><a href="/privacy/" class="nav-link">Privacy</a></li>
          <li><a href="/terms/" class="nav-link">Terms</a></li>
          <li><a href="/contact/" class="nav-link">Contact</a></li>
        </ul>
      </nav>

      <div class="live-badge">
        <span class="pulse-dot"></span>
        <span>AUTONOMOUS FEED</span>
      </div>
    </div>
  </header>

  <!-- Hero Section -->
  <main>
    <section class="hero-section">
      <div class="hero-glow-aura"></div>
      <div class="hero-eyebrow">
        <span>⚡</span> 100% GOOGLE AMP WEB STORIES
      </div>
      <h1 class="hero-title">
        The Future Of Tech in <span class="gradient-text">45-Second Visual Stories</span>
      </h1>
      <p class="hero-subtitle">
        Instant, mobile-first Google Web Stories breaking down frontier AI, flagship smartphone leaks, quantum breakthroughs, and futuristic computing.
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
          {SITE_NAME} is an autonomous Google AMP Web Stories portal dedicated to high-speed visual journalism across artificial intelligence, computing hardware, consumer tech, and future frontiers.
        </p>
      </div>

      <div class="footer-col">
        <h4 class="footer-col-title">Navigation</h4>
        <ul class="footer-links">
          <li><a href="/">Latest Stories</a></li>
          <li><a href="/about/">About & Mission</a></li>
          <li><a href="/contact/">Editorial Desk</a></li>
          <li><a href="/sitemap.xml">XML Sitemap</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <h4 class="footer-col-title">Policies</h4>
        <ul class="footer-links">
          <li><a href="/privacy/">Privacy Policy (AdSense & GDPR)</a></li>
          <li><a href="/terms/">Terms of Service & Fair Use</a></li>
          <li><a href="/about/#ai-disclosure">AI Editorial Disclosure</a></li>
          <li><a href="/contact/">Corrections & DMCA</a></li>
        </ul>
      </div>
    </div>

    <div class="footer-bottom">
      <div>© {current_year} {SITE_NAME}. All rights reserved. 100% Google AMP Story Compliant.</div>
      <div>Autonomous Pipeline Built with Python & Hosted on Vercel.</div>
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

  <!-- Google Search Console Verification -->
  <meta name="google-site-verification" content="{GOOGLE_SITE_VERIFICATION}">

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
          <li><a href="/about/" class="nav-link{' active' if page_id == 'about' else ''}">About</a></li>
          <li><a href="/privacy/" class="nav-link{' active' if page_id == 'privacy' else ''}">Privacy</a></li>
          <li><a href="/terms/" class="nav-link{' active' if page_id == 'terms' else ''}">Terms</a></li>
          <li><a href="/contact/" class="nav-link{' active' if page_id == 'contact' else ''}">Contact</a></li>
        </ul>
      </nav>

      <div class="live-badge">
        <span class="pulse-dot"></span>
        <span>AUTONOMOUS FEED</span>
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
          {SITE_NAME} is an autonomous Google AMP Web Stories portal dedicated to high-speed visual journalism across artificial intelligence, computing hardware, consumer tech, and future frontiers.
        </p>
      </div>

      <div class="footer-col">
        <h4 class="footer-col-title">Navigation</h4>
        <ul class="footer-links">
          <li><a href="/">Latest Stories</a></li>
          <li><a href="/about/">About & Mission</a></li>
          <li><a href="/contact/">Editorial Desk</a></li>
          <li><a href="/sitemap.xml">XML Sitemap</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <h4 class="footer-col-title">Policies</h4>
        <ul class="footer-links">
          <li><a href="/privacy/">Privacy Policy (AdSense & GDPR)</a></li>
          <li><a href="/terms/">Terms of Service & Fair Use</a></li>
          <li><a href="/about/#ai-disclosure">AI Editorial Disclosure</a></li>
          <li><a href="/contact/">Corrections & DMCA</a></li>
        </ul>
      </div>
    </div>

    <div class="footer-bottom">
      <div>© {current_year} {SITE_NAME}. All rights reserved. 100% Google AMP Story Compliant.</div>
      <div>Autonomous Pipeline Built with Python & Hosted on Vercel.</div>
    </div>
  </footer>

</body>
</html>"""
    return html


def get_about_page_content() -> str:
    return f"""
    <h2>Our Journalism Mission</h2>
    <p>
      Welcome to <strong>{SITE_NAME}</strong>. In an era inundated with clickbait, thousand-word fluff pieces, and sluggish web pages loaded with bloated scripts, we believe technology journalism must be rapid, verifiable, and visually compelling.
    </p>
    <p>
      {SITE_NAME} pioneers the autonomous Google AMP Web Story format. Every breakthrough in generative intelligence, silicon semiconductor lithography, flagship mobile devices, quantum mechanics, and consumer robotics is distilled into 5 high-impact, 45-second interactive visual slides.
    </p>

    <h2>Editorial Independence & Standards</h2>
    <p>
      We maintain strict journalistic independence. We do not accept sponsored content disguised as editorial news, nor do we enter into pay-to-play hardware benchmarking agreements. Our stories cite primary sources, engineering whitepapers, and direct manufacturer disclosures.
    </p>

    <h2 id="ai-disclosure">Transparent AI Editorial Disclosure</h2>
    <p>
      Transparency is the cornerstone of our platform. {SITE_NAME} utilizes an autonomous tech news pipeline powered by Google Gemini and advanced natural language synthesis models to ingest public RSS wires, parse technical benchmarks, and construct initial story storyboards.
    </p>
    <p>
      All algorithmic synthesis adheres to our deterministic verification checks:
    </p>
    <ul>
      <li><strong>Fact Verification</strong>: Core specifications, clock speeds, sensor sizes, and price quotes are grounded in verifiable vendor documentation.</li>
      <li><strong>Source Attribution</strong>: Every generated story credits the original reporting outlet, manufacturer press release, or scientific journal.</li>
      <li><strong>Human Oversight</strong>: Our editorial desk actively supervises model prompt templates, algorithmic biases, and correction requests.</li>
    </ul>

    <h2>Contact The Editorial Desk</h2>
    <p>
      We welcome feedback, press releases, embargoed news tips, and partnership requests. Reach out to our lead team at:
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
      {SITE_NAME} is an autonomous technology news aggregation and visual commentary portal. The content, quotes, excerpts, product specifications, and imagery featured on this site are utilized in accordance with the <strong>Fair Use Doctrine (17 U.S.C. § 107)</strong> for purposes including:
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
      All content on {SITE_NAME} is provided on an "as is" and "as available" basis without warranties of any kind. While our automated pipeline and editorial team endeavor to maintain accurate and up-to-date technical information, we cannot guarantee the complete accuracy or future availability of third-party products.
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


def generate_sitemap_xml(stories: List[Dict[str, Any]]) -> str:
    """
    Builds dynamic sitemap.xml adhering to Sitemaps Protocol 0.9 with Google Image extensions.
    """
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    urls = [
        {"loc": f"{SITE_URL}/", "priority": "1.0", "changefreq": "hourly", "image": None},
        {"loc": f"{SITE_URL}/about/", "priority": "0.7", "changefreq": "monthly", "image": None},
        {"loc": f"{SITE_URL}/privacy/", "priority": "0.5", "changefreq": "monthly", "image": None},
        {"loc": f"{SITE_URL}/terms/", "priority": "0.5", "changefreq": "monthly", "image": None},
        {"loc": f"{SITE_URL}/contact/", "priority": "0.6", "changefreq": "monthly", "image": None},
    ]

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
            "priority": "0.9",
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
    Renders and writes portal homepage, legal pages, sitemap, robots, and stories.json.
    """
    # 1. Homepage dist/index.html
    home_html = build_portal_html(stories)
    (dist_dir / "index.html").write_text(home_html, encoding="utf-8")
    print(f"[+] Generated homepage: dist/index.html")

    # 2. Legal Pages
    legal_pages = [
        ("about", f"About {SITE_NAME} & Editorial Mission", f"Learn about {SITE_NAME}'s mission, journalistic standards, and transparent AI disclosure.", get_about_page_content()),
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

    # 3. Dynamic Sitemap.xml
    sitemap_xml = generate_sitemap_xml(stories)
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
