from typing import Annotated

from fastapi import Depends

from core.application.handlers.commands.auth import (
    CreateUserCommandHandler,
    LoginCommandHandler,
)
from core.application.handlers.queries.auth import GetMeQueryHandler
from core.domain.interfaces import IPasswordHasher
from core.domain.repositories import IUserRepository
from infrastructure.database.repositories import SQLUserRepository
from infrastructure.services.password_hasher import PasswordHasher
from presentation.http.wiring import JWTServiceDep, SessionDep


def get_user_repository(session: SessionDep) -> IUserRepository:
    return SQLUserRepository(session)


def get_password_hasher() -> IPasswordHasher:
    return PasswordHasher()


def create_user_handler(
    session: SessionDep,
    repository: Annotated[IUserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[IPasswordHasher, Depends(get_password_hasher)],
) -> CreateUserCommandHandler:
    return CreateUserCommandHandler(
        db_session=session,
        repository=repository,
        password_hasher=password_hasher,
    )


def login_handler(
    repository: Annotated[IUserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[IPasswordHasher, Depends(get_password_hasher)],
    jwt_service: JWTServiceDep,
) -> LoginCommandHandler:
    return LoginCommandHandler(
        repository=repository,
        password_hasher=password_hasher,
        jwt_service=jwt_service,
    )


def get_me_handler(
    repository: Annotated[IUserRepository, Depends(get_user_repository)],
) -> GetMeQueryHandler:
    return GetMeQueryHandler(repository=repository)
