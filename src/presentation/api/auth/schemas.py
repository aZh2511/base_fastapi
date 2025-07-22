from pydantic import BaseModel, EmailStr


class UserSignupRequest(BaseModel):
    email: EmailStr
    fullname: str
    password_1: str
    password_2: str


class UserSignupResponse(BaseModel):
    uuid: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str


class GetMeResponse(BaseModel):
    uuid: str
    email: EmailStr
    fullname: str
