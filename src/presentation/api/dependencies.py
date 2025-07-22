from typing import Annotated

from fastapi import Depends
from fastapi import status, HTTPException
from fastapi.security import OAuth2PasswordBearer

from core.application.dto import UserJWTTokenDTO, JWTToken, TokenType
from core.application.exceptions import JWTException
from core.application.interfaces import IJWTService
from infrastructure.config import Config
from infrastructure.services.jwt_tokens import JWTService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_config() -> Config:
    return Config()


def get_jwt_service(config: Config = Depends(get_config)) -> IJWTService:
    return JWTService(config.jwt_auth)


def get_user_jwt_dto(
    jwt_service: IJWTService = Depends(get_jwt_service),
    token: JWTToken = Depends(oauth2_scheme),
) -> UserJWTTokenDTO:
    try:
        dto = jwt_service.decode_token(token)
        if dto.token_type != TokenType.access_token:
            raise CREDENTIALS_EXCEPTION

        return dto
    except JWTException:
        raise CREDENTIALS_EXCEPTION


CurrentUserJWTData = Annotated[UserJWTTokenDTO, Depends(get_user_jwt_dto)]
