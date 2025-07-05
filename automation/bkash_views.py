from rest_framework.decorators import action, api_view
from rest_framework.response import Response
import requests
from django.conf import settings
from .models import AutomatedOrder
from order.models import ResolvedOrder
from django.shortcuts import redirect
from rest_framework import status
import logging
import json, os
from datetime import datetime, timedelta
from django.utils.timezone import now

from payment.models import BkashToken

from resend import Emails
logger = logging.getLogger(__name__)

BKASH_BASE_URL = settings.BKASH_BASE_URL
APP_KEY = settings.BKASH_APP_KEY
APP_SECRET = settings.BKASH_APP_SECRET
USERNAME = settings.BKASH_USERNAME
PASSWORD = settings.BKASH_PASSWORD
BKASH_CALLBACK_URL = settings.BKASH_AUTOMATION_CALLBACK_URL
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

def start_payment(id):
    try:
        print(id)
        order = AutomatedOrder.objects.get(id=id)

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
            "amount": str(order.bdt_total) if order.status == "pending" else str(order.due - order.discount if order.discount is not None else 0),
            "currency": "BDT",
            "intent": "sale",
            "merchantInvoiceNumber": order.id
        }
        print(BKASH_CALLBACK_URL)
        print(order.status)
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
        return res_data.get("bkashURL")
    
    except AutomatedOrder.DoesNotExist:
        return "Order not found"
    except requests.exceptions.RequestException as e:
        logger.error(f"Payment initiation failed: {str(e)}")
        order.delete() if order else None
        return "Failed to initiate payment"
    except Exception as e:
        order.delete() if order else None
        logger.error(f"Unexpected error in payment initiation: {str(e)}")
        return "An unexpected error occurred"

@api_view(['GET'])
def bkash_callback(request):
    try:
        print(BKASH_CALLBACK_URL)
        payment_id = request.GET.get("paymentID")
        bkash_status = request.GET.get("status")

        print(bkash_status)
        print('')

        if bkash_status != "success":
            order = AutomatedOrder.objects.filter(payment_id=payment_id).first()
            order.delete() if order else None
            return redirect(FRONTEND_CANCEL_URL)

        if not payment_id:
            return redirect(FRONTEND_FAILURE_URL) 

        print("Payment ID from callback:", payment_id)
        try:
            order = AutomatedOrder.objects.get(payment_id=payment_id)
        except AutomatedOrder.DoesNotExist:
            logger.error(f"Order not found for payment ID: {payment_id}")
            return redirect(FRONTEND_FAILURE_URL)   

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
            order.delete() if order else None
            logger.error(f"Execute request failed: {str(e)}")
            return redirect(FRONTEND_FAILURE_URL)
        except ValueError:
            order.delete() if order else None
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
            if order.status == "pending":
                return redirect(FRONTEND_SUCCESS_URL)
            order.status = "accepted"
            order.cost = order.bdt_total + order.due - (order.discount if order.discount is not None else 0)
            order.save()
            user = order.user
            Emails.send({
                "from": "America to BD <noreply@americatobd.com>",
                "to": [user.email],
                "subject": "Payment Confirmation - America to BD",
                "html": f"""
                <h2>Your payment is confirmed!</h2>
                <p>Dear {user.first_name} {user.last_name},</p>
                <p>Your order is being processed now. Title: {order.title}</p>
                <p>Total cost: {order.cost}</p>
                <p>Thank you for choosing America to BD!</p>
                """
            })
            return redirect(FRONTEND_SUCCESS_URL)

        # Handle known failure
        if data.get("statusCode") == "2056" or data.get("transactionStatus") == "Failed":
            return redirect(FRONTEND_FAILURE_URL)

        return redirect(FRONTEND_FAILURE_URL)

    except Exception as e:
        logger.error(f"Unexpected error in payment callback: {str(e)}")
        return redirect(FRONTEND_FAILURE_URL)

