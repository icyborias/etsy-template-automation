import json
import os
import time
from typing import List, Dict

from pytrends.request import TrendReq

from config import NICHES, TRENDS_REGION, TRENDS_TIMEFRAME, OUTPUT_DIR


def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/briefs", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/listings", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/mockups", exist_ok=True)


def get_trends_for_keyword(pytrends: TrendReq, kw: str) -> Dict:
    try:
        pytrends.build_payload([kw], timeframe=TRENDS_TIMEFRAME, geo=TRENDS_REGION)
        data = pytrends.interest_over_time()
        if data.empty:
            return {"keyword": kw, "scores": [], "rising": []}
        scores = data[kw].tolist()
        rising = []
        try:
            related = pytrends.related_queries()
            rising_q = related.get(kw, {}).get("rising")
            if isinstance(rising_q, dict) and "query" in rising_q:
                rising = rising_q["query"].tolist()
            elif isinstance(rising_q, list):
                rising = [r["query"] for r in rising_q]
        except Exception:
            rising = []
        return {"keyword": kw, "scores": scores, "rising": rising}
    except Exception as e:
        return {"keyword": kw, "error": str(e)}


def scan_niche(niche_key: str, top_n: int = 5) -> Dict:
    pytrends = TrendReq(hl="en-US", tz=360)
    niche = NICHES[niche_key]
    results = []
    for kw in niche["seed_keywords"]:
        info = get_trends_for_keyword(pytrends, kw)
        # naive opportunity score: latest score + number of rising queries
        scores = info.get("scores") or []
        latest = scores[-1] if scores else 0
        rising_count = len(info.get("rising") or [])
        opportunity = round(latest + rising_count * 5, 2)
        results.append({"keyword": kw, "latest": latest, "rising": info.get("rising"), "opportunity": opportunity})
        time.sleep(1)

    results_sorted = sorted(results, key=lambda r: r["opportunity"], reverse=True)[:top_n]
    return {"niche": niche_key, "results": results_sorted}


def run_scan() -> Dict:
    ensure_dirs()
    scout = {"date": time.strftime("%Y-%m-%d"), "niches": []}
    for k in NICHES.keys():
        print("Scanning", k)
        try:
            res = scan_niche(k)
            scout["niches"].append(res)
        except Exception as e:
            print("Error scanning niche", k, e)
    # save scout
    outpath = f"{OUTPUT_DIR}/briefs/{scout['date']}-scout.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(scout, f, indent=2)
    return scout


if __name__ == "__main__":
    run_scan()
