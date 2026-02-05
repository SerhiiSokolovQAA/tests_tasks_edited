"""
Файл для запуска скрапера товаров из корня проекта.
"""

import os
import sys
import asyncio
import argparse
import importlib.util
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

from modules.phone_queries import PHONE_QUERIES


file_path = Path(__file__).parent / "modules" / "1_playwright_model.py"
spec = importlib.util.spec_from_file_location("write_model", file_path)
scraper_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scraper_module)


def main():
    parser = argparse.ArgumentParser(description="Run product scraper")
    parser.add_argument(
        "phone",
        nargs="?",
        help="Phone name to scrape (optional)"
    )

    args = parser.parse_args()

    if args.phone:
        queries = [args.phone]
    else:
        queries = PHONE_QUERIES

    asyncio.run(scraper_module.run(queries))


if __name__ == "__main__":
    main()
