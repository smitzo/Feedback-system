from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .common import Record


class AuditEvent(Record, Base):
    __tablename__ = "audit_events"
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[str] = mapped_column(String(80), index=True)
    resource_type: Mapped[str] = mapped_column(String(32))
    resource_id: Mapped[str | None] = mapped_column(String(36), index=True)
