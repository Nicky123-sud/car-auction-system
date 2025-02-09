import requests
import base64
import datetime
from django.conf import settings
from django.http import JsonResponse
from .models import Payment
from .mpesa import get_mpesa_access_token
from django.views.decorators.csrf import csrf_exempt
import json


# ✅ Triggers an STK Push request to M-Pesa API
# ✅ Sends payment request to buyer's phone


def stk_push(request):
    phone_number = request.GET.get("phone_number")
    amount = request.GET.get("amount")

    access_token = get_mpesa_access_token()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()).decode()

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://yourdomain.com/api/mpesa/callback/",
        "AccountReference": "CarAuction",
        "TransactionDesc": "Car Auction Payment"
    }

    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
    response = requests.post(url, json=payload, headers=headers)

    return JsonResponse(response.json())


# ✅ Handles M-Pesa callback response
# ✅ Updates payment status in the database
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body)
    result_code = data["Body"]["stkCallback"]["ResultCode"]
    phone_number = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][4]["Value"]

    if result_code == 0:
        amount = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][0]["Value"]
        payment = Payment.objects.create(phone_number=phone_number, amount=amount, status="Completed")
        return JsonResponse({"message": "Payment successful"}, status=200)

    return JsonResponse({"message": "Payment failed"}, status=400)


