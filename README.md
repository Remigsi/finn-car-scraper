# 🚗 FINN.no Car Scraper & Best Deal Analyzer

A full-stack automated data pipeline for scraping used car listings from [FINN.no](https://www.finn.no/), ranking them based on value, and publishing the top listings to a lightweight GitHub Pages dashboard.

Built with Playwright for headless web scraping, pandas for data processing and scoring, and GitHub Pages for public data hosting—no backend required.

---

## 🌟 Key Features

- 🔁 **Automatic Scraping Loop**  
  Runs continuously every 15 minutes (configurable) to fetch the latest car listings.

- 🧠 **Intelligent Ranking Algorithm**  
  Each listing is scored based on:
  - ✅ Lower Price (weighted ×10)
  - ✅ Lower Mileage
  - ✅ Newer Year

- 📊 **Lightweight Data Output**  
  Outputs the top 20,000 ranked listings to a viewer-optimized JSON file.

- 🌐 **GitHub Pages Frontend**  
  View top cars live via a static HTML/JS viewer. No backend or server required.

- 📁 **Full Logging**  
  Rotating logs to `logs/main.log` for easy debugging and tracking.

---

## 🗂️ Project Structure

```bash
finn-car-scraper/
├── main.py                    # Orchestrates scraping and saving
├── data/
│   ├── finn_cars.json         # Full dataset of scraped ads (latest 10k)
│   └── sorted_cars.json       # Ranked results (top 20k)
├── docs/                      # GitHub Pages frontend (viewer UI + JSON)
│   └── sorted_cars.json       # Synced JSON for frontend
├── logs/
│   └── main.log               # Rotating log of scraper activity
├── src/
│   ├── scraper.py             # Playwright-based scraper
│   ├── data_handler.py        # Saves and triggers ranking
│   └── finn_cars_best_match.py # Scoring and ranking script
├── requirements.txt           # Python dependencies
└── README.md                  # You're here!
```

---

## 🛠️ Tech Stack

- Python 3.10+
- Playwright (headless browser automation)
- pandas (data analysis)
- JSON (storage + frontend-friendly)
- GitHub Actions (optional: for automated deploy)
- GitHub Pages (public viewer)

---

## 🔧 Setup Instructions

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/finn-car-scraper.git
   cd finn-car-scraper
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

3. Run the scraper loop:
   ```bash
   python main.py
   ```

4. View output in `data/sorted_cars.json`, or serve via GitHub Pages.

---

## 🧪 Sample Output (JSON format)

```json
{
  "Annonse ID": "123456789",
  "Title": "Toyota Yaris 2020",
  "Price": 89000,
  "Year": 2020,
  "Mileage": 67000,
  "Transmission": "Automatic",
  "Fuel": "Petrol",
  "Location": "Oslo",
  "No": 54321
}
```

---

## 📈 Future Improvements

- Add Telegram/Email alerts for best deals
- Add make/model/region filters
- Add thumbnail previews

---

## 🔐 Disclaimer

This tool is intended for educational and research purposes only. It respects FINN.no's fair use policies. No scraping of user data or personal information is involved.