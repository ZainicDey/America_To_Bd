# scraper.py

import requests
from bs4 import BeautifulSoup as soup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Currency": "USD"
}
cookies = {
    "lc-main": "en_US",
    "ubid-main": "133-1234567-8901234"
}

def get_amazon_product_data(url):
    html = requests.get(url, headers=headers, cookies=cookies)
    bsobj = soup(html.content, 'lxml')

    title_tag = bsobj.find(id="productTitle")
    title = title_tag.text.strip() if title_tag else None

    container = bsobj.select_one('div.a-section.a-spacing-none.aok-align-center.aok-relative')
    if container:
        price_elem = container.select_one('span.aok-offscreen')
        # print(price_elem)
        if price_elem:
            price_text = price_elem.text.strip().replace('$', '')
            if '.' in price_text:
                integer_part, decimal_part = price_text.split('.')
                decimal_part = decimal_part[:2]
                price_text = f"{integer_part}.{decimal_part}"
            try:
                price = float(price_text)
            except ValueError:
                price = None
        else:
            price = None
    else:
        price = None

    if price is None:
        price_range_container = bsobj.select_one('span.a-price-range')
        if price_range_container:
            price_spans = price_range_container.select('span.a-offscreen')
            prices = []
            for span in price_spans:
                price_text = span.text.strip().replace('$', '')
                try:
                    price = float(price_text)
                    prices.append(price)
                except ValueError:
                    continue
            price = max(prices) if prices else None

    image_tag = bsobj.find("img", {"id": "landingImage"})
    image_url = image_tag['src'] if image_tag else None
    # print(title, image_url, price)
    if title and image_url and price:
        return {
            "title": title,
            "image": image_url,
            "price": price
        }
    return None
