# main.py

from src.scraper import scrape_finn_cars
from src.data_handler import save_data
import os
import json
import time

DATA_FILE = "data/finn_cars.json"
INTERVAL_MINUTES = 15

def load_existing_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def run_loop():
    all_ads = load_existing_data()
    known_ids = {item["Annonse ID"] for item in all_ads}
    last_no = max((item.get("No", 0) for item in all_ads), default=0)

    print(f"🔁 Scraping every {INTERVAL_MINUTES} min. Press Ctrl+C to stop.")

    try:
        while True:
            print("\n⏳ Scraping new data...")
            new_ads = scrape_finn_cars(return_data=True)
            added = 0

            for ad in new_ads:
                if ad["Annonse ID"] not in known_ids:
                    last_no += 1
                    ad["No"] = last_no
                    all_ads.append(ad)
                    known_ids.add(ad["Annonse ID"])
                    added += 1

            print(f"🆕 Added {added} new ads.")
            save_data(all_ads)  # Trims to 10,000 and runs best match script
            time.sleep(INTERVAL_MINUTES * 60)
    except KeyboardInterrupt:
        print("\n❌ Scraper stopped by user.")

if __name__ == "__main__":
    run_loop()
