from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .common import Record

if TYPE_CHECKING:
    from .grant import Grant


class User(Record, Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('employee','manager','senior_management','admin')", name="valid_role"
        ),
    )
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    role: Mapped[str] = mapped_column(String(30), default="employee", index=True)
    department: Mapped[str] = mapped_column(String(80), default="General")
    title: Mapped[str] = mapped_column(String(120), default="")
    manager_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    grants: Mapped[list["Grant"]] = relationship(
        "Grant", cascade="all, delete-orphan", lazy="selectin"
    )
