from core.domain import entities
from factory import Factory, Faker, LazyAttribute
from core.domain import value_objects as vo


class User(Factory):
    uuid: vo.UserUUID = LazyAttribute(lambda _: vo.UserUUID())
    fullname: str = Faker("name")
    email: str = Faker("email")
    hashed_password: str = Faker("password")

    class Meta:
        model = entities.User
