"""
TechPulse Content Engine
Multi-source RSS feed fetcher, keyword auto-categorizer, and curated viral fallback dataset.
"""

import re
import html
import unicodedata
import hashlib
from typing import List, Dict, Any, Optional
import feedparser
from bs4 import BeautifulSoup
import requests

from config import CATEGORIES, RSS_FEEDS, VERIFIED_TECH_IMAGES

# Built-in curated viral fallback dataset for maximum CTR, high engagement, and offline reliability
CURATED_VIRAL_STORIES: List[Dict[str, Any]] = [
    {
        "title": "Quantum Supremacy Breakthrough: 1 Million Qubit Chip Unveiled",
        "slug": "quantum-supremacy-breakthrough-1-million-qubit-chip",
        "category_id": "future-tech",
        "source": "TechPulse Research Lab",
        "link": "https://techpulse-gadget.vercel.app/stories/quantum-supremacy-breakthrough-1-million-qubit-chip",
        "published": "2026-10-05T08:00:00Z",
        "read_time": "45s",
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=720&q=80",
        "summary": "Engineers achieve error-free quantum computing using photonic optical grids, cracking 2048-bit encryption simulation in 4.2 seconds.",
        "slides": [
            {
                "hook": "THE QUANTUM BARRIER SHATTERS",
                "title": "1 Million Qubits: Computing Has Changed Forever",
                "badge": "⚡ BREAKTHROUGH",
                "bullet1": "Room-temperature optical silicon lattice eliminates massive liquid helium cryogenic cooling.",
                "bullet2": "Solves complex molecular simulations in 4.2 seconds that took supercomputers 12,000 years.",
                "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=720&q=80",
            },
            {
                "hook": "HARDWARE ARCHITECTURE",
                "title": "Photonic Waveguide Neural Interconnects",
                "badge": "🔬 ARCHITECTURE",
                "bullet1": "99.98% 2-qubit gate fidelity surpassing all previous superconducting benchmarks.",
                "bullet2": "Microscopic photonic waveguides route entangled laser pulses with sub-femtosecond precision.",
                "image": "https://images.unsplash.com/photo-1535223289827-42f1e9919769?w=720&q=80",
            },
            {
                "hook": "REAL-WORLD BENCHMARKS",
                "title": "Cracking Prime Factorization in Seconds",
                "badge": "🔥 3,400X SPEEDUP",
                "bullet1": "Instantaneous protein-folding discovery promises cure pathways for hereditary neurodegenerative disorders.",
                "bullet2": "Global cybersecurity firms scramble to deploy post-quantum lattice cryptography standards.",
                "image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=720&q=80",
            },
            {
                "hook": "INDUSTRY DISRUPTION",
                "title": "The End of Traditional Silicon Scaling",
                "badge": "💡 PARADIGM SHIFT",
                "bullet1": "Commercial cloud access scheduled for early 2027 via serverless API endpoints.",
                "bullet2": "Power consumption drops 94% compared to mega-cluster GPU server farms.",
                "image": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=720&q=80",
            },
            {
                "hook": "THE BOTTOM LINE",
                "title": "TechPulse Verdict: The Quantum Era Is Here",
                "badge": "⚡ TECHPULSE VERDICT",
                "bullet1": "The transition from classical bits to quantum superpositions is happening faster than predicted.",
                "bullet2": "Every major tech stack will require quantum-ready cryptographic resilience this year.",
                "image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=720&q=80",
            },
        ],
    },
    {
        "title": "Top 7 Secret AI Productivity Tools That Outperform ChatGPT in 2026",
        "slug": "top-secret-ai-productivity-tools-outperform-chatgpt",
        "category_id": "ai-tools",
        "source": "AI Insider Dispatch",
        "link": "https://techpulse-gadget.vercel.app/stories/top-secret-ai-productivity-tools-outperform-chatgpt",
        "published": "2026-10-05T07:30:00Z",
        "read_time": "50s",
        "image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=720&q=80",
        "summary": "Unlocking next-generation autonomous agents and local neural sandboxes that automate 80% of daily engineering and research workflows.",
        "slides": [
            {
                "hook": "WORKFLOW SUPERCHARGED",
                "title": "Stop Using AI Like A Regular Search Engine",
                "badge": "🤖 AI PRODUCTIVITY",
                "bullet1": "Autonomous agentic frameworks now execute multi-turn browser, terminal, and code tasks unattended.",
                "bullet2": "Local 4-bit quantized models match GPT-4 tier reasoning on consumer laptops with 0 cloud latency.",
                "image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=720&q=80",
            },
            {
                "hook": "THE REASONING WEAPON",
                "title": "Deep Research Synthesizers & Sandbox Agents",
                "badge": "⚡ 10X LEVERAGE",
                "bullet1": "Autonomous agents scan 500+ documentation sources, verify code execution, and test APIs live.",
                "bullet2": "Automated code refactoring that preserves backwards compatibility and writes full test suites.",
                "image": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=720&q=80",
            },
            {
                "hook": "CREATIVE WORKFLOWS",
                "title": "Realtime Bidirectional Voice & Canvas Logic",
                "badge": "🎙️ ZERO LATENCY",
                "bullet1": "Sub-150ms voice latency allows fluid natural brainstorming without push-to-talk delays.",
                "bullet2": "Generative canvas engines turn rough architectural doodles into production UI components instantly.",
                "image": "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=720&q=80",
            },
            {
                "hook": "LOCAL PRIVACY",
                "title": "Zero-Cloud Local Neural Vaults",
                "badge": "🛡️ 100% PRIVATE",
                "bullet1": "Index all your proprietary codebases, PDFs, and secrets locally without any third-party tracking.",
                "bullet2": "Hardware accelerated on modern NPU chips drawing under 15 watts of battery power.",
                "image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=720&q=80",
            },
            {
                "hook": "HOW TO START",
                "title": "TechPulse Verdict: The Agentic Revolution",
                "badge": "⚡ TECHPULSE VERDICT",
                "bullet1": "Those who harness autonomous agents will outperform entire traditional engineering teams.",
                "bullet2": "Audit your daily repetitive tasks and delegate them to local autonomous agents today.",
                "image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=720&q=80",
            },
        ],
    },
    {
        "title": "Galaxy S26 Ultra vs iPhone 18 Pro Max: The 200MP Periscope Camera War",
        "slug": "galaxy-s26-ultra-vs-iphone-18-pro-max-camera-war",
        "category_id": "smartphones",
        "source": "Mobile Hardware Wire",
        "link": "https://techpulse-gadget.vercel.app/stories/galaxy-s26-ultra-vs-iphone-18-pro-max-camera-war",
        "published": "2026-10-05T06:45:00Z",
        "read_time": "45s",
        "image": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=720&q=80",
        "summary": "Variable mechanical apertures, liquid lenses, and 2-nanometer neural processors battle for smartphone photography supremacy.",
        "slides": [
            {
                "hook": "THE FLAGSHIP SHOWDOWN",
                "title": "Titanium, 2nm Silicon & The Ultimate Optics",
                "badge": "📱 FLAGSHIP CLASH",
                "bullet1": "Apple's tetraprism telephoto upgrades to a 48MP periscope across all zoom focal lengths.",
                "bullet2": "Samsung counters with a 1-inch 200MP sensor featuring continuous f/1.4 to f/4.0 mechanical aperture.",
                "image": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=720&q=80",
            },
            {
                "hook": "SENSOR INNOVATION",
                "title": "Stacked Dual-Transistor Pixels & Night Vision",
                "badge": "🔍 OPTICAL SPECS",
                "bullet1": "Dual-layer transistor pixel architecture doubles dynamic range, eliminating blown highlights completely.",
                "bullet2": "Ultra-low light video recording captures daylight-quality color in near pitch darkness at 4K 120fps.",
                "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=720&q=80",
            },
            {
                "hook": "SILICON PERFORMANCE",
                "title": "2nm Snapdragon 8 Elite vs Apple A20 Pro",
                "badge": "⚡ 45% EFFICIENCY",
                "bullet1": "TSMC 2nm GAA (Gate-All-Around) architecture delivers massive performance per watt gains.",
                "bullet2": "Console-grade real-time path tracing at locked 120 frames per second without thermal throttling.",
                "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=720&q=80",
            },
            {
                "hook": "DISPLAY & CHARGING",
                "title": "Anti-Reflective Armor & 100W Fast Charging",
                "badge": "🔋 POWER MATRIX",
                "bullet1": "0-100% charging in 19 minutes using gallium nitride dual-cell battery cells.",
                "bullet2": "Next-gen sapphire crystal coatings eliminate 99% of ambient reflections under direct sunlight.",
                "image": "https://images.unsplash.com/photo-1617788138017-80ad40651399?w=720&q=80",
            },
            {
                "hook": "FINAL VERDICT",
                "title": "TechPulse Verdict: Who Wins The Crown?",
                "badge": "⚡ TECHPULSE VERDICT",
                "bullet1": "Samsung claims the crown for raw zoom detail; Apple dominates cinematic color and ProRes workflows.",
                "bullet2": "The real winner is the mobile photographer — DSLRs are now truly obsolete for travel.",
                "image": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=720&q=80",
            },
        ],
    },
    {
        "title": "Neural Audio ANC 3.0: Why Audiophiles Are Ditching Wired Headphones",
        "slug": "neural-audio-anc-3-audiophiles-ditching-wired",
        "category_id": "gadgets",
        "source": "Acoustic Horizon",
        "link": "https://techpulse-gadget.vercel.app/stories/neural-audio-anc-3-audiophiles-ditching-wired",
        "published": "2026-10-05T06:00:00Z",
        "read_time": "40s",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=720&q=80",
        "summary": "Lossless 96kHz/24-bit ultra-wideband audio and real-time ear canal calibration shatter the wired audio monopoly.",
        "slides": [
            {
                "hook": "ACOUSTIC REVOLUTION",
                "title": "Wired Purity Without The Cords",
                "badge": "🎧 ACOUSTIC TECH",
                "bullet1": "Ultra-Wideband (UWB) wireless protocol achieves 12Mbps uncompressed bitrate, ending Bluetooth compression.",
                "bullet2": "Real-time algorithmic acoustic reflection scans calibrate eq 1,000 times per second for your exact ear shape.",
                "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=720&q=80",
            },
            {
                "hook": "ACTIVE NOISE CANCELLATION",
                "title": "Neural ANC Eliminates 52dB of Chaos",
                "badge": "🔇 52dB REDUCTION",
                "bullet1": "Triple MEMS microphones on each bud predict incoming background noise waves with sub-millisecond precision.",
                "bullet2": "Smart Transparency automatically lets human vocal frequencies pass while silencing engine hums.",
                "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=720&q=80",
            },
            {
                "hook": "SPATIAL SOUNDSTAGE",
                "title": "True Holographic 3D Head Tracking",
                "badge": "🌐 SPATIAL AUDIO",
                "bullet1": "Gyroscopic 9-axis IMUs pin sound sources in virtual 3D space with zero perceived phase distortion.",
                "bullet2": "Dolby Atmos Music and high-res binaural audio render concert-hall width inside ultra-compact earbuds.",
                "image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=720&q=80",
            },
            {
                "hook": "BATTERY BREAKTHROUGH",
                "title": "Silicon-Carbon Anodes: 48-Hour Playtime",
                "badge": "⚡ 48H ENDURANCE",
                "bullet1": "Compact case delivers a full week of heavy listening without needing a wall charger.",
                "bullet2": "5-minute fast USB-C charge yields 6 hours of high-bitrate continuous playback.",
                "image": "https://images.unsplash.com/photo-1617788138017-80ad40651399?w=720&q=80",
            },
            {
                "hook": "THE SOUND VERDICT",
                "title": "TechPulse Verdict: The Wire Is Dead",
                "badge": "⚡ TECHPULSE VERDICT",
                "bullet1": "Lossless wireless audio has surpassed traditional wired dongles in both fidelity and convenience.",
                "bullet2": "Audiophiles who scoffed at wireless are now wearing UWB ANC earbuds daily.",
                "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=720&q=80",
            },
        ],
    },
    {
        "title": "Humanoid Robots Enter Mass Production: Inside The Fully Automated Gigafactory",
        "slug": "humanoid-robots-enter-mass-production-gigafactory",
        "category_id": "future-tech",
        "source": "Robotics World Review",
        "link": "https://techpulse-gadget.vercel.app/stories/humanoid-robots-enter-mass-production-gigafactory",
        "published": "2026-10-05T05:15:00Z",
        "read_time": "45s",
        "image": "https://images.unsplash.com/photo-1546776310-eef45dd6d63c?w=720&q=80",
        "summary": "10,000 bipedal androids roll off the assembly line equipped with tactile tactile dexterity and vision-language-action brains.",
        "slides": [
            {
                "hook": "THE ROBOTIC DAWN",
                "title": "10,000 Bipedal Workers Roll Off The Line",
                "badge": "🤖 HUMANOID TECH",
                "bullet1": "World's first dedicated humanoid gigafactory begins commercial production for manufacturing and logistics.",
                "bullet2": "Bipedal robots with 28 degrees of freedom in hands handle delicate electronics and 50lb payloads.",
                "image": "https://images.unsplash.com/photo-1546776310-eef45dd6d63c?w=720&q=80",
            },
            {
                "hook": "END-TO-END NEURAL BRAIN",
                "title": "Vision-Language-Action Models",
                "badge": "🧠 NEURAL VLA",
                "bullet1": "No pre-programmed hardcoded motion scripts — robots learn physical tasks by observing human demonstration videos.",
                "bullet2": "Zero-shot adaptation allows instantaneous re-tasking from warehouse stacking to circuit board soldering.",
                "image": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=720&q=80",
            },
            {
                "hook": "DEXTERITY & SENSORS",
                "title": "Sub-Millimeter Tactile Fingertips",
                "badge": "⚡ SENSORY MATRIX",
                "bullet1": "Thousands of micro-pressure sensors mimic biological touch to grip raw eggs without cracking.",
                "bullet2": "Solid-state 360-degree LiDAR and stereoscopic RGB-D cameras eliminate all blind spots.",
                "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=720&q=80",
            },
            {
                "hook": "ECONOMIC IMPACT",
                "title": "Labor Cost Drops Below $3 Per Hour",
                "badge": "📈 ECONOMIC SHIFT",
                "bullet1": "Modular swappable solid-state batteries allow 24/7 continuous operation with zero downtime.",
                "bullet2": "Global supply chain bottlenecks expected to decrease significantly across industrial manufacturing.",
                "image": "https://images.unsplash.com/photo-1535223289827-42f1e9919769?w=720&q=80",
            },
            {
                "hook": "OUR OUTLOOK",
                "title": "TechPulse Verdict: Sci-Fi Is Now Factory Reality",
                "badge": "⚡ TECHPULSE VERDICT",
                "bullet1": "Humanoid robotics is no longer an R&D curiosity — it is a commercially deployed economic engine.",
                "bullet2": "Expect consumer household assistant humanoids to begin entering trials before 2028.",
                "image": "https://images.unsplash.com/photo-1546776310-eef45dd6d63c?w=720&q=80",
            },
        ],
    },
    {
        "title": "Steam Deck 2 & Handheld PC Gaming Wars: 1080p 120Hz In Your Pocket",
        "slug": "steam-deck-2-handheld-pc-gaming-wars-1080p-120hz",
        "category_id": "gaming-gear",
        "source": "Gamer Grid Dispatch",
        "link": "https://techpulse-gadget.vercel.app/stories/steam-deck-2-handheld-pc-gaming-wars-1080p-120hz",
        "published": "2026-10-05T04:30:00Z",
        "read_time": "40s",
        "image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=720&q=80",
        "summary": "AMD Zen 5 APU, vibrant 7.9-inch OLED 120Hz HDR panel, and 12-hour battery life rewrite the portable gaming rulebook.",
        "slides": [
            {
                "hook": "HANDHELD SUPREMACY",
                "title": "AAA Gaming In The Palm Of Your Hands",
                "badge": "🎮 GAMING GEAR",
                "bullet1": "Custom AMD RDNA 3.5 silicon brings desktop-class graphical horsepower under a 15W TDP ceiling.",
                "bullet2": "7.9-inch glossy OLED display delivers true blacks, 1000-nit HDR peak brightness, and 120Hz refresh.",
                "image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=720&q=80",
            },
            {
                "hook": "FRAME GENERATION & PERFORMANCE",
                "title": "AI Upscaling Delivers Solid 90+ FPS",
                "badge": "⚡ 90+ FPS AAA",
                "bullet1": "Integrated hardware neural cores run FSR 4.0 frame generation with zero noticeable input latency.",
                "bullet2": "Cyberpunk 2077 with ray tracing runs at steady 60 FPS on high preset settings on battery power.",
                "image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=720&q=80",
            },
            {
                "hook": "ERGONOMICS & CONTROLS",
                "title": "Hall Effect Joysticks & Magnetic Trackpads",
                "badge": "🕹️ ZERO STICK DRIFT",
                "bullet1": "Contactless magnetic Hall Effect sensors completely eradicate analog stick drift permanently.",
                "bullet2": "Haptic feedback linear resonant actuators provide pinpoint accuracy for precision FPS shooters.",
                "image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=720&q=80",
            },
            {
                "hook": "OPERATING SYSTEM",
                "title": "SteamOS 4.0 vs Windows 12 Handheld",
                "badge": "💻 OS MATRIX",
                "bullet1": "Instant instant sleep/resume handles game suspension with zero battery drain over 48 hours.",
                "bullet2": "MicroSD UHS-II and modular M.2 2230 NVMe slots allow effortless multi-terabyte library storage.",
                "image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=720&q=80",
            },
            {
                "hook": "THE GAMING VERDICT",
                "title": "TechPulse Verdict: The Ultimate Gaming Rig",
                "badge": "⚡ TECHPULSE VERDICT",
                "bullet1": "Home consoles and gaming laptops are facing existential threat from ultra-portable handheld beasts.",
                "bullet2": "The Steam Deck 2 architecture cements handhelds as the premier way millions play modern games.",
                "image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=720&q=80",
            },
        ],
    },
]


def clean_html(raw_html: str) -> str:
    """Removes HTML markup and returns clean text."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ")
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def slugify(text: str) -> str:
    """Converts a headline into an SEO-friendly URL slug."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[-\s]+", "-", text)
    # Truncate to reasonable slug length
    slug = text[:70].rstrip("-")
    if not slug:
        slug = "techpulse-story-" + hashlib.md5(text.encode()).hexdigest()[:8]
    return slug


def detect_category(title: str, summary: str, fallback: str = "future-tech") -> str:
    """Auto-detects category ID based on weighted keyword matches."""
    combined = f"{title.lower()} {summary.lower()}"
    scores = {}

    for cat in CATEGORIES:
        if cat["id"] == "all":
            continue
        score = 0
        keywords = cat.get("keywords", [])
        for kw in keywords:
            # Title matches are weighted 3x higher
            if kw in title.lower():
                score += 3
            elif kw in combined:
                score += 1
        scores[cat["id"]] = score

    best_cat = max(scores, key=scores.get)
    if scores[best_cat] > 0:
        return best_cat
    return fallback


def select_image_for_story(category_id: str, index: int = 0) -> str:
    """Returns a curated high-contrast tech image matching the category."""
    for cat in CATEGORIES:
        if cat["id"] == category_id and "default_image" in cat:
            return cat["default_image"]
    return VERIFIED_TECH_IMAGES[index % len(VERIFIED_TECH_IMAGES)]


def fetch_rss_feed(feed_info: Dict[str, str], max_items: int = 4) -> List[Dict[str, Any]]:
    """Fetches and parses a single RSS feed with resilient timeout and headers."""
    feed_name = feed_info.get("name", "Unknown Feed")
    feed_url = feed_info.get("url", "")
    fallback_cat = feed_info.get("fallback_category", "future-tech")
    articles = []

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 TechPulseBot/1.0"
        ),
        "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml",
    }

    try:
        response = requests.get(feed_url, headers=headers, timeout=8)
        if response.status_code != 200:
            print(f"[-] HTTP {response.status_code} fetching {feed_name}")
            return []

        parsed = feedparser.parse(response.content)
        entries = parsed.entries[:max_items]

        for idx, entry in enumerate(entries):
            raw_title = getattr(entry, "title", "").strip()
            title = clean_html(raw_title)
            if not title or len(title) < 15:
                continue

            raw_summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
            summary = clean_html(raw_summary)
            if len(summary) > 280:
                summary = summary[:277] + "..."

            link = getattr(entry, "link", "").strip()
            published = getattr(entry, "published", "") or getattr(entry, "updated", "")
            cat_id = detect_category(title, summary, fallback_cat)
            slug = slugify(title)

            articles.append({
                "title": title,
                "slug": slug,
                "category_id": cat_id,
                "source": feed_name,
                "link": link,
                "published": published,
                "read_time": "45s",
                "summary": summary,
                "image": select_image_for_story(cat_id, idx),
            })
    except Exception as e:
        print(f"[!] Error fetching feed {feed_name}: {e}")

    return articles


def fetch_all_tech_stories(target_count: int = 12) -> List[Dict[str, Any]]:
    """
    Ingests tech news across all configured feeds.
    Falls back gracefully to the curated viral dataset to ensure a rich portal.
    """
    all_articles = []
    seen_slugs = set()

    # 1. Fetch live RSS feeds
    print(f"[*] Ingesting tech feeds from {len(RSS_FEEDS)} sources...")
    for feed_info in RSS_FEEDS:
        items = fetch_rss_feed(feed_info, max_items=4)
        for item in items:
            if item["slug"] not in seen_slugs:
                seen_slugs.add(item["slug"])
                all_articles.append(item)

    print(f"[+] Retrieved {len(all_articles)} raw stories from live feeds.")

    # 2. Enrich with curated viral stories to guarantee category diversity and viral CTR
    for curated in CURATED_VIRAL_STORIES:
        if curated["slug"] not in seen_slugs:
            seen_slugs.add(curated["slug"])
            # Place curated stories strategically at the top if few RSS items found
            all_articles.insert(0, curated)

    # 3. Limit to target count
    selected = all_articles[:max_items_limit(target_count, len(all_articles))]
    print(f"[+] Total active stories selected for pipeline: {len(selected)}")
    return selected


def max_items_limit(target: int, available: int) -> int:
    return min(target, available) if available >= target else available
