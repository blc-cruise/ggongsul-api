from typing import List

from rest_framework.exceptions import ValidationError


def validate_dict_key(d: dict, keys: List[str]):
    error_msgs = []

    for k in keys:
        if k in d:
            continue
        error_msgs.append(f"{k} is required!")

    if not error_msgs:
        return [d[k] for k in keys]

    raise ValidationError(error_msgs)
