from core.domain.entities import User
from core.domain.repositories import IUserRepository
from core.domain.value_objects import Email, UserUUID


class FakeUserRepository(IUserRepository):
    def __init__(self, seed: list[User] | None = None) -> None:
        self.added: list[User] = []
        self._by_uuid: dict[str, User] = {}
        self._by_email: dict[str, User] = {}
        for user in seed or []:
            self._index(user)

    async def add_user(self, user: User) -> None:
        self.added.append(user)
        self._index(user)

    async def get_user_by_email(self, email: Email) -> User | None:
        return self._by_email.get(str(email))

    async def get_user_by_uuid(self, user_uuid: UserUUID) -> User | None:
        return self._by_uuid.get(str(user_uuid))

    def _index(self, user: User) -> None:
        self._by_uuid[str(user.uuid)] = user
        self._by_email[str(user.email)] = user
