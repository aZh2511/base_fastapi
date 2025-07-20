from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from core.application.interfaces import IDBSession
from infrastructure.config import PostgresConfig


def new_session_maker(psql_config: PostgresConfig) -> async_sessionmaker[AsyncSession]:
    database_uri = psql_config.database_url

    engine = create_async_engine(
        database_uri,
        pool_size=15,
        max_overflow=15,
        connect_args={
            "timeout": 5,
        },


    )
    return async_sessionmaker(engine, class_=AsyncSession, autoflush=False, expire_on_commit=False)


class SQLDBSession(IDBSession):
    async def commit(self) -> None:
        print(f'{self.__class__.__name__}: {id(self)}')

    async def flush(self) -> None:
        print(f'{self.__class__.__name__}: {id(self)}')
