from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .common import Record


class Goal(Record, Base):
    __tablename__ = "goals"
    __table_args__ = (
        CheckConstraint("progress BETWEEN 0 AND 100", name="valid_goal_progress"),
        CheckConstraint("state IN ('active','completed','cancelled')", name="valid_goal_state"),
    )
    employee_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    creator_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")
    due_on: Mapped[str | None] = mapped_column(String(10))
    progress: Mapped[int] = mapped_column(Integer, default=0)
    state: Mapped[str] = mapped_column(String(16), default="active")
    version: Mapped[int] = mapped_column(Integer, default=1)
