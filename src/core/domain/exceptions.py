class DomainException(Exception):
    """Base domain exception"""


class EmailIsAlreadyInUse(DomainException):
    pass


class PasswordsShouldMatch(DomainException):
    pass
