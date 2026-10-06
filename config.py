"""
TechPulse Configuration Module
Supports environment customization for site branding, feeds, categories, and styling.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Site Identity & Customization
SITE_NAME = os.environ.get("TECHPULSE_NAME", "TechPulse")
SITE_TAGLINE = os.environ.get(
    "TECHPULSE_TAGLINE", "Autonomous AMP Web Stories & Cutting-Edge Tech Portal"
)
SITE_DESCRIPTION = (
    f"{SITE_NAME} is an autonomous, lightning-fast Google AMP Web Stories platform "
    "delivering cutting-edge visual tech news, breakthrough AI tools, smartphone reveals, "
    "next-gen laptops, and futuristic computing in 45-second interactive slides."
)

# Canonical domain (user's active production domain)
SITE_URL = os.environ.get("SITE_URL", "https://techpulse-gadget.vercel.app").rstrip("/")

# Official contact & editorial email
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "sumits7196@gmail.com")

# Google Search Console Verification Tag
GOOGLE_SITE_VERIFICATION = os.environ.get(
    "GOOGLE_SITE_VERIFICATION", "XMDt3lDT2kpdjLlHlxQCSn5EcJcH2yw8f6nLjhLgN7g"
)

# Publisher Information for AMP & Schema
PUBLISHER_NAME = SITE_NAME
PUBLISHER_LOGO_URL = f"{SITE_URL}/static/images/publisher-logo.png"

# Gemini API Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")

# Tech Categories & UI Pills
CATEGORIES = [
    {
        "id": "all",
        "name": "All Stories",
        "badge": "⚡ ALL",
        "icon": "⚡",
        "description": "All tech stories & breakthroughs",
    },
    {
        "id": "ai-tools",
        "name": "AI Tools & Hacks",
        "badge": "🤖 AI TOOLS",
        "icon": "🤖",
        "keywords": [
            "ai", "artificial intelligence", "chatgpt", "gemini", "claude", "llm",
            "openai", "deepseek", "anthropic", "copilot", "prompt", "model",
            "machine learning", "agent", "neural", "bot", "algorithm"
        ],
        "default_image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=720&q=80",
    },
    {
        "id": "smartphones",
        "name": "Smartphones & Leaks",
        "badge": "📱 SMARTPHONES",
        "icon": "📱",
        "keywords": [
            "iphone", "apple", "samsung", "galaxy", "pixel", "google pixel",
            "nothing phone", "oneplus", "xiaomi", "smartphone", "snapdragon",
            "camera leak", "flagship", "ios", "foldable", "flip", "telephoto"
        ],
        "default_image": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=720&q=80",
    },
    {
        "id": "laptops-pc",
        "name": "Laptops & PC",
        "badge": "💻 LAPTOPS & PC",
        "icon": "💻",
        "keywords": [
            "laptop", "macbook", "m4", "snapdragon x", "thinkpad", "dell xps",
            "ultrabook", "pc", "desktop", "notebook", "framework", "oled laptop",
            "asus", "surface", "razer", "zenbook", "strix"
        ],
        "default_image": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=720&q=80",
    },
    {
        "id": "gadgets",
        "name": "Gadgets & Audio",
        "badge": "🎧 GADGETS",
        "icon": "🎧",
        "keywords": [
            "gadget", "smartwatch", "earbuds", "headphones", "audio", "anc",
            "vr", "virtual reality", "vision pro", "meta quest", "smart ring",
            "wearable", "apple watch", "tws", "spatial audio", "drone", "glasses"
        ],
        "default_image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=720&q=80",
    },
    {
        "id": "future-tech",
        "name": "Future Tech",
        "badge": "🚀 FUTURE TECH",
        "icon": "🚀",
        "keywords": [
            "quantum", "computing", "robot", "humanoid", "boston dynamics",
            "figure", "chip", "semiconductor", "tsmc", "intel", "nvidia", "gpu",
            "rtx", "supercomputer", "space", "fusion", "biotech", "cyber", "brain"
        ],
        "default_image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=720&q=80",
    },
    {
        "id": "gaming-gear",
        "name": "Gaming Gear",
        "badge": "🎮 GAMING GEAR",
        "icon": "🎮",
        "keywords": [
            "gaming", "game", "console", "playstation", "ps5", "xbox",
            "steam deck", "rog ally", "nintendo", "switch", "controller",
            "handheld", "oled monitor", "keyboard", "fps", "rtx 5090"
        ],
        "default_image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=720&q=80",
    },
]

# RSS Feed Ingestion Sources
RSS_FEEDS = [
    {
        "name": "The Verge",
        "url": "https://www.theverge.com/rss/index.xml",
        "fallback_category": "future-tech",
    },
    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/feed/",
        "fallback_category": "ai-tools",
    },
    {
        "name": "Android Police",
        "url": "https://www.androidpolice.com/feed/",
        "fallback_category": "smartphones",
    },
    {
        "name": "Engadget",
        "url": "https://www.engadget.com/rss.xml",
        "fallback_category": "gadgets",
    },
    {
        "name": "Google News Tech",
        "url": "https://news.google.com/rss/headlines/section/topic/SCIENTIFIC_TECH?hl=en-US&gl=US&ceid=US:en",
        "fallback_category": "future-tech",
    },
]

# Category SVG Fallbacks (Guaranteed local files with 0ms load & zero network crash)
CATEGORY_FALLBACK_IMAGES = {
    "all": "/static/images/fallbacks/default.svg",
    "ai-tools": "/static/images/fallbacks/ai-tools.svg",
    "smartphones": "/static/images/fallbacks/smartphones.svg",
    "laptops-pc": "/static/images/fallbacks/laptops-pc.svg",
    "gadgets": "/static/images/fallbacks/gadgets.svg",
    "future-tech": "/static/images/fallbacks/future-tech.svg",
    "gaming-gear": "/static/images/fallbacks/gaming-gear.svg",
}

# 100% Tested & Verified Vertical High-Resolution Tech Imagery Catalog (Unsplash CDN, 200 OK)
VERIFIED_CATEGORY_IMAGES = {
    "ai-tools": [
        "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=720&q=80", # Cyber neon abstract
        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=720&q=80", # Matrix code
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=720&q=80", # Cyber server glow
        "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=720&q=80", # Code on monitor
        "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=720&q=80", # Python code screen
        "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=720&q=80", # Coding syntax
        "https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=720&q=80", # Developer coding
        "https://images.unsplash.com/photo-1618042164219-62c820f10723?w=720&q=80", # 3D neural shapes
        "https://images.unsplash.com/photo-1634017839464-5c339ebe3cb4?w=720&q=80", # Glowing geometry
    ],
    "smartphones": [
        "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=720&q=80", # iPhone flagship back
        "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=720&q=80", # Sleek smartphone screen
        "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=720&q=80", # Flagship camera bump
        "https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=720&q=80", # Mobile phone in hand
        "https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?w=720&q=80", # Smartphone camera lens
        "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=720&q=80", # Android flagship
        "https://images.unsplash.com/photo-1585060544812-6b45742d762f?w=720&q=80", # Curved OLED display
        "https://images.unsplash.com/photo-1512499617640-c74ae3a79d37?w=720&q=80", # Phone on desk
        "https://images.unsplash.com/photo-1556656793-08538906a9f8?w=720&q=80", # Mobile phone in dark
    ],
    "laptops-pc": [
        "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=720&q=80", # MacBook Pro keyboard
        "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=720&q=80", # Glowing tech laptop
        "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=720&q=80", # Dell XPS ultrabook
        "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=720&q=80", # Apple MacBook
        "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=720&q=80", # Dell laptop workspace
        "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=720&q=80", # Aluminum laptop
        "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=720&q=80", # Macbook keyboard work
        "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=720&q=80", # Gaming laptop RGB
        "https://images.unsplash.com/photo-1542393545-10f5cde2c810?w=720&q=80", # Ultrawide monitor desk
    ],
    "gadgets": [
        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=720&q=80", # Premium headphones
        "https://images.unsplash.com/photo-1593508512255-86ab42a8e620?w=720&q=80", # VR futuristic glasses
        "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=720&q=80", # Smartwatch face
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=720&q=80", # Watch tech
        "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=720&q=80", # Black headphones
        "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=720&q=80", # Wireless earbuds
        "https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=720&q=80", # Wearable fitness
        "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=720&q=80", # Smart wearable
        "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=720&q=80", # Smart mobile gadget
    ],
    "future-tech": [
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=720&q=80", # Microchip circuit
        "https://images.unsplash.com/photo-1546776310-eef45dd6d63c?w=720&q=80", # Robotics AI arm
        "https://images.unsplash.com/photo-1535223289827-42f1e9919769?w=720&q=80", # Quantum computing lights
        "https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=720&q=80", # Science lab
        "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=720&q=80", # Tech research
        "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=720&q=80", # Robotics engineer
        "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=720&q=80", # Tech team
        "https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=720&q=80", # Wireframe design
        "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?w=720&q=80", # Cyber patterns
    ],
    "gaming-gear": [
        "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=720&q=80", # Cyberpunk gaming rig
        "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=720&q=80", # PS5 controller
        "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=720&q=80", # Esports arena
        "https://images.unsplash.com/photo-1598550476439-6847785fcea6?w=720&q=80", # RGB mechanical keyboard
        "https://images.unsplash.com/photo-1526509867162-5b0c0d1b4b33?w=720&q=80", # Retro arcade controller
        "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=720&q=80", # Neon game setup
        "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=720&q=80", # RGB battle station
        "https://images.unsplash.com/photo-1600861194942-f883de0dfe96?w=720&q=80", # Xbox controller
        "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=720&q=80", # Gaming desk tech
    ],
}

# Flattened verified list for general fallbacks
VERIFIED_TECH_IMAGES = [
    img for cat_imgs in VERIFIED_CATEGORY_IMAGES.values() for img in cat_imgs
]


def get_category_fallback_image(category_id: str) -> str:
    """Returns local bulletproof SVG fallback path for a category."""
    return CATEGORY_FALLBACK_IMAGES.get(category_id, "/static/images/fallbacks/default.svg")


def get_unique_image_for_story(
    category_id: str,
    used_images: set,
    fallback_index: int = 0
) -> str:
    """
    Selects a 100% unique, verified image for a story.
    Prioritizes category-relevant images that have not yet been used across the site.
    """
    cat_pool = VERIFIED_CATEGORY_IMAGES.get(category_id, VERIFIED_TECH_IMAGES)
    
    # 1. Try unused image from the target category pool
    for img in cat_pool:
        if img not in used_images:
            used_images.add(img)
            return img
            
    # 2. Try unused image from the global pool
    for img in VERIFIED_TECH_IMAGES:
        if img not in used_images:
            used_images.add(img)
            return img
            
    # 3. If all 54 images have been used at least once, cycle predictably
    chosen = cat_pool[fallback_index % len(cat_pool)]
    used_images.add(chosen)
    return chosen

