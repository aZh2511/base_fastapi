from core.application.interfaces import IDBSession


class MockedDbSession(IDBSession):
    async def commit(self) -> None:
        pass

    async def flush(self) -> None:
        pass
