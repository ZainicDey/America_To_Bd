from rest_framework.decorators import action, api_view
from rest_framework.response import Response
import requests
from django.conf import settings
from product.models import Order
from django.shortcuts import redirect
from rest_framework import status
import logging
import json, os
from datetime import datetime, timedelta
from django.utils.timezone import now

from payment.models import BkashToken

logger = logging.getLogger(__name__)

BKASH_BASE_URL = settings.BKASH_BASE_URL
APP_KEY = settings.BKASH_APP_KEY
APP_SECRET = settings.BKASH_APP_SECRET
USERNAME = settings.BKASH_USERNAME
PASSWORD = settings.BKASH_PASSWORD
BKASH_CALLBACK_URL = settings.BKASH_PRODUCT_CALLBACK_URL
BKASH_PAYMENT_MODE = settings.BKASH_PAYMENT_MODE
FRONTEND_SUCCESS_URL = settings.FRONTEND_SUCCESS_URL
FRONTEND_CANCEL_URL = settings.FRONTEND_CANCEL_URL
FRONTEND_FAILURE_URL = settings.FRONTEND_FAILURE_URL

def get_bkash_token():
    token_obj = BkashToken.objects.last()
    if token_obj and now() - token_obj.created_at < timedelta(minutes=55):
        return token_obj.token
    else:
        if token_obj:
            token_obj.delete()

    try:
        token_url = f"{BKASH_BASE_URL}/tokenized/checkout/token/grant"
        headers = {
            "username": USERNAME,
            "password": PASSWORD,
            "Content-Type": "application/json",
            "accept": "application/json" 
        }
        data = {
            "app_key": APP_KEY,
            "app_secret": APP_SECRET
        }
        print("Requesting token with:", headers, data)
        response = requests.post(token_url, json=data, headers=headers)
        print("Token response:", response.status_code, response.text)
        response.raise_for_status()
        
        token = response.json().get("id_token")
        
        # Save the token to the database
        new_token_obj = BkashToken(token=token)
        new_token_obj.save()

        return token
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get bKash token: {str(e)}")
        raise

def start_payment(tracker):
    print(tracker)
    order = Order.objects.get(tracker = tracker)
    print(order)
    try:
        order = Order.objects.get(tracker=tracker)

        if order.status == "PD":
            return Response({"error": "Order is already paid"}, status=status.HTTP_400_BAD_REQUEST)

        print('hit')
        token = get_bkash_token()

        print('')
        print('')
        print('')
        print('')
        print('')
        print(token)
        payload = {
            "mode": BKASH_PAYMENT_MODE,
            "payerReference": str(order.user.email),
            "callbackURL": BKASH_CALLBACK_URL,
            # "amount": str(1),
            "amount": str(order.totalPrice),
            "currency": "BDT",
            "intent": "sale",
            "merchantInvoiceNumber": str(order.tracker)
        }

        headers = {
            "Authorization": token,
            "X-APP-Key": APP_KEY,
            "Content-Type": "application/json",
            "accept": "application/json" 
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
            "orderID": order.tracker
        })
    except order.DoesNotExist:
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
        bkash_status = request.GET.get("status")

        print(bkash_status)
        print('')

        if bkash_status != "success":
            return redirect(FRONTEND_CANCEL_URL)

        if not payment_id:
            return redirect(FRONTEND_FAILURE_URL) 

        print("Payment ID from callback:", payment_id)
        try:
            order = Order.objects.get(payment_id=payment_id)
        except Order.DoesNotExist:
            logger.error(f"Order not found for payment ID: {payment_id}")
            return redirect(FRONTEND_FAILURE_URL)   

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
            "trxId": data.get("trxID", ""),
            "amount": data.get("amount", ""),
            "currency": data.get("currency", ""),
            "intent": data.get("authroization", ""),
            "merchantInvoiceNumber": data.get("merchantInvoiceNumber", ""),
        }
        log_dir = os.path.join(os.path.dirname(__file__), "bkash_logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"bkash_callback_{payment_id}.json")
        with open(log_file, "w") as f:
            json.dump(log_data, f, indent=4)

        # Handle success
        if data.get("statusCode") == "0000" and data.get("transactionStatus") == "Completed":
            order.status = "Accepted"
            order.save()
            return redirect(FRONTEND_SUCCESS_URL)

        # Handle known failure
        if data.get("statusCode") == "2056" or data.get("transactionStatus") == "Failed":
            return redirect(FRONTEND_FAILURE_URL)

        return redirect(FRONTEND_FAILURE_URL)

    except Exception as e:
        logger.error(f"Unexpected error in payment callback: {str(e)}")
        return redirect(FRONTEND_FAILURE_URL)

def bkash_url(tracker):
    print(tracker)
    print('')
    print('')
    print('')
    print('')
    print('')
    print('')
    print('')
    response = start_payment(tracker)
    print(response)
    print('')
    print('')
    print('')
    print('')
    print('')
    print('')
    if isinstance(response, Response) and response.status_code == 200:
        return response.data.get("bkashURL")
    return None