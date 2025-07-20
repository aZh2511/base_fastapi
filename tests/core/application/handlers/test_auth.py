import pytest

from core.application.handlers import auth as handlers
from core.application.interfaces import IDBSession, IJWTService
from core.domain import exceptions
from core.domain.interfaces import IPasswordHasher
from core.domain.repositories import IUserRepository
from infrastructure.services.password_hasher import PasswordHasher
from infrastructure.services.jwt_tokens import JWTService
from tests.core.application.commands.auth import CreateUserCommand, LoginCommand
from tests.core.domain.entities import User
from tests.mocks.core.application.interfaces import MockedDbSession
from tests.mocks.core.domain.repositories import MockedUserRepository
from datetime import datetime


@pytest.fixture
def db_session() -> IDBSession:
    return MockedDbSession()


@pytest.fixture
def repository() -> IUserRepository:
    return MockedUserRepository()


@pytest.fixture
def password_hasher() -> IPasswordHasher:
    return PasswordHasher()


@pytest.fixture()
def create_user_command_handler(
    db_session, repository, password_hasher
) -> handlers.CreateUserCommandHandler:
    return handlers.CreateUserCommandHandler(db_session, repository, password_hasher)


@pytest.fixture
def jwt_service(config) -> IJWTService:
    return JWTService(config.jwt_auth)


@pytest.fixture
def login_command_handler(
    repository, password_hasher, jwt_service
) -> handlers.LoginCommandHandler:
    return handlers.LoginCommandHandler(repository, password_hasher, jwt_service)


async def test_create_user__user_is_saved_and_can_be_retrieved(
    create_user_command_handler, repository
) -> None:
    command = CreateUserCommand()

    result = await create_user_command_handler.handle(command)

    assert result is not None
    assert await repository.check_user_exists_by_email(command.email) is True


async def test_create_user__email_must_be_unique(
    create_user_command_handler, repository, db_session
) -> None:
    existing_user = User()
    await repository.add_user(existing_user)
    await db_session.commit()

    command = CreateUserCommand(email=existing_user.email)

    with pytest.raises(exceptions.EmailIsAlreadyInUse):
        await create_user_command_handler.handle(command)


async def test_create_user__mismatching_passwords_raise_exception(
    create_user_command_handler,
) -> None:
    command = CreateUserCommand(mismatching_passwords=True)
    with pytest.raises(exceptions.PasswordsShouldMatch):
        await create_user_command_handler.handle(command)


async def test_create_user__validates_password_requirements(
    create_user_command_handler,
) -> None:
    command = CreateUserCommand(insecure_password=True)
    with pytest.raises(exceptions.PasswordIsNotSecure):
        await create_user_command_handler.handle(command)


async def test_login__if_wrong_password_exception_is_raised(
    login_command_handler, repository, db_session, password_hasher
) -> None:
    correct_password = "adfgyuio!2N"
    hashed_password = password_hasher.hash_password(correct_password)
    existing_user = User(hashed_password=hashed_password)
    await repository.add_user(existing_user)
    await db_session.commit()

    command = LoginCommand(
        email=existing_user.email, password=correct_password + "different_password"
    )
    with pytest.raises(exceptions.UserWithSuchCredentialsDoesNotExist):
        await login_command_handler.handle(command)


async def test_login__if_user_does_not_exist_exception_is_raised(
    faker, login_command_handler
) -> None:
    command = LoginCommand()

    with pytest.raises(exceptions.UserWithSuchCredentialsDoesNotExist):
        await login_command_handler.handle(command)


async def test_login__happy_path(
    login_command_handler, repository, db_session, password_hasher
) -> None:
    correct_password = "adfgyuio!2N"
    hashed_password = password_hasher.hash_password(correct_password)
    existing_user = User(hashed_password=hashed_password)
    await repository.add_user(existing_user)
    await db_session.commit()

    command = LoginCommand(email=existing_user.email, password=correct_password)
    result = await login_command_handler.handle(command)

    assert result.access_token.expires_at.timestamp() > datetime.now().timestamp()
    assert result.refresh_token.expires_at.timestamp() > datetime.now().timestamp()
