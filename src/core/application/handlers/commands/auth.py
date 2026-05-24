from core.application.commands.auth import CreateUserCommand, LoginCommand
from core.application.dto import JWTTokensPair, TokenType, UserJWTTokenDTO
from core.application.handlers.base import CommandHandler
from core.application.interfaces import IDBSession, IJWTService
from core.domain.entities import User
from core.domain.exceptions import (
    EmailIsAlreadyInUse,
    PasswordsShouldMatch,
    UserWithSuchCredentialsDoesNotExist,
)
from core.domain.interfaces import IPasswordHasher
from core.domain.repositories import IUserRepository
from core.domain.value_objects import Email, Password, UserUUID


class CreateUserCommandHandler(CommandHandler[CreateUserCommand, UserUUID]):
    def __init__(
        self,
        db_session: IDBSession,
        repository: IUserRepository,
        password_hasher: IPasswordHasher,
    ) -> None:
        self._db_session = db_session
        self._repository = repository
        self._password_hasher = password_hasher

    async def handle(self, command: CreateUserCommand) -> UserUUID:
        if command.password_1 != command.password_2:
            raise PasswordsShouldMatch()

        password = Password(command.password_1)
        email = Email(str(command.email))

        existing = await self._repository.get_user_by_email(email)
        if existing is not None:
            raise EmailIsAlreadyInUse()

        user = User(
            uuid=UserUUID(),
            fullname=command.fullname,
            email=email,
            hashed_password=self._password_hasher.hash_password(password.value),
        )

        await self._repository.add_user(user)
        await self._db_session.commit()
        return user.uuid


class LoginCommandHandler(CommandHandler[LoginCommand, JWTTokensPair]):
    def __init__(
        self,
        repository: IUserRepository,
        password_hasher: IPasswordHasher,
        jwt_service: IJWTService,
    ) -> None:
        self._repository = repository
        self._password_hasher = password_hasher
        self._jwt_service = jwt_service

    async def handle(self, command: LoginCommand) -> JWTTokensPair:
        email = Email(str(command.email))
        maybe_user = await self._repository.get_user_by_email(email)
        if maybe_user is None:
            raise UserWithSuchCredentialsDoesNotExist()

        is_correct = self._password_hasher.verify_password(
            command.password, maybe_user.hashed_password
        )
        if not is_correct:
            raise UserWithSuchCredentialsDoesNotExist()

        access_token = self._jwt_service.encode_token(
            UserJWTTokenDTO(
                user_uuid=str(maybe_user.uuid),
                token_type=TokenType.access_token,
            )
        )
        refresh_token = self._jwt_service.encode_token(
            UserJWTTokenDTO(
                user_uuid=str(maybe_user.uuid),
                token_type=TokenType.refresh_token,
            )
        )
        return JWTTokensPair(access_token=access_token, refresh_token=refresh_token)
