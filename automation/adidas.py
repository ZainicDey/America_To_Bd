from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import warnings

# Suppress pkg_resources deprecation warning
warnings.filterwarnings("ignore", category=UserWarning, module="playwright_stealth")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        stealth_sync(page)

        url = "https://www.adidas.com/us/hilo-short-sleeve-volleyball-jersey-kids/KA4478.html"
        page.goto(url, timeout=60000)
        print("Page title:", page.title())

        # Extract Title
        try:
            title = page.locator("h1[data-testid='product-title'] span").text_content().strip()
            print("Title:", title)
        except Exception as e:
            print("Title not found:", e)

        # Extract Price
        try:
            price = page.locator("div[data-testid='main-price'] span").nth(1).text_content().strip()
            print("Price:", price)
        except Exception as e:
            print("Price not found:", e)

        # Extract Image URL
        try:
            image_url = page.locator("img[alt*='HILO Short Sleeve Volleyball Jersey']").first.get_attribute("src")
            print("Image URL:", image_url)
        except Exception as e:
            print("Image not found:", e)

        browser.close()

if __name__ == "__main__":
    main()
