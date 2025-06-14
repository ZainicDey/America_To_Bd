from urllib.request import urlopen
from bs4 import BeautifulSoup as soup
import requests

# Set headers and cookies
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Currency": "USD"
}
cookies = {
    "lc-main": "en_US",
    "ubid-main": "133-1234567-8901234"  
}

# Ask user for URL
def get_nike_product_data(url):
    html = requests.get(url, headers=headers, cookies=cookies)

    # Create soup object
    bsobj = soup(html.content, 'lxml')

    # Extract Title
    title_tag = bsobj.select_one('h1[data-testid="product_title"]')
    title = title_tag.text.strip() if title_tag else None


    # Extract Price
    price_tag = bsobj.select_one('span[data-testid="currentPrice-container"]')
    price = price_tag.text.strip() if price_tag else None


    # Extract First Image
    image_tag = bsobj.select_one('img[data-testid="mobile-image-carousel-image"]')
    image_url = image_tag['src'] if image_tag and image_tag.has_attr('src') else None

    if title and image_url and price:
        return {
            "title": title,
            "image": image_url,
            "price": price
        }
    return None