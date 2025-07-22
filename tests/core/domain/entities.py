from core.domain import entities
from factory import Factory, Faker, LazyAttribute
from core.domain import value_objects as vo


def secure_password() -> str:
    mandatory = "A!a3"

    return mandatory + "a" * 8


class User(Factory):
    uuid: vo.UserUUID = LazyAttribute(lambda _: vo.UserUUID())
    fullname: str = Faker("name")
    email: str = Faker("email")
    hashed_password: str = LazyAttribute(lambda _: secure_password())

    class Meta:
        model = entities.User
