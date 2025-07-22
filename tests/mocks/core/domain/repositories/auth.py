from core.domain.repositories import IUserRepository
from core.domain.entities import User
from collections import defaultdict


class MockedUserRepository(IUserRepository):
    def __init__(self) -> None:
        self._tables = defaultdict(dict)

    async def check_user_exists_by_email(self, email: str) -> bool:
        maybe_record = next(
            filter(
                lambda r: r.email == email,
                self._tables["user"].values(),
            ),
            None,
        )
        return bool(maybe_record)

    async def add_user(self, new_user: User) -> None:
        self._tables["user"][str(new_user.uuid)] = new_user

    async def get_user_by_email(self, email: str) -> User | None:
        maybe_record = next(
            filter(
                lambda r: r.email == email,
                self._tables["user"].values(),
            ),
            None,
        )
        return maybe_record

    async def get_user_by_uuid(self, user_uuid: str) -> User | None:
        maybe_record = self._tables["user"].get(user_uuid)
        return maybe_record
