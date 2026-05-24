class ApplicationException(Exception):
    """Base application exception."""


class AuthenticationFailed(ApplicationException):
    pass
