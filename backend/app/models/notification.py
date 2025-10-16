from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .common import Record


class Notification(Record, Base):
    __tablename__ = "notifications"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    kind: Mapped[str] = mapped_column(String(40))
    message: Mapped[str] = mapped_column(String(200))
    resource_id: Mapped[str | None] = mapped_column(String(36))
    read_at: Mapped[str | None] = mapped_column(String(40))
