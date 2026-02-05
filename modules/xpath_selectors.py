"""
All XPath's for parsing brain.com.ua
"""
CURRENT_PRICE = '//div[@class="br-pr-np"][@data-pid="1145443"]'

SEARCH_INPUT = '//div[2]//div[2]/form/input[@type="search"]'

FULL_NAME_XPATH = '//h1[@class="desktop-only-title"]'

FIRST_RESULT = '(//div[contains(@class, "br-pp-desc")])[1]'

SPEC_TAB_BUTTON = '//*[@id="br-pr-7"]/button'

SPECS_CONTAINER = 'div#br-pr-7'

PRICE_CURRENT = '//span[@class="red-price"]'

PRICE_OLD = '//div[@class="br-pr-op"]//div[@class="price-wrapper"]/span'

PHOTO_IMG = 'img'

PRODUCT_CODE = '//div[4]//div[1]/div[6]/div/span[2]'

PRODUCT_CODE_1 = '//*[@id="product_code"]/span[2]'

REVIEWS_LINK = 'a[href="#reviews-list"]'

REVIEWS_LINK_SELENIUM = '//div[4]/div[2]/div[2]/div[1]/div[1]/div/a'

REV = '//a[@href="#reviews-list"]/text()'

COLOR_XPATH = '//*[@id="br-pr-7"]//div[.//span[text()="Колір"]]/span[2]'

MEMORY_XPATH = "//*[@id='br-pr-7']//div[.//span[text()=\"Вбудована пам'ять\"]]/span[2]"

MANUFACTURER_XPATH = '//*[@id="br-pr-7"]//div[.//span[text()="Виробник"]]/span[2]'

PRODUCT_WRAPPER = '//div[@class="product-wrapper"]'

SCREEN_DIAGONAL = '//*[@id="br-pr-7"]//div[.//span[text()="Діагональ екрану"]]/span[2]'

SCREEN_RESOLUTION = '//*[@id="br-pr-7"]//div[.//span[text()="Роздільна здатність екрану"]]/span[2]'

NAME_XPATH = './@data-name'

VENDOR_XPATH = './@data-vendor'

PRICE_XPATH = './@data-price'

CODE_XPATH = './@data-articul'

MEMORY_XPATH_1 = './@data-articul'

CATEGORY_XPATH = './@data-category-name'

PHOTO_MAIN_XPATH = './/img[@data-observe-src]/@data-observe-src'

REVIEWS_XPATH = './/span[contains(@class,"br-pp-bu-bld")]/text()'