def make_user(client, email="owner@example.com"):
    return client.post("/users", json={"email": email, "password": "password123"}).json()["id"]


def test_create_and_get_task(client):
    owner_id = make_user(client)
    response = client.post("/tasks", json={"title": "Write tests", "owner_id": owner_id})
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "todo"
    assert client.get(f"/tasks/{body['id']}").json()["title"] == "Write tests"


def test_create_task_unknown_owner(client):
    response = client.post("/tasks", json={"title": "orphan", "owner_id": 999})
    assert response.status_code == 404


def test_update_task_status(client):
    owner_id = make_user(client)
    task_id = client.post("/tasks", json={"title": "t", "owner_id": owner_id}).json()["id"]
    response = client.patch(f"/tasks/{task_id}", json={"status": "done"})
    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_list_tasks_filtered_by_owner(client):
    owner_a = make_user(client)
    owner_b = make_user(client, email="b@example.com")
    client.post("/tasks", json={"title": "a", "owner_id": owner_a})
    client.post("/tasks", json={"title": "b", "owner_id": owner_b})
    assert len(client.get("/tasks", params={"owner_id": owner_a}).json()) == 1
    assert len(client.get("/tasks").json()) == 2


def test_update_missing_task(client):
    assert client.patch("/tasks/999", json={"status": "done"}).status_code == 404
