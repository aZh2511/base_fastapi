import pytest

from core.application.interfaces import IDBSession, IJWTService
from core.domain.interfaces import IPasswordHasher
from core.domain.repositories import IUserRepository
from infrastructure.services.jwt_tokens import JWTService
from infrastructure.services.password_hasher import PasswordHasher
from tests.mocks.core.application.interfaces import MockedDbSession
from tests.mocks.core.domain.repositories import MockedUserRepository


@pytest.fixture
def db_session() -> IDBSession:
    return MockedDbSession()


@pytest.fixture
def user_repository() -> IUserRepository:
    return MockedUserRepository()


@pytest.fixture
def password_hasher() -> IPasswordHasher:
    return PasswordHasher()


@pytest.fixture
def jwt_service(config) -> IJWTService:
    return JWTService(config.jwt_auth)
