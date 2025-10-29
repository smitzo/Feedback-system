from fastapi.testclient import TestClient

from backend.app.factory import create_app
from backend.app.settings import Settings


def test_health_has_request_identifier_and_readiness_requires_migrations():
    with TestClient(
        create_app(Settings(environment="test", database_url="sqlite:///:memory:"))
    ) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.headers["X-Request-ID"]
        assert client.get("/api/v1/ready").status_code == 503


def test_application_instances_do_not_share_database_engine():
    settings = Settings(environment="test", database_url="sqlite:///:memory:")
    assert create_app(settings).state.engine is not create_app(settings).state.engine
