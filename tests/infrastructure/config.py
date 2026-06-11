from pydantic import Field
from pydantic_settings import SettingsConfigDict

from infrastructure.config import Config


class FakeConfig(Config):
    """Test-only Config that supplies defaults for required fields and skips `.env`."""

    model_config = SettingsConfigDict(extra="ignore")

    database_url: str = Field(
        default="postgresql+asyncpg://test:test@localhost:5432/test",
        alias="DATABASE_URL",
    )
    jwt_secret_key: str = Field(default="test-secret-key", alias="JWT_SECRET_KEY")
