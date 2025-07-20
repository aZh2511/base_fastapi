from dataclasses import dataclass

from core.domain.value_objects import UserUUID
from pydantic import EmailStr


@dataclass(slots=True)
class User:
    uuid: UserUUID
    fullname: str
    email: EmailStr
    hashed_password: str
