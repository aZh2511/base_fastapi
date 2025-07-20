from pydantic import BaseModel, Field
from os import environ as env


class PostgresConfig(BaseModel):
    database_url: str = Field(alias="DATABASE_URL")


class JWTAuthConfig(BaseModel):
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_access_token_lifetime: int = Field(
        alias="JWT_ACCESS_TOKEN_LIFETIME", default=10 * 60
    )
    jwt_refresh_token_lifetime: int = Field(
        alias="JWT_REFRESH_TOKEN_LIFETIME", default=24 * 60 * 60
    )


class Config(BaseModel):
    postgres: PostgresConfig = Field(default_factory=lambda: PostgresConfig(**env))
    jwt_auth: JWTAuthConfig = Field(default_factory=lambda: JWTAuthConfig(**env))
