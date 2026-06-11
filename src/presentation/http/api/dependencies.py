from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from core.application.dto import JWTToken, TokenType, UserJWTTokenDTO
from core.application.exceptions import AuthenticationFailed
from presentation.http.wiring import JWTServiceDep


_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user_jwt(
    jwt_service: JWTServiceDep,
    token: Annotated[str, Depends(_oauth2_scheme)],
) -> UserJWTTokenDTO:
    dto = jwt_service.decode_token(JWTToken(token))
    if dto.token_type is not TokenType.access_token:
        raise AuthenticationFailed("Access token required")
    return dto


AuthenticatedUser = Annotated[UserJWTTokenDTO, Depends(get_current_user_jwt)]
