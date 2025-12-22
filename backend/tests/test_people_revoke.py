from fastapi.testclient import TestClient

from .conftest import ORIGIN, PASSWORD


def test_role_changes_and_grants_revoke_other_sessions(sign_in, app):
    with TestClient(app) as employee:
        employee.post(
            "/api/v1/auth/login",
            json={"email": "employee@example.com", "password": PASSWORD},
            headers={"Origin": ORIGIN},
        )
        client = sign_in("admin")
        assert client.patch("/api/v1/people/employee", json={"role": "manager"}).status_code == 200
        assert employee.get("/api/v1/auth/me").status_code == 401
