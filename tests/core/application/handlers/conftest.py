import pytest

from core.application.interfaces import IDBSession, IJWTService
from core.domain.interfaces import IPasswordHasher
from core.domain.repositories import IUserRepository
from infrastructure.config import Config
from infrastructure.services.jwt_tokens import JWTService
from tests.mocks.core.application.interfaces import FakeDBSession
from tests.mocks.core.domain.interfaces import FakePasswordHasher
from tests.mocks.core.domain.repositories import FakeUserRepository


@pytest.fixture
def db_session() -> IDBSession:
    return FakeDBSession()


@pytest.fixture
def user_repository() -> IUserRepository:
    return FakeUserRepository()


@pytest.fixture
def password_hasher() -> IPasswordHasher:
    return FakePasswordHasher()


@pytest.fixture
def jwt_service(config: Config) -> IJWTService:
    return JWTService(config)
