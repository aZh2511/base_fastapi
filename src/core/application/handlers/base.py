from typing import Generic, TypeVar, Any

from core.application import commands, queries


CommandType = TypeVar("CommandType", bound=commands.Command)
QueryType = TypeVar("QueryType", bound=queries.Query)


class CommandHandler(Generic[CommandType]):
    async def handle(self, command: CommandType) -> Any:
        raise NotImplementedError


class QueryHandler(Generic[QueryType]):
    async def handle(self, query: QueryType) -> QueryType:
        raise NotImplementedError
