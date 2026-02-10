"""Triage Service - AI agent for analyzing learner struggles."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests

from openai import OpenAI

app = FastAPI(
    title="triage-service",
    description="AI agent that analyzes learner struggles and routes to appropriate services",
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

# OpenAI configuration
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

STRUGGLE_KEYWORDS = [
    "i don't understand", "i'm stuck", "help me", "confused",
    "i can't figure", "what am i doing wrong", "doesn't make sense",
    "i'm lost", "too hard", "give up",
]

SYSTEM_PROMPT = """You are the Triage Agent for LearnFlow, an AI-powered Python learning platform.
Your role is to analyze student questions and struggles, then route them to the appropriate service:
- If the student needs a concept explained -> route to "concepts-service"
- If the student needs a coding exercise -> route to "exercise-service"
- If the student wants to run code -> route to "code-execution-service"
- If the student has a code error or bug -> route to "debug-service"
- If the student wants code feedback or review -> route to "code-review-service"
- If the student asks about their progress or mastery -> route to "progress-service"

Respond with a JSON object containing:
- "analysis": brief analysis of the student's need
- "route_to": the service name to route to
- "confidence": confidence score 0-1
- "suggestion": a helpful suggestion for the student
"""


class TriageRequest(BaseModel):
    question: str
    user_id: str = ""
    context: dict = {}


class TriageResponse(BaseModel):
    analysis: str
    route_to: str
    confidence: float
    suggestion: str


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "triage-service"}


@app.get("/dapr/subscribe")
async def subscribe():
    """Dapr pub/sub subscriptions."""
    return [
        {"pubsubname": "pubsub", "topic": "struggle.detected", "route": "/events/struggle"}
    ]


@app.post("/triage", response_model=TriageResponse)
@app.post("/api/triage", response_model=TriageResponse, include_in_schema=False)
async def triage_question(request: TriageRequest):
    """Analyze a student question and route to appropriate service."""
    # Detect struggle keywords
    question_lower = request.question.lower()
    is_struggling = any(kw in question_lower for kw in STRUGGLE_KEYWORDS)

    if is_struggling and request.user_id:
        try:
            requests.post(
                f"{DAPR_BASE_URL}/v1.0/publish/pubsub/struggle.detected",
                json={
                    "user_id": request.user_id,
                    "struggle_type": "verbal_expression",
                    "details": {"message": request.question},
                },
            )
        except Exception:
            pass

    try:
        import json

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.question}
            ],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        result = json.loads(content) if content else {}

        analysis = result.get("analysis") or "Your question has been received."
        route_to = result.get("route_to") or "concepts-service"
        raw_confidence = result.get("confidence")
        try:
            confidence = float(raw_confidence) if raw_confidence is not None else 0.5
        except (TypeError, ValueError):
            confidence = 0.5
        confidence = max(0.0, min(1.0, confidence))
        suggestion = result.get("suggestion") or "Try asking a specific Python question to get started!"

        # Publish triage event via Dapr
        try:
            requests.post(
                f"{DAPR_BASE_URL}/v1.0/publish/pubsub/learning.events",
                json={
                    "type": "triage",
                    "user_id": request.user_id,
                    "question": request.question,
                    "route_to": route_to,
                }
            )
        except Exception:
            pass

        return TriageResponse(
            analysis=analysis,
            route_to=route_to,
            confidence=confidence,
            suggestion=suggestion,
        )
    except json.JSONDecodeError:
        return TriageResponse(
            analysis="Your question has been received.",
            route_to="concepts-service",
            confidence=0.5,
            suggestion="Try asking a specific Python question to get started!",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/events/struggle")
async def handle_struggle_event(event: dict):
    """Handle struggle detection events from other services."""
    data = event.get("data", {})
    user_id = data.get("user_id", "")
    struggle_type = data.get("struggle_type", "unknown")

    # Auto-triage the struggle
    try:
        triage_result = await triage_question(TriageRequest(
            question=f"Student is struggling with: {struggle_type}",
            user_id=user_id,
        ))
        return {"status": "processed", "routed_to": triage_result.route_to}
    except Exception:
        return {"status": "processed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
