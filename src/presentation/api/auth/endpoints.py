from fastapi import APIRouter, Depends
from pydantic import EmailStr

from core.application.commands import auth as commands
from core.application.handlers import auth as handlers
from presentation.api.auth import controllers
from presentation.api.auth import schemas
from uuid import UUID


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
        fullname=data.fullname
    )
    new_user_uuid = await handler.handle(command)

    response = schemas.UserSignupResponse(
        uuid=new_user_uuid,
    )
    return response
