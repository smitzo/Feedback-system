from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .common import Record


class Revision(Record, Base):
    __tablename__ = "revisions"
    __table_args__ = (UniqueConstraint("feedback_id", "version", name="unique_feedback_revision"),)
    feedback_id: Mapped[str] = mapped_column(ForeignKey("feedback.id"), index=True)
    editor_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    version: Mapped[int] = mapped_column(Integer)
    strengths: Mapped[str] = mapped_column(Text)
    improvements: Mapped[str] = mapped_column(Text)
    sentiment: Mapped[str] = mapped_column(String(24))


class Comment(Record, Base):
    __tablename__ = "comments"
    feedback_id: Mapped[str] = mapped_column(ForeignKey("feedback.id"), index=True)
    author_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)
