"""
File to run script for parsing products from the brain.com.ua website via Requests/BS4 and saving them into the Product model
"""

import os
import sys
import json
import importlib.util


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, "modules"))

module_path = os.path.join(
    BASE_DIR,
    "modules",
    "4_requests_bs4_model.py"
)

spec = importlib.util.spec_from_file_location(
    "requests_bs4_model",
    module_path
)
parser_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser_module)


if __name__ == "__main__":
    product = parser_module.parse_product()
    print(json.dumps(product, ensure_ascii=False, indent=2))
