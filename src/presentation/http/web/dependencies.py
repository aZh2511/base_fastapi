from typing import Annotated

from fastapi import Cookie
from fastapi.responses import RedirectResponse

from core.application.dto import JWTToken, TokenType, UserJWTTokenDTO
from core.application.exceptions import AuthenticationFailed
from presentation.http.wiring import JWTServiceDep


_LOGIN_REDIRECT = RedirectResponse(url="/login", status_code=303)


async def get_current_user_from_cookie(
    jwt_service: JWTServiceDep,
    access_token: Annotated[str | None, Cookie()] = None,
) -> UserJWTTokenDTO:
    if not access_token:
        raise _LoginRedirect()
    try:
        dto = jwt_service.decode_token(JWTToken(access_token))
    except AuthenticationFailed as exc:
        raise _LoginRedirect() from exc
    if dto.token_type is not TokenType.access_token:
        raise _LoginRedirect()
    return dto


class _LoginRedirect(Exception):
    """Raised by the web auth dependency to redirect unauthenticated visitors to /login."""


__all__ = ["get_current_user_from_cookie"]
