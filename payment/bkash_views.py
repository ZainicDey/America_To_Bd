# from rest_framework.decorators import action, api_view
# from rest_framework.response import Response
# import requests
# from django.conf import settings
# from order.models import ResolvedOrder
# from django.shortcuts import redirect
# from rest_framework import status
# import logging

# logger = logging.getLogger(__name__)

# BKASH_BASE_URL = settings.BKASH_BASE_URL
# APP_KEY = settings.BKASH_APP_KEY
# APP_SECRET = settings.BKASH_APP_SECRET
# USERNAME = settings.BKASH_USERNAME
# PASSWORD = settings.BKASH_PASSWORD
# BKASH_CALLBACK_URL = settings.BKASH_CALLBACK_URL
# BKASH_PAYMENT_MODE = settings.BKASH_PAYMENT_MODE
# FRONTEND_SUCCESS_URL = settings.FRONTEND_SUCCESS_URL
# FRONTEND_FAILURE_URL = settings.FRONTEND_FAILURE_URL

# def get_bkash_token():
#     try:
#         token_url = f"{BKASH_BASE_URL}/tokenized/checkout/token/grant"
#         headers = {
#             "username": USERNAME,
#             "password": PASSWORD,
#             "Content-Type": "application/json"
#         }
#         data = {
#             "app_key": APP_KEY,
#             "app_secret": APP_SECRET
#         }
#         response = requests.post(token_url, json=data, headers=headers)
#         response.raise_for_status()
#         return response.json().get("id_token")
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Failed to get bKash token: {str(e)}")
#         raise

# @api_view(["POST"])
# def start_payment(request, pk):
#     try:
#         order = ResolvedOrder.objects.get(pk=pk)

#         if order.status == "PD":
#             return Response({"error": "Order is already paid"}, status=status.HTTP_400_BAD_REQUEST)

#         token = get_bkash_token()

#         payload = {
#             "mode": BKASH_PAYMENT_MODE,
#             "payerReference": str(request.user.id if request.user.is_authenticated else "anonymous"),
#             "callbackURL": BKASH_CALLBACK_URL,
#             "amount": str(order.converted_price),
#             "currency": "BDT",
#             "intent": "authorization",
#             "merchantInvoiceNumber": order.tracker
#         }

#         headers = {
#             "Authorization": token,
#             "X-APP-Key": APP_KEY,
#             "Content-Type": "application/json"
#         }

#         create_url = f"{BKASH_BASE_URL}/tokenized/checkout/create"
#         res = requests.post(create_url, json=payload, headers=headers)
#         res.raise_for_status()
#         res_data = res.json()

#         if not res_data.get("paymentID") or not res_data.get("bkashURL"):
#             raise ValueError("Invalid response from bKash API")

#         order.payment_id = res_data.get("paymentID")
#         order.payment_url = res_data.get("bkashURL")
#         order.save()

#         return Response({
#             "bkashURL": res_data.get("bkashURL"),
#             "paymentID": res_data.get("paymentID"),
#             "orderID": order.id
#         })
#     except ResolvedOrder.DoesNotExist:
#         return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Payment initiation failed: {str(e)}")
#         return Response({"error": "Failed to initiate payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     except Exception as e:
#         logger.error(f"Unexpected error in payment initiation: {str(e)}")
#         return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['GET'])
# def bkash_callback(request):
#     try:
#         payment_id = request.GET.get("paymentID")
#         if not payment_id:
#             return Response({"error": "Payment ID is required"}, status=status.HTTP_400_BAD_REQUEST)

#         order = ResolvedOrder.objects.get(payment_id=payment_id)
        
#         if order.status == "PD":
#             return redirect(FRONTEND_SUCCESS_URL)

#         token = get_bkash_token()

#         headers = {
#             "Authorization": token,
#             "X-APP-Key": APP_KEY,
#             "Content-Type": "application/json"
#         }

#         payload = {"paymentID": payment_id}
#         exec_url = f"{BKASH_BASE_URL}/tokenized/checkout/execute"
#         response = requests.post(exec_url, json=payload, headers=headers)
#         response.raise_for_status()
#         data = response.json()

#         if data.get("transactionStatus") == "Completed":
#             order.update_order_status("PD")
#             return redirect(FRONTEND_SUCCESS_URL)
#         elif data.get("transactionStatus") == "Failed":
#             return redirect(FRONTEND_FAILURE_URL)
#         else:
#             logger.warning(f"Unexpected transaction status: {data.get('transactionStatus')}")
#             return redirect(FRONTEND_FAILURE_URL)
            
#     except ResolvedOrder.DoesNotExist:
#         logger.error(f"Order not found for payment ID: {payment_id}")
#         return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Payment verification failed: {str(e)}")
#         return Response({"error": "Failed to verify payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     except Exception as e:
#         logger.error(f"Unexpected error in payment callback: {str(e)}")
#         return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
