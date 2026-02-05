"""
Script for parsing products from the brain.com.ua website via Requests/BS4 and saving them into the Product model
"""

import os
import sys
import re
import requests
from lxml import html

from modules.setting import URL, BASE_URL, HEADERS

# --- Django init ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, "modules"))

from modules.load_django import start_django
start_django()
import django
django.setup()


from parser_app.models import Product
import xpath_selectors as xp


def clean_price(text: str) -> str:
    return (
        text.replace("₴", "")
        .replace(" ", "")
        .replace(",", ".")
        .strip()
    )


def main():
    url = URL
    headers = HEADERS

    response = requests.get(url, headers=headers, timeout=60)
    if response.status_code != 200:
        print(f"Error! Status Code: {response.status_code}")
        return

    tree = html.fromstring(response.text)
    data = {}

    # PRODUCT CODE
    try:
        data["product_code"] = tree.xpath(xp.PRODUCT_CODE_1)[0].text_content().strip()
    except Exception:
        data["product_code"] = None

    # FULL NAME
    try:
        data["full_name"] = tree.xpath(xp.FULL_NAME_XPATH)[0].text_content().strip()
    except Exception:
        data["full_name"] = None

    # MANUFACTURER
    try:
        data["manufacturer"] = tree.xpath(xp.MANUFACTURER_XPATH)[0].text_content().strip()
    except Exception:
        data["manufacturer"] = None

    # COLOR
    try:
        data["color"] = tree.xpath(xp.COLOR_XPATH)[0].text_content().strip()
    except Exception:
        data["color"] = None

    # MEMORY
    try:
        data["memory"] = tree.xpath(xp.MEMORY_XPATH)[0].text_content().strip()
    except Exception:
        data["memory"] = None

    # SCREEN DIAGONAL
    try:
        data["screen_diagonal"] = tree.xpath(xp.SCREEN_DIAGONAL)[0].text_content().strip()
    except Exception:
        data["screen_diagonal"] = None

    # SCREEN RESOLUTION
    try:
        res = tree.xpath(xp.SCREEN_RESOLUTION)[0].text_content().strip()
        data["screen_resolution"] = res.replace("×", " x ")
    except Exception:
        data["screen_resolution"] = None

    # REGULAR PRICE
    try:
        price = tree.xpath(xp.CURRENT_PRICE)[0].text_content().strip()
        data["regular_price"] = clean_price(price)
    except Exception:
        data["regular_price"] = None

    # PROMO PRICE
    try:
        promo = tree.xpath(xp.PRICE_CURRENT)[0].text_content().strip()
        data["promo_price"] = clean_price(promo)
    except Exception:
        data["promo_price"] = None

    # REVIEWS COUNT
    try:
        reviews_text = tree.xpath(xp.REV)
        if reviews_text:
            match = re.search(r"\((\d+)\)", reviews_text[0])
            if match:
                data["reviews_count"] = int(match.group(1))
            else:
                data["reviews_count"] = None
        else:
            data["reviews_count"] = None
    except Exception:
        data["reviews_count"] = None

    # PHOTOS
    data["photos"] = []
    if data.get("product_code"):
        try:
            imgs = tree.xpath(f'//img[contains(@src,"{data["product_code"]}")]')
            for img in imgs:
                try:
                    src = img.get("src")
                    if not src:
                        continue
                    if src.startswith("//"):
                        src = "https:" + src
                    elif src.startswith("/"):
                        src = BASE_URL + src
                    if src not in data["photos"]:
                        data["photos"].append(src)
                except Exception:
                    continue
        except Exception:
            data["photos"] = []

    # SAVE TO DB
    try:
        product, created = Product.objects.update_or_create(
            full_name=data.get("full_name") or "Unknown",
            defaults=data
        )
    except Exception as e:
        print("Error saving to DB:", e)
        return

    # OUTPUT
    print("\nParsing result")
    print("=" * 50)
    for k, v in data.items():
        if k == "photos":
            print(f"{k}:")
            for p in v:
                print(f"  - {p}")
        else:
            print(f"{k}: {v}")
    print("=" * 50)
    print("New record created" if created else "Record updated")
    print(f"ID in DB: {product.id}")


if __name__ == "__main__":
    main()
