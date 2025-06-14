import requests
from bs4 import BeautifulSoup as soup

# Set headers to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# Ask user for URL
def get_walmart_product_data(url):
    html = requests.get(url, headers=headers)
    bsobj = soup(html.content, 'lxml')

    # Extract Title
    title_tag = bsobj.select_one('h1#main-title[data-seo-id="hero-carousel-image"]')
    title = title_tag.text.strip() if title_tag else None

    # Extract Price
    price_tag = bsobj.select_one('span[itemprop="price"][data-seo-id="hero-price"]')
    price = price_tag.text.strip() if price_tag else None

    # Extract Image URL
    image_tag = bsobj.select_one('img[data-testid="hero-image"][data-seo-id="hero-image"]')
    image_url = image_tag['src'] if image_tag and image_tag.has_attr('src') else None

    if title and image_url and price:
        return {
            "title": title,
            "image": image_url,
            "price": price
        }
    return None