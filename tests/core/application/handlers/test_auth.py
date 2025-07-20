import pytest

from core.application.handlers import auth as handlers
from core.application.interfaces import IDBSession
from core.domain import exceptions
from core.domain.interfaces import IPasswordHasher
from core.domain.repositories import IUserRepository
from infrastructure.services.password_hasher import PasswordHasher
from tests.core.application.commands.auth import CreateUserCommand
from tests.core.domain.entities import User
from tests.mocks.core.application.interfaces import MockedDbSession
from tests.mocks.core.domain.repositories import MockedUserRepository


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
