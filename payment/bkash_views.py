from rest_framework.decorators import action, api_view
from rest_framework.response import Response
import requests
from django.conf import settings
from order.models import ResolvedOrder
from django.shortcuts import redirect
from rest_framework import status
import logging
import json, os
from datetime import datetime

logger = logging.getLogger(__name__)

BKASH_BASE_URL = settings.BKASH_BASE_URL
APP_KEY = settings.BKASH_APP_KEY
APP_SECRET = settings.BKASH_APP_SECRET
USERNAME = settings.BKASH_USERNAME
PASSWORD = settings.BKASH_PASSWORD
BKASH_CALLBACK_URL = settings.BKASH_CALLBACK_URL
BKASH_PAYMENT_MODE = settings.BKASH_PAYMENT_MODE
FRONTEND_SUCCESS_URL = settings.FRONTEND_SUCCESS_URL
FRONTEND_FAILURE_URL = settings.FRONTEND_FAILURE_URL

def get_bkash_token():
    print('token hit')
    try:
        token_url = f"{BKASH_BASE_URL}/tokenized/checkout/token/grant"
        headers = {
            "username": USERNAME,
            "password": PASSWORD,
            "Content-Type": "application/json",
            "accept": "application/json"  # <- ADD THIS
        }
        data = {
            "app_key": APP_KEY,
            "app_secret": APP_SECRET
        }
        print("Requesting token with:", headers, data)
        response = requests.post(token_url, json=data, headers=headers)
        print("Token response:", response.status_code, response.text)
        response.raise_for_status()
        return response.json().get("id_token")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get bKash token: {str(e)}")
        raise

@api_view(["GET"])
def start_payment(request, pk):
    print('hit')
    try:
        order = ResolvedOrder.objects.get(pk=pk)

        if order.status == "PD":
            return Response({"error": "Order is already paid"}, status=status.HTTP_400_BAD_REQUEST)

        token = get_bkash_token()

        payload = {
            "mode": BKASH_PAYMENT_MODE,
            "payerReference": str(request.user.id if request.user.is_authenticated else "anonymous"),
            "callbackURL": BKASH_CALLBACK_URL,
            # "amount": str(1),
            "amount": str(order.converted_price),
            "currency": "BDT",
            "intent": "sale",
            "merchantInvoiceNumber": order.tracker
        }

        headers = {
            "Authorization": token,
            "X-APP-Key": APP_KEY,
            "Content-Type": "application/json",
            "accept": "application/json"  # <- ADD THIS
        }

        create_url = f"{BKASH_BASE_URL}/tokenized/checkout/create"
        res = requests.post(create_url, json=payload, headers=headers)
        res.raise_for_status()
        res_data = res.json()

        if not res_data.get("paymentID") or not res_data.get("bkashURL"):
            raise ValueError("Invalid response from bKash API")

        order.payment_id = res_data.get("paymentID")
        order.payment_url = res_data.get("bkashURL")
        order.save()

        print('')
        print('')
        print('')
        print('')
        print(res_data)
        print('')
        print('')
        print('')
        return Response({
            "bkashURL": res_data.get("bkashURL"),
            "paymentID": res_data.get("paymentID"),
            "orderID": order.id
        })
    except ResolvedOrder.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    except requests.exceptions.RequestException as e:
        logger.error(f"Payment initiation failed: {str(e)}")
        return Response({"error": "Failed to initiate payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Unexpected error in payment initiation: {str(e)}")
        return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def bkash_callback(request):
    try:
        payment_id = request.GET.get("paymentID")
        if not payment_id:
            return redirect(FRONTEND_FAILURE_URL)  # changed

        print("Payment ID from callback:", payment_id)

        try:
            order = ResolvedOrder.objects.get(payment_id=payment_id)
        except ResolvedOrder.DoesNotExist:
            logger.error(f"Order not found for payment ID: {payment_id}")
            return redirect(FRONTEND_FAILURE_URL)  # changed

        if order.status == "PD":
            return redirect(FRONTEND_SUCCESS_URL)

        # Get token
        token = get_bkash_token()
        headers = {
            "Authorization": token,
            "X-APP-Key": APP_KEY,
            "Content-Type": "application/json"
        }

        exec_url = f"{BKASH_BASE_URL}/tokenized/checkout/execute"
        try:
            response = requests.post(exec_url, json={"paymentID": payment_id}, headers=headers)
            data = response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Execute request failed: {str(e)}")
            return redirect(FRONTEND_FAILURE_URL)
        except ValueError:
            logger.error(f"Invalid JSON in execute response")
            return redirect(FRONTEND_FAILURE_URL)

        print("Execute API response:", data)

        log_data = {
            "paymentID": data.get("paymentID", payment_id),
            "createTime": data.get("createTime", datetime.utcnow().isoformat()),
            "orgLogo": data.get("orgLogo", ""),
            "orgName": data.get("orgName", ""),
            "transactionStatus": data.get("transactionStatus", ""),
            "amount": data.get("amount", ""),
            "currency": data.get("currency", ""),
            "intent": data.get("intent", ""),
            "merchantInvoiceNumber": data.get("merchantInvoiceNumber", ""),
        }
        log_dir = os.path.join(os.path.dirname(__file__), "bkash_logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"bkash_callback_{payment_id}.json")
        with open(log_file, "w") as f:
            json.dump(log_data, f, indent=4)

        # Handle success
        if data.get("statusCode") == "0000" and data.get("transactionStatus") == "Completed":
            order.update_order_status("PD")
            return redirect(FRONTEND_SUCCESS_URL)

        # Handle known failure
        if data.get("statusCode") == "2056" or data.get("transactionStatus") == "Failed":
            return redirect(FRONTEND_FAILURE_URL)

        return redirect(FRONTEND_FAILURE_URL)

    except Exception as e:
        logger.error(f"Unexpected error in payment callback: {str(e)}")
        return redirect(FRONTEND_FAILURE_URL)
