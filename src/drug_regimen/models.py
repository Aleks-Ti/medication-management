from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base import Base


class Management(Base):
    __tablename__ = "management"

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True, nullable=False, unique=True)
    username: Mapped[str] = mapped_column(sa.String(64), nullable=False, unique=False)
    tg_user_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(sa.String(64), nullable=True, unique=False)
    last_name: Mapped[str] = mapped_column(sa.String(64), nullable=True, unique=False)
    registered_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.now)

    # management = relationship("Management", back_populates="user", uselist=False)
