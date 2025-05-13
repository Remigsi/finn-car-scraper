# 🚗 finn.no Car Scraper & Best Match Viewer

A full-stack data pipeline to **scrape used car listings from FINN.no**, **rank them by best deal**, and **publish the top results** to a public GitHub Pages viewer.

Built with [Playwright](https://playwright.dev/) for fast headless browsing, `pandas` for data analysis, and auto-synced with GitHub Pages for a live dashboard.

---

## 🌟 Features

- 🔁 **Scheduled Scraping Loop** (every 15 min by default)
- 🧠 **Ranking Algorithm** (price, mileage, and year weighted)
- 📊 **Top 20,000 Cars Published** to a web-friendly JSON
- 🌐 **HTML Viewer** for GitHub Pages (zero backend required)
- 📁 **Auto-Logs** all activities to `logs/main.log`

---

## 📦 Project Structure

