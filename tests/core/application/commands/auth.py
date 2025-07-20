from core.application.commands import auth as commands
from factory import Factory, Faker
from pydantic import EmailStr


class CreateUserCommand(Factory):
    email: EmailStr = Faker("email")
    fullname: str = Faker("name")

    class Meta:
        model = commands.CreateUserCommand
