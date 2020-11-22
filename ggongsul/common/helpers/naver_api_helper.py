import requests

from django.conf import settings
from rest_framework import status

from ggongsul.core import exceptions


class NaverApiHelper:
    _client_id: str
    _client_secret: str
    _session: requests.Session

    _access_token: str = None
    _refresh_token: str = None

    def __init__(
        self,
        code: str,
        client_id: str = None,
        client_secret: str = None,
    ):
        self._client_id = client_id if client_id else settings.NAVER_API_CLIENT_ID
        self._client_secret = (
            client_secret if client_secret else settings.NAVER_API_CLIENT_SECRET
        )
        self._session = requests.Session()

        self._get_token(code)
        self._update_auth_header()

    def __del__(self):
        if self._session is not None:
            self._session.close()

    def _request(
        self, url: str, method: str, data: dict = None, json: dict = None
    ) -> dict:
        if method == "get":
            res = self._session.get(url, data=data, json=json)
        elif method == "post":
            res = self._session.post(url, data=data, json=json)
        else:
            raise exceptions.CommError("Not allowed Method!")

        if res.status_code == status.HTTP_400_BAD_REQUEST:
            raise exceptions.InvalidArgumentError("잘못된 NAVER code 인증입니다!")

        if res.status_code == status.HTTP_401_UNAUTHORIZED:
            res_json = res.json()
            if "code" in res_json and res_json["code"] == -401:
                self._update_token()
                res = self._request(url, method, data=data, json=json)

        if res.status_code != status.HTTP_200_OK:
            raise exceptions.BadResponse(res.text, url, res.status_code)

        return res.json()

    def _update_auth_header(self):
        if not self._access_token:
            raise exceptions.CommError("There is no access token!")

        self._session.headers.update(
            {
                "Authorization": "Bearer " + self._access_token,
            }
        )

    def _get_token(self, code: str):
        base_url = "https://nid.naver.com"
        uri = "/oauth2.0/token"
        method = "post"
        data = {
            "grant_type": "authorization_code",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "code": code,
        }
        res = self._request(base_url + uri, method, data=data)

        self._access_token = res["access_token"]
        self._refresh_token = res["refresh_token"]

    def _update_token(self):
        if not self._refresh_token:
            raise exceptions.CommError("There is no refresh token!")

        base_url = "https://nid.naver.com"
        uri = "/oauth2.0/token"
        method = "post"
        data = {
            "grant_type": "refresh_token",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "refresh_token": self._refresh_token,
        }
        res = self._request(base_url + uri, method, data=data)

        self._access_token = res["access_token"]
        if "refresh_token" in res:
            self._refresh_token = res["refresh_token"]

        self._update_auth_header()

    def get_user_info(self):
        base_url = "https://openapi.naver.com"
        uri = "/v1/nid/me"
        method = "get"

        return self._request(base_url + uri, method)
