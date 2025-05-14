from playwright.sync_api import sync_playwright, TimeoutError
import logging
import time
import re

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
            logging.info(f"📄 Scraping page {page_number}")
            try:
                page.wait_for_selector("article.sf-search-ad", timeout=8000)
            except TimeoutError:
                logging.warning("⏱️ Listings not found, skipping page.")
                break

            listings = page.query_selector_all("article.sf-search-ad")

            for listing in listings:
                try:
                    title_elem = listing.query_selector("h2 a")
                    if not title_elem:
                        continue

                    title = title_elem.inner_text().strip()
                    link = title_elem.get_attribute("href")
                    if not link:
                        continue

                    # Parse price
                    raw_price_elem = listing.query_selector("span.t3.font-bold")
                    raw_price = raw_price_elem.inner_text().strip() if raw_price_elem else "0"
                    price = int(re.sub(r"\D", "", raw_price) or 0)

                    if price == 0:
                        logging.info(f"⏩ Skipped (price is 0): {title}")
                        continue



                    # Parse year, mileage
                    details_text_elem = listing.query_selector("span.text-caption.font-bold")
                    details_text = details_text_elem.inner_text() if details_text_elem else ""
                    details = details_text.split(" ∙ ")
                    year = int(details[0]) if len(details) > 0 and details[0].isdigit() else 0
                    mileage = int(re.sub(r"\D", "", details[1])) if len(details) > 1 else 999999

                    # ✅ Pre-filter the ads (price <= 10000 and year >= 2020 and mileage <= 100000)
                    if price <= 15000 and year >= 2019 and mileage <= 100000:
                        logging.info(
                            f"✅ Found suspicious car: {title} (Price: {price}, Year: {year}, Mileage: {mileage})")

                        # Open ad page to check for monthly payment info
                        ad_page = context.new_page()
                        try:
                            ad_page.goto(link, timeout=10000)
                            ad_page.wait_for_selector("body", timeout=3000)

                            # Check for "Månedspris"
                            monthly_info = ad_page.query_selector_all("p")
                            if any("Månedspris" in (p.inner_text() or "") for p in monthly_info):
                                logging.info(f"⏩ Skipped (monthly payment): {title}")
                                continue  # Skip ads with monthly payments

                        except Exception as e:
                            logging.warning(f"⚠️ Could not open ad page for '{title}': {e}")
                            continue
                        finally:
                            ad_page.close()

                        logging.info(
                            f"✅ {title} passed suspicious test: (Price: {price}, Year: {year}, Mileage: {mileage})")
                        # ✅ Passed all checks → Add car
                        transmission = details[2] if len(details) > 2 else "N/A"
                        fuel = details[3] if len(details) > 3 else "N/A"
                        location_elem = listing.query_selector("div.text-detail span:first-child")
                        location = location_elem.inner_text().strip() if location_elem else "N/A"
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

                    else:

                        # logging.info(f"⏩ Car is not suspicious: {title}")



                        # ✅ Add car to list regardless of being suspicious
                        transmission = details[2] if len(details) > 2 else "N/A"
                        fuel = details[3] if len(details) > 3 else "N/A"
                        location_elem = listing.query_selector("div.text-detail span:first-child")
                        location = location_elem.inner_text().strip() if location_elem else "N/A"
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



                except Exception as e:
                    logging.error(f"⚠️ Error parsing listing: {e}")
                    continue

            # Go to the next page
            if not go_to_next_page(page, page_number):
                break
            page_number += 1

        browser.close()

        if return_data:
            return car_data
