def test_long_reporting_cycles_and_manager_demotion_are_rejected(sign_in):
    client = sign_in("admin")
    assert client.patch("/api/v1/people/other", json={"manager_id":"manager"}).status_code == 200
    assert client.patch("/api/v1/people/manager", json={"manager_id":"other"}).status_code == 422
    assert client.patch("/api/v1/people/manager", json={"role":"employee"}).status_code == 409
