import requests

from django.conf import settings
from rest_framework import status

from ggongsul.core import exceptions


class KakaoApiHelper:
    _api_key: str
    _session: requests.Session

    def __init__(self, api_key: str = None):
        self._api_key = api_key if api_key else settings.KAKAO_REST_API_KEY
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"KakaoAK {self._api_key}"})

    def __del__(self):
        if self._session is not None:
            self._session.close()

    def _request(
        self,
        url: str,
        method: str,
        params: dict = None,
        data: dict = None,
        json: dict = None,
    ) -> dict:
        if method == "get":
            res = self._session.get(url, params=params, data=data, json=json)
        elif method == "post":
            res = self._session.post(url, params=params, data=data, json=json)
        else:
            raise exceptions.CommError("Not allowed Method!")

        if res.status_code != status.HTTP_200_OK:
            raise exceptions.BadResponse(res.text, url, res.status_code)

        return res.json()

    def search_address(self, query: str, page: int = 1, address_size: int = 10) -> dict:
        base_url = "https://dapi.kakao.com"
        uri = "/v2/local/search/address.json"
        method = "get"

        return self._request(
            base_url + uri,
            method,
            params={"query": query, "page": page, "AddressSize": address_size},
        )
