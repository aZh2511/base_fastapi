from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from core.application.exceptions import ApplicationException, AuthenticationFailed
from core.domain.exceptions import (
    DomainException,
    EmailIsAlreadyInUse,
    InvalidEmailFormat,
    PasswordIsNotSecure,
    PasswordsShouldMatch,
    SuchUserDoesNotExist,
    UserWithSuchCredentialsDoesNotExist,
)


_EXCEPTION_STATUS_MAP: dict[type[Exception], int] = {
    InvalidEmailFormat: status.HTTP_400_BAD_REQUEST,
    PasswordIsNotSecure: status.HTTP_400_BAD_REQUEST,
    PasswordsShouldMatch: status.HTTP_400_BAD_REQUEST,
    EmailIsAlreadyInUse: status.HTTP_400_BAD_REQUEST,
    UserWithSuchCredentialsDoesNotExist: status.HTTP_400_BAD_REQUEST,
    SuchUserDoesNotExist: status.HTTP_404_NOT_FOUND,
    AuthenticationFailed: status.HTTP_401_UNAUTHORIZED,
}


def _lookup_status(exc_type: type[Exception]) -> int:
    for klass in exc_type.mro():
        if klass in _EXCEPTION_STATUS_MAP:
            return _EXCEPTION_STATUS_MAP[klass]
    return status.HTTP_500_INTERNAL_SERVER_ERROR


async def _domain_exception_handler(
    request: Request, exc: DomainException
) -> JSONResponse:
    return JSONResponse(
        status_code=_lookup_status(type(exc)),
        content={"detail": str(exc) or exc.__class__.__name__},
    )


async def _application_exception_handler(
    request: Request, exc: ApplicationException
) -> JSONResponse:
    return JSONResponse(
        status_code=_lookup_status(type(exc)),
        content={"detail": str(exc) or exc.__class__.__name__},
    )


def register(app: FastAPI) -> None:
    app.add_exception_handler(DomainException, _domain_exception_handler)
    app.add_exception_handler(ApplicationException, _application_exception_handler)
