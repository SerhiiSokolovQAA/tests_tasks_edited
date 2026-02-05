"""
File to run script for parsing products from the brain.com.ua website via Selenium and saving them into the Product model
"""


import os
import sys
import importlib.util

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

module_path = os.path.join(BASE_DIR, "modules", "3_selenium_model.py")

spec = importlib.util.spec_from_file_location("selenium_model", module_path)
selenium_model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(selenium_model)


if __name__ == "__main__":
    selenium_model.selenium_parser()
