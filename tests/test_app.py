import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))

from app import app


def test_health_route_exists():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code in [200, 503]


def test_create_todo_without_title():
    client = app.test_client()

    response = client.post("/todos", json={})

    assert response.status_code == 400
    assert response.get_json()["error"] == "Title is required"


def test_create_todo_with_empty_title():
    client = app.test_client()

    response = client.post("/todos", json={"title": ""})

    assert response.status_code == 400
    assert response.get_json()["error"] == "Title is required"

def  test_update_todo_with_missing_json():
    
    client = app.test_client()
    response = client.put("/todos/1", json={})

    assert response.status_code == 400
    assert response.get_json()["error"] == "completed is required"
