from .base import Query, BaseResultDTO
from pydantic import EmailStr


class GetMeQuery(Query):
    user_uuid: str

    class ResultDTO(BaseResultDTO):
        uuid: str
        email: EmailStr
        fullname: str
