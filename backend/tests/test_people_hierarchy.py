def test_hierarchy_rejects_self_cycles_and_non_managers(sign_in):
    client = sign_in("admin")
    for target, manager in [("manager", "manager"), ("employee", "peer")]:
        assert (
            client.patch(f"/api/v1/people/{target}", json={"manager_id": manager}).status_code
            == 422
        )
    assert client.patch("/api/v1/people/other", json={"manager_id": "manager"}).status_code == 200
    assert client.patch("/api/v1/people/manager", json={"manager_id": "other"}).status_code == 422
