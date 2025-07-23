from fastapi import APIRouter, Depends, HTTPException, status, Response
from core.application.commands import auth as commands
from core.application.handlers.queries import auth as query_handlers
from core.application.handlers.commands import auth as cmd_handlers
from core.application.queries import auth as queries
from presentation.api.auth import controllers
from presentation.api.auth import schemas
from core.domain import exceptions
from presentation.api.dependencies import CurrentUserJWTData


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
async def user_signup(
    data: schemas.UserSignupRequest,
    handler: cmd_handlers.CreateUserCommandHandler = Depends(
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
    handler: cmd_handlers.LoginCommandHandler = Depends(
        controllers.login_command_handler
    ),
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


@router.get("/me")
async def get_me(
    current_user: CurrentUserJWTData,
    handler: query_handlers.GetMeQueryHandler = Depends(
        controllers.get_me_query_handler
    ),
) -> schemas.GetMeResponse:
    query = queries.GetMeQuery(user_uuid=current_user.user_uuid)
    user_dto = await handler.handle(query)

    return schemas.GetMeResponse(
        email=user_dto.email,
        fullname=user_dto.fullname,
        uuid=user_dto.uuid,
    )
