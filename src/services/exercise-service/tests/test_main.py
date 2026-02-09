"""Tests for the Exercise Service."""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "exercise-service"


def test_dapr_subscribe():
    response = client.get("/dapr/subscribe")
    assert response.status_code == 200
    subs = response.json()
    assert len(subs) == 1
    assert subs[0]["topic"] == "learning.events"


@patch("app.main.requests.post")
def test_create_exercise(mock_post):
    mock_post.return_value = MagicMock(status_code=204)

    response = client.post("/exercises", json={
        "title": "Hello World",
        "description": "Print hello world",
        "difficulty": "beginner",
        "starter_code": "# Write your code here",
        "expected_output": "Hello, World!",
        "hints": ["Use the print() function"],
    })

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Hello World"
    assert data["id"] is not None
    assert len(data["id"]) > 0


@patch("app.main.requests.post")
def test_create_exercise_dapr_failure(mock_post):
    mock_post.return_value = MagicMock(status_code=500)

    response = client.post("/exercises", json={
        "title": "Test",
        "description": "Test exercise",
    })

    assert response.status_code == 500


@patch("app.main.requests.get")
def test_get_exercise(mock_get):
    mock_get.return_value = MagicMock(
        status_code=200,
        text='{"id": "abc-123", "title": "Test", "description": "Desc", "difficulty": "beginner"}',
        json=lambda: {
            "id": "abc-123",
            "title": "Test",
            "description": "Desc",
            "difficulty": "beginner",
        }
    )

    response = client.get("/exercises/abc-123")
    assert response.status_code == 200
    assert response.json()["title"] == "Test"


@patch("app.main.requests.get")
def test_get_exercise_not_found(mock_get):
    mock_get.return_value = MagicMock(status_code=204, text="")

    response = client.get("/exercises/nonexistent")
    assert response.status_code == 404


@patch("app.main.requests.post")
def test_list_exercises(mock_post):
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "results": [
                {"data": {"id": "1", "title": "Ex1", "description": "D1", "difficulty": "beginner"}},
                {"data": {"id": "2", "title": "Ex2", "description": "D2", "difficulty": "intermediate"}},
            ]
        }
    )

    response = client.get("/exercises")
    assert response.status_code == 200
    exercises = response.json()
    assert len(exercises) == 2


@patch("app.main.requests.post")
def test_list_exercises_empty(mock_post):
    mock_post.side_effect = Exception("Dapr unavailable")

    response = client.get("/exercises")
    assert response.status_code == 200
    assert response.json() == []


@patch("app.main.requests.post")
def test_submit_exercise(mock_post):
    mock_post.return_value = MagicMock(status_code=200)

    response = client.post("/exercises/abc-123/submit", json={
        "exercise_id": "abc-123",
        "user_id": "user-1",
        "code": "print('hello')",
    })

    assert response.status_code == 200
    assert response.json()["status"] == "submitted"
    # Verify Dapr publish was called
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert "publish/pubsub/code.submitted" in call_args[0][0]


def test_handle_learning_event():
    response = client.post("/events/learning", json={
        "data": {"type": "test"}
    })
    assert response.status_code == 200
    assert response.json()["status"] == "processed"
