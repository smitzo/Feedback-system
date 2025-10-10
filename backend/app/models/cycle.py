from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .common import Record


class Cycle(Record, Base):
    __tablename__ = "cycles"
    __table_args__ = (
        CheckConstraint("state IN ('draft','open','closed')", name="valid_cycle_state"),
        CheckConstraint("starts_on <= ends_on", name="valid_cycle_dates"),
    )
    name: Mapped[str] = mapped_column(String(120))
    starts_on: Mapped[str] = mapped_column(String(10))
    ends_on: Mapped[str] = mapped_column(String(10))
    state: Mapped[str] = mapped_column(String(12), default="draft")
