def register(client, email="ada@example.com"):
    return client.post(
        "/users",
        json={"email": email, "password": "password123", "full_name": "Ada"},
    )


def test_register_user(client):
    response = register(client)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "ada@example.com"
    assert body["global_role"] == "member"
    # The password hash must never be exposed in a response.
    assert "hashed_password" not in body
    assert "password" not in body


def test_duplicate_email_rejected(client):
    register(client)
    response = register(client)
    assert response.status_code == 409


def test_password_min_length_enforced(client):
    response = client.post("/users", json={"email": "x@example.com", "password": "short"})
    assert response.status_code == 422


def test_list_and_get_user(client):
    user_id = register(client).json()["id"]
    assert len(client.get("/users").json()) == 1
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id


def test_get_missing_user(client):
    assert client.get("/users/999").status_code == 404
