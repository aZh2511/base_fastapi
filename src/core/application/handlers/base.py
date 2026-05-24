from typing import Generic, TypeVar

from core.application.commands.base import Command
from core.application.queries.base import BaseResultDTO, Query


CmdT = TypeVar("CmdT", bound=Command)
CmdResultT = TypeVar("CmdResultT")
QueryT = TypeVar("QueryT", bound=Query)
QueryResultT = TypeVar("QueryResultT", bound=BaseResultDTO)


class CommandHandler(Generic[CmdT, CmdResultT]):
    async def handle(self, command: CmdT) -> CmdResultT:
        raise NotImplementedError


class QueryHandler(Generic[QueryT, QueryResultT]):
    async def handle(self, query: QueryT) -> QueryResultT:
        raise NotImplementedError
