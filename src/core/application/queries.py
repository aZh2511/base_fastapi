from pydantic import BaseModel


class BaseResultDTO(BaseModel):
    class Config:
        from_attributes = True


class Query(BaseModel):
    class ResultDTO(BaseResultDTO):
        pass
