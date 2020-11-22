import typing


class ERROR(Exception):
    text: str

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return f"{self.__class__.__name__}: {self.text}"

    def __repr__(self):
        return self.__str__()


class InvalidArgumentError(ERROR):
    pass


class ValidationError(ERROR):
    pass


class IntegrityError(ERROR):
    pass


class PasswordMismatch(ERROR):
    pass


class NotAuthError(ERROR):
    pass


class NotAllowedError(ERROR):
    pass


class CommError(ERROR):
    pass


class BadResponse(ERROR):
    uri: typing.Union[str, None]
    status_code: typing.Union[int, None]

    def __init__(self, text, uri=None, status_code=None):
        super().__init__(text)
        self.uri = uri
        self.status_code = status_code

    def __str__(self):
        if self.uri and self.status_code:
            return f"{self.__class__.__name__}: {self.uri} -> response status code: {self.status_code}, response body: {self.text}"
        super().__str__()

    def __repr__(self):
        return self.__str__()
