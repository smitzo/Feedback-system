def test_only_administrators_manage_explicit_grants(sign_in):
    assert (
        sign_in("manager")
        .post("/api/v1/people/employee/grants", json={"permission": "people.manage"})
        .status_code
        == 403
    )
    client = sign_in("admin")
    assert (
        client.post(
            "/api/v1/people/employee/grants", json={"permission": "dashboard.organization"}
        ).status_code
        == 204
    )
    assert (
        client.post("/api/v1/people/employee/grants", json={"permission": "unknown"}).status_code
        == 422
    )
    assert client.get("/api/v1/people/employee/grants").json()["items"] == [
        "dashboard.organization"
    ]
    assert sign_in("employee").get("/api/v1/auth/me").json()["capabilities"]["organization"]
