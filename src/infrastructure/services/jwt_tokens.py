from datetime import UTC, datetime, timedelta
from typing import ClassVar

import jwt

from core.application.dto import JWTToken, JWTTokenDTO, TokenType, UserJWTTokenDTO
from core.application.exceptions import AuthenticationFailed
from core.application.interfaces import IJWTService
from infrastructure.config import Config


class JWTService(IJWTService):
    ALGORITHM: ClassVar[str] = "HS256"

    def __init__(self, config: Config) -> None:
        self._secret_key = config.jwt_secret_key
        self._access_lifetime = config.jwt_access_token_lifetime_seconds
        self._refresh_lifetime = config.jwt_refresh_token_lifetime_seconds

    def encode_token(self, data: UserJWTTokenDTO) -> JWTTokenDTO:
        seconds_alive = self._lifetime_for(data.token_type)
        alive_until = datetime.now(UTC) + timedelta(seconds=seconds_alive)
        payload = {
            "user_uuid": data.user_uuid,
            "token_type": data.token_type.value,
            "iat": datetime.now(UTC),
            "exp": alive_until,
        }
        token = jwt.encode(payload, key=self._secret_key, algorithm=self.ALGORITHM)
        return JWTTokenDTO(
            token=JWTToken(token),
            alive_seconds=seconds_alive,
            expires_at=alive_until,
        )

    def decode_token(self, token: JWTToken) -> UserJWTTokenDTO:
        try:
            payload = jwt.decode(
                token, self._secret_key, algorithms=[self.ALGORITHM]
            )
            return UserJWTTokenDTO(
                user_uuid=payload["user_uuid"],
                token_type=TokenType(payload["token_type"]),
            )
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError, ValueError) as exc:
            raise AuthenticationFailed("Invalid or expired token") from exc

    def _lifetime_for(self, token_type: TokenType) -> int:
        if token_type is TokenType.access_token:
            return self._access_lifetime
        if token_type is TokenType.refresh_token:
            return self._refresh_lifetime
        raise ValueError(f"Unknown token type: {token_type}")
