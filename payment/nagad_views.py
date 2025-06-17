# # Core Django and DRF
# from django.conf import settings
# from django.shortcuts import redirect
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status

# # Networking & Utilities
# import requests
# import base64
# import json
# import logging

# # Your app models and helpers
# from order.models import ResolvedOrder

# # If you implement generate_challenge() somewhere else
# from .utils import generate_challenge  # or however it's defined

# logger = logging.getLogger(__name__)

# def get_nagad_token():
#     try:
#         url = f"{settings.NAGAD_BASE_URL}/checkout/token/issue"

#         headers = {
#             "Content-Type": "application/json"
#         }

#         payload = {
#             "accountNumber": settings.NAGAD_MERCHANT_PHONE
#         }

#         # Step 1: Encode payload
#         payload_str = json.dumps(payload)
#         encoded_payload = base64.b64encode(payload_str.encode()).decode()

#         # Step 2: Make the request
#         response = requests.post(url, data=encoded_payload, headers=headers)
#         response.raise_for_status()

#         response_data = response.json()

#         access_token = response_data.get("access_token")
#         if not access_token:
#             raise ValueError("Failed to get access token")

#         return access_token

#     except Exception as e:
#         logger.error(f"Error getting Nagad token: {str(e)}")
#         raise

# @api_view(["POST"])
# def start_nagad_payment(request, pk):
#     try:
#         order = ResolvedOrder.objects.get(pk=pk)

#         if order.status == "PD":
#             return Response({"error": "Order already paid"}, status=status.HTTP_400_BAD_REQUEST)

#         # Step 1: Get token from Nagad (same idea as bKash)
#         access_token = get_nagad_token()  # Implement this like get_bkash_token()

#         # Step 2: Initiate payment
#         payload = {
#             "merchantId": settings.NAGAD_MERCHANT_ID,
#             "amount": str(order.converted_price),
#             "currencyCode": "050",
#             "orderId": order.tracker,
#             "challenge": generate_challenge(),
#             "merchantCallbackURL": settings.NAGAD_CALLBACK_URL,  # 👈 Add this
#             # other fields if required
#         }

#         headers = {
#             "Authorization": f"Bearer {access_token}",
#             "Content-Type": "application/json"
#         }

#         create_url = f"{settings.NAGAD_BASE_URL}/checkout/initiate"
#         response = requests.post(create_url, json=payload, headers=headers)
#         response.raise_for_status()

#         res_data = response.json()
#         redirect_url = res_data.get("paymentURL")

#         if not redirect_url:
#             return Response({"error": "Failed to get redirect URL"}, status=500)

#         # Save payment ID or transaction reference if needed
#         order.payment_id = res_data.get("paymentRefId")  # or similar
#         order.payment_url = redirect_url
#         order.save()

#         return Response({"nagadURL": redirect_url})

#     except ResolvedOrder.DoesNotExist:
#         return Response({"error": "Order not found"}, status=404)
#     except Exception as e:
#         logger.error(f"Nagad payment error: {str(e)}")
#         return Response({"error": "Failed to start payment"}, status=500)
    
# @api_view(['GET'])
# def nagad_callback(request):
#     try:
#         payment_ref = request.GET.get("paymentRefId")

#         if not payment_ref:
#             return Response({"error": "Missing paymentRefId"}, status=400)

#         order = ResolvedOrder.objects.get(payment_id=payment_ref)

#         if order.status == "PD":
#             return redirect("your-frontend-success-page")

#         # Step 1: Get token
#         access_token = get_nagad_token()

#         # Step 2: Verify transaction
#         verify_url = f"{settings.NAGAD_BASE_URL}/checkout/verify/payment"
#         headers = {
#             "Authorization": f"Bearer {access_token}",
#             "Content-Type": "application/json"
#         }

#         payload = {
#             "paymentRefId": payment_ref
#         }

#         response = requests.post(verify_url, json=payload, headers=headers)
#         response.raise_for_status()
#         data = response.json()

#         if data.get("status") == "Success":  # Adjust based on Nagad response
#             order.update_order_status("PD")
#             return redirect("your-frontend-success-page")
#         else:
#             return redirect("your-frontend-failure-page")

#     except ResolvedOrder.DoesNotExist:
#         logger.error("Order not found for Nagad paymentRefId")
#         return Response({"error": "Order not found"}, status=404)
#     except Exception as e:
#         logger.error(f"Nagad callback error: {str(e)}")
#         return Response({"error": "Failed to verify payment"}, status=500)