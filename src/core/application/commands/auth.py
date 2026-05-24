from pydantic import EmailStr

from core.application.commands.base import Command


class CreateUserCommand(Command):
    email: EmailStr
    fullname: str
    password_1: str
    password_2: str


class LoginCommand(Command):
    email: EmailStr
    password: str
