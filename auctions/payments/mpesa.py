import requests
from django.conf import settings
# ✅ Generates an access token for authentication


def get_mpesa_access_token():
    url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
    access_token = response.json().get("access_token")
    return access_token
