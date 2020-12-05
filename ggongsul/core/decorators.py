import logging
import time
import traceback

from functools import wraps

from django.http import HttpResponse, QueryDict
from requests.exceptions import ReadTimeout, ConnectTimeout
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from ggongsul.common import utils
from ggongsul.core.exceptions import (
    ValidationError,
    PasswordMismatch,
    NotAuthError,
    IntegrityError,
    NotAllowedError,
    InvalidArgumentError,
)

logger = logging.getLogger(__name__)


def _print_args(args):
    for arg in args:
        if isinstance(arg, Request):
            arg_dict = arg.data
            if isinstance(arg.data, QueryDict):
                arg_dict = arg.data.dict()

            if "password" in arg_dict:
                arg_dict.pop("password")
            logger.error(arg_dict)
        else:
            logger.error(arg)


def api_status_response(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        tag = "status_response"
        try:
            result = func(*args, **kwargs)
            return Response(result, status=status.HTTP_200_OK)
        except (ValidationError, InvalidArgumentError) as error:
            logger.error("{}.{} error: {}".format(tag, func.__name__, error))
            _print_args(args)
            return HttpResponse(str(error), status=status.HTTP_400_BAD_REQUEST)
        except PasswordMismatch as error:
            logger.error("{}.{} error: {}".format(tag, func.__name__, error))
            _print_args(args)
            return HttpResponse(str(error), status=status.HTTP_403_FORBIDDEN)
        except NotAuthError as error:
            logger.error("{}.{} error: {}".format(tag, func.__name__, error))
            _print_args(args)
            return HttpResponse(str(error), status=status.HTTP_403_FORBIDDEN)
        except IntegrityError as error:
            logger.error("{}.{} error: {}".format(tag, func.__name__, error))
            _print_args(args)
            return HttpResponse(str(error), status=status.HTTP_404_NOT_FOUND)
        except NotAllowedError as error:
            logger.error("{}.{} error: {}".format(tag, func.__name__, error))
            _print_args(args)
            return HttpResponse(str(error), status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as error:
            logger.error("{}.{} error: {}".format(tag, func.__name__, error))
            utils.logging_traceback()
            _print_args(args)
            return HttpResponse(
                "서버에 오류가 발생했습니다.", status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return decorated


def exponential_backoff_retry(func):
    """
    To retry a specific exception
    """

    @wraps(func)
    def decorated(*args, **kwargs):
        for i in range(6):
            try:
                return func(*args, **kwargs)
            except (ReadTimeout, ConnectTimeout) as e:
                # exponential backoff retry
                time.sleep(pow(2, i))
            except Exception as e:
                traceback.print_exc()
                raise e
        raise Exception("ERROR: {} {}".format(func.__name__, "max retry over!!"))

    return decorated
