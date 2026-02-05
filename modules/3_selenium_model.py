"""
Selenium scraper for brain.com.ua, saves products into Django DB
"""

import os
import sys
import time
import json
import traceback
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from django.core.management import call_command

# -------------------------------
# Django setup
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, "modules"))
from modules.load_django import start_django
start_django()
from parser_app.models import Product
from modules.results_dir import RESULTS_DIR, dump_path
from modules.setting import BASE_URL, TIMEOUT_SEARCH, TIMEOUT_FIRST_RESULT, TIMEOUT_SPEC_TAB
from modules.xpath_selectors import *
from modules.phone_queries import PHONE_QUERIES  # список телефонов

# -------------------------------
# Save product helper (synchronous)
# -------------------------------
def save_product_sync(product_dict):
    """Save product to Django DB synchronously"""
    try:
        obj, created = Product.objects.update_or_create(
            full_name=product_dict.get("full_name"),
            defaults=product_dict
        )
        print(f"Saved product ID={obj.pk}, created={created}")
    except Exception:
        traceback.print_exc()


# -------------------------------
# Main Selenium parser
# -------------------------------
def selenium_parser(queries=None):
    if queries is None:
        queries = PHONE_QUERIES

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")  # uncomment for headless mode

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    for query in queries:
        print(f"\n=== START PARSING: {query} ===")
        product = {}

        try:
            # -------------------------------
            # Open main page
            # -------------------------------
            driver.get(BASE_URL)
            time.sleep(2)

            # -------------------------------
            # Search phone
            # -------------------------------
            search_input = WebDriverWait(driver, TIMEOUT_SEARCH).until(
                EC.element_to_be_clickable((By.XPATH, SEARCH_INPUT))
            )
            driver.execute_script("arguments[0].value = '';", search_input)
            search_input.send_keys(query)
            search_input.send_keys(Keys.ENTER)
            time.sleep(3)

            # -------------------------------
            # Open first result
            # -------------------------------
            first_result = WebDriverWait(driver, TIMEOUT_FIRST_RESULT).until(
                EC.element_to_be_clickable((By.XPATH, FIRST_RESULT))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_result)
            time.sleep(1)
            first_result.click()
            time.sleep(2)

            # -------------------------------
            # Open SPEC tab
            # -------------------------------
            def click_spec_tab(driver, query):
                try:
                    spec_tab = WebDriverWait(driver, TIMEOUT_SPEC_TAB).until(
                        EC.presence_of_element_located((By.XPATH, SPEC_TAB_BUTTON))
                    )

                    for attempt in range(3):
                        try:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", spec_tab)
                            WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, SPEC_TAB_BUTTON)))
                            spec_tab.click()
                            time.sleep(1)
                            return True
                        except Exception:
                            time.sleep(0.5)
                    print(f"Spec tab click failed for {query}")
                    return False
                except Exception:
                    print(f"Spec tab not found for {query}")
                    return False

            # -------------------------------
            # Parse page
            # -------------------------------
            click_spec_tab(driver, query)
            soup = BeautifulSoup(driver.page_source, 'html.parser')


            # Full name
            try:
                full_name_el = driver.find_element(By.XPATH, FULL_NAME_XPATH)
                product["full_name"] = full_name_el.text.strip().replace("₴", "")
            except Exception:
                product["full_name"] = None

            # Promo price
            try:
                promo_el = driver.find_element(By.XPATH, PRICE_CURRENT)
                product["promo_price"] = promo_el.text.strip().replace("₴", "").replace(" ", "")
            except Exception:
                product["promo_price"] = None

            # Regular price
            try:
                regular_el = driver.find_element(By.XPATH, PRICE_OLD)
                product["regular_price"] = regular_el.text.strip().replace("₴", "").replace(" ", "")
            except Exception:
                product["regular_price"] = None

            # Product code
            try:
                code_el = driver.find_element(By.XPATH, PRODUCT_CODE)
                product["product_code"] = code_el.text.strip()
            except Exception:
                product["product_code"] = None

            # Manufacturer
            try:
                manufacturer_el = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, MANUFACTURER_XPATH))
                )
                WebDriverWait(driver, 2).until(lambda d: manufacturer_el.text.strip() != "")
                product["manufacturer"] = manufacturer_el.text.strip()
            except Exception:
                product["manufacturer"] = None

            # Color
            try:
                color_el = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, COLOR_XPATH))
                )
                WebDriverWait(driver, 2).until(lambda d: color_el.text.strip() != "")
                product["color"] = color_el.text.strip()
            except Exception:
                product["color"] = None

            # Memory
            try:
                memory_el = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, MEMORY_XPATH))
                )
                WebDriverWait(driver, 2).until(lambda d: memory_el.text.strip() != "")
                product["memory"] = memory_el.text.strip()
            except Exception:
                product["memory"] = None


            try:
                reviews_el = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, REVIEWS_LINK_SELENIUM))
                )
                product["reviews_count"] = int(re.search(r'\d+', reviews_el.text).group())
            except TimeoutException:
                product["reviews_count"] = None

                # Photos
            photos = []
            for img in soup.find_all("img"):
                src = img.get("src") or ""
                if "prod_img" in src:
                    if src.startswith("//"):
                        src = "https:" + src
                    photos.append(src)
            product["photos"] = photos

            # Specs
            try:
                specs_container = soup.select_one(SPECS_CONTAINER)
                product["specs"] = specs_container.text.strip() if specs_container else None
            except Exception:
                product["specs"] = None

            # -------------------------------
            # Print result
            # -------------------------------
            print("="*40)
            for k, v in product.items():
                print(f"{k}: {v}")

            # -------------------------------
            # Save to DB (synchronously!)
            # -------------------------------
            save_product_sync(product)

            # JSON
            json_path = os.path.join(RESULTS_DIR, f"{product.get('full_name', 'product')}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(product, f, ensure_ascii=False, indent=4)

            # CSV
            csv_path = os.path.join(RESULTS_DIR, "products.csv")
            fieldnames = list(product.keys())
            write_header = not os.path.exists(csv_path)
            with open(csv_path, "a", newline="", encoding="utf-8") as f:
                from csv import DictWriter
                writer = DictWriter(f, fieldnames=fieldnames)
                if write_header:
                    writer.writeheader()
                writer.writerow(product)

            # DB dump
            try:
                with open(dump_path, "w", encoding="utf-8") as f:
                    call_command("dumpdata", stdout=f)
            except Exception as e:
                print("Failed to dump DB:", e)

            print(f"=== DONE: {query} ===")

        except Exception:
            traceback.print_exc()

    driver.quit()
    print("All queries finished.")


# -------------------------------
# Run script
# -------------------------------
if __name__ == "__main__":
    selenium_parser()
