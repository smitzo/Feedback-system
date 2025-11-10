def test_logout_revokes_server_session(sign_in):
    client = sign_in()
    token = client.cookies.get("feedback_session")
    assert client.post("/api/v1/auth/logout").status_code == 204
    client.cookies.set("feedback_session", token)
    assert client.get("/api/v1/auth/me").status_code == 401
