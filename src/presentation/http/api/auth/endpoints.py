from typing import Annotated

from fastapi import APIRouter, Depends, Response

from core.application.commands.auth import CreateUserCommand, LoginCommand
from core.application.handlers.commands.auth import (
    CreateUserCommandHandler,
    LoginCommandHandler,
)
from core.application.handlers.queries.auth import GetMeQueryHandler
from core.application.queries.auth import GetMeQuery
from presentation.http.api.auth import providers, schemas
from presentation.http.api.dependencies import AuthenticatedUser


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
async def signup(
    data: schemas.UserSignupRequest,
    handler: Annotated[
        CreateUserCommandHandler, Depends(providers.create_user_handler)
    ],
) -> schemas.UserSignupResponse:
    command = CreateUserCommand(
        email=data.email,
        fullname=data.fullname,
        password_1=data.password_1,
        password_2=data.password_2,
    )
    new_uuid = await handler.handle(command)
    return schemas.UserSignupResponse(uuid=str(new_uuid))


@router.post("/login")
async def login(
    data: schemas.LoginRequest,
    response: Response,
    handler: Annotated[LoginCommandHandler, Depends(providers.login_handler)],
) -> schemas.LoginResponse:
    command = LoginCommand(email=data.email, password=data.password)
    tokens = await handler.handle(command)
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token.token,
        httponly=True,
        secure=True,
        max_age=tokens.refresh_token.alive_seconds,
    )
    return schemas.LoginResponse(access_token=tokens.access_token.token)


@router.get("/me")
async def get_me(
    current_user: AuthenticatedUser,
    handler: Annotated[GetMeQueryHandler, Depends(providers.get_me_handler)],
) -> schemas.GetMeResponse:
    query = GetMeQuery(user_uuid=current_user.user_uuid)
    result = await handler.handle(query)
    return schemas.GetMeResponse(
        uuid=result.uuid,
        email=result.email,
        fullname=result.fullname,
    )
