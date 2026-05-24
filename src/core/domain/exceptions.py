class DomainException(Exception):
    """Base domain exception."""


class InvalidEmailFormat(DomainException):
    pass


class PasswordIsNotSecure(DomainException):
    pass


class PasswordsShouldMatch(DomainException):
    pass


class EmailIsAlreadyInUse(DomainException):
    pass


class UserWithSuchCredentialsDoesNotExist(DomainException):
    pass


class SuchUserDoesNotExist(DomainException):
    pass
