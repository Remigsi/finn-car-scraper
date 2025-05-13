
# src/data_handler.py

import json
import subprocess
import logging
import sys
import os

# Get the project root directory (one level up from src/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'finn_cars.json')

def save_data(data, max_entries=10000):
    data = sorted(data, key=lambda x: x.get("No", 0))

    if len(data) > max_entries:
        data = data[-max_entries:]

    # Ensure data directory exists
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logging.info(f"💾 Saved {len(data)} entries to '{DATA_PATH}'")

    try:
        # Use absolute path for best_match script
        best_match_script = os.path.join(BASE_DIR, 'src', 'finn_cars_best_match.py')
        subprocess.run([sys.executable, best_match_script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running finn_cars_best_match.py: {e}")