from .base import Command
from pydantic import EmailStr


class CreateUserCommand(Command):
    email: EmailStr
    # password: str
    fullname: str
