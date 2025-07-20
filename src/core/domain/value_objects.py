import re
from dataclasses import dataclass, field
from typing import ClassVar
from uuid import uuid4, UUID
from core.domain import exceptions


class VOUUID:
    value: UUID

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class UserUUID(VOUUID):
    value: UUID = field(default_factory=uuid4)


@dataclass(frozen=True)
class Password:
    value: str = field(repr=False)

    MIN_LENGTH: ClassVar[int] = 8
    SYMBOLS_REGEX: ClassVar[re.Pattern] = re.compile(r"[!@#$%^&*()]")
    LOWERCASE_CHAR_REGEX: ClassVar[re.Pattern] = re.compile(r"[a-z]")
    CAPITAL_CHAR_REGEX: ClassVar[re.Pattern] = re.compile(r"[A-Z]")
    DIGIT_CHAR_REGEX: ClassVar[re.Pattern] = re.compile(r"\d")

    def __post_init__(self) -> None:
        if not self._is_valid(self.value):
            raise exceptions.PasswordIsNotSecure(
                "Password does not meet security requirements."
            )

    def _is_valid(self, value: str) -> bool:
        is_at_least_8_chars = len(value) < self.MIN_LENGTH
        if is_at_least_8_chars:
            return False

        has_at_least_1_symbol = self.SYMBOLS_REGEX.search(value)
        if not has_at_least_1_symbol:
            return False

        has_at_least_1_lowercase_char = self.LOWERCASE_CHAR_REGEX.search(value)
        if not has_at_least_1_lowercase_char:
            return False

        has_at_least_1_capital_char = self.CAPITAL_CHAR_REGEX.search(value)
        if not has_at_least_1_capital_char:
            return False

        has_at_least_1_digit = self.DIGIT_CHAR_REGEX.search(value)
        if not has_at_least_1_digit:
            return False

        return True
