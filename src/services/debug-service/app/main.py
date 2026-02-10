"""Debug Service - AI agent for analyzing code errors and providing hints."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import os
import json
import requests
import time

from openai import OpenAI

app = FastAPI(
    title="debug-service",
    description="AI agent that analyzes code errors, identifies root causes, and provides progressive hints",
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

# Track error counts per user for struggle detection
error_tracker: Dict[str, Dict[str, int]] = {}

SYSTEM_PROMPT = """You are the Debug Agent for LearnFlow, an AI-powered Python learning platform.
Analyze the student's code and error message to:
1. Identify the error type (SyntaxError, TypeError, NameError, etc.)
2. Determine the root cause
3. Provide progressive hints (from subtle to explicit)
4. Provide the corrected solution with explanation

Respond with a JSON object containing:
- "error_type": the Python error type
- "root_cause": clear explanation of why the error occurs
- "hints": array of 3 hints, from vague to specific
- "solution": the corrected code
- "explanation": why the fix works
"""


class DebugRequest(BaseModel):
    code: str
    error_message: str = ""
    user_id: str = ""


class DebugResponse(BaseModel):
    error_type: str
    root_cause: str
    hints: List[str]
    solution: str
    explanation: str


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "debug-service"}


@app.get("/dapr/subscribe")
async def subscribe():
    return [
        {"pubsubname": "pubsub", "topic": "code.submitted", "route": "/events/code"}
    ]


@app.post("/api/debug/analyze", response_model=DebugResponse)
async def analyze_error(request: DebugRequest):
    """Analyze a code error and provide progressive hints."""
    try:
        user_msg = f"Code:\n```python\n{request.code}\n```\n"
        if request.error_message:
            user_msg += f"\nError:\n{request.error_message}"

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        result = json.loads(content) if content else {}

        error_type = result.get("error_type", "Unknown")
        root_cause = result.get("root_cause", "Unable to determine root cause")
        hints = result.get("hints", ["Check your syntax", "Review the error message", "See the solution"])
        solution = result.get("solution", "")
        explanation = result.get("explanation", "")

        # Track errors for struggle detection
        if request.user_id:
            _track_error(request.user_id, error_type)

        # Publish debug event
        try:
            requests.post(
                f"{DAPR_BASE_URL}/v1.0/publish/pubsub/learning.events",
                json={
                    "type": "debug_analysis",
                    "user_id": request.user_id,
                    "error_type": error_type,
                },
            )
        except Exception:
            pass

        return DebugResponse(
            error_type=error_type,
            root_cause=root_cause,
            hints=hints if isinstance(hints, list) else [str(hints)],
            solution=solution,
            explanation=explanation,
        )

    except json.JSONDecodeError:
        return DebugResponse(
            error_type="Unknown",
            root_cause="Unable to parse AI response",
            hints=["Check your syntax carefully", "Review the error message", "Try simplifying your code"],
            solution="",
            explanation="The AI analysis could not be parsed. Please try again.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _track_error(user_id: str, error_type: str):
    """Track error counts and trigger struggle detection."""
    if user_id not in error_tracker:
        error_tracker[user_id] = {}

    tracker = error_tracker[user_id]
    tracker[error_type] = tracker.get(error_type, 0) + 1

    # Struggle trigger: same error 3+ times
    if tracker[error_type] >= 3:
        try:
            requests.post(
                f"{DAPR_BASE_URL}/v1.0/publish/pubsub/struggle.detected",
                json={
                    "user_id": user_id,
                    "struggle_type": "repeated_error",
                    "details": {
                        "error_type": error_type,
                        "count": tracker[error_type],
                    },
                    "timestamp": time.time(),
                },
            )
        except Exception:
            pass
        # Reset counter after alerting
        tracker[error_type] = 0


@app.post("/events/code")
async def handle_code_event(event: dict):
    """Handle code submission events for automatic error analysis."""
    data = event.get("data", event)
    code = data.get("code", "")
    error = data.get("error", "")
    user_id = data.get("user_id", "")

    if error and code:
        await analyze_error(DebugRequest(
            code=code,
            error_message=error,
            user_id=user_id,
        ))

    return {"status": "processed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
