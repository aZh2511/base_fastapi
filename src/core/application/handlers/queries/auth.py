from core.application.handlers.base import QueryHandler
from core.application.queries import auth as queries
from core.domain.repositories import IUserRepository

from core.domain import exceptions


class GetMeQueryHandler(QueryHandler[queries.GetMeQuery]):
    def __init__(self, repository: IUserRepository) -> None:
        self._repository = repository

    async def handle(self, query: queries.GetMeQuery) -> queries.GetMeQuery.ResultDTO:
        maybe_user = await self._repository.get_user_by_uuid(query.user_uuid)
        if maybe_user is None:
            raise exceptions.SuchUserDoesNotExist()

        return queries.GetMeQuery.ResultDTO(
            email=maybe_user.email,
            fullname=maybe_user.fullname,
            uuid=str(maybe_user.uuid),
        )
