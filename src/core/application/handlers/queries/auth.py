from uuid import UUID

from core.application.handlers.base import QueryHandler
from core.application.queries.auth import GetMeQuery, GetMeResult
from core.domain.exceptions import SuchUserDoesNotExist
from core.domain.repositories import IUserRepository
from core.domain.value_objects import UserUUID


class GetMeQueryHandler(QueryHandler[GetMeQuery, GetMeResult]):
    def __init__(self, repository: IUserRepository) -> None:
        self._repository = repository

    async def handle(self, query: GetMeQuery) -> GetMeResult:
        user_uuid = UserUUID(UUID(query.user_uuid))
        maybe_user = await self._repository.get_user_by_uuid(user_uuid)
        if maybe_user is None:
            raise SuchUserDoesNotExist()

        return GetMeResult(
            uuid=str(maybe_user.uuid),
            email=str(maybe_user.email),
            fullname=maybe_user.fullname,
        )
