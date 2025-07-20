from typing import Union, AsyncIterable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core.application.handlers import auth as handlers
from core.application.interfaces import IDBSession
from core.domain.repositories import IUserRepository
from infrastructure.config import Config
from infrastructure.database.db_session import new_session_maker
from infrastructure.database.repositories import SQLUserRepository


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    return new_session_maker(Config().postgres)


async def get_db_session(
        session_maker: async_sessionmaker[AsyncSession] = Depends(get_session_maker),
) -> AsyncIterable[Union[AsyncSession, IDBSession]]:
    async with session_maker() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_repository(db_session: AsyncSession = Depends(get_db_session)) -> IUserRepository:
    return SQLUserRepository(db_session)


async def user_signup_command_handler(
        db_session: AsyncSession = Depends(get_db_session),
        repository: IUserRepository = Depends(get_repository),
) -> handlers.CreateUserCommandHandler:
    return handlers.CreateUserCommandHandler(
        db_session=db_session,
        repository=repository,
    )
