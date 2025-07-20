from pydantic import BaseModel


class PostgresConfig(BaseModel):
    database_url: str = "some-url"


class JWTAuthConfig(BaseModel):
    jwt_secret_key: str = "secret-key"
    jwt_access_token_lifetime: int = 10 * 60
    jwt_refresh_token_lifetime: int = 24 * 60 * 60


class MockedConfig(BaseModel):
    postgres: PostgresConfig = PostgresConfig()
    jwt_auth: JWTAuthConfig = JWTAuthConfig()
