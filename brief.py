import os
import time
import json
from typing import Dict

from anthropic import Anthropic
from dotenv import load_dotenv

from config import BRIEFS_DIR, NICHES

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = None
if ANTHROPIC_API_KEY:
    try:
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
    except Exception:
        client = None


def ensure_dir():
    os.makedirs(BRIEFS_DIR, exist_ok=True)


PROMPT_TEMPLATE = """
You are an expert product designer and seller-focused copywriter. Produce a concise, actionable design brief for an Etsy template.

Requirements:
- Output a Markdown document.
- At the very top include a JSON metadata fence with keys: `headline`, `fonts` (array of {"name","role"}), `colors` (array of {"hex","usage"}), `seller_description`, `plan` (array of step strings).
- After the JSON metadata, include human-friendly Markdown sections with headings: "Idea Headline", "Fonts", "Colors", "Seller Description", "First 90 Minutes Plan".
- Be specific: give exact font names (Google Fonts or common commercial fonts), provide HEX codes, and give a clear 90-minute step-by-step plan for building in Canva (each step 1-2 short sentences).
- Keep the whole brief scannable: short bullets and concise sentences.

Niche: {niche}
Idea: {idea}

Return only the Markdown document.
"""


def generate_brief(niche: str, idea: str) -> str:
    ensure_dir()
    filename = f"{BRIEFS_DIR}/{time.strftime('%Y-%m-%d')}-brief-{niche}.md"
    if client is None:
        # Fallback: simple stub markdown with JSON metadata block
        metadata = {
            "headline": idea,
            "fonts": [{"name": "Playfair Display", "role": "Headline"}, {"name": "Inter", "role": "Body"}, {"name": "Montserrat", "role": "Accent"}],
            "colors": [{"hex": "#000000", "usage": "Primary"}, {"hex": "#F5F5F5", "usage": "Background"}, {"hex": "#C59A6A", "usage": "Accent"}],
            "seller_description": f"A high-end {niche} template for {idea}.",
            "plan": ["Open Canva and create a new 1080x1350 canvas.", "Add headline and image placeholders.", "Apply color palette and fonts.", "Export PNG at high quality."]
        }
        md = "```json\n" + json.dumps(metadata, indent=2) + "\n```\n\n"
        md += f"# {idea}\n\n**Niche:** {niche}\n\n"
        md += "## Fonts\n- Playfair Display (Headline)\n- Inter (Body)\n- Montserrat (Accent)\n\n"
        md += "## Colors\n- #000000 Primary\n- #F5F5F5 Background\n- #C59A6A Accent\n\n"
        md += "## Seller Description\nA high-end template designed for professional sellers.\n\n"
        md += "## First 90 Minutes Plan\n"
        for i, s in enumerate(metadata["plan"], 1):
            md += f"{i}. {s}\n"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(md)
        return filename

    prompt = PROMPT_TEMPLATE.format(niche=niche, idea=idea)
    try:
        resp = client.messages.create(model="claude-3-5-sonnet-20241022", max_tokens=800, messages=[{"role": "user", "content": prompt}])
        text = resp.content[0].text
    except Exception:
        text = f"# {idea}\n\n**Niche:** {niche}\n\n- Fonts: ...\n"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    return filename


def parse_brief_metadata(path: str) -> dict:
    """Extract the leading JSON metadata fence from a brief markdown file.

    Returns parsed dict or empty dict on failure.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception:
        return {}
    # find first ```json ... ``` block
    start = text.find("```json")
    if start == -1:
        return {}
    end = text.find("```", start + 7)
    if end == -1:
        return {}
    json_text = text[start + 7:end].strip()
    try:
        return json.loads(json_text)
    except Exception:
        return {}


if __name__ == "__main__":
    print(generate_brief("luxury_real_estate", "Black & Cream Just Sold Carousel"))
