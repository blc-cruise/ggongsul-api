from enum import Enum


class SlackAlertLevel(Enum):
    INFO = "good"
    WARNING = "warning"
    DANGER = "danger"
