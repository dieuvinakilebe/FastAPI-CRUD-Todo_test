# tests/test_integration.py

from .conftest import create_todo  # если  использовать helper напрямую


def test_create_todo_success(client):
    payload = {
        "title": "Buy milk",
        "description": "2 liters",
        "completed": False,
    }

    response = client.post("/todos", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["completed"] is False


def test_create_todo_validation_error(client):
    payload = {
        "description": "No title here",
        "completed": False,
    }

    response = client.post("/todos", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body


def test_get_todos_list(client):
    todo1 = create_todo(client, title="Task 1")
    todo2 = create_todo(client, title="Task 2")

    response = client.get("/todos")
    assert response.status_code == 200

    data = response.json()
    ids = {item["id"] for item in data}
    assert todo1["id"] in ids
    assert todo2["id"] in ids


def test_update_todo_success(client):
    todo = create_todo(client, title="Old title", description="Old desc")

    updated_payload = {
        "title": "New title",
        "description": "New desc",
        "completed": True,
    }

    response = client.put(f"/todos/{todo['id']}", json=updated_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == todo["id"]
    assert data["title"] == "New title"
    assert data["description"] == "New desc"
    assert data["completed"] is True


def test_delete_todo_and_not_found_after(client):
    todo = create_todo(client)

    delete_resp = client.delete(f"/todos/{todo['id']}")
    assert delete_resp.status_code in (200, 204)

    get_resp = client.get(f"/todos/{todo['id']}")
    assert get_resp.status_code == 404
