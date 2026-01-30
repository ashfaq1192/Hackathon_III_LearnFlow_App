"""Concepts Service - AI agent for explaining Python concepts."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests

from openai import OpenAI

app = FastAPI(
    title="concepts-service",
    description="AI agent that explains Python concepts with examples and analogies",
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

SYSTEM_PROMPT = """You are a Python teaching assistant for LearnFlow.
Explain Python concepts clearly with:
1. A simple analogy
2. A clear explanation
3. A practical code example
4. Common mistakes to avoid

Adjust your explanation level based on the student's context.
Keep explanations concise but thorough."""


class ConceptRequest(BaseModel):
    concept: str
    level: str = "beginner"
    user_id: str = ""


class ConceptResponse(BaseModel):
    concept: str
    explanation: str
    code_example: str
    common_mistakes: str


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "concepts-service"}


@app.get("/dapr/subscribe")
async def subscribe():
    """Dapr pub/sub subscriptions."""
    return [
        {"pubsubname": "pubsub", "topic": "learning.events", "route": "/events/learning"}
    ]


@app.post("/explain", response_model=ConceptResponse)
async def explain_concept(request: ConceptRequest):
    """Explain a Python concept using AI."""
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Explain this Python concept for a {request.level} student: {request.concept}"}
            ]
        )

        content = response.choices[0].message.content

        # Publish learning event via Dapr
        requests.post(
            f"{DAPR_BASE_URL}/v1.0/publish/pubsub/learning.events",
            json={
                "type": "concept_explained",
                "user_id": request.user_id,
                "concept": request.concept,
                "level": request.level,
            }
        )

        return ConceptResponse(
            concept=request.concept,
            explanation=content,
            code_example="",
            common_mistakes="",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/events/learning")
async def handle_learning_event(event: dict):
    """Handle learning events from other services."""
    return {"status": "processed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
