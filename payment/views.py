import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from order import models
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST'])
def payment_success(request):
    # Validate if needed
    try:
        resolved_order = models.ResolvedOrder.objects.get(tracker=request.data['tran_id'])
        resolved_order.update_order_status('PD')
    except models.ResolvedOrder.DoesNotExist:
        return Response({'message': 'Order not found'}, status=404)
    
    return Response({'message': 'Payment successful!', 'data': request.data})

@csrf_exempt
@api_view(['POST'])
def payment_fail(request):
    return Response({'message': 'Payment failed', 'data': request.data})

@csrf_exempt
@api_view(['POST'])
def payment_cancel(request):
    return Response({'message': 'Payment cancelled', 'data': request.data})

@csrf_exempt
@api_view(['POST'])
def payment_ipn(request):
    # Optional: Validate transaction from SSLCOMMERZ
    return Response({'message': 'IPN received', 'data': request.data})



@api_view(['POST'])
def initiate_payment(request):
    data = request.data
    url = 'https://sandbox.sslcommerz.com/gwprocess/v4/api.php' if settings.SSLCOMMERZ_SANDBOX else 'https://securepay.sslcommerz.com/gwprocess/v4/api.php'

    # Fetch the order from the database
    order = models.ResolvedOrder.objects.filter(tracker=data['tran_id']).first()
    if not order:
        return Response({'message': 'Order not found'}, status=404)

    if order.cost > data['amount']:  # Ensure you're comparing compatible types (e.g., both as Decimal or Integer)
        return Response({'message': 'Less money'}, status=402)

    post_data = {
        'store_id': settings.SSLCOMMERZ_STORE_ID,
        'store_passwd': settings.SSLCOMMERZ_STORE_PASSWORD,
        'total_amount': data['amount'],
        'currency': 'BDT',
        'tran_id': data['tran_id'],
        'success_url': 'https://america-to-bd.vercel.app/payment/success/',
        'fail_url': 'https://america-to-bd.vercel.app/payment/fail/',
        'cancel_url': 'https://america-to-bd.vercel.app/payment/cancel/',
        'ipn_url': 'https://america-to-bd.vercel.app/payment/ipn/',
        'cus_name': data['cus_name'],
        'cus_email': data['cus_email'],
        'cus_phone': data['cus_phone'],
        'cus_add1': data['cus_add1'],
        'cus_city': data['cus_city'],
        'cus_country': data['cus_country'],
        'shipping_method': 'NO',
        'product_name': 'Test Product',
        'product_category': 'General',
        'product_profile': 'general',
    }

    response = requests.post(url, data=post_data)
    result = response.json()
    
    return Response(result)

