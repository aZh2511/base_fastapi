from .base import Command
from pydantic import EmailStr


class CreateUserCommand(Command):
    email: EmailStr
    password_1: str
    password_2: str
    fullname: str
