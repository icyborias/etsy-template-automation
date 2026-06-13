from typing import Dict, List

NICHES: Dict[str, Dict] = {
    "luxury_real_estate": {
        "display_name": "Luxury Real Estate",
        "seed_keywords": [
            "luxury real estate social media carousel",
            "just sold carousel",
            "real estate listing carousel",
            "luxury realtor instagram template",
        ],
    },
    "birthday_magazine": {
        "display_name": "Birthday Magazines",
        "seed_keywords": [
            "birthday magazine template",
            "birthday memory book",
            "party program template",
            "birthday magazine layout",
        ],
    },
    "airbnb_welcome_book": {
        "display_name": "Airbnb Welcome Books",
        "seed_keywords": [
            "airbnb welcome book template",
            "guest welcome guide",
            "airbnb guest manual",
            "short term rental welcome book",
        ],
    },
}

# Google Trends settings
TRENDS_REGION = "US"
TRENDS_TIMEFRAME = "now 7-d"  # last 7 days for freshness

# Output paths
OUTPUT_DIR = "output"
BRIEFS_DIR = f"{OUTPUT_DIR}/briefs"
LISTINGS_DIR = f"{OUTPUT_DIR}/listings"
MOCKUPS_DIR = f"{OUTPUT_DIR}/mockups"
