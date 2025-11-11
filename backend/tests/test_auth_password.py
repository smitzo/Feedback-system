from .conftest import PASSWORD


def test_password_change_revokes_current_session(sign_in):
    client = sign_in("employee")
    assert (
        client.post(
            "/api/v1/auth/password",
            json={"current_password": PASSWORD, "new_password": "Updated workplace password 43"},
        ).status_code
        == 204
    )
    assert client.get("/api/v1/auth/me").status_code == 401
