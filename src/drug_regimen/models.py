from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base import Base


class Manager(Base):
    __tablename__ = "manager"

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(sa.String(128), nullable=False, unique=False)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, unique=False, default=False)
    start_date: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.now)
    finish_date: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.now)
    timezone: Mapped[str] = mapped_column(sa.String(64), nullable=False, unique=False)

    user_id: Mapped[int] = mapped_column(sa.ForeignKey("user.id"), nullable=False, unique=False)

    user = relationship("User", back_populates="managers", uselist=False)
    drugs = relationship("Drug", back_populates="manager", uselist=True)


class Drug(Base):
    __tablename__ = "drug"

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(sa.String(128), nullable=False, unique=False)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, unique=False, default=False)
    start_date: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.now)
    finish_date: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.now)

    manager_id: Mapped[int] = mapped_column(sa.ForeignKey("manager.id"), nullable=False, unique=False)

    manager = relationship("Manager", back_populates="drugs", uselist=False)
    regimens = relationship("Regimen", back_populates="drug", uselist=True)


class Regimen(Base):
    __tablename__ = "regimen"

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True, nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, unique=False, default=False)
    drug_time: Mapped[datetime] = mapped_column(sa.DateTime, unique=False, nullable=False)
    supplement: Mapped[str] = mapped_column(sa.String(128), nullable=False, unique=False)
    """После еды или до/на тощак/запить/рассосать и тп."""

    drug_id: Mapped[int] = mapped_column(sa.ForeignKey("drug.id"), nullable=False, unique=False)

    drug = relationship("Drug", back_populates="regimens", uselist=False)
