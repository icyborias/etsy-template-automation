import os
import time
import argparse
from typing import List

from dotenv import load_dotenv

from config import LISTINGS_DIR

load_dotenv()
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except Exception:
    Anthropic = None
    ANTHROPIC_AVAILABLE = False

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = None
if ANTHROPIC_AVAILABLE and ANTHROPIC_API_KEY:
    try:
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
    except Exception:
        client = None


PROMPT = """
You are an Etsy listing copywriter. Produce STRICT JSON only (no surrounding text) with these keys:
- `title`: a single string, max 140 characters
- `tags`: an array of exactly 13 short tag strings (no commas inside tags)
- `description`: a long description, 3-5 short paragraphs, buyer-focused
- `category`: a suggested Etsy category string

Constraints:
- Return valid JSON only. Example:
  {
    "title": "...",
    "tags": ["tag1","tag2",...],
    "description": "...",
    "category": "..."
  }

Niche: {niche}
Title (seed): {title}
Brief: {brief}
"""


def ensure_dir():
    os.makedirs(LISTINGS_DIR, exist_ok=True)


def generate_listing(niche: str, title: str, brief: str = "") -> str:
    ensure_dir()
    filename = f"{LISTINGS_DIR}/{time.strftime('%Y-%m-%d')}-listing-{niche}.json"
    if client is None:
        stub = {"title": title[:140], "tags": [f"{niche}", "template", "etsy"], "description": "Description stub.", "category": "Home & Living"}
        with open(filename, "w", encoding="utf-8") as f:
            import json

            json.dump(stub, f, indent=2)
        return filename

    prompt = PROMPT.format(niche=niche, title=title, brief=brief)
    try:
        resp = client.completions.create(model="claude-2.1", prompt=prompt, max_tokens=800)
        text = resp.completion
    except Exception:
        text = ""

    # Parse JSON
    import json

    try:
        j = json.loads(text)
    except Exception:
        j = {"raw": text}
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(j, f, indent=2)
    return filename


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--niche", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--from-brief", required=False)
    args = p.parse_args()
    brief = ""
    if args.from_brief:
        with open(args.from_brief, "r", encoding="utf-8") as f:
            brief = f.read()
    print(generate_listing(args.niche, args.title, brief))
