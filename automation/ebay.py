#import libraries

from urllib.request import urlopen
from bs4 import BeautifulSoup as soup
import requests

#set headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Currency": "USD"
}
cookies = {
    "lc-main": "en_US",
    "ubid-main": "133-1234567-8901234"  
}
#Define URL and send get request

# url = 'https://www.amazon.com/JBL-Tune-510BT-Ear-Headphones/dp/B08WM3LMJF/ref=mp_s_a_1_10?crid=39EC93GM4JS7L&dib=eyJ2IjoiMSJ9.Y7QlKJHACY24iPbNFr2WKbl7gBKlKXVH8Z5lgWGMwQWN8lAdhUqHSUnqsWBbuYPBdIfL5fX7kwrowdeCTnfZCqJTxyVuTPtUYZuhfUL9fFojaNqKt8ctNboy-PDwxQn2VVKjqmSCB9FURPM0l57RqTFsB2aRytBs35AK-MaJTSRlPxC9yw68IxAAvUe8ADI79iJId17-xC-HAtEqNMPdGQ.srqztyUu0xEBIFh7Np_9XUcIEHvl4OOo8UC08tXkbUE&dib_tag=se&keywords=headphones&qid=1749119223&sprefix=headpho%2Caps%2C450&sr=8-10'

def get_ebay_product_data(url):
    html = requests.get(url,headers=headers, cookies=cookies)

    #Create BeautifulSoup object
    bsobj = soup(html.content,'lxml')

    #Title
    title_tag = bsobj.select_one('h1.x-item-title__mainTitle span.ux-textspans')
    if title_tag:
        title = title_tag.text.strip()
    else:
        title = None

    #Price
    price_tag = bsobj.select_one('div.x-price-primary span.ux-textspans')

    if price_tag:
        raw_price = price_tag.text.strip()
        cleaned_price = raw_price.replace('US', '').replace('$', '').strip()
        try:
            price = float(cleaned_price)
        except ValueError:
            price = None
    else:
        price = None

    img_container = bsobj.select_one('div.ux-image-carousel-item')

    if img_container:
        img_tag = img_container.find('img')
        if img_tag and img_tag.has_attr('src'):
            image_url = img_tag['src']
        else:
            image_url = None
    else:
        image_url = None
    
    if title and image_url and price:
        return {
            "title": title,
            "image": image_url,
            "price": price
        }
    return None