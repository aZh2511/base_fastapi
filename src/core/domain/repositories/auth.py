from typing import Protocol

from core.domain.entities import User
from core.domain.value_objects import Email, UserUUID


class IUserRepository(Protocol):
    async def add_user(self, user: User) -> None: ...

    async def get_user_by_email(self, email: Email) -> User | None: ...

    async def get_user_by_uuid(self, user_uuid: UserUUID) -> User | None: ...
