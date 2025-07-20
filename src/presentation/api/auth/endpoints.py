from fastapi import APIRouter, Depends, HTTPException, status, Response
from core.application.commands import auth as commands
from core.application.handlers import auth as handlers
from presentation.api.auth import controllers
from presentation.api.auth import schemas
from core.domain import exceptions


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
async def user_signup(
    data: schemas.UserSignupRequest,
    handler: handlers.CreateUserCommandHandler = Depends(
        controllers.user_signup_command_handler
    ),
) -> schemas.UserSignupResponse:
    command = commands.CreateUserCommand(
        email=data.email,
        fullname=data.fullname,
        password_1=data.password_1,
        password_2=data.password_2,
    )
    try:
        new_user_uuid = await handler.handle(command)
    except exceptions.EmailIsAlreadyInUse:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )
    except exceptions.PasswordsShouldMatch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords should match.",
        )
    except exceptions.PasswordIsNotSecure:  # todo: pass down the requirements
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password is not secure."
        )

    response = schemas.UserSignupResponse(
        uuid=new_user_uuid,
    )
    return response


@router.post("/login")
async def login(
    data: schemas.LoginRequest,
    response: Response,
    handler: handlers.LoginCommandHandler = Depends(controllers.login_command_handler),
) -> schemas.LoginResponse:
    command = commands.LoginCommand(email=data.email, password=data.password)

    try:
        tokens_pair = await handler.handle(command)
    except exceptions.UserWithSuchCredentialsDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with such credentials does not exist.",
        )

    response.set_cookie(
        key="refresh_token",
        value=tokens_pair.refresh_token.token,
        httponly=True,
        secure=True,
        expires=tokens_pair.refresh_token.alive_seconds,
        max_age=tokens_pair.refresh_token.alive_seconds,
    )
    return schemas.LoginResponse(access_token=tokens_pair.access_token.token)
