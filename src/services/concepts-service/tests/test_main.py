"""Tests for the Concepts Service."""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "concepts-service"


def test_dapr_subscribe():
    response = client.get("/dapr/subscribe")
    assert response.status_code == 200
    subs = response.json()
    assert len(subs) == 1
    assert subs[0]["topic"] == "learning.events"
    assert subs[0]["pubsubname"] == "pubsub"


@patch("app.main.requests.post")
@patch("app.main.client")
def test_explain_concept(mock_openai, mock_post):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = (
        "A for loop iterates over a sequence. Example: for i in range(10): print(i)"
    )
    mock_openai.chat.completions.create.return_value = mock_response
    mock_post.return_value = MagicMock(status_code=200)

    response = client.post("/explain", json={
        "concept": "for loops",
        "level": "beginner",
        "user_id": "user-1",
    })

    assert response.status_code == 200
    data = response.json()
    assert data["concept"] == "for loops"
    assert len(data["explanation"]) > 0


@patch("app.main.requests.post")
@patch("app.main.client")
def test_explain_publishes_dapr_event(mock_openai, mock_post):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Explanation"
    mock_openai.chat.completions.create.return_value = mock_response
    mock_post.return_value = MagicMock(status_code=200)

    client.post("/explain", json={"concept": "variables"})

    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert "publish/pubsub/learning.events" in call_args[0][0]
    event_data = call_args[1]["json"]
    assert event_data["type"] == "concept_explained"
    assert event_data["concept"] == "variables"


@patch("app.main.client")
def test_explain_error_handling(mock_openai):
    mock_openai.chat.completions.create.side_effect = Exception("API error")

    response = client.post("/explain", json={"concept": "test"})
    assert response.status_code == 500


def test_handle_learning_event():
    response = client.post("/events/learning", json={
        "data": {"type": "test_event"}
    })
    assert response.status_code == 200
    assert response.json()["status"] == "processed"


@patch("app.main.requests.post")
@patch("app.main.client")
def test_explain_with_level(mock_openai, mock_post):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Advanced explanation of decorators"
    mock_openai.chat.completions.create.return_value = mock_response
    mock_post.return_value = MagicMock(status_code=200)

    response = client.post("/explain", json={
        "concept": "decorators",
        "level": "advanced",
    })

    assert response.status_code == 200
    # Verify the level was passed to OpenAI prompt
    call_args = mock_openai.chat.completions.create.call_args
    user_msg = call_args[1]["messages"][1]["content"]
    assert "advanced" in user_msg
