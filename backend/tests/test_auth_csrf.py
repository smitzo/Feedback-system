def test_mutations_require_session_bound_csrf_and_trusted_origin(sign_in):
    client = sign_in()
    for headers in [
        {"X-CSRF-Token": "invalid"},
        {"Origin": "https://evil.example"},
        {"Origin": ""},
    ]:
        assert client.post("/api/v1/auth/logout", headers=headers).status_code == 403
    assert client.post("/api/v1/auth/logout").status_code == 204
