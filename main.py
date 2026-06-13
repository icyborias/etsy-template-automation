import os
import argparse
import glob
import time
from scout import run_scan
from brief import generate_brief
from listing_writer import generate_listing
from dotenv import load_dotenv

from config import NICHES, BRIEFS_DIR

load_dotenv()


def orchestrate():
    scout = run_scan()
    brief_paths = []
    # For each niche, pick top idea and generate brief
    for niche in scout["niches"]:
        nk = niche["niche"]
        top = niche["results"][0]
        idea = top["keyword"]
        print("Generating brief for", nk, idea)
        path = generate_brief(nk, idea)
        brief_paths.append(path)
    # Generate listing stubs for top ideas
    listing_paths = []
    for b in brief_paths:
        nk = os.path.basename(b).split("-brief-")[1].split(".md")[0]
        title = f"{nk} template"
        lp = generate_listing(nk, title, open(b, "r", encoding="utf-8").read())
        listing_paths.append(lp)
    print("Orchestration complete. Briefs:", brief_paths)
    return {
        "scout": scout,
        "briefs": brief_paths,
        "listings": listing_paths,
    }


if __name__ == "__main__":
    orchestrate()
