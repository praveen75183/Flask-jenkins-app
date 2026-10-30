def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "message" in data
    assert data["app"] == "flask-jenkins-app"


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_create_and_get_item(client):
    resp = client.post("/api/items", json={"name": "widget"})
    assert resp.status_code == 201
    item = resp.get_json()
    assert item["name"] == "widget"

    resp = client.get(f"/api/items/{item['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "widget"


def test_create_item_validation(client):
    resp = client.post("/api/items", json={})
    assert resp.status_code == 400


def test_list_items(client):
    client.post("/api/items", json={"name": "a"})
    client.post("/api/items", json={"name": "b"})
    resp = client.get("/api/items")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_get_missing_item(client):
    assert client.get("/api/items/999").status_code == 404


def test_delete_item(client):
    item = client.post("/api/items", json={"name": "temp"}).get_json()
    assert client.delete(f"/api/items/{item['id']}").status_code == 204
    assert client.get(f"/api/items/{item['id']}").status_code == 404


def test_delete_missing_item(client):
    assert client.delete("/api/items/123").status_code == 404
