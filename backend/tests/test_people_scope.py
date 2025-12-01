def test_directory_scopes_and_secret_projection(sign_in):
    client = sign_in("employee")
    data = client.get("/api/v1/people").json()
    assert [u["id"] for u in data["items"]] == ["employee"]
    client = sign_in("manager")
    response = client.get("/api/v1/people")
    assert {u["id"] for u in response.json()["items"]} == {"manager", "employee", "peer", "third"}
    assert "password" not in response.text
    assert len(sign_in("admin").get("/api/v1/people").json()["items"]) == 8
