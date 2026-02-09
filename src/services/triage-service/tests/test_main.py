"""Tests for the Triage Service."""
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "triage-service"


def test_dapr_subscribe():
    response = client.get("/dapr/subscribe")
    assert response.status_code == 200
    subs = response.json()
    assert len(subs) == 1
    assert subs[0]["topic"] == "struggle.detected"
    assert subs[0]["pubsubname"] == "pubsub"


@patch("app.main.requests.post")
@patch("app.main.client")
def test_triage_question(mock_openai, mock_post):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "analysis": "Student needs help with loops",
        "route_to": "concepts-service",
        "confidence": 0.9,
        "suggestion": "Try reviewing for loop syntax",
    })
    mock_openai.chat.completions.create.return_value = mock_response
    mock_post.return_value = MagicMock(status_code=200)

    response = client.post("/triage", json={
        "question": "How do for loops work?",
        "user_id": "user-1",
    })

    assert response.status_code == 200
    data = response.json()
    assert data["route_to"] == "concepts-service"
    assert data["confidence"] == 0.9
    assert "loops" in data["analysis"]


@patch("app.main.requests.post")
@patch("app.main.client")
def test_triage_routes_to_exercise(mock_openai, mock_post):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "analysis": "Student wants to practice",
        "route_to": "exercise-service",
        "confidence": 0.85,
        "suggestion": "Try a coding exercise",
    })
    mock_openai.chat.completions.create.return_value = mock_response
    mock_post.return_value = MagicMock(status_code=200)

    response = client.post("/triage", json={
        "question": "Give me a coding exercise for lists",
    })

    assert response.status_code == 200
    assert response.json()["route_to"] == "exercise-service"


@patch("app.main.requests.post")
@patch("app.main.client")
def test_triage_publishes_dapr_event(mock_openai, mock_post):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "analysis": "test",
        "route_to": "concepts-service",
        "confidence": 0.5,
        "suggestion": "test",
    })
    mock_openai.chat.completions.create.return_value = mock_response
    mock_post.return_value = MagicMock(status_code=200)

    client.post("/triage", json={"question": "test"})

    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert "publish/pubsub/learning.events" in call_args[0][0]


@patch("app.main.client")
def test_triage_error_handling(mock_openai):
    mock_openai.chat.completions.create.side_effect = Exception("API error")

    response = client.post("/triage", json={"question": "test"})
    assert response.status_code == 500


def test_handle_struggle_event():
    with patch("app.main.client") as mock_openai, \
         patch("app.main.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "analysis": "auto-triage",
            "route_to": "concepts-service",
            "confidence": 0.7,
            "suggestion": "help",
        })
        mock_openai.chat.completions.create.return_value = mock_response
        mock_post.return_value = MagicMock(status_code=200)

        response = client.post("/events/struggle", json={
            "data": {
                "user_id": "user-1",
                "struggle_type": "syntax_error",
            }
        })

        assert response.status_code == 200
        assert response.json()["status"] == "processed"
