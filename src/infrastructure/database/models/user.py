from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.models.base import Base


class User(Base):
    __tablename__ = "users"

    fullname: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
