from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core.application.dto import JWTToken, TokenType, UserJWTTokenDTO
from core.application.exceptions import AuthenticationFailed
from core.application.interfaces import IDBSession, IJWTService
from infrastructure.config import Config
from infrastructure.database.db_session import new_session_maker
from infrastructure.services.jwt_tokens import JWTService


_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


@lru_cache
def get_config() -> Config:
    return Config()


def get_session_maker(
    config: Annotated[Config, Depends(get_config)],
) -> async_sessionmaker[AsyncSession]:
    return new_session_maker(config)


async def get_db_session(
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_session_maker)
    ],
) -> AsyncIterator[IDBSession]:
    async with session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_jwt_service(
    config: Annotated[Config, Depends(get_config)],
) -> IJWTService:
    return JWTService(config)


async def get_current_user_jwt(
    jwt_service: Annotated[IJWTService, Depends(get_jwt_service)],
    token: Annotated[str, Depends(_oauth2_scheme)],
) -> UserJWTTokenDTO:
    try:
        dto = jwt_service.decode_token(JWTToken(token))
    except AuthenticationFailed:
        raise _CREDENTIALS_EXCEPTION

    if dto.token_type is not TokenType.access_token:
        raise _CREDENTIALS_EXCEPTION

    return dto


SessionDep = Annotated[IDBSession, Depends(get_db_session)]
JWTServiceDep = Annotated[IJWTService, Depends(get_jwt_service)]
AuthenticatedUser = Annotated[UserJWTTokenDTO, Depends(get_current_user_jwt)]
