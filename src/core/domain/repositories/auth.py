from .base import IRepository
from core.domain.entities import User


class IUserRepository(IRepository):
    async def check_user_exists_by_email(self, email: str) -> bool: ...

    async def add_user(self, new_user: User) -> None: ...

    async def get_user_by_email(self, email: str) -> User | None: ...
