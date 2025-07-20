import pytest
from faker import Faker
from infrastructure.config import Config
from tests.infrastructure.config import MockedConfig


@pytest.fixture
def faker() -> Faker:
    return Faker()


@pytest.fixture
def config() -> Config:
    return MockedConfig()
