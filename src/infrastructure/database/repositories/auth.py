from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.domain.entities import User as UserEntity
from core.domain.repositories import IUserRepository
from core.domain.value_objects import Email, UserUUID
from infrastructure.database.models import User as UserModel


class SQLUserRepository(IUserRepository):
    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session = db_session

    async def add_user(self, user: UserEntity) -> None:
        model = UserModel(
            uuid=str(user.uuid),
            fullname=user.fullname,
            email=str(user.email),
            hashed_password=user.hashed_password,
        )
        self._db_session.add(model)

    async def get_user_by_email(self, email: Email) -> UserEntity | None:
        stmt = select(UserModel).where(UserModel.email == str(email))
        result = await self._db_session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row is not None else None

    async def get_user_by_uuid(self, user_uuid: UserUUID) -> UserEntity | None:
        stmt = select(UserModel).where(UserModel.uuid == str(user_uuid))
        result = await self._db_session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row is not None else None

    @staticmethod
    def _to_entity(model: UserModel) -> UserEntity:
        return UserEntity(
            uuid=UserUUID(UUID(str(model.uuid))),
            fullname=model.fullname,
            email=Email(model.email),
            hashed_password=model.hashed_password,
        )
