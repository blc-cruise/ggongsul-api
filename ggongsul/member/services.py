import logging

from enum import Enum
from ggongsul.common import exceptions
from django.http import QueryDict

from ggongsul.common.helpers import KakaoApiHelper, NaverApiHelper

logger = logging.getLogger(__name__)


class LoginType(Enum):
    Kakao = "KAKAO"
    Naver = "NAVER"


def login(req_dict: QueryDict, login_type: LoginType = None):
    logger.debug(req_dict)
    if login_type == LoginType.Kakao:
        if code := req_dict.get("code", None):
            _login_with_kakao(code, req_dict.get("state", None))
        else:
            raise exceptions.ValidationError(f"There is no code in query params!")
    elif login_type == LoginType.Naver:
        if code := req_dict.get("code", None):
            _login_with_naver(code, req_dict.get("state", None))
        else:
            raise exceptions.ValidationError(f"There is no code in query params!")
    else:
        raise exceptions.InvalidArgumentError(f"Invalid login type {login_type}!")

    return {}


def _login_with_kakao(code: str, state: str):
    logger.debug(f"code: {code}")
    logger.debug(f"state: {state}")
    user_info = KakaoApiHelper(code).get_user_info()

    logger.debug(f"user_info: {user_info}")


def _login_with_naver(code: str, state: str):
    logger.debug(f"code: {code}")
    logger.debug(f"state: {state}")
    user_info = NaverApiHelper(code).get_user_info()

    logger.debug(f"user_info: {user_info}")
