import pytest

from core.application.handlers import auth as handlers
from core.domain import exceptions
from tests.core.application.queries.auth import GetMeQuery
from tests.core.domain.entities import User


@pytest.fixture()
def get_me_query_handler(user_repository) -> handlers.GetMeQueryHandler:
    return handlers.GetMeQueryHandler(user_repository)


async def test_get_me__exception_is_raised_when_no_user(get_me_query_handler) -> None:
    query = GetMeQuery()

    with pytest.raises(exceptions.SuchUserDoesNotExist):
        await get_me_query_handler.handle(query)


async def test_get_me__returns_the_user(
    get_me_query_handler, user_repository, db_session
) -> None:
    existing_user = User()
    await user_repository.add_user(existing_user)
    await db_session.commit()
    query = GetMeQuery(user_uuid=str(existing_user.uuid))

    result = await get_me_query_handler.handle(query)

    assert result.email == existing_user.email
    assert result.fullname == existing_user.fullname
