from core.application.commands import auth as commands
from factory import Factory, Faker, SelfAttribute, Trait, LazyAttribute
from pydantic import EmailStr


class CreateUserCommand(Factory):
    email: EmailStr = Faker("email")
    fullname: str = Faker("name")
    password_1: str = Faker("password")
    password_2: str = SelfAttribute("password_1")

    class Meta:
        model = commands.CreateUserCommand

    class Params:
        mismatching_passwords = Trait(
            password_2=LazyAttribute(lambda obj: obj.password_1 + "different_password")
        )
