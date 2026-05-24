import re
from dataclasses import dataclass, field
from typing import ClassVar
from uuid import UUID, uuid4

from core.domain.exceptions import InvalidEmailFormat, PasswordIsNotSecure


@dataclass(frozen=True, slots=True)
class UserUUID:
    value: UUID = field(default_factory=uuid4)

    def __str__(self) -> str:
        return str(self.value)


_EMAIL_RE: re.Pattern[str] = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if not _EMAIL_RE.match(self.value):
            raise InvalidEmailFormat(f"Invalid email: {self.value!r}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Password:
    value: str = field(repr=False)

    MIN_LENGTH: ClassVar[int] = 8
    _SYMBOLS: ClassVar[re.Pattern[str]] = re.compile(r"[!@#$%^&*()]")
    _LOWERCASE: ClassVar[re.Pattern[str]] = re.compile(r"[a-z]")
    _UPPERCASE: ClassVar[re.Pattern[str]] = re.compile(r"[A-Z]")
    _DIGIT: ClassVar[re.Pattern[str]] = re.compile(r"\d")

    def __post_init__(self) -> None:
        if not self._is_secure(self.value):
            raise PasswordIsNotSecure("Password does not meet security requirements.")

    @classmethod
    def _is_secure(cls, value: str) -> bool:
        if len(value) < cls.MIN_LENGTH:
            return False
        if not cls._SYMBOLS.search(value):
            return False
        if not cls._LOWERCASE.search(value):
            return False
        if not cls._UPPERCASE.search(value):
            return False
        if not cls._DIGIT.search(value):
            return False
        return True
