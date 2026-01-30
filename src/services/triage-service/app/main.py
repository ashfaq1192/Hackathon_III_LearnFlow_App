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

SYSTEM_PROMPT = """You are the Triage Agent for LearnFlow, an AI-powered Python learning platform.
Your role is to analyze student questions and struggles, then route them to the appropriate service:
- If the student needs a concept explained -> route to "concepts-service"
- If the student needs a coding exercise -> route to "exercise-service"
- If the student wants to run code -> route to "code-execution-service"

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
async def triage_question(request: TriageRequest):
    """Analyze a student question and route to appropriate service."""
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.question}
            ],
            response_format={"type": "json_object"}
        )

        import json
        result = json.loads(response.choices[0].message.content)

        # Publish triage event via Dapr
        requests.post(
            f"{DAPR_BASE_URL}/v1.0/publish/pubsub/learning.events",
            json={
                "type": "triage",
                "user_id": request.user_id,
                "question": request.question,
                "route_to": result.get("route_to", "concepts-service"),
            }
        )

        return TriageResponse(
            analysis=result.get("analysis", ""),
            route_to=result.get("route_to", "concepts-service"),
            confidence=result.get("confidence", 0.5),
            suggestion=result.get("suggestion", ""),
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
