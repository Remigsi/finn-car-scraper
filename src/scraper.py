# src/scraper.py

from playwright.sync_api import sync_playwright, TimeoutError
from urllib.parse import urljoin
import logging
import time
import re

BASE_URL = "https://www.finn.no"

def accept_cookie_consent(page):
    try:
        iframe = page.wait_for_selector("iframe[id^='sp_message_iframe_']", timeout=8000)
        frame = iframe.content_frame()
        frame.click("button.sp_choice_type_11", timeout=5000)
        logging.info("✅ Cookie consent accepted.")
        time.sleep(0.5)
    except TimeoutError:
        logging.warning("⚠️ Cookie consent iframe not found.")
    except Exception:
        logging.warning("⚠️ Error accepting cookie consent.")

def go_to_next_page(page, page_number):
    try:
        next_btn = page.query_selector("a:has-text('Neste')")
        if not next_btn or not next_btn.is_enabled():
            logging.info("✅ Reached last page.")
            return False
        next_btn.click()
        time.sleep(1)
        return True
    except Exception:
        logging.info("✅ No more pages (or navigation failed).")
        return False

def scrape_finn_cars(return_data=False):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
            viewport={"width": 1280, "height": 800},
            locale="no-NO"
        )
        page = context.new_page()

        page.goto("https://www.finn.no/mobility/search/car?registration_class=1", timeout=30000)
        accept_cookie_consent(page)

        car_data = []
        page_number = 1

        while True:
            logging.info(f"📄 Scraping page {page_number}...")
            try:
                page.wait_for_selector("article.sf-search-ad", timeout=8000)
            except TimeoutError:
                logging.warning("⏱️ Listings not found, skipping page.")
                break

            listings = page.query_selector_all("article.sf-search-ad")

            for listing in listings:
                try:
                    title_elem = listing.query_selector("h2 a")
                    title = title_elem.inner_text().strip()
                    href = title_elem.get_attribute("href")
                    ad_url = urljoin(BASE_URL, href)

                    title_elem = listing.query_selector("h2 a")
                    price_elem = listing.query_selector("span.t3.font-bold")
                    details_elem = listing.query_selector("span.text-caption.font-bold")
                    location_elem = listing.query_selector("div.text-detail span:first-child")

                    if not (title_elem and price_elem and details_elem and location_elem):
                        raise ValueError("Missing required fields")

                    title = title_elem.inner_text().strip()
                    raw_price = price_elem.inner_text().strip()
                    details_text = details_elem.inner_text().strip()
                    location = location_elem.inner_text().strip()

                    price_digits = re.sub(r"\D", "", raw_price)
                    price = int(price_digits) if price_digits else None

                    details_text = listing.query_selector("span.text-caption.font-bold").inner_text()
                    details = details_text.split(" ∙ ")
                    year = int(details[0]) if len(details) > 0 and details[0].isdigit() else None
                    mileage_digits = re.sub(r"\D", "", details[1]) if len(details) > 1 else ""
                    mileage = int(mileage_digits) if mileage_digits else None
                    transmission = details[2] if len(details) > 2 else "N/A"
                    fuel = details[3] if len(details) > 3 else "N/A"

                    location = listing.query_selector("div.text-detail span:first-child").inner_text().strip()
                    ad_id_elem = listing.query_selector("div.absolute[aria-owns^='search-ad-']")
                    ad_id = ad_id_elem.get_attribute("aria-owns").replace("search-ad-", "") if ad_id_elem else "N/A"

                    # ✅ Custom filtering logic
                    if (price is None or price > 10000 or
                            year is None or year < 2020 or
                            mileage is None or mileage > 100000):
                        continue

                    # ✅ Visit ad page to check for Månedspris
                    detail_page = context.new_page()
                    detail_page.goto(ad_url, timeout=10000)
                    detail_page.wait_for_timeout(2000)  # allow lazy content to load

                    # Check if element exists
                    has_monthly = detail_page.query_selector("p.s-text-subtle.mb-0")
                    if has_monthly:
                        text = has_monthly.inner_text().strip()
                        if "Månedspris" in text:
                            logging.warning(f"🚫 Skipped Månedspris ad: {ad_url}")
                            detail_page.close()
                            continue

                    # ✅ Keep the ad
                    car_data.append({
                        "Annonse ID": ad_id,
                        "Title": title,
                        "Price": price,
                        "Year": year,
                        "Mileage": mileage,
                        "Transmission": transmission,
                        "Fuel": fuel,
                        "Location": location,
                        "URL": ad_url
                    })
                    detail_page.close()

                except Exception as e:
                    logging.warning(f"⚠️ Failed to process one listing: {e}")
                    continue

            if not go_to_next_page(page, page_number):
                break
            page_number += 1

        browser.close()

        if return_data:
            return car_data
