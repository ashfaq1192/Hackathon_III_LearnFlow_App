"""Progress Service - Tracks student mastery, progress, and curriculum data."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import requests
import time

from openai import OpenAI
from app.curriculum import get_all_modules, get_module

app = FastAPI(
    title="progress-service",
    description="Tracks student mastery and progress across the Python curriculum",
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

# OpenAI configuration
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# In-memory storage for local dev (Dapr state store for K8s)
user_progress: Dict[str, dict] = {}
struggle_alerts: List[dict] = []

MASTERY_LEVELS = {
    "beginner": (0, 40),
    "learning": (41, 70),
    "proficient": (71, 90),
    "mastered": (91, 100),
}


class RecordActivity(BaseModel):
    activity_type: str  # exercise_completed, quiz_taken, code_executed
    module_id: str
    score: float = 0.0
    details: dict = {}


class StruggleEvent(BaseModel):
    user_id: str
    struggle_type: str
    module_id: str = ""
    details: dict = {}


def get_mastery_level(score: float) -> str:
    for level, (low, high) in MASTERY_LEVELS.items():
        if low <= score <= high:
            return level
    return "beginner"


def init_user_progress(user_id: str) -> dict:
    modules = get_all_modules()
    return {
        "user_id": user_id,
        "modules": {
            m["id"]: {
                "module_id": m["id"],
                "module_name": m["name"],
                "exercise_score": 0.0,
                "quiz_score": 0.0,
                "code_quality": 0.0,
                "streak_bonus": 0.0,
                "mastery": 0.0,
                "mastery_level": "beginner",
                "exercises_completed": 0,
                "quizzes_taken": 0,
            }
            for m in modules
        },
        "streak": 0,
        "last_activity": None,
        "total_exercises": 0,
        "total_quizzes": 0,
    }


def calculate_mastery(module_data: dict) -> float:
    return round(
        0.4 * module_data["exercise_score"]
        + 0.3 * module_data["quiz_score"]
        + 0.2 * module_data["code_quality"]
        + 0.1 * module_data["streak_bonus"],
        1,
    )


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "progress-service"}


@app.get("/dapr/subscribe")
async def subscribe():
    return [
        {"pubsubname": "pubsub", "topic": "learning.events", "route": "/events/learning"},
        {"pubsubname": "pubsub", "topic": "code.submitted", "route": "/events/code"},
    ]


@app.get("/api/curriculum")
async def list_curriculum():
    return get_all_modules()


@app.get("/api/curriculum/{module_id}")
async def get_curriculum_module(module_id: str):
    module = get_module(module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module


@app.get("/api/progress/struggles")
async def get_all_struggles():
    return [s for s in struggle_alerts if not s["resolved"]]


@app.get("/api/progress/struggles/{user_id}")
async def get_user_struggles(user_id: str):
    return [s for s in struggle_alerts if s["user_id"] == user_id and not s["resolved"]]


@app.get("/api/progress/{user_id}")
async def get_progress(user_id: str):
    if user_id not in user_progress:
        user_progress[user_id] = init_user_progress(user_id)
    return user_progress[user_id]


@app.post("/api/progress/{user_id}/record")
async def record_activity(user_id: str, activity: RecordActivity):
    if user_id not in user_progress:
        user_progress[user_id] = init_user_progress(user_id)

    progress = user_progress[user_id]
    mod = progress["modules"].get(activity.module_id)
    if not mod:
        raise HTTPException(status_code=404, detail="Module not found")

    now = time.time()

    if activity.activity_type == "exercise_completed":
        mod["exercises_completed"] += 1
        progress["total_exercises"] += 1
        # Running average
        n = mod["exercises_completed"]
        mod["exercise_score"] = round(((n - 1) * mod["exercise_score"] + activity.score) / n, 1)

    elif activity.activity_type == "quiz_taken":
        mod["quizzes_taken"] += 1
        progress["total_quizzes"] += 1
        n = mod["quizzes_taken"]
        mod["quiz_score"] = round(((n - 1) * mod["quiz_score"] + activity.score) / n, 1)

        # Struggle detection: quiz score < 50%
        if activity.score < 50:
            _add_struggle(user_id, "low_quiz_score", activity.module_id, {
                "score": activity.score
            })

    elif activity.activity_type == "code_executed":
        code_quality = activity.details.get("quality_score", 0)
        if code_quality > 0:
            mod["code_quality"] = round((mod["code_quality"] + code_quality) / 2, 1) if mod["code_quality"] > 0 else code_quality

    # Update streak
    last = progress.get("last_activity")
    if last and (now - last) < 86400:  # within 24 hours
        progress["streak"] += 1
    elif not last or (now - last) >= 172800:  # gap > 48 hours
        progress["streak"] = 1
    mod["streak_bonus"] = min(progress["streak"] * 5, 100)

    progress["last_activity"] = now

    # Recalculate mastery
    mod["mastery"] = calculate_mastery(mod)
    mod["mastery_level"] = get_mastery_level(mod["mastery"])

    # Publish progress event
    try:
        requests.post(
            f"{DAPR_BASE_URL}/v1.0/publish/pubsub/learning.events",
            json={
                "type": "progress_updated",
                "user_id": user_id,
                "module_id": activity.module_id,
                "mastery": mod["mastery"],
                "mastery_level": mod["mastery_level"],
            }
        )
    except Exception:
        pass

    return {"status": "recorded", "mastery": mod["mastery"], "mastery_level": mod["mastery_level"]}


@app.get("/api/progress/{user_id}/mastery/{module_id}")
async def get_mastery(user_id: str, module_id: str):
    if user_id not in user_progress:
        user_progress[user_id] = init_user_progress(user_id)
    mod = user_progress[user_id]["modules"].get(module_id)
    if not mod:
        raise HTTPException(status_code=404, detail="Module not found")
    return mod


def _add_struggle(user_id: str, struggle_type: str, module_id: str, details: dict):
    alert = {
        "user_id": user_id,
        "struggle_type": struggle_type,
        "module_id": module_id,
        "details": details,
        "timestamp": time.time(),
        "resolved": False,
    }
    struggle_alerts.append(alert)
    # Publish struggle event
    try:
        requests.post(
            f"{DAPR_BASE_URL}/v1.0/publish/pubsub/struggle.detected",
            json=alert,
        )
    except Exception:
        pass


@app.post("/events/learning")
async def handle_learning_event(event: dict):
    data = event.get("data", event)
    user_id = data.get("user_id", "")
    event_type = data.get("type", "")

    if user_id and event_type == "exercise_completed":
        activity = RecordActivity(
            activity_type="exercise_completed",
            module_id=data.get("module_id", "mod-1"),
            score=data.get("score", 0),
        )
        await record_activity(user_id, activity)

    return {"status": "processed"}


@app.post("/events/code")
async def handle_code_event(event: dict):
    data = event.get("data", event)
    user_id = data.get("user_id", "")
    if user_id:
        # Track failed executions for struggle detection
        if data.get("status") == "error":
            progress = user_progress.get(user_id, {})
            fails = progress.get("_consecutive_failures", 0) + 1
            if user_id not in user_progress:
                user_progress[user_id] = init_user_progress(user_id)
            user_progress[user_id]["_consecutive_failures"] = fails
            if fails >= 5:
                _add_struggle(user_id, "repeated_failures", data.get("module_id", ""), {
                    "consecutive_failures": fails,
                })
                user_progress[user_id]["_consecutive_failures"] = 0
        else:
            if user_id in user_progress:
                user_progress[user_id]["_consecutive_failures"] = 0

    return {"status": "processed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
