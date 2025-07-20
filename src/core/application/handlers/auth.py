from core.application.commands import auth
from core.application.dto import JWTTokensPair, TokenType
from core.application.interfaces import IDBSession
from core.application.interfaces import IJWTService, UserJWTTokenDTO
from core.domain import entities
from core.domain import exceptions
from core.domain import value_objects as vo
from core.domain.interfaces import IPasswordHasher
from core.domain.repositories import IUserRepository
from .base import CommandHandler


class CreateUserCommandHandler(CommandHandler[auth.CreateUserCommand]):
    def __init__(
        self,
        db_session: IDBSession,
        repository: IUserRepository,
        password_hasher: IPasswordHasher,
    ) -> None:
        self._db_session = db_session
        self._repository = repository
        self._password_hasher = password_hasher

    async def handle(self, command: auth.CreateUserCommand) -> str:
        if command.password_1 != command.password_2:
            raise exceptions.PasswordsShouldMatch()

        password = vo.Password(command.password_1)

        is_there_such_user = await self._repository.check_user_exists_by_email(
            email=str(command.email)
        )
        if is_there_such_user:
            raise exceptions.EmailIsAlreadyInUse()

        uuid = vo.UserUUID()

        hashed_password = self._password_hasher.hash_password(password.value)
        user = entities.User(
            email=command.email,
            fullname=command.fullname,
            uuid=uuid,
            hashed_password=hashed_password,
        )

        await self._repository.add_user(user)
        await self._db_session.commit()
        return str(uuid)


class LoginCommandHandler(CommandHandler[auth.LoginCommand]):
    def __init__(
        self,
        # db_session: IDBSession,
        repository: IUserRepository,
        password_hasher: IPasswordHasher,
        jwt_service: IJWTService,
    ) -> None:
        # self._db_session = db_session
        self._repository = repository
        self._password_hasher = password_hasher
        self._jwt_service = jwt_service

    async def handle(self, command: auth.LoginCommand) -> JWTTokensPair:
        maybe_user = await self._repository.get_user_by_email(command.email)
        if not maybe_user:
            raise exceptions.UserWithSuchCredentialsDoesNotExist()

        is_password_correct = self._password_hasher.verify_password(
            command.password, maybe_user.hashed_password
        )
        if not is_password_correct:
            raise exceptions.UserWithSuchCredentialsDoesNotExist()

        jwt_access_token_dto = UserJWTTokenDTO(
            user_uuid=str(maybe_user.uuid),
            token_type=TokenType.access_token,
        )
        access_token = self._jwt_service.encode_token(jwt_access_token_dto)

        jwt_refresh_token_dto = UserJWTTokenDTO(
            user_uuid=str(maybe_user.uuid),
            token_type=TokenType.refresh_token,
        )
        refresh_token = self._jwt_service.encode_token(jwt_refresh_token_dto)

        return JWTTokensPair(access_token, refresh_token)
