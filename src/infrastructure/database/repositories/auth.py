from core.domain.repositories import IUserRepository
from core.domain import entities as domain
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database import models as db


class SQLUserRepository(IUserRepository):
    def __init__(self, db_session) -> None:
        self._db_session = db_session

    async def check_user_exists_by_email(self, email: str) -> bool:
        print(f'{self.__class__.__name__} - session id: {id(self._db_session)}')
        print('ooops')
        stmt = select(db.User.uuid).where(db.User.email == email)
        result = await self._db_session.execute(stmt)
        return result.scalar_one_or_none() is not None


    async def add_user(self, new_user: domain.User) -> None:
        print(f'{self.__class__.__name__} - session id: {id(self._db_session)}')
        print('added')
        new_user = db.User(
            email=new_user.email,
            fullname=new_user.fullname,
            uuid=str(new_user.uuid),
        )
        self._db_session.add(new_user)
