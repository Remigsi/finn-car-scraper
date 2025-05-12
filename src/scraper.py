# src/scraper.py

from playwright.sync_api import sync_playwright, TimeoutError
import time
import re


def accept_cookie_consent(page):
    try:
        iframe = page.wait_for_selector("iframe[id^='sp_message_iframe_']", timeout=8000)
        frame = iframe.content_frame()
        frame.click("button.sp_choice_type_11", timeout=5000)
        print("✅ Cookie consent accepted.")
        time.sleep(0.5)
    except TimeoutError:
        print("⚠️ Cookie consent iframe not found.")
    except Exception:
        print("⚠️ Error accepting cookie consent.")

def go_to_next_page(page, page_number):
    try:
        next_btn = page.query_selector("a:has-text('Neste')")
        if not next_btn or not next_btn.is_enabled():
            print("✅ Reached last page.")
            return False
        next_btn.click()
        time.sleep(1)
        return True
    except Exception:
        print("✅ No more pages (or navigation failed).")
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
            print(f"📄 Scraping page {page_number}...")
            try:
                page.wait_for_selector("article.sf-search-ad", timeout=8000)
            except TimeoutError:
                print("⏱️ Listings not found, skipping page.")
                break

            listings = page.query_selector_all("article.sf-search-ad")

            for listing in listings:
                try:
                    title = listing.query_selector("h2 a").inner_text().strip()
                    raw_price = listing.query_selector("span.t3.font-bold").inner_text().strip()
                    price = re.sub(r"(?<=\d)\s+(?=\d)", "", raw_price.replace("kr", "")).strip()

                    details_text = listing.query_selector("span.text-caption.font-bold").inner_text()
                    details = details_text.split(" ∙ ")
                    year = details[0] if len(details) > 0 else "N/A"
                    mileage = details[1] if len(details) > 1 else "N/A"
                    transmission = details[2] if len(details) > 2 else "N/A"
                    fuel = details[3] if len(details) > 3 else "N/A"

                    location = listing.query_selector("div.text-detail span:first-child").inner_text().strip()
                    ad_id_elem = listing.query_selector("div.absolute[aria-owns^='search-ad-']")
                    ad_id = ad_id_elem.get_attribute("aria-owns").replace("search-ad-", "") if ad_id_elem else "N/A"

                    car_data.append({
                        "Annonse ID": ad_id,
                        "Title": title,
                        "Price": price,
                        "Year": year,
                        "Mileage": mileage,
                        "Transmission": transmission,
                        "Fuel": fuel,
                        "Location": location
                    })
                except Exception:
                    continue

            if not go_to_next_page(page, page_number):
                break
            page_number += 1

        browser.close()

        if return_data:
            return car_data
