def test_healthy(client):
    response = client.get("/healthy")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
