from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
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
