import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from order import models
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST'])
def payment_webhook(request):
    # This is Aamarpay's webhook
    # Aamarpay sends a POST request with payment status updates
    data = request.data

    # Validate the webhook and ensure the signature matches for security (if Aamarpay provides it)
    # You can use your business logic to verify the payment status and update order

    if data.get('status') == 'Successful':
        try:
            resolved_order = models.ResolvedOrder.objects.get(tracker=data['tran_id'])
            resolved_order.update_order_status('PD')  # Update status to Paid
        except models.ResolvedOrder.DoesNotExist:
            return Response({'message': 'Order not found'}, status=404)

    return Response({'message': 'Webhook received and processed', 'data': data})

@api_view(['POST'])
def initiate_payment(request):
    data = request.data
    url = "https://sandbox.aamarpay.com/index.php"

    # Fetch the order from the database
    order = models.ResolvedOrder.objects.filter(tracker=data['tran_id']).first()
    if not order:
        return Response({'message': 'Order not found'}, status=404)

    if order.cost > data['amount']:  # Ensure you're comparing compatible types (e.g., both as Decimal or Integer)
        return Response({'message': 'Less money'}, status=402)

    # Payload for initiating payment with Aamarpay
    payload = {
        'store_id': settings.AAMARPAY_STORE_ID,
        'signature_key': settings.AAMARPAY_SIGNATURE_KEY,
        'cus_name': data['cus_name'],
        'cus_email': data['cus_email'],
        'cus_phone': data['cus_phone'],
        'amount': str(data['amount']),  # Ensure it's in string format
        'currency': 'BDT',
        'tran_id': data['tran_id'],
        'desc': 'Test Transaction',
        'success_url': 'https://america-to-bd.vercel.app/payment/success/',
        'fail_url': 'https://america-to-bd.vercel.app/payment/fail/',
        'cancel_url': 'https://america-to-bd.vercel.app/payment/cancel/',
        'type': 'json',
    }

    # Sending POST request to Aamarpay
    response = requests.post(url, data=payload)
    result = response.json()

    # Process Aamarpay response
    if result['status'] == 'success':  # If Aamarpay responds with success
        return Response({'message': 'Payment initiated successfully', 'data': result})
    else:
        return Response({'message': 'Payment initiation failed', 'data': result}, status=400)


