"""
Script for checking data in the database
"""

import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the function to run Django
from modules.load_django import start_django

# First, initialize Django
start_django()

# After this, models can be imported
from parser_app.models import Product

# Print all products
for p in Product.objects.all():
    print(f"{p.pk}: {p.full_name}, {p.promo_price} ₴, {p.regular_price} ₴, {p.color}, {p.memory}")
