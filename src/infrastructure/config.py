from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


_REPO_ROOT = Path(__file__).resolve().parents[2]


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(alias="DATABASE_URL")
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_access_token_lifetime_seconds: int = Field(
        default=10 * 60, alias="JWT_ACCESS_TOKEN_LIFETIME"
    )
    jwt_refresh_token_lifetime_seconds: int = Field(
        default=24 * 60 * 60, alias="JWT_REFRESH_TOKEN_LIFETIME"
    )
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    frontend_origins: list[str] = Field(default_factory=list, alias="FRONTEND_ORIGINS")

    @field_validator("frontend_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value
