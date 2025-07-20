from pydantic import BaseModel, Field
from os import environ as env


class PostgresConfig(BaseModel):
    database_url: str = Field(alias='DATABASE_URL')


class Config(BaseModel):
    postgres: PostgresConfig = Field(default_factory=lambda: PostgresConfig(**env))
