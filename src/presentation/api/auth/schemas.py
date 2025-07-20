from pydantic import BaseModel, EmailStr


class UserSignupRequest(BaseModel):
    email: EmailStr
    fullname: str
    password_1: str
    password_2: str


class UserSignupResponse(BaseModel):
    uuid: str
