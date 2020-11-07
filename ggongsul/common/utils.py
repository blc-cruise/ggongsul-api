import sys
import traceback
import logging

logger = logging.getLogger(__name__)


def logging_traceback():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    error_message = "".join(lines)
    logger.error(error_message)
