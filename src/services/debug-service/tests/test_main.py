"""Tests for the Debug Service."""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app, error_tracker

client = TestClient(app)


def setup_function():
    error_tracker.clear()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "debug-service"


def test_dapr_subscribe():
    response = client.get("/dapr/subscribe")
    assert response.status_code == 200
    subs = response.json()
    assert len(subs) == 1
    assert subs[0]["topic"] == "code.submitted"


@patch("app.main.requests.post")
@patch("app.main.client")
def test_analyze_error(mock_openai, mock_post):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"error_type": "SyntaxError", "root_cause": "Missing colon after if statement", "hints": ["Check your if statement syntax", "Python requires a colon after conditions", "Add : after if x > 5"], "solution": "if x > 5:\\n    print(x)", "explanation": "Python if statements require a colon"}'
    mock_openai.chat.completions.create.return_value = mock_response
    mock_post.return_value = MagicMock(status_code=200)

    response = client.post("/api/debug/analyze", json={
        "code": "if x > 5\n    print(x)",
        "error_message": "SyntaxError: expected ':'",
        "user_id": "user-1",
    })

    assert response.status_code == 200
    data = response.json()
    assert data["error_type"] == "SyntaxError"
    assert len(data["hints"]) == 3
    assert data["solution"] != ""


@patch("app.main.requests.post")
@patch("app.main.client")
def test_analyze_publishes_event(mock_openai, mock_post):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"error_type": "NameError", "root_cause": "Variable not defined", "hints": ["Check variable names"], "solution": "x = 5", "explanation": "Define before use"}'
    mock_openai.chat.completions.create.return_value = mock_response
    mock_post.return_value = MagicMock(status_code=200)

    client.post("/api/debug/analyze", json={
        "code": "print(x)",
        "error_message": "NameError: name 'x' is not defined",
        "user_id": "user-1",
    })

    mock_post.assert_called()
    call_args = mock_post.call_args_list[0]
    assert "publish/pubsub/learning.events" in call_args[0][0]


@patch("app.main.requests.post")
@patch("app.main.client")
def test_repeated_errors_trigger_struggle(mock_openai, mock_post):
    setup_function()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"error_type": "TypeError", "root_cause": "Type mismatch", "hints": ["Check types"], "solution": "str(x)", "explanation": "Convert types"}'
    mock_openai.chat.completions.create.return_value = mock_response
    mock_post.return_value = MagicMock(status_code=200)

    for _ in range(3):
        client.post("/api/debug/analyze", json={
            "code": "x + 'hello'",
            "error_message": "TypeError",
            "user_id": "user-2",
        })

    # Check that struggle.detected was published
    struggle_calls = [
        c for c in mock_post.call_args_list
        if "struggle.detected" in str(c)
    ]
    assert len(struggle_calls) >= 1


@patch("app.main.client")
def test_analyze_error_handling(mock_openai):
    mock_openai.chat.completions.create.side_effect = Exception("API error")

    response = client.post("/api/debug/analyze", json={
        "code": "test",
        "error_message": "error",
    })
    assert response.status_code == 500


def test_handle_code_event():
    response = client.post("/events/code", json={
        "data": {"code": "", "error": "", "user_id": "user-1"}
    })
    assert response.status_code == 200
    assert response.json()["status"] == "processed"
