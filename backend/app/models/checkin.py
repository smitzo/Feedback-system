from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .common import Record


class CheckIn(Record, Base):
    __tablename__ = "checkins"
    __table_args__ = (
        UniqueConstraint("employee_id", "week_of", name="unique_employee_week"),
        CheckConstraint("mood IN ('great','okay','struggling')", name="valid_checkin_mood"),
        CheckConstraint("workload IN ('light','balanced','heavy')", name="valid_checkin_workload"),
    )
    employee_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    week_of: Mapped[str] = mapped_column(String(10))
    mood: Mapped[str] = mapped_column(String(16))
    workload: Mapped[str] = mapped_column(String(16))
    note: Mapped[str] = mapped_column(Text, default="")
    response: Mapped[str | None] = mapped_column(Text)
    responder_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
