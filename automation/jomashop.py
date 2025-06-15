# from playwright.sync_api import sync_playwright

# def main(url):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True) 
#         page = browser.new_page()
#         page.goto(url)
        
#         title = page.title()

#         # Grab the price text inside the first span within .now-price div
#         price = page.locator("div.now-price > span").first.text_content()

#         # Grab the image src attribute of the img with id 'product-main-image-gallery'
#         img_src = page.locator("img#product-main-image-gallery").get_attribute("src")

#         if price and img_src and title:
#             product_data = {
#                 "title": title,
#                 "image": img_src,
#                 "price": price
#             }
#             browser.close()
#             return product_data
#         browser.close()
#         return None
        
# if __name__ == "__main__":
#     main()

