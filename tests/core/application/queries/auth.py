from factory import Factory, LazyAttribute

from core.application.queries import auth as queries
from core.domain import value_objects as vo


class GetMeQuery(Factory):
    user_uuid: str = LazyAttribute(lambda _: str(vo.UserUUID()))

    class Meta:
        model = queries.GetMeQuery
