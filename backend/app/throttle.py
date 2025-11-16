import time

from fastapi import HTTPException
from sqlalchemy import delete, func, select

from .dependencies import digest
from .models import LoginAttempt


def login_keys(request, email):
    ip = request.client.host if request.client else "unknown"
    return [digest("email:" + email.lower()), digest("ip:" + ip)]


def check_login(request, db, email):
    settings = request.app.state.settings
    cutoff = int(time.time()) - settings.login_window_seconds
    db.execute(delete(LoginAttempt).where(LoginAttempt.attempted_at < cutoff))
    for key, limit in zip(
        login_keys(request, email),
        [settings.login_attempts, settings.login_attempts * 3],
        strict=True,
    ):
        count = db.scalar(
            select(func.count()).select_from(LoginAttempt).where(LoginAttempt.key == key)
        )
        if count >= limit:
            raise HTTPException(
                429,
                "Too many sign-in attempts. Try again later",
                headers={"Retry-After": str(settings.login_window_seconds)},
            )


def failed_login(request, db, email):
    for key in login_keys(request, email):
        db.add(LoginAttempt(key=key, attempted_at=int(time.time())))
    # Persist failed attempts even though the enclosing HTTP operation is rejected.
    db.commit()
