import secrets
import time

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..dependencies import (
    CSRF_COOKIE,
    SESSION_COOKIE,
    capabilities,
    current_user,
    digest,
    get_db,
    public_user,
)
from ..errors import fail
from ..models import LoginSession, User
from ..passwords import hash_password, verify_password
from ..schemas import Login, PasswordChange

router = APIRouter(prefix="/auth", tags=["Authentication"])
DUMMY_HASH = hash_password("Unused timing equalizer 42")


def start_session(request, response, db, user):
    token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    settings = request.app.state.settings
    db.add(
        LoginSession(
            user_id=user.id,
            token_hash=digest(token),
            csrf_hash=digest(csrf),
            expires_at=int(time.time()) + settings.session_seconds,
        )
    )
    options = dict(
        secure=settings.secure_cookies, samesite="lax", path="/", max_age=settings.session_seconds
    )
    response.set_cookie(SESSION_COOKIE, token, httponly=True, **options)
    response.set_cookie(CSRF_COOKIE, csrf, httponly=False, **options)


@router.post("/login")
def login(data: Login, request: Request, response: Response, db: Session = Depends(get_db)):
    if request.headers.get("origin") not in request.app.state.settings.allowed_origins:
        fail(403, "Sign in from the workspace")
    user = db.scalar(select(User).where(User.email == data.email))
    valid = verify_password(data.password, user.password_hash if user else DUMMY_HASH)
    if not user or not valid or not user.active:
        fail(401, "Email or password is incorrect")
    start_session(request, response, db, user)
    return {"user": public_user(user), "capabilities": capabilities(user)}


@router.get("/me")
def me(actor: User = Depends(current_user)):
    return {"user": public_user(actor), "capabilities": capabilities(actor)}


@router.post("/logout", status_code=204)
def logout(
    request: Request,
    response: Response,
    actor: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    db.delete(request.state.login_session)
    response.delete_cookie(SESSION_COOKIE, path="/")
    response.delete_cookie(CSRF_COOKIE, path="/")
