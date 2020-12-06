from enum import Enum


class SlackAlertLevel(Enum):
    INFO = "good"
    WARNING = "warning"
    DANGER = "danger"
    GOOGLE = "#009ef3"
