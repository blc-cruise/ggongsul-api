import requests
from rest_framework import status

from ggongsul import settings
from ggongsul.core import exceptions


class IMPHelper:
    _api_key: str
    _api_secret: str
    _session: requests.Session
    _base_url: str

    def __init__(self, api_key: str = None, api_secret: str = None):
        self._api_key = api_key if api_key else settings.IMP_REST_API_KEY
        self._api_secret = api_secret if api_secret else settings.IMP_REST_API_SECRET

        self._session = requests.Session()
        self._base_url = "https://api.iamport.kr"
        self._update_auth_token()

    def __del__(self):
        if self._session is not None:
            self._session.close()

    def _request(
        self,
        uri: str,
        method: str,
        data: dict = None,
        json: dict = None,
        retry_cnt: int = 0,
    ) -> requests.Response:
        if retry_cnt > 3:
            raise exceptions.CommError(
                f"Too many retry count! uri: {uri}, cnt: {retry_cnt}"
            )

        url = f"{self._base_url}{uri}"
        if method == "get":
            res = self._session.get(url, data=data, json=json)
        elif method == "post":
            res = self._session.post(url, data=data, json=json)
        elif method == "delete":
            res = self._session.delete(url, data=data, json=json)
        else:
            raise exceptions.CommError("Not allowed Method!")

        if res.status_code == status.HTTP_401_UNAUTHORIZED:
            self._update_auth_token()
            res = self._request(
                uri, method, data=data, json=json, retry_cnt=retry_cnt + 1
            )

        if res.status_code != status.HTTP_200_OK:
            raise exceptions.BadResponse(res.text, uri, res.status_code)

        return res

    def _get_imp_response(self, raw_resp: requests.Response):
        result: dict = raw_resp.json()
        if result["code"] != 0:
            raise exceptions.BadResponse(
                result.get("message"),
                "imp response",
                result.get("code"),
            )
        return result.get("response")

    def _get_token(self):
        uri = "/users/getToken"
        method = "post"
        json = {"imp_key": self._api_key, "imp_secret": self._api_secret}
        resp = self._request(uri, method, json=json)
        return self._get_imp_response(resp)["access_token"]

    def _update_auth_token(self):
        self._session.headers.update({"Authorization": f"Bearer {self._get_token()}"})

    def get_customer_uid_info(self, customer_uid: str):
        uri = f"/subscribe/customers/{customer_uid}"
        method = "get"
        resp = self._request(uri, method)
        return self._get_imp_response(resp)

    def delete_customer_uid_info(self, customer_uid: str):
        uri = f"/subscribe/customers/{customer_uid}"
        method = "delete"
        resp = self._request(uri, method)
        return self._get_imp_response(resp)

    def make_payment(
        self, customer_uid: str, merchant_uid: str, amount: int, name: str
    ):
        uri = f"/subscribe/payments/again"
        method = "post"
        json = {
            "customer_uid": customer_uid,
            "merchant_uid": merchant_uid,
            "amount": amount,
            "name": name,
        }
        resp = self._request(uri, method, json=json)
        return self._get_imp_response(resp)

    def cancel_payment(
        self,
        imp_uid: str,
        merchant_uid: str = None,
        amount: int = None,
        reason: str = None,
    ):
        uri = f"/payments/cancel"
        method = "post"
        json = {
            "imp_uid": imp_uid,
            "merchant_uid": merchant_uid,
            "amount": amount,
            "reason": reason,
        }
        resp = self._request(uri, method, json=json)
        return self._get_imp_response(resp)

    def is_customer_uid_exist(self, customer_uid: str) -> bool:
        try:
            self.get_customer_uid_info(customer_uid=customer_uid)
        except exceptions.BadResponse as e:
            if e.status_code != 1:
                raise e
            return False
        return True
