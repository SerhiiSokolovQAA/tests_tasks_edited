"""
Script for parsing products from the brain.com.ua website via Playwright and saving them into the Product model
"""
import json
import os
import sys
import asyncio
import re
import traceback
from bs4 import BeautifulSoup
from asgiref.sync import sync_to_async
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from lxml import html as lxml_html
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.load_django import start_django
start_django()
from parser_app.models import Product
from modules.results_dir import RESULTS_DIR, dump_path
import csv
from django.core.management import call_command

# -------------------------------
# Scrapper Settings
# -------------------------------
from modules.setting import BASE_URL, TIMEOUT_SEARCH, TIMEOUT_FIRST_RESULT, TIMEOUT_SPEC_TAB, HEADLESS
from modules.xpath_selectors import *
from modules.phone_queries import PHONE_QUERIES

# -------------------------------
# Main function
# -------------------------------
async def run(queries=None):
    if queries is None:
        queries = PHONE_QUERIES

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        page = await browser.new_page()

        # -------------------------------
        # Save product to the DB
        # -------------------------------
        @sync_to_async
        def save_product(product_dict):
            try:
                obj, created = Product.objects.update_or_create(
                    full_name=product_dict.get("full_name"),
                    defaults=product_dict
                )
                print(f"Saved product ID={obj.pk}, created={created}")
            except Exception:
                traceback.print_exc()

        # -------------------------------
        # Loop over each phone query
        # -------------------------------
        for query in queries:
            print(f"\n=== START PARSING: {query} ===")
            product = {}

            # -------------------------------
            # Open main page & search
            # -------------------------------
            try:
                await page.goto(BASE_URL)
                await asyncio.sleep(2)
            except Exception as e:
                print("Failed to open main page:", e)
                continue

            try:
                search_input = await page.wait_for_selector(f'xpath={SEARCH_INPUT}', timeout=TIMEOUT_SEARCH)
                await search_input.fill("")
                await search_input.fill(query)
                await search_input.press("Enter")
                await asyncio.sleep(3)
            except PWTimeout:
                print(f"Search input not found for query: {query}")
                continue

            # -------------------------------
            # Open first result
            # -------------------------------
            try:
                first_result = await page.wait_for_selector(f'xpath={FIRST_RESULT}', timeout=TIMEOUT_FIRST_RESULT)
                await first_result.click()
                await asyncio.sleep(3)
            except PWTimeout:
                print(f"First product not found for query: {query}")
                continue

            # -------------------------------
            # Open SPEC tab
            # -------------------------------
            try:
                tab = await page.wait_for_selector(f'xpath={SPEC_TAB_BUTTON}', timeout=TIMEOUT_SPEC_TAB)
                await tab.click()
                await asyncio.sleep(2)
            except PWTimeout:
                print(f"Spec tab not found for query: {query}")
                # не прерываем, парсинг можно делать и без вкладки

            # -------------------------------
            # Parse HTML content
            # -------------------------------
            html_content = await page.content()
            tree = lxml_html.fromstring(html_content)
            soup = BeautifulSoup(html_content, "html.parser")

            # Full name
            full_name_list = tree.xpath(FULL_NAME_XPATH + "/text()")
            product["full_name"] = full_name_list[0].strip() if full_name_list else None

            # Prices
            try:
                promo_price = tree.xpath(PRICE_CURRENT + '/text()')
                product["promo_price"] = promo_price[0].strip().replace("₴", "").replace(" ", "") if promo_price else None
            except Exception:
                product["promo_price"] = None

            try:
                regular_price = tree.xpath(PRICE_OLD + '/text()')
                product["regular_price"] = regular_price[0].strip().replace("₴", "").replace(" ", "") if regular_price else None
            except Exception:
                product["regular_price"] = None

            # Product code
            try:
                product_code_el = await page.wait_for_selector(f'xpath={PRODUCT_CODE}', timeout=10000)
                product_code_text = await product_code_el.text_content()
                product["product_code"] = product_code_text.strip() if product_code_text else None
            except Exception:
                product["product_code"] = None

            # Manufacturer
            try:
                manufacturer_list = tree.xpath(MANUFACTURER_XPATH + '/text()')
                product["manufacturer"] = manufacturer_list[0].strip() if manufacturer_list else None
            except Exception:
                product["manufacturer"] = None

            # Color
            try:
                product["color"] = tree.xpath(f'string({COLOR_XPATH})').strip()
            except Exception:
                product["color"] = None

            # Memory
            try:
                memory_text = tree.xpath(f'string({MEMORY_XPATH})')
                product["memory"] = memory_text.strip() if memory_text else None
            except Exception:
                product["memory"] = None

            # Photos
            photos = []
            for img in soup.find_all("img"):
                src = img.get("src") or ""
                if "prod_img" in src:
                    if src.startswith("//"):
                        src = "https:" + src
                    photos.append(src)
            product["photos"] = photos

            # Reviews count
            try:
                reviews_tag = soup.select_one(REVIEWS_LINK)
                product["reviews_count"] = int(re.search(r"\d+", reviews_tag.text).group())
            except Exception:
                product["reviews_count"] = 0

            # Specs container
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
            # Save product
            # -------------------------------
            await save_product(product)

            # Save JSON
            json_path = os.path.join(RESULTS_DIR, f"{product.get('full_name', 'product')}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(product, f, ensure_ascii=False, indent=4)

            # Save CSV
            csv_path = os.path.join(RESULTS_DIR, "products.csv")
            fieldnames = list(product.keys())
            write_header = not os.path.exists(csv_path)
            with open(csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if write_header:
                    writer.writeheader()
                writer.writerow(product)

            # DB dump (sync in async context)
            try:
                await sync_to_async(call_command)("dumpdata", stdout=open(dump_path, "w", encoding="utf-8"))
            except Exception as e:
                print("Failed to dump DB:", e)

            print(f"=== DONE: {query} ===")

        await browser.close()


if __name__ == "__main__":
    print("Use run_playwright_scraper.py to start the scraper with optional phone argument")
