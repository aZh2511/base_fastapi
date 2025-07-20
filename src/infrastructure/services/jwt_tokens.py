from datetime import datetime, timedelta, UTC

import jwt
from core.application.interfaces import IJWTService
from core.application.dto import JWTToken, JWTTokenDTO, UserJWTTokenDTO, TokenType
from infrastructure.config import JWTAuthConfig


class JWTException(Exception):
    pass


class InvalidTokenException(JWTException):
    pass


class TokenExpiredException(JWTException):
    pass


class JWTService(IJWTService):
    ALGORITHM = "HS256"

    def __init__(self, jwt_config: JWTAuthConfig) -> None:
        self._settings = jwt_config

    def encode_token(self, data: UserJWTTokenDTO) -> JWTTokenDTO:
        if data.token_type is TokenType.access_token:
            seconds_alive = self._settings.jwt_access_token_lifetime
        elif data.token_type is TokenType.refresh_token:
            seconds_alive = self._settings.jwt_refresh_token_lifetime
        else:
            raise ValueError
        alive_until = datetime.now(UTC) + timedelta(seconds=int(seconds_alive))
        payload = {
            "user_uuid": data.user_uuid,
            "token_type": data.token_type.value,
            "iat": datetime.now(UTC),
            "exp": alive_until,
        }
        token = jwt.encode(
            payload, key=self._settings.jwt_secret_key, algorithm=self.ALGORITHM
        )
        return JWTTokenDTO(
            token=token,
            alive_seconds=seconds_alive,
            expires_at=alive_until,
        )

    def decode_token(self, token: JWTToken) -> UserJWTTokenDTO:
        try:
            decoded_payload = jwt.decode(
                token, self._settings.jwt_secret_key, algorithms=JWTService.ALGORITHM
            )
            return UserJWTTokenDTO(
                user_uuid=decoded_payload["user_uuid"],
                token_type=TokenType(decoded_payload["token_type"]),
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpiredException()
        except (jwt.InvalidTokenError, KeyError):
            raise InvalidTokenException()
