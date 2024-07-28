from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base import Base
from src.drug_regimen.models import Manager  # noqa: F401


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True, nullable=False, unique=True)
    username: Mapped[str] = mapped_column(sa.String(64), nullable=False, unique=False)
    tg_user_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(sa.String(64), nullable=True, unique=False)
    last_name: Mapped[str] = mapped_column(sa.String(64), nullable=True, unique=False)
    registered_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.now)

    managers = relationship("Manager", back_populates="user", uselist=True)
