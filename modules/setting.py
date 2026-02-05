"""
Project configuration: website URL, timeouts, and other settings.
"""

BASE_URL = "https://brain.com.ua/"

# Timeout Setting
TIMEOUT_SEARCH = 45000
TIMEOUT_FIRST_RESULT = 45000
TIMEOUT_SPEC_TAB = 20000

# Any other global constants can be added
HEADLESS = False  # Run the browser in headless mode or not (HEADLESS = True)

URL = "https://brain.com.ua/ukr/Mobilniy_telefon_Apple_iPhone_16_Pro_Max_256GB_Black_Titanium-p1145443.html"

HEADERS = {
            "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
            )
}

REQUEST_TIMEOUT = 30