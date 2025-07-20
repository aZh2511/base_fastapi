from core.application.commands import auth
from core.application.interfaces import IDBSession
from core.domain import entities
from core.domain import value_objects as vo
from core.domain.repositories import IUserRepository
from .base import CommandHandler
from core.domain import exceptions


class CreateUserCommandHandler(CommandHandler[auth.CreateUserCommand]):
    def __init__(
        self,
        db_session: IDBSession,
        repository: IUserRepository,
    ) -> None:
        self._db_session = db_session
        self._repository = repository

    async def handle(self, command: auth.CreateUserCommand) -> str:
        is_there_such_user = await self._repository.check_user_exists_by_email(
            email=str(command.email)
        )
        if is_there_such_user:
            raise exceptions.EmailIsAlreadyInUse()

        uuid = vo.UserUUID()
        user = entities.User(
            email=command.email,
            fullname=command.fullname,
            uuid=uuid,
        )

        await self._repository.add_user(user)
        await self._db_session.commit()
        return str(uuid)
