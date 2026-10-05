"""
TechPulse Story Synthesizer
Transforms raw tech articles into high-CTR 5-slide Google AMP Web Stories.
Powered by Google Gemini 3.8 Flash (with robust deterministic rule-based fallback).
"""

import os
import json
import re
from typing import Dict, Any, List, Optional

from config import GEMINI_API_KEY, GEMINI_MODEL, SITE_NAME, VERIFIED_TECH_IMAGES


def synthesize_story(article: Dict[str, Any], index: int = 0) -> Dict[str, Any]:
    """
    Synthesizes a 5-slide story structure from an article.
    If pre-crafted slides already exist, returns them.
    Otherwise attempts Gemini API, falling back to deterministic heuristic rules.
    """
    # 1. Check if the article already has high-quality curated slides
    if "slides" in article and len(article["slides"]) == 5:
        return article

    title = article.get("title", "Tech Breakthrough")
    summary = article.get("summary", "")
    category_id = article.get("category_id", "future-tech")
    primary_image = article.get("image", VERIFIED_TECH_IMAGES[index % len(VERIFIED_TECH_IMAGES)])

    # 2. Attempt Gemini API if key is configured
    slides = None
    if GEMINI_API_KEY and len(GEMINI_API_KEY.strip()) > 10:
        try:
            print(f"[*] Calling Gemini ({GEMINI_MODEL}) for story: {title[:40]}...")
            slides = call_gemini_synthesizer(title, summary, category_id, primary_image, index)
            if slides and len(slides) == 5:
                article["slides"] = slides
                article["synthesizer"] = "gemini-3.8-flash"
                return article
        except Exception as e:
            print(f"[!] Gemini synthesis failed, falling back to rule-based engine: {e}")

    # 3. Deterministic rule-based fallback engine
    print(f"[*] Generating deterministic 5-slide story for: {title[:40]}...")
    slides = generate_rule_based_slides(title, summary, category_id, primary_image, index)
    article["slides"] = slides
    article["synthesizer"] = "deterministic-rule-engine"
    return article


def call_gemini_synthesizer(
    title: str, summary: str, category_id: str, primary_image: str, index: int
) -> Optional[List[Dict[str, Any]]]:
    """
    Calls Google Gemini API using google-genai SDK to generate structured 5-slide JSON.
    """
    from google import genai

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""You are an elite Silicon Valley tech journalist and Web Stories architect for "{SITE_NAME}".
Create a 5-slide Google AMP Web Story based on this tech story:
Title: {title}
Summary: {summary}
Category: {category_id}

Slide Specifications (Strictly 5 slides):
- Slide 1: High-curiosity hook & punchy headline.
- Slide 2: Core breakthrough, key reveal, or problem being solved.
- Slide 3: Deep dive specs, actionable details, or benchmarks.
- Slide 4: Competitive edge, secret advantage, or why it matters.
- Slide 5: Verdict, future impact, and "{SITE_NAME} Verdict" takeaway.

Format your response as a valid JSON array of exactly 5 slide objects, with NO markdown code fences, NO formatting text, ONLY pure JSON.
Each object must contain these string keys:
- "hook": Short uppercase curiosity tag (e.g. "THE BREAKTHROUGH", "CHIP ARCHITECTURE")
- "title": Punchy slide headline (under 8 words, bold)
- "badge": Vibrant cyberpunk badge (e.g. "⚡ 3.4X FASTER", "🔥 ZERO LATENCY", "🔍 200MP OPTICS", "⚡ TECHPULSE VERDICT")
- "bullet1": First takeaway sentence (informative, snappiest tech facts)
- "bullet2": Second takeaway sentence (forward-looking or actionable)
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        text = response.text.strip()
        # Clean any accidental markdown markers
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        slides_data = json.loads(text)
        if isinstance(slides_data, list) and len(slides_data) == 5:
            # Attach imagery to each slide
            for i, s in enumerate(slides_data):
                img_idx = (index + i) % len(VERIFIED_TECH_IMAGES)
                s["image"] = primary_image if i == 0 else VERIFIED_TECH_IMAGES[img_idx]
            return slides_data
    except Exception as e:
        print(f"[!] Error parsing Gemini response: {e}")

    return None


def generate_rule_based_slides(
    title: str, summary: str, category_id: str, primary_image: str, index: int
) -> List[Dict[str, Any]]:
    """
    Intelligent deterministic tech journalism synthesizer.
    Generates compelling 5-slide stories with high-CTR hooks, badges, and takeaways.
    """
    # Clean and split summary sentences
    sentences = [s.strip() for s in re.split(r"[.!?]+", summary) if len(s.strip()) > 15]
    if not sentences:
        sentences = [
            "Engineers and researchers reveal significant architectural breakthroughs.",
            "Benchmarking demonstrates massive performance and efficiency improvements over current standards.",
            "Consumer and enterprise hardware deployments are expected to begin immediately.",
        ]

    # Category-specific theme badges and hooks
    cat_themes = {
        "ai-tools": {
            "hook1": "AI BREAKTHROUGH UNVEILED",
            "badge1": "🤖 NEURAL ENGINE",
            "hook2": "AUTONOMOUS SPEED",
            "badge2": "⚡ 10X ACCELERATION",
            "hook3": "KEY CAPABILITIES",
            "badge3": "🧠 DEEP REASONING",
            "hook4": "REAL-WORLD VALUE",
            "badge4": "🔥 0ms LATENCY",
            "verdict": f"⚡ {SITE_NAME} VERDICT",
        },
        "smartphones": {
            "hook1": "FLAGSHIP HARDWARE LEAK",
            "badge1": "📱 SILICON REVEAL",
            "hook2": "NEXT-GEN OPTICS",
            "badge2": "🔍 200MP MATRIX",
            "hook3": "BATTERY & CHARGING",
            "badge3": "⚡ 100W POWER",
            "hook4": "PERFORMANCE BENCHMARK",
            "badge4": "🚀 2nm CHIPSET",
            "verdict": f"⚡ {SITE_NAME} VERDICT",
        },
        "gadgets": {
            "hook1": "WEARABLE REVOLUTION",
            "badge1": "🎧 AUDIO HORIZON",
            "hook2": "NEURAL NOISE CANCELLATION",
            "badge2": "🔇 52dB REDUCTION",
            "hook3": "BATTERY INNOVATION",
            "badge3": "🔋 48H ENDURANCE",
            "hook4": "ERGONOMIC DESIGN",
            "badge4": "💎 TITANIUM BUILD",
            "verdict": f"⚡ {SITE_NAME} VERDICT",
        },
        "future-tech": {
            "hook1": "FRONTIER COMPUTING",
            "badge1": "⚡ QUANTUM SHIFT",
            "hook2": "BREAKTHROUGH SILICON",
            "badge2": "🔬 NANOMETER SCALE",
            "hook3": "LAB BENCHMARKS",
            "badge3": "📊 3,400X SPEEDUP",
            "hook4": "GLOBAL IMPACT",
            "badge4": "🌐 INDUSTRY STANDARD",
            "verdict": f"⚡ {SITE_NAME} VERDICT",
        },
        "gaming-gear": {
            "hook1": "NEXT-GEN HANDHELD RIG",
            "badge1": "🎮 120Hz OLED",
            "hook2": "GRAPHICS SILICON",
            "badge2": "⚡ 90+ FPS AAA",
            "hook3": "TACTILE CONTROLS",
            "badge3": "🕹️ ZERO DRIFT",
            "hook4": "BATTERY & COOLING",
            "badge4": "❄️ CRYO-COOLING",
            "verdict": f"⚡ {SITE_NAME} VERDICT",
        },
    }

    theme = cat_themes.get(category_id, cat_themes["future-tech"])

    # Slide 1: Hook & Poster
    slide1 = {
        "hook": theme["hook1"],
        "title": title[:65] + ("..." if len(title) > 65 else ""),
        "badge": theme["badge1"],
        "bullet1": sentences[0] if len(sentences) > 0 else "New frontier specs shatter previous performance records.",
        "bullet2": "A massive visual paradigm shift for early adopters and tech professionals.",
        "image": primary_image,
    }

    # Slide 2: Core breakthrough
    slide2 = {
        "hook": theme["hook2"],
        "title": "Architectural Shift & The Core Discovery",
        "badge": theme["badge2"],
        "bullet1": sentences[1] if len(sentences) > 1 else "Hardware optimizations dramatically reduce power draw and latency.",
        "bullet2": "Engineered from the ground up to solve critical bottlenecks in legacy consumer devices.",
        "image": VERIFIED_TECH_IMAGES[(index + 1) % len(VERIFIED_TECH_IMAGES)],
    }

    # Slide 3: Specs & Deep Dive
    slide3 = {
        "hook": theme["hook3"],
        "title": "Hardware Specs & Real-World Metrics",
        "badge": theme["badge3"],
        "bullet1": sentences[2] if len(sentences) > 2 else "Independent lab benchmarks verify substantial efficiency and throughput gains.",
        "bullet2": "Next-generation thermal dissipation keeps peak performance sustained under heavy loads.",
        "image": VERIFIED_TECH_IMAGES[(index + 2) % len(VERIFIED_TECH_IMAGES)],
    }

    # Slide 4: Market Advantage
    slide4 = {
        "hook": theme["hook4"],
        "title": "Why This Shakes The Entire Industry",
        "badge": theme["badge4"],
        "bullet1": "Direct competition is forced to rethink roadmaps as technological barriers crumble.",
        "bullet2": "Early commercial availability brings enterprise-grade performance into consumer hands.",
        "image": VERIFIED_TECH_IMAGES[(index + 3) % len(VERIFIED_TECH_IMAGES)],
    }

    # Slide 5: Verdict & Call to Action
    slide5 = {
        "hook": "THE BOTTOM LINE",
        "title": f"{SITE_NAME} Verdict: A Must-Watch Leap",
        "badge": theme["verdict"],
        "bullet1": f"This leap marks an undeniable milestone in modern tech evolution.",
        "bullet2": "Tap the link below to dive deeper into full technical documentation and analysis.",
        "image": VERIFIED_TECH_IMAGES[(index + 4) % len(VERIFIED_TECH_IMAGES)],
    }

    return [slide1, slide2, slide3, slide4, slide5]
