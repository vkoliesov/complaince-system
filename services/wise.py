import requests
import json
import uuid
from decouple import config

from fastapi.exceptions import HTTPException

class WiseService:
    def __init__(self):
        self.main_url = config("WISE_URL")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config('WISE_TOKEN')}"
        }
        self.profile_id = self._get_profile_id()

    def _get_profile_id(self):
        url = self.main_url + "/v2/profiles"
        resp = requests.get(url, headers=self.headers)

        if resp.status_code == 200:
            resp = resp.json()
            return [el["id"] for el in resp if el["type"] == "PERSONAL"][0]
        print(resp)
        raise HTTPException(500, "Payment provider is not available at the moment.")

    def create_quote(self, amount):
        url = self.main_url + f"/v3/profiles/{self.profile_id}/quotes"
        data = {
            "sourceCurrency": "EUR",
            "targetCurrency": "EUR",
            "sourceAmount": amount,
        }

        resp = requests.post(
            url,
            headers=self.headers,
            data=json.dumps(data)
        )

        if resp.status_code == 200:
            resp = resp.json()
            return resp["id"]
        print(resp)
        raise HTTPException(500, "Payment provider is not available at the moment.")

    def create_recipient_account(self, full_name, iban):
        url = self.main_url + "/v1/accounts"
        data = {
          "currency": "EUR",
          "type": "iban",
          "profile": self.profile_id,
          "ownedByCustomer": True,
          "accountHolderName": full_name,
           "details": {
              "legalType": "PRIVATE",
              "iban": iban
           }
         }

        resp = requests.post(
            url,
            headers=self.headers,
            data=json.dumps(data)
        )

        if resp.status_code == 200:
            resp = resp.json()
            return resp["id"]
        print(resp)
        raise HTTPException(500, "Payment provider is not available at the moment.")

    def create_transfer(self, target_account_id, quote_id):
        customer_transaction_id = str(uuid.uuid4())
        url = self.main_url + "/v1/transfers"
        data = {
            "targetAccount": target_account_id,
            "quoteUuid": quote_id,
            "customerTransactionId": customer_transaction_id,
        }
        resp = requests.post(
            url,
            headers=self.headers,
            data=json.dumps(data)
        )

        if resp.status_code == 200:
            resp = resp.json()
            return resp["id"]
        print(resp)
        raise HTTPException(500, "Payment provider is not available at the moment.")

    def fund_transfer(self, tranfer_id):
        url = self.main_url + f"/v3/profiles/{self.profile_id}/transfers/{tranfer_id}/payments"
        data = {
            "type": "BALANCE"
        }
        resp = requests.post(
            url,
            headers=self.headers,
            data=json.dumps(data)
        )

        if resp.status_code == 201:
            resp = resp.json()
            return resp
        print(resp)
        raise HTTPException(500, "Payment provider is not available at the moment.")
