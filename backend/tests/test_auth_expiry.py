import time

from sqlalchemy import update

from backend.app.models import LoginSession


def test_expired_and_forged_cookies_are_rejected(sign_in, app):
    client = sign_in()
    with app.state.sessions.begin() as db:
        db.execute(update(LoginSession).values(expires_at=int(time.time()) - 1))
    assert client.get("/api/v1/auth/me").status_code == 401
    client.cookies.clear()
    client.cookies.set("feedback_session", "forged")
    assert client.get("/api/v1/auth/me").status_code == 401
