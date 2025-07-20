from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import Column, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    uuid: Mapped[str] = mapped_column(
        "uuid",
        sa.Uuid,
        primary_key=True,
    )
    created_at: Mapped[datetime] = Column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
