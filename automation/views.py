from rest_framework.response import Response
from rest_framework import views
from . import amazon, ebay, nike, jomashop, walmart
from urllib.parse import urlparse

domains = ["amazon.com", "nike.com", "ebay.com", "jomashop.com", "walmart.com"]

def is_valid_url(url):
    try:
        parsed = urlparse(url)
        return all([parsed.scheme in ('http', 'https'), parsed.netloc])
    except Exception:
        return False

def get_matching_domain(url):
    if not is_valid_url(url):
        return None
    netloc = urlparse(url).netloc.lower()
    for domain in domains:
        if domain in netloc:
            return domain  
    return None

class ReturnData(views.APIView):
    def post(self, request):
        original_url = request.data.get('url')

        if not original_url:
            return Response({'message': 'No URL provided'}, status=400)

        domain = get_matching_domain(original_url)
        if domain is None:
            return Response({'message': 'URL is not valid or supported'}, status=400)

        if domain == 'amazon.com':
            result = amazon.get_amazon_product_data(original_url)
            if result:
                return Response({
                    "title": result["title"],
                    "image": result["image"],
                    "price": result["price"]
                })
            else: 
                return Response({"message": "Failed to fetch data"}, status=500)
        elif domain == 'ebay.com':  
            result = ebay.get_ebay_product_data(original_url)
            if result:
                return Response({
                    "title": result["title"],
                    "image": result["image"],
                    "price": result["price"]
                })
            else:
                return Response({"message": "Failed to fetch data"}, status=500)
        elif domain == 'nike.com':
            result = nike.get_nike_product_data(original_url)
            if result:
                return Response({
                    "title": result["title"],
                    "image": result["image"],
                    "price": result["price"]
                })
            else:
                return Response({"message": "Failed to fetch data"}, status=500)
        elif domain == 'jomashop.com':
            result = jomashop.main(original_url)
            if result:
                return Response({
                    "title": result["title"],
                    "image": result["image"],
                    "price": result["price"]
                })
            else:
                return Response({"message": "Failed to fetch data"}, status=500)
        elif domain == 'walmart.com':
            result = walmart.get_walmart_product_data(original_url)
            if result:
                return Response({
                    "title": result["title"],
                    "image": result["image"],
                    "price": result["price"]
                })
            else:
                return Response({"message": "Failed to fetch data"}, status=500)
        return Response({"message": f"Scraping for {domain} is not implemented yet"}, status=501)
