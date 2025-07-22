class ApplicationException(Exception):
    pass


# todo: where does it really belong to? application does not know about implementation details. hence, how can I
#  maintain infra exceptions on the application level?
class JWTException(ApplicationException):
    pass


class InvalidTokenException(JWTException):
    pass


class TokenExpiredException(JWTException):
    pass
