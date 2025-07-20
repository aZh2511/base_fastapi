from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TypeVar


JWTToken = TypeVar("JWTToken", bound=str)


@dataclass
class JWTTokenDTO:
    token: JWTToken
    alive_seconds: int
    expires_at: datetime


class TokenType(Enum):
    access_token = "access_token"
    refresh_token = "refresh_token"


@dataclass
class UserJWTTokenDTO:
    user_uuid: str
    token_type: TokenType


@dataclass
class JWTTokensPair:
    access_token: JWTTokenDTO
    refresh_token: JWTTokenDTO
