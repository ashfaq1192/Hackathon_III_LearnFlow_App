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
Explain Python concepts clearly. You MUST respond with a JSON object containing exactly these fields:
- "explanation": A clear explanation of the concept with a simple analogy
- "code_example": A practical Python code example demonstrating the concept
- "common_mistakes": Common mistakes to avoid when using this concept

Adjust your explanation level based on the student's context.
Keep explanations concise but thorough. Always respond with valid JSON only."""


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
@app.post("/api/concepts/explain", response_model=ConceptResponse, include_in_schema=False)
async def explain_concept(request: ConceptRequest):
    """Explain a Python concept using AI."""
    try:
        import json as json_lib

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Explain this Python concept for a {request.level} student: {request.concept}"}
            ],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        parsed = json_lib.loads(content)

        def to_str(val, default=""):
            if val is None:
                return default
            if isinstance(val, list):
                return "\n".join(f"- {item}" for item in val)
            return str(val)

        explanation = to_str(parsed.get("explanation"), content)
        code_example = to_str(parsed.get("code_example"))
        common_mistakes = to_str(parsed.get("common_mistakes"))

        # Publish learning event via Dapr
        try:
            requests.post(
                f"{DAPR_BASE_URL}/v1.0/publish/pubsub/learning.events",
                json={
                    "type": "concept_explained",
                    "user_id": request.user_id,
                    "concept": request.concept,
                    "level": request.level,
                }
            )
        except Exception:
            pass

        return ConceptResponse(
            concept=request.concept,
            explanation=explanation,
            code_example=code_example,
            common_mistakes=common_mistakes,
        )
    except json_lib.JSONDecodeError:
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
