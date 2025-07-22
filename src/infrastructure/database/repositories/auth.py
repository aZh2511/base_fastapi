from sqlalchemy import select

from core.domain import entities as domain
from core.domain.entities import User
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
        user = self._translate_db_user_to_domain(maybe_user)
        return user

    async def get_user_by_uuid(self, user_uuid: str) -> domain.User | None:
        stmt = select(db.User).where(db.User.uuid == user_uuid)
        result = await self._db_session.execute(stmt)
        maybe_user = result.scalar_one_or_none()
        if not maybe_user:
            return None
        user = self._translate_db_user_to_domain(maybe_user)
        return user

    def _translate_db_user_to_domain(self, user_in_db: User) -> domain.User:
        return domain.User(  # todo: use pydantic.BaseModel
            uuid=user_in_db.uuid,
            email=user_in_db.email,
            fullname=user_in_db.fullname,
            hashed_password=user_in_db.hashed_password,
        )
