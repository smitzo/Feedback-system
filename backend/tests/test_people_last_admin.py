def test_last_active_administrator_and_active_reports_are_protected(sign_in):
    client = sign_in("admin")
    assert client.patch("/api/v1/people/admin", json={"active": False}).status_code == 409
    assert client.patch("/api/v1/people/admin", json={"role": "employee"}).status_code == 409
    assert client.patch("/api/v1/people/manager", json={"active": False}).status_code == 409
    assert client.patch("/api/v1/people/employee", json={"name": None}).status_code == 422
