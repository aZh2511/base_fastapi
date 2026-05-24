from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import NewType


JWTToken = NewType("JWTToken", str)


@dataclass(frozen=True, slots=True)
class JWTTokenDTO:
    token: JWTToken
    alive_seconds: int
    expires_at: datetime


class TokenType(Enum):
    access_token = "access_token"
    refresh_token = "refresh_token"


@dataclass(frozen=True, slots=True)
class UserJWTTokenDTO:
    user_uuid: str
    token_type: TokenType


@dataclass(frozen=True, slots=True)
class JWTTokensPair:
    access_token: JWTTokenDTO
    refresh_token: JWTTokenDTO
