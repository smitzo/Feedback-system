import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from backend.app.factory import create_app
from backend.app.models import User
from backend.app.passwords import hash_password
from backend.app.settings import Settings

PASSWORD = "Workplace test password 42"
ORIGIN = "http://localhost:5173"


@pytest.fixture
def app(tmp_path):
    url = f"sqlite:///{tmp_path / 'test.db'}"
    cfg = Config("alembic.ini")
    cfg.attributes["database_url"] = url
    command.upgrade(cfg, "head")
    application = create_app(Settings(environment="test", database_url=url, login_attempts=3))
    with application.state.sessions.begin() as db:
        hashed = hash_password(PASSWORD)
        for id, role, manager in [
            ("admin", "admin", None),
            ("senior", "senior_management", None),
            ("manager", "manager", None),
            ("other", "manager", None),
            ("employee", "employee", "manager"),
            ("peer", "employee", "manager"),
            ("third", "employee", "manager"),
            ("outsider", "employee", "other"),
        ]:
            db.add(
                User(
                    id=id,
                    name=id.title(),
                    email=f"{id}@example.com",
                    password_hash=hashed,
                    role=role,
                    manager_id=manager,
                    department="Engineering" if manager == "manager" else "Operations",
                )
            )
            db.flush()
    yield application
    application.state.engine.dispose()


@pytest.fixture
def client(app):
    with TestClient(app) as value:
        yield value


@pytest.fixture
def sign_in(client):
    def login(id="manager"):
        client.cookies.clear()
        response = client.post(
            "/api/v1/auth/login",
            json={"email": f"{id}@example.com", "password": PASSWORD},
            headers={"Origin": ORIGIN},
        )
        assert response.status_code == 200, response.text
        client.headers.update(
            {"Origin": ORIGIN, "X-CSRF-Token": client.cookies.get("feedback_csrf")}
        )
        return client

    return login
