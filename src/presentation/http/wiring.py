from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Annotated

import httpx
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core.application.interfaces import IDBSession, IJWTService
from infrastructure.config import Config
from infrastructure.database.db_session import new_session_maker
from infrastructure.services.jwt_tokens import JWTService


@lru_cache
def get_config() -> Config:
    return Config()


@lru_cache
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


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


SessionDep = Annotated[IDBSession, Depends(get_db_session)]
JWTServiceDep = Annotated[IJWTService, Depends(get_jwt_service)]
HttpClientDep = Annotated[httpx.AsyncClient, Depends(get_http_client)]
