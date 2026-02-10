"""Code Review Service - AI agent for reviewing code quality."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import requests

from openai import OpenAI

app = FastAPI(
    title="code-review-service",
    description="AI agent that reviews Python code for correctness, style, efficiency, and readability",
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

SYSTEM_PROMPT = """You are the Code Review Agent for LearnFlow, an AI-powered Python learning platform.
Review the student's Python code and evaluate it on these criteria:
1. Correctness: Does it work as intended?
2. Style: Does it follow PEP 8 conventions?
3. Efficiency: Is it well-optimized?
4. Readability: Is it easy to understand?

Respond with a JSON object containing:
- "score": overall score 0-100
- "correctness": score 0-100 for correctness
- "style": score 0-100 for PEP 8 compliance
- "efficiency": score 0-100 for efficiency
- "readability": score 0-100 for readability
- "suggestions": array of improvement suggestions (max 5)
- "overall_feedback": a brief encouraging summary
"""


class ReviewRequest(BaseModel):
    code: str
    user_id: str = ""
    exercise_id: Optional[str] = None


class ReviewResponse(BaseModel):
    score: int
    correctness: int
    style: int
    efficiency: int
    readability: int
    suggestions: List[str]
    overall_feedback: str


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "code-review-service"}


@app.get("/dapr/subscribe")
async def subscribe():
    return [
        {"pubsubname": "pubsub", "topic": "code.submitted", "route": "/events/code"}
    ]


@app.post("/api/review", response_model=ReviewResponse)
async def review_code(request: ReviewRequest):
    """Review code quality and provide feedback."""
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Review this Python code:\n```python\n{request.code}\n```"},
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        result = json.loads(content) if content else {}

        score = min(100, max(0, int(result.get("score", 50))))
        correctness = min(100, max(0, int(result.get("correctness", 50))))
        style = min(100, max(0, int(result.get("style", 50))))
        efficiency = min(100, max(0, int(result.get("efficiency", 50))))
        readability = min(100, max(0, int(result.get("readability", 50))))
        suggestions = result.get("suggestions", [])
        overall_feedback = result.get("overall_feedback", "Code reviewed successfully.")

        # Publish quality score for mastery tracking
        if request.user_id:
            try:
                requests.post(
                    f"{DAPR_BASE_URL}/v1.0/publish/pubsub/learning.events",
                    json={
                        "type": "code_reviewed",
                        "user_id": request.user_id,
                        "exercise_id": request.exercise_id,
                        "quality_score": score,
                    },
                )
            except Exception:
                pass

        return ReviewResponse(
            score=score,
            correctness=correctness,
            style=style,
            efficiency=efficiency,
            readability=readability,
            suggestions=suggestions if isinstance(suggestions, list) else [str(suggestions)],
            overall_feedback=overall_feedback,
        )

    except json.JSONDecodeError:
        return ReviewResponse(
            score=50,
            correctness=50,
            style=50,
            efficiency=50,
            readability=50,
            suggestions=["Unable to parse AI review. Please try again."],
            overall_feedback="Review could not be completed. Please try again.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/events/code")
async def handle_code_event(event: dict):
    """Handle code submission events for automatic review."""
    data = event.get("data", event)
    code = data.get("code", "")
    user_id = data.get("user_id", "")

    if code:
        await review_code(ReviewRequest(
            code=code,
            user_id=user_id,
            exercise_id=data.get("exercise_id"),
        ))

    return {"status": "processed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
