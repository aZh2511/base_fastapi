from pydantic import EmailStr

from core.application.queries.base import BaseResultDTO, Query


class GetMeQuery(Query):
    user_uuid: str


class GetMeResult(BaseResultDTO):
    uuid: str
    email: EmailStr
    fullname: str
