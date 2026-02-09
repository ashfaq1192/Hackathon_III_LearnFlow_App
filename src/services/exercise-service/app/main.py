"""Exercise Service - CRUD API for managing coding exercises."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import requests
import uuid

app = FastAPI(
    title="exercise-service",
    description="CRUD API for managing Python coding exercises",
    version="1.0.0"
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


class Exercise(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    difficulty: str = "beginner"
    starter_code: str = ""
    expected_output: str = ""
    hints: List[str] = []


class Submission(BaseModel):
    exercise_id: str
    user_id: str
    code: str


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
    # Dapr state store query for exercises
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
    # Publish code submission via Dapr
    requests.post(
        f"{DAPR_BASE_URL}/v1.0/publish/pubsub/code.submitted",
        json={
            "exercise_id": exercise_id,
            "user_id": submission.user_id,
            "code": submission.code,
        }
    )

    return {"status": "submitted", "exercise_id": exercise_id}


@app.post("/events/learning")
async def handle_learning_event(event: dict):
    """Handle learning events."""
    return {"status": "processed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
