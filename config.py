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

# High-resolution vertical imagery pool (2:3 / 9:16 aspect ratio, verified Unsplash CDN)
VERIFIED_TECH_IMAGES = [
    "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=720&q=80", # Cyber neon abstract
    "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=720&q=80", # Sleek MacBook laptop
    "https://images.unsplash.com/photo-1518770660439-4636190af475?w=720&q=80", # Microchip circuit
    "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=720&q=80", # Smartphone close-up
    "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=720&q=80", # Modern glowing laptop
    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=720&q=80", # Premium headphones
    "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=720&q=80", # Cyberpunk gaming rig
    "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=720&q=80", # Ultrabook laptop
    "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=720&q=80", # Sleek mobile display
    "https://images.unsplash.com/photo-1546776310-eef45dd6d63c?w=720&q=80", # Robotics AI arm
    "https://images.unsplash.com/photo-1593508512255-86ab42a8e620?w=720&q=80", # AR/VR futuristic glasses
    "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=720&q=80", # Matrix cyber code
    "https://images.unsplash.com/photo-1535223289827-42f1e9919769?w=720&q=80", # Quantum computing lights
    "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=720&q=80", # Gaming console controller
    "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=720&q=80", # Flagship camera smartphone
]
