from pydantic import BaseModel, EmailStr


class UserSignupRequest(BaseModel):
    email: EmailStr
    fullname: str


class UserSignupResponse(BaseModel):
    uuid: str
