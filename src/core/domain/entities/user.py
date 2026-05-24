from dataclasses import dataclass

from core.domain.value_objects import Email, UserUUID


@dataclass(slots=True)
class User:
    uuid: UserUUID
    fullname: str
    email: Email
    hashed_password: str
