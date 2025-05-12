# src/finn_cars_best_match.py


import sys
import os
import pandas as pd
import json

# Get the project root directory (one level up from src/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'finn_cars.json')
OUTPUT_PATH = os.path.join(BASE_DIR, 'data', 'sorted_cars.json')

try:
    # Verify file exists
    if not os.path.exists(DATA_PATH):
        print(f"❌ Error: '{DATA_PATH}' does not exist. Run main.py from the project root to generate it.")
        sys.exit(1)

    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    # Clean numeric fields
    df['Price'] = pd.to_numeric(df['Price'].astype(str).str.replace(r'\D', '', regex=True), errors='coerce')
    df['Mileage'] = pd.to_numeric(df['Mileage'].astype(str).str.replace(r'\D', '', regex=True), errors='coerce')
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')

    df.dropna(subset=['Year', 'Price', 'Mileage'], inplace=True)

    # Compute score
    df['score'] = (
        df['Year'].rank(ascending=False) +
        df['Mileage'].rank(ascending=True) +
        df['Price'].rank(ascending=True) * 10
    )

    df_sorted = df.sort_values(by='score').head(20000)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(df_sorted.to_dict(orient='records'), f, ensure_ascii=False, indent=2)

    print(f"✅ Saved top {len(df_sorted)} best-matched ads to '{OUTPUT_PATH}'")
except Exception as e:
    print(f"❌ Error in best-match analysis: {e}")
    sys.exit(1)

docs_output_path = os.path.join(BASE_DIR, 'docs', 'sorted_cars.json')
os.makedirs(os.path.dirname(docs_output_path), exist_ok=True)
with open(docs_output_path, 'w', encoding='utf-8') as f:
    json.dump(df_sorted.to_dict(orient='records'), f, ensure_ascii=False, indent=2)