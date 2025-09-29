from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .common import Record, now


class Feedback(Record, Base):
    __tablename__ = "feedback"
    __table_args__ = (
        CheckConstraint("state IN ('draft','published','archived')", name="valid_feedback_state"),
        CheckConstraint(
            "sentiment IN ('positive','balanced','needs_attention')", name="valid_sentiment"
        ),
    )
    employee_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    author_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    cycle_id: Mapped[str | None] = mapped_column(ForeignKey("cycles.id"), index=True)
    strengths: Mapped[str] = mapped_column(Text)
    improvements: Mapped[str] = mapped_column(Text)
    sentiment: Mapped[str] = mapped_column(String(24))
    state: Mapped[str] = mapped_column(String(16), default="draft", index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[str] = mapped_column(String(40), default=now)
    published_at: Mapped[str | None] = mapped_column(String(40))
    acknowledged_at: Mapped[str | None] = mapped_column(String(40))
    acknowledged_version: Mapped[int | None] = mapped_column(Integer)
    escalated: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    escalation_note: Mapped[str | None] = mapped_column(Text)
    resolution_note: Mapped[str | None] = mapped_column(Text)
    resolved_at: Mapped[str | None] = mapped_column(String(40))
