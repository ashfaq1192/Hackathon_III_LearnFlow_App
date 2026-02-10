"""Tests for the Progress Service."""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app, user_progress, struggle_alerts

client = TestClient(app)


def setup_function():
    user_progress.clear()
    struggle_alerts.clear()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "progress-service"


def test_dapr_subscribe():
    response = client.get("/dapr/subscribe")
    assert response.status_code == 200
    subs = response.json()
    assert len(subs) == 2
    topics = [s["topic"] for s in subs]
    assert "learning.events" in topics
    assert "code.submitted" in topics


def test_list_curriculum():
    response = client.get("/api/curriculum")
    assert response.status_code == 200
    modules = response.json()
    assert len(modules) == 8
    assert modules[0]["id"] == "mod-1"
    assert modules[0]["name"] == "Python Basics"


def test_get_curriculum_module():
    response = client.get("/api/curriculum/mod-3")
    assert response.status_code == 200
    module = response.json()
    assert module["name"] == "Data Structures"
    assert "Lists" in module["topics"]


def test_get_curriculum_module_not_found():
    response = client.get("/api/curriculum/mod-99")
    assert response.status_code == 404


def test_get_progress_initializes():
    setup_function()
    response = client.get("/api/progress/user-1")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user-1"
    assert len(data["modules"]) == 8
    assert data["modules"]["mod-1"]["mastery"] == 0.0


@patch("app.main.requests.post")
def test_record_exercise_completed(mock_post):
    setup_function()
    mock_post.return_value = MagicMock(status_code=200)

    response = client.post("/api/progress/user-1/record", json={
        "activity_type": "exercise_completed",
        "module_id": "mod-1",
        "score": 80.0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "recorded"
    assert data["mastery"] > 0


@patch("app.main.requests.post")
def test_record_quiz_taken(mock_post):
    setup_function()
    mock_post.return_value = MagicMock(status_code=200)

    response = client.post("/api/progress/user-1/record", json={
        "activity_type": "quiz_taken",
        "module_id": "mod-2",
        "score": 90.0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["mastery"] > 0


@patch("app.main.requests.post")
def test_low_quiz_triggers_struggle(mock_post):
    setup_function()
    mock_post.return_value = MagicMock(status_code=200)

    client.post("/api/progress/user-1/record", json={
        "activity_type": "quiz_taken",
        "module_id": "mod-1",
        "score": 30.0,
    })
    assert len(struggle_alerts) == 1
    assert struggle_alerts[0]["struggle_type"] == "low_quiz_score"


def test_get_mastery():
    setup_function()
    response = client.get("/api/progress/user-1/mastery/mod-1")
    assert response.status_code == 200
    data = response.json()
    assert data["module_id"] == "mod-1"
    assert data["mastery_level"] == "beginner"


def test_get_mastery_module_not_found():
    setup_function()
    # First initialize user progress
    client.get("/api/progress/user-1")
    response = client.get("/api/progress/user-1/mastery/mod-99")
    assert response.status_code == 404


def test_handle_learning_event():
    setup_function()
    response = client.post("/events/learning", json={
        "data": {"type": "test_event"}
    })
    assert response.status_code == 200
    assert response.json()["status"] == "processed"


def test_handle_code_event():
    setup_function()
    response = client.post("/events/code", json={
        "data": {"user_id": "user-1", "status": "success"}
    })
    assert response.status_code == 200
    assert response.json()["status"] == "processed"


@patch("app.main.requests.post")
def test_repeated_failures_trigger_struggle(mock_post):
    setup_function()
    mock_post.return_value = MagicMock(status_code=200)

    for i in range(5):
        client.post("/events/code", json={
            "data": {"user_id": "user-2", "status": "error", "module_id": "mod-1"}
        })
    assert any(s["struggle_type"] == "repeated_failures" for s in struggle_alerts)


def test_get_struggles_empty():
    setup_function()
    response = client.get("/api/progress/struggles")
    assert response.status_code == 200
    assert response.json() == []
