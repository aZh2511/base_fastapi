class DomainException(Exception):
    """Base domain exception"""


class PasswordIsNotSecure(DomainException):
    pass


class EmailIsAlreadyInUse(DomainException):
    pass


class PasswordsShouldMatch(DomainException):
    pass


class UserWithSuchCredentialsDoesNotExist(DomainException):
    pass
