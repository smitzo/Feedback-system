from .conftest import ORIGIN, PASSWORD


def test_login_requires_no_public_signup_and_returns_no_secrets(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": PASSWORD},
        headers={"Origin": ORIGIN},
    )
    assert response.status_code == 200
    assert "hash" not in response.text and "password" not in response.text
    assert "HttpOnly" in response.headers.get_list("set-cookie")[0]
    assert client.post("/auth/register", json={"role": "admin"}).status_code == 404


def test_bad_and_missing_users_have_same_error(client):
    outputs = [
        client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "wrong"},
            headers={"Origin": ORIGIN},
        )
        for email in ["missing@example.com", "employee@example.com"]
    ]
    assert all(response.status_code == 401 for response in outputs)
    assert outputs[0].json()["error"]["message"] == outputs[1].json()["error"]["message"]
