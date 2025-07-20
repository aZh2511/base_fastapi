import pytest

from core.application.handlers import auth as handlers
from core.application.interfaces import IDBSession
from core.domain.repositories import IUserRepository
from tests.core.application.commands.auth import CreateUserCommand
from tests.mocks.core.application.interfaces import MockedDbSession
from tests.mocks.core.domain.repositories import MockedUserRepository


@pytest.fixture
def db_session() -> IDBSession:
    return MockedDbSession()


@pytest.fixture
def repository() -> IUserRepository:
    return MockedUserRepository()


async def test_user_is_saved_and_can_be_retrieved(db_session, repository) -> None:
    handler = handlers.CreateUserCommandHandler(db_session, repository)
    command = CreateUserCommand()

    result = await handler.handle(command)

    assert result is not None
    assert await repository.check_user_exists_by_email(command.email) is True
