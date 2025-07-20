from sqlalchemy import select

from core.domain import entities as domain
from core.domain.repositories import IUserRepository
from infrastructure.database import models as db


class SQLUserRepository(IUserRepository):
    def __init__(self, db_session) -> None:
        self._db_session = db_session

    async def check_user_exists_by_email(self, email: str) -> bool:
        stmt = select(db.User.uuid).where(db.User.email == email)
        result = await self._db_session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def add_user(self, new_user: domain.User) -> None:
        new_user = db.User(
            email=new_user.email,
            fullname=new_user.fullname,
            uuid=str(new_user.uuid),
            hashed_password=new_user.hashed_password,
        )
        self._db_session.add(new_user)

    async def get_user_by_email(self, email: str) -> domain.User | None:
        stmt = select(db.User).where(db.User.email == email)
        result = await self._db_session.execute(stmt)
        maybe_user = result.scalar_one_or_none()
        if not maybe_user:
            return None
        user = domain.User(
            uuid=maybe_user.uuid,
            email=maybe_user.email,
            fullname=maybe_user.fullname,
            hashed_password=maybe_user.hashed_password,
        )
        return user
