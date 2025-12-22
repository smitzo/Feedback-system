def test_search_and_pagination_preserve_scope(sign_in):
    client = sign_in("manager")
    assert client.get("/api/v1/people?q=Outsider").json()["total"] == 0
    first = client.get("/api/v1/people?limit=1").json()
    second = client.get("/api/v1/people?limit=1&offset=1").json()
    assert first["total"] == 4 and first["items"][0]["id"] != second["items"][0]["id"]
    assert client.get("/api/v1/people?limit=1000").status_code == 422
    assert client.get("/api/v1/people?q=%25").json()["total"] == 0
