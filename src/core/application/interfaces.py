from typing import Protocol

from core.application.dto import JWTToken, JWTTokenDTO, UserJWTTokenDTO


class IDBSession(Protocol):
    async def commit(self) -> None: ...

    async def flush(self) -> None: ...

    async def rollback(self) -> None: ...


class IJWTService(Protocol):
    def encode_token(self, data: UserJWTTokenDTO) -> JWTTokenDTO: ...

    def decode_token(self, token: JWTToken) -> UserJWTTokenDTO: ...
