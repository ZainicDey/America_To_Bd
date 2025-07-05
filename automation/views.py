from rest_framework.response import Response
from rest_framework import views
from rest_framework.viewsets import ModelViewSet
from . import amazon, ebay, nike, jomashop, walmart, models, serializers, bkash_views
from rest_framework import permissions
from urllib.parse import urlparse
from order.models import ResolvedOrder
from userrole.models import Address
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
    print(netloc)
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
                res_obj = {
                    "title": result["title"],
                    "image": result["image"],
                    "price": result["price"]
                }
            else: 
                return Response({"message": "Failed to fetch data"}, status=500)
        elif domain == 'ebay.com':  
            result = ebay.get_ebay_product_data(original_url)
            if result:
                res_obj = {
                    "title": result["title"],
                    "image": result["image"],
                    "price": result["price"]
                }
            else:
                return Response({"message": "Failed to fetch data"}, status=500)
        elif domain == 'nike.com':
            result = nike.get_nike_product_data(original_url)
            if result:
                res_obj = {
                    "title": result["title"],
                    "image": result["image"],
                    "price": result["price"]
                }
            else:
                return Response({"message": "Failed to fetch data"}, status=500)
        elif domain == 'jomashop.com':
            result = jomashop.main(original_url)
            if result:
                res_obj = {
                    "title": result["title"],
                    "image": result["image"],
                    "price": result["price"]
                }
            else:
                return Response({"message": "Failed to fetch data"}, status=500)
        elif domain == 'walmart.com':
            result = walmart.get_walmart_product_data(original_url)
            if result:
                res_obj = {
                    "title": result["title"],
                    "image": result["image"],
                    "price": result["price"]
                }
                print(f"haha {result['title']}")
            else:
                return Response({"message": "Failed to fetch data"}, status=500)
        import math
        res_obj["us_tax"] = "8.87%"
        res_obj["us_tax_amount_in_usd"] = round(res_obj["price"] * 0.0887, 2)
        res_obj["us_total"] = round(res_obj["price"] + res_obj["us_tax_amount_in_usd"], 2)
        res_obj["dollar_rate"] = 125.0
        res_obj["bdt_total"] = round(res_obj["us_total"] * res_obj["dollar_rate"], 2)
        res_obj["bdt_total"] = math.ceil(res_obj["bdt_total"])
        res_obj["url"] = original_url
        
        return Response(res_obj, status=200)
    
class OrderData(ModelViewSet):
    serializer_class = serializers.AutomationSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return models.AutomatedOrder.objects.all()
        else:
            return models.AutomatedOrder.objects.filter(user=self.request.user)
        
    def create(self, request):
        data = request.data
        if not data:
            return Response({"message": "No data provided"}, status=400)
        try:
            if data.get("id"):
                bkash_url = bkash_views.start_payment(data.get("id"))
                print(bkash_url)
                return Response({
                    "message": "Order created successfully",
                    "order_id": data.get("id"),
                    "payment_url": bkash_url,
                }, status=201)
            
            address = data.get("address") or None
            if address:
                address = Address.objects.get(id=address)
            else:address = None
            order = models.AutomatedOrder.objects.create(
                url=data.get("url"),
                user=request.user,
                title=data.get("title"),
                image=data.get("image"),
                price=data.get("price"),
                address=address,
                quantity=data.get("quantity", 1),
                description=data.get("description", ""),
                us_tax=data.get("us_tax", "8.87%"),
                us_tax_amount_in_usd=data.get("us_tax_amount_in_usd", 0.0),
                us_total=data.get("us_total", 0.0),
                dollar_rate=data.get("dollar_rate", 125.0),
                bdt_total=data.get("bdt_total", 0.0)*data.get("quantity", 1),
            )
            if order.status != "due":
                return Response({"message": "Order is already paid"}, status=400)
            print(order.id)
            bkash_url = bkash_views.start_payment(order.id)
            print(bkash_url)
            return Response({
                "message": "Order created successfully",
                "order_id": order.id,
                "payment_url": bkash_url,
            }, status=201)
        except Exception as e:
            return Response({"message": str(e)}, status=500)
        