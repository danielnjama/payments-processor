import requests
import base64
from datetime import datetime
from django.conf import settings
import logging

logger = logging.getLogger("payments")



class DarajaService:

    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.callback_url = settings.MPESA_CALLBACK_URL
        self.environment = settings.MPESA_ENVIRONMENT

        if self.environment == "live":
            self.base_url = "https://api.safaricom.co.ke"
        else:
            self.base_url = "https://sandbox.safaricom.co.ke"

    # ---------------------------
    # 1️⃣ Generate Access Token
    # ---------------------------
    def get_access_token(self):

        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"

        response = requests.get(
            url,
            auth=(self.consumer_key, self.consumer_secret)
        )

        return response.json().get("access_token")

    # ---------------------------
    # 2️⃣ Generate STK Password
    # ---------------------------
    def generate_password(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        data_to_encode = self.shortcode + self.passkey + timestamp
        encoded_string = base64.b64encode(data_to_encode.encode()).decode()

        return encoded_string, timestamp

    # ---------------------------
    # 3️⃣ Initiate STK Push
    # ---------------------------
    def stk_push(self, phone_number, amount, reference, description):

        access_token = self.get_access_token()
        password, timestamp = self.generate_password()

        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": self.callback_url,
            "AccountReference": reference,
            "TransactionDesc": description,
        }

        logger.info(f"Initiating STK for {phone_number} amount {amount}")

        
        response = requests.post(url, json=payload, headers=headers)
        logger.info(f"Daraja Response: {response.json()}")


        try:
            return response.json()
        except ValueError:
            return {
                "error": "Invalid response from Daraja",
                "status_code": response.status_code,
                "response_text": response.text
            }
