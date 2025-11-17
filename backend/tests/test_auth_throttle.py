from .conftest import ORIGIN, PASSWORD


def test_failed_logins_survive_request_rollback_and_throttle(client):
    for _ in range(3):
        assert (
            client.post(
                "/api/v1/auth/login",
                json={"email": "employee@example.com", "password": "wrong"},
                headers={"Origin": ORIGIN},
            ).status_code
            == 401
        )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "employee@example.com", "password": PASSWORD},
        headers={"Origin": ORIGIN},
    )
    assert response.status_code == 429
    assert int(response.headers["Retry-After"]) > 0
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"email": "peer@example.com", "password": PASSWORD},
            headers={"Origin": ORIGIN},
        ).status_code
        == 200
    )
