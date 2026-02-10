"""Tests for the Exercise Service."""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app, quizzes

client = TestClient(app)


def setup_function():
    quizzes.clear()


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
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert "publish/pubsub/code.submitted" in call_args[0][0]


@patch("app.main.requests.post")
@patch("app.main.requests.get")
def test_grade_exercise_pass(mock_get, mock_post):
    mock_get.return_value = MagicMock(
        status_code=200,
        text='{}',
        json=lambda: {
            "id": "ex-1", "title": "Test", "description": "Desc",
            "expected_output": "Hello", "module_id": "mod-1",
        },
    )
    # First post is code execution, second is dapr publish
    exec_response = MagicMock(
        status_code=200,
        json=lambda: {"output": "Hello", "error": ""},
    )
    mock_post.return_value = exec_response

    response = client.post("/api/exercises/ex-1/grade", json={
        "user_id": "user-1",
        "code": "print('Hello')",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["passed"] is True
    assert data["score"] == 100.0


@patch("app.main.requests.post")
@patch("app.main.requests.get")
def test_grade_exercise_fail(mock_get, mock_post):
    mock_get.return_value = MagicMock(
        status_code=200,
        text='{}',
        json=lambda: {
            "id": "ex-1", "title": "Test", "description": "Desc",
            "expected_output": "Hello", "module_id": "mod-1",
        },
    )
    exec_response = MagicMock(
        status_code=200,
        json=lambda: {"output": "Wrong", "error": ""},
    )
    mock_post.return_value = exec_response

    response = client.post("/api/exercises/ex-1/grade", json={
        "user_id": "user-1",
        "code": "print('Wrong')",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["passed"] is False
    assert data["score"] == 30.0


@patch("app.main.client")
def test_generate_exercises(mock_openai):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"exercises": [{"title": "Sum", "description": "Add two numbers", "starter_code": "# code here", "expected_output": "5", "hints": ["Use +"]}]}'
    mock_openai.chat.completions.create.return_value = mock_response

    response = client.post("/api/exercises/generate", json={
        "topic": "arithmetic",
        "difficulty": "beginner",
        "count": 1,
    })
    assert response.status_code == 200
    exercises = response.json()
    assert len(exercises) == 1
    assert exercises[0]["title"] == "Sum"


@patch("app.main.client")
def test_generate_quiz(mock_openai):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"questions": [{"question": "What is 1+1?", "options": ["1", "2", "3", "4"], "correct_answer": 1, "explanation": "Basic math"}]}'
    mock_openai.chat.completions.create.return_value = mock_response

    response = client.post("/api/quizzes/generate", json={
        "module_id": "mod-1",
        "topic": "basics",
        "num_questions": 1,
    })
    assert response.status_code == 200
    quiz = response.json()
    assert quiz["module_id"] == "mod-1"
    assert len(quiz["questions"]) == 1


@patch("app.main.client")
def test_submit_quiz(mock_openai):
    setup_function()
    # First generate a quiz
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"questions": [{"question": "Q1", "options": ["A", "B", "C", "D"], "correct_answer": 1, "explanation": "B is correct"}]}'
    mock_openai.chat.completions.create.return_value = mock_response

    gen_response = client.post("/api/quizzes/generate", json={
        "module_id": "mod-1",
        "topic": "basics",
        "num_questions": 1,
    })
    quiz_id = gen_response.json()["id"]
    question_id = gen_response.json()["questions"][0]["id"]

    # Submit correct answer
    response = client.post(f"/api/quizzes/{quiz_id}/submit", json={
        "answers": {question_id: 1},
    })
    assert response.status_code == 200
    result = response.json()
    assert result["score"] == 1
    assert result["percentage"] == 100.0


def test_submit_quiz_not_found():
    setup_function()
    response = client.post("/api/quizzes/nonexistent/submit", json={
        "answers": {},
    })
    assert response.status_code == 404


def test_handle_learning_event():
    response = client.post("/events/learning", json={
        "data": {"type": "test"}
    })
    assert response.status_code == 200
    assert response.json()["status"] == "processed"
