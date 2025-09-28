from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .common import Record


class LoginSession(Record, Base):
    __tablename__ = "sessions"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    csrf_hash: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[int] = mapped_column(Integer, index=True)


class LoginAttempt(Record, Base):
    __tablename__ = "login_attempts"
    key: Mapped[str] = mapped_column(String(64), index=True)
    attempted_at: Mapped[int] = mapped_column(Integer, index=True)
