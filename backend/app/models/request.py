from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .common import Record


class FeedbackRequest(Record, Base):
    __tablename__ = "feedback_requests"
    __table_args__ = (
        CheckConstraint("state IN ('open','fulfilled','cancelled')", name="valid_request_state"),
    )
    employee_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    manager_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    topic: Mapped[str] = mapped_column(String(160))
    note: Mapped[str] = mapped_column(Text, default="")
    state: Mapped[str] = mapped_column(String(16), default="open")
    feedback_id: Mapped[str | None] = mapped_column(ForeignKey("feedback.id"))
