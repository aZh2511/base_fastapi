from core.application.interfaces import IDBSession


class FakeDBSession(IDBSession):
    def __init__(self) -> None:
        self.commits: int = 0
        self.flushes: int = 0
        self.rollbacks: int = 0

    async def commit(self) -> None:
        self.commits += 1

    async def flush(self) -> None:
        self.flushes += 1

    async def rollback(self) -> None:
        self.rollbacks += 1
