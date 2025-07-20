from fastapi import APIRouter, Depends, HTTPException, status
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

    response = schemas.UserSignupResponse(
        uuid=new_user_uuid,
    )
    return response
