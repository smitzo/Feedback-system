def test_create_requires_administration_and_normalizes_email(sign_in):
    body = {
        "name": "New Person",
        "email": "NEW@example.com",
        "password": "Provisioned passphrase 42",
        "manager_id": "manager",
    }
    assert sign_in("employee").post("/api/v1/people", json=body).status_code == 403
    client = sign_in("admin")
    response = client.post("/api/v1/people", json=body)
    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"
    assert "password" not in response.text
    assert client.post("/api/v1/people", json=body).status_code == 409
