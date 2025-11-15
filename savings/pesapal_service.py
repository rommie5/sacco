import json, uuid, requests
from django.conf import settings

PESAPAL_BASE_URL = "https://pay.pesapal.com/v3"
CONSUMER_KEY = settings.PESAPAL_CONSUMER_KEY
CONSUMER_SECRET = settings.PESAPAL_CONSUMER_SECRET
IPN_ID = settings.PESAPAL_IPN_ID


def get_access_token():
    resp = requests.post(
        f"{PESAPAL_BASE_URL}/Auth/RequestToken",
        json={
            "consumer_key": "8sdX0mBowUeoJZGvX+HX1BcAP3HnwbXA",
            "consumer_secret": "5QcPzMsvQ8suffgtyNg9px/ovw4=",
        }
    )
    resp.raise_for_status()
    return resp.json()["token"]


def submit_order(amount, email, phone, callback_url, purpose="Deposit"):
    token = get_access_token()
    payload = {
        "id": str(uuid.uuid4()),
        "currency": "UGX",
        "amount": float(amount),
        "description": purpose,
        "callback_url": callback_url,
        "notification_id": IPN_ID,
        "billing_address": {
            "email_address": email,
            "phone_number": phone,
            "country_code": "UG",
            "first_name": "User",
            "last_name": "Member",
        },
    }
    resp = requests.post(
        f"{PESAPAL_BASE_URL}/Transactions/SubmitOrderRequest",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )
    resp.raise_for_status()
    return resp.json()
