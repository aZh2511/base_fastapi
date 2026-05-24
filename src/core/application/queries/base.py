from pydantic import BaseModel, ConfigDict


class BaseResultDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Query(BaseModel):
    pass
