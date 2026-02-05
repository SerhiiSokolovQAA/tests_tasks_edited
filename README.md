# Brain.com.ua Product Scraper

This project is a Python-based scraper for extracting product information from brain.com.ua and saving it into a Django database. 
It also stores the scraped data in JSON and CSV files, as well as a Django database dump.

---

## Features

- Scrapes product details such as:
  - Full name
  - Manufacturer
  - Color
  - Memory
  - Promo price and regular price
  - Product code
  - Photos
  - Reviews count
  - Specifications
  - Description
- Saves data into a Django model (`Product`)
- Exports data to:
  - `results/*.json`
  - `results/products.csv`
  - `results/db_dump.json`
- Supports scraping multiple phones or a specific phone
- Automatically handles missing elements with safe fallbacks

---

---

## Installation

1. Clone the repository:
   ```bash
   git clone <repo_url>
   cd braincom_project

# Playwright Usage
python run_playwright_scraper.py

# Run Playwright scraper for a specific phone
python run_playwright_scraper.py "Apple iPhone 15 128GB Black" 

# Selenium Usage
python run_selenium_scraper.py
# Requests/BS4 Usage
python run_requests_bs4_scraper.py
# Check saved products in the database
python 2_read_model.py

# Notes

**The scraper is async and uses Playwright for browser automation.**

**All interactions with Django are wrapped in sync_to_async to prevent async conflicts.**

**XPath selectors are maintained in modules/xpath_selectors.py for easy updates.**

**Phone list is maintained in modules/phone_queries.py.**