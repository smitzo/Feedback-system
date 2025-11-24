from backend.app.models import User


def test_disabled_account_cannot_reuse_existing_session(sign_in, app):
    client = sign_in("employee")
    with app.state.sessions.begin() as db:
        db.get(User, "employee").active = False
    assert client.get("/api/v1/auth/me").status_code == 401
