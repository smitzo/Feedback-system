from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .common import Record


class Grant(Record, Base):
    __tablename__ = "grants"
    __table_args__ = (UniqueConstraint("user_id", "permission", name="unique_user_grant"),)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    permission: Mapped[str] = mapped_column(String(64))
