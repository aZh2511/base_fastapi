from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from infrastructure.config import Config


def new_session_maker(config: Config) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(
        config.database_url,
        pool_size=15,
        max_overflow=15,
        connect_args={"timeout": 5},
    )
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )
