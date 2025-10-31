import hashlib
import hmac
import time

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import transaction
from .errors import fail
from .models import LoginSession, User
from .policy import Permission, has_permission

SESSION_COOKIE = "feedback_session"
CSRF_COOKIE = "feedback_csrf"


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def get_db(request: Request):
    yield from transaction(request.app.state.sessions)


def current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(SESSION_COOKIE, "")
    if not token or len(token) > 256:
        fail(401, "Sign in to continue")
    login_session = db.scalar(select(LoginSession).where(LoginSession.token_hash == digest(token)))
    if login_session is None or login_session.expires_at <= int(time.time()):
        fail(401, "Your session has expired. Sign in again")
    user = db.get(User, login_session.user_id)
    if not user or not user.active:
        fail(401, "This account is not available")
    request.state.login_session = login_session
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        origin = request.headers.get("origin", "")
        csrf = request.headers.get("x-csrf-token", "")
        if (
            origin not in request.app.state.settings.allowed_origins
            or not csrf
            or not hmac.compare_digest(digest(csrf), login_session.csrf_hash)
        ):
            fail(403, "Refresh this page before submitting again")
    return user


def require(actor: User, permission: Permission):
    if not has_permission(actor, permission):
        fail(403, "You do not have permission for this action")


def public_user(user: User) -> dict:
    return {
        key: getattr(user, key)
        for key in ("id", "name", "email", "role", "department", "title", "manager_id", "active")
    }


def capabilities(user: User) -> dict:
    return {
        "team": user.role == "manager",
        "organization": has_permission(user, Permission.ORGANIZATION_READ),
        "people_manage": has_permission(user, Permission.PEOPLE_MANAGE),
        "grants_manage": user.role == "admin",
        "cycles_manage": has_permission(user, Permission.CYCLES_MANAGE),
        "audit_read": has_permission(user, Permission.AUDIT_READ),
        "feedback_export": has_permission(user, Permission.FEEDBACK_EXPORT),
    }
