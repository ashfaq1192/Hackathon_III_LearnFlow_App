"""Tests for the Code Review Service."""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "code-review-service"


def test_dapr_subscribe():
    response = client.get("/dapr/subscribe")
    assert response.status_code == 200
    subs = response.json()
    assert len(subs) == 1
    assert subs[0]["topic"] == "code.submitted"


@patch("app.main.requests.post")
@patch("app.main.client")
def test_review_code(mock_openai, mock_post):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"score": 85, "correctness": 90, "style": 80, "efficiency": 85, "readability": 85, "suggestions": ["Add docstrings", "Use more descriptive variable names"], "overall_feedback": "Good code! Clean and efficient."}'
    mock_openai.chat.completions.create.return_value = mock_response
    mock_post.return_value = MagicMock(status_code=200)

    response = client.post("/api/review", json={
        "code": "def add(a, b):\n    return a + b",
        "user_id": "user-1",
    })

    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 85
    assert data["correctness"] == 90
    assert len(data["suggestions"]) == 2
    assert data["overall_feedback"] != ""


@patch("app.main.requests.post")
@patch("app.main.client")
def test_review_publishes_event(mock_openai, mock_post):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"score": 70, "correctness": 70, "style": 70, "efficiency": 70, "readability": 70, "suggestions": ["Improve naming"], "overall_feedback": "Decent code."}'
    mock_openai.chat.completions.create.return_value = mock_response
    mock_post.return_value = MagicMock(status_code=200)

    client.post("/api/review", json={
        "code": "x = 1 + 2",
        "user_id": "user-1",
        "exercise_id": "ex-1",
    })

    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert "publish/pubsub/learning.events" in call_args[0][0]
    event_data = call_args[1]["json"]
    assert event_data["type"] == "code_reviewed"
    assert event_data["quality_score"] == 70


@patch("app.main.client")
def test_review_error_handling(mock_openai):
    mock_openai.chat.completions.create.side_effect = Exception("API error")

    response = client.post("/api/review", json={
        "code": "test",
    })
    assert response.status_code == 500


@patch("app.main.client")
def test_review_json_decode_error(mock_openai):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "not json"
    mock_openai.chat.completions.create.return_value = mock_response

    response = client.post("/api/review", json={
        "code": "print('hello')",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 50  # default fallback


def test_handle_code_event():
    response = client.post("/events/code", json={
        "data": {"code": "", "user_id": "user-1"}
    })
    assert response.status_code == 200
    assert response.json()["status"] == "processed"
