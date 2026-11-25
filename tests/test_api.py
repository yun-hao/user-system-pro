import pytest
from fastapi.testclient import TestClient

import api
from storage import SQLiteStorage
from user_manager import UserManager


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_storage = SQLiteStorage(tmp_path / "test_api.db")
    test_manager = UserManager(test_storage)
    monkeypatch.setattr(api, "manager", test_manager)
    return TestClient(api.app)



def test_create_and_get_user(client):
    resp = client.post("/users", json={"name":"张三", "age": 20})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "张三"
    assert data["age"] == 20
    assert isinstance(data["id"], int)

    resp = client.get(f"/users")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data[0]["name"] == "张三"
    assert data[0]["age"] == 20

def test_get_and_not_found_user(client):
    resp = client.post("/users", json={"name": "张三", "age": 20})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "张三"
    assert data["age"] == 20
    assert isinstance(data["id"], int)

    user_id = data["id"]
    resp = client.get(f"/users/{user_id}")
    assert resp.status_code == 200

    resp = client.get(f"/users/999")
    assert resp.status_code == 404


def test_add_validation_error(client):
    resp = client.post("/users",json={"name": "张三", "age": -5})
    assert resp.status_code == 400

    resp = client.post("/users",json={"name": "张三", "age": "abc" })
    assert resp.status_code == 422

def test_update_user(client):
    resp = client.post("/users", json={"name": "张三", "age": 20})
    user_id = resp.json()["id"]
    resp = client.patch(f"/users/{user_id}",json={"name":"李四"})
    assert resp.status_code == 200
    assert resp.json()["age"] == 20
    assert resp.json()["name"] == "李四"

def test_delete_user(client):
    resp = client.post("/users", json={"name": "张三", "age": 20})
    user_id = resp.json()["id"]

    resp = client.delete(f"/users/{user_id}")
    assert resp.status_code == 204

    resp = client.get(f"/users/{user_id}")
    assert resp.status_code == 404