from typing import Protocol


class IDBSession(Protocol):
    async def commit(self) -> None:
        ...

    async def flush(self) -> None:
        ...
