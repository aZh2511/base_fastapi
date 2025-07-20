from dataclasses import dataclass, field
from uuid import uuid4, UUID


class VOUUID:
    value: UUID

    def __str__(self) -> str:
        return str(self.value)

@dataclass(frozen=True)
class UserUUID(VOUUID):
    value: UUID = field(default_factory=uuid4)
