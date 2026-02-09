"""Tests for the Code Execution Service."""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app, check_code_safety

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "code-execution-service"


def test_dapr_subscribe():
    response = client.get("/dapr/subscribe")
    assert response.status_code == 200
    subs = response.json()
    assert len(subs) == 1
    assert subs[0]["topic"] == "code.submitted"


# Safety check tests
def test_safety_allows_safe_code():
    assert check_code_safety("print('hello')") is None


def test_safety_blocks_subprocess():
    result = check_code_safety("import subprocess")
    assert result is not None
    assert "subprocess" in result


def test_safety_blocks_socket():
    result = check_code_safety("import socket")
    assert result is not None
    assert "socket" in result


def test_safety_blocks_from_import():
    result = check_code_safety("from shutil import copy")
    assert result is not None
    assert "shutil" in result


def test_safety_blocks_file_write():
    result = check_code_safety("f = open('file.txt', 'w')")
    assert result is not None
    assert "write" in result.lower()


def test_safety_blocks_exec():
    result = check_code_safety("exec('print(1)')")
    assert result is not None
    assert "exec" in result


def test_safety_blocks_eval():
    result = check_code_safety("eval('1+1')")
    assert result is not None
    assert "eval" in result


# Execution tests
@patch("app.main.requests.post")
def test_execute_safe_code(mock_post):
    mock_post.return_value = MagicMock(status_code=200)

    response = client.post("/execute", json={
        "code": "print('hello')",
    })

    assert response.status_code == 200
    data = response.json()
    assert "hello" in data["output"]
    assert data["exit_code"] == 0
    assert data["timed_out"] is False


@patch("app.main.requests.post")
def test_execute_with_error(mock_post):
    mock_post.return_value = MagicMock(status_code=200)

    response = client.post("/execute", json={
        "code": "raise ValueError('test error')",
    })

    assert response.status_code == 200
    data = response.json()
    assert data["exit_code"] != 0
    assert "ValueError" in data["error"]


def test_execute_blocked_import():
    response = client.post("/execute", json={
        "code": "import subprocess\nsubprocess.run(['ls'])",
    })

    assert response.status_code == 200
    data = response.json()
    assert data["exit_code"] == 1
    assert "subprocess" in data["error"]


@patch("app.main.requests.post")
def test_execute_timeout(mock_post):
    mock_post.return_value = MagicMock(status_code=200)

    response = client.post("/execute", json={
        "code": "import time\ntime.sleep(60)",
        "timeout": 1,
    })

    assert response.status_code == 200
    data = response.json()
    assert data["timed_out"] is True


@patch("app.main.requests.post")
def test_execute_publishes_dapr_event(mock_post):
    mock_post.return_value = MagicMock(status_code=200)

    client.post("/execute", json={
        "code": "print(1)",
        "user_id": "user-1",
    })

    # Should have been called for Dapr publish
    assert mock_post.called
    call_args = mock_post.call_args
    assert "publish/pubsub/learning.events" in call_args[0][0]


def test_handle_code_event_with_code():
    with patch("app.main.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200)

        response = client.post("/events/code", json={
            "data": {
                "code": "print('from event')",
                "user_id": "user-1",
            }
        })

        assert response.status_code == 200
        assert response.json()["status"] == "executed"


def test_handle_code_event_empty():
    response = client.post("/events/code", json={
        "data": {}
    })

    assert response.status_code == 200
    assert response.json()["status"] == "processed"
