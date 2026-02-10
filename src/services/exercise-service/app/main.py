"""Exercise Service - CRUD API for managing coding exercises, grading, and quizzes."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import json
import requests
import uuid

from openai import OpenAI

app = FastAPI(
    title="exercise-service",
    description="CRUD API for managing Python coding exercises, auto-grading, and quizzes",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dapr configuration
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
STATE_STORE = "statestore"

# OpenAI configuration
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# In-memory quiz store
quizzes: Dict[str, dict] = {}


class Exercise(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    difficulty: str = "beginner"
    module_id: str = "mod-1"
    topic: str = ""
    starter_code: str = ""
    expected_output: str = ""
    hints: List[str] = []
    test_cases: List[dict] = []


class Submission(BaseModel):
    exercise_id: str
    user_id: str
    code: str


class GradeRequest(BaseModel):
    user_id: str
    code: str


class GradeResponse(BaseModel):
    passed: bool
    score: float
    feedback: str


class GenerateRequest(BaseModel):
    topic: str
    difficulty: str = "beginner"
    count: int = 3


class QuizQuestion(BaseModel):
    id: str
    question: str
    options: List[str]
    correct_answer: int
    explanation: str = ""


class Quiz(BaseModel):
    id: str
    module_id: str
    topic: str
    questions: List[QuizQuestion]


class QuizGenerateRequest(BaseModel):
    module_id: str
    topic: str
    num_questions: int = 5


class QuizSubmitRequest(BaseModel):
    answers: Dict[str, int]  # question_id -> selected option index


class QuizResult(BaseModel):
    score: int
    total: int
    percentage: float
    results: List[dict]


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "exercise-service"}


@app.get("/dapr/subscribe")
async def subscribe():
    """Dapr pub/sub subscriptions."""
    return [
        {"pubsubname": "pubsub", "topic": "learning.events", "route": "/events/learning"}
    ]


@app.post("/exercises", response_model=Exercise)
@app.post("/api/exercises", response_model=Exercise, include_in_schema=False)
async def create_exercise(exercise: Exercise):
    """Create a new coding exercise."""
    exercise.id = str(uuid.uuid4())

    response = requests.post(
        f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE}",
        json=[{"key": f"exercise-{exercise.id}", "value": exercise.model_dump()}]
    )

    if response.status_code not in (200, 204):
        raise HTTPException(status_code=500, detail="Failed to save exercise")

    return exercise


@app.get("/exercises/{exercise_id}", response_model=Exercise)
async def get_exercise(exercise_id: str):
    """Get an exercise by ID."""
    response = requests.get(
        f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE}/exercise-{exercise_id}"
    )

    if response.status_code == 204 or not response.text:
        raise HTTPException(status_code=404, detail="Exercise not found")

    return Exercise(**response.json())


@app.get("/exercises", response_model=List[Exercise])
@app.get("/api/exercises", response_model=List[Exercise], include_in_schema=False)
async def list_exercises():
    """List all exercises (from state store query)."""
    try:
        response = requests.post(
            f"{DAPR_BASE_URL}/v1.0-alpha1/state/{STATE_STORE}/query",
            json={
                "filter": {"EQ": {"value.id": {"NEQ": ""}}},
                "sort": [{"key": "value.difficulty", "order": "ASC"}],
            }
        )
        if response.status_code == 200:
            results = response.json().get("results", [])
            return [Exercise(**r["data"]) for r in results]
    except Exception:
        pass

    return []


@app.post("/exercises/{exercise_id}/submit")
async def submit_exercise(exercise_id: str, submission: Submission):
    """Submit code for an exercise and publish for execution."""
    requests.post(
        f"{DAPR_BASE_URL}/v1.0/publish/pubsub/code.submitted",
        json={
            "exercise_id": exercise_id,
            "user_id": submission.user_id,
            "code": submission.code,
        }
    )

    return {"status": "submitted", "exercise_id": exercise_id}


@app.post("/api/exercises/{exercise_id}/grade", response_model=GradeResponse)
async def grade_exercise(exercise_id: str, request: GradeRequest):
    """Auto-grade a code submission by running it and comparing output."""
    # Get the exercise to compare expected output
    try:
        ex_response = requests.get(
            f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE}/exercise-{exercise_id}"
        )
        if ex_response.status_code == 200 and ex_response.text:
            exercise = Exercise(**ex_response.json())
        else:
            exercise = None
    except Exception:
        exercise = None

    # Execute the code
    exec_url = os.getenv("CODE_EXECUTION_SERVICE_URL", "http://code-execution-service:8000")
    try:
        exec_response = requests.post(
            f"{exec_url}/execute",
            json={"code": request.code},
            timeout=15,
        )
        exec_result = exec_response.json()
        output = exec_result.get("output", "")
        error = exec_result.get("error", "")
    except Exception:
        output = ""
        error = "Code execution service unavailable"

    if error:
        score = 0.0
        passed = False
        feedback = f"Code execution error: {error}"
    elif exercise and exercise.expected_output:
        if output.strip() == exercise.expected_output.strip():
            score = 100.0
            passed = True
            feedback = "All tests passed! Great job!"
        else:
            score = 30.0
            passed = False
            feedback = f"Output mismatch. Expected: {exercise.expected_output.strip()}, Got: {output.strip()}"
    else:
        # No expected output; if code runs without error, give partial credit
        score = 70.0
        passed = True
        feedback = "Code executed successfully."

    # Publish grade event
    try:
        requests.post(
            f"{DAPR_BASE_URL}/v1.0/publish/pubsub/learning.events",
            json={
                "type": "exercise_completed",
                "user_id": request.user_id,
                "exercise_id": exercise_id,
                "score": score,
                "module_id": exercise.module_id if exercise else "mod-1",
            },
        )
    except Exception:
        pass

    return GradeResponse(passed=passed, score=score, feedback=feedback)


@app.post("/api/exercises/generate", response_model=List[Exercise])
async def generate_exercises(request: GenerateRequest):
    """AI-generated exercises for a given topic."""
    try:
        prompt = f"""Generate {request.count} Python coding exercises about "{request.topic}" at {request.difficulty} level.

For each exercise return a JSON object with:
- "title": short title
- "description": clear problem statement
- "starter_code": template code for the student
- "expected_output": what the correct solution should print
- "hints": array of 2 hints

Return a JSON object with key "exercises" containing the array."""

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are a Python exercise generator. Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        result = json.loads(content) if content else {}
        exercises_data = result.get("exercises", [])

        exercises = []
        for ex in exercises_data[:request.count]:
            exercises.append(Exercise(
                id=str(uuid.uuid4()),
                title=ex.get("title", "Untitled"),
                description=ex.get("description", ""),
                difficulty=request.difficulty,
                topic=request.topic,
                starter_code=ex.get("starter_code", ""),
                expected_output=ex.get("expected_output", ""),
                hints=ex.get("hints", []),
            ))

        return exercises

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quizzes/generate", response_model=Quiz)
async def generate_quiz(request: QuizGenerateRequest):
    """Generate a quiz for a module/topic."""
    try:
        prompt = f"""Generate a Python quiz with {request.num_questions} multiple-choice questions about "{request.topic}" (module: {request.module_id}).

For each question return:
- "question": the question text
- "options": array of 4 answer options
- "correct_answer": index (0-3) of the correct option
- "explanation": why the correct answer is right

Return a JSON object with key "questions" containing the array."""

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are a Python quiz generator. Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        result = json.loads(content) if content else {}
        questions_data = result.get("questions", [])

        quiz_id = str(uuid.uuid4())
        questions = []
        for i, q in enumerate(questions_data[:request.num_questions]):
            questions.append(QuizQuestion(
                id=f"{quiz_id}-q{i}",
                question=q.get("question", ""),
                options=q.get("options", ["A", "B", "C", "D"]),
                correct_answer=q.get("correct_answer", 0),
                explanation=q.get("explanation", ""),
            ))

        quiz = Quiz(
            id=quiz_id,
            module_id=request.module_id,
            topic=request.topic,
            questions=questions,
        )
        quizzes[quiz_id] = quiz.model_dump()
        return quiz

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quizzes/{quiz_id}/submit", response_model=QuizResult)
async def submit_quiz(quiz_id: str, request: QuizSubmitRequest):
    """Submit quiz answers and get score."""
    quiz_data = quizzes.get(quiz_id)
    if not quiz_data:
        raise HTTPException(status_code=404, detail="Quiz not found")

    quiz = Quiz(**quiz_data)
    correct = 0
    total = len(quiz.questions)
    results = []

    for q in quiz.questions:
        selected = request.answers.get(q.id, -1)
        is_correct = selected == q.correct_answer
        if is_correct:
            correct += 1
        results.append({
            "question_id": q.id,
            "correct": is_correct,
            "selected": selected,
            "correct_answer": q.correct_answer,
            "explanation": q.explanation,
        })

    percentage = round((correct / total) * 100, 1) if total > 0 else 0

    return QuizResult(
        score=correct,
        total=total,
        percentage=percentage,
        results=results,
    )


@app.post("/events/learning")
async def handle_learning_event(event: dict):
    """Handle learning events."""
    return {"status": "processed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
