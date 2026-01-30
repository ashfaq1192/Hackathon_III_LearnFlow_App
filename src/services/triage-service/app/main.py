"""FastAPI application with Dapr integration."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os\nfrom openai import OpenAI

app = FastAPI(
    title="triage-service",
    description="Triage Service microservice",
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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "triage-service"}

@app.get("/dapr/subscribe")
async def subscribe():
    """Dapr pub/sub subscriptions."""
    return [
        {"pubsubname": "pubsub", "topic": "triage_service", "route": "/events"}
    ]


# OpenAI configuration
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class AgentRequest(BaseModel):
    prompt: str
    context: dict = {}

class AgentResponse(BaseModel):
    response: str
    tokens_used: int

@app.post("/process", response_model=AgentResponse)
async def process_request(request: AgentRequest):
    """Process request using AI agent."""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant for {service_name}."},
                {"role": "user", "content": request.prompt}
            ]
        )

        return AgentResponse(
            response=response.choices[0].message.content,
            tokens_used=response.usage.total_tokens
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/events")
async def handle_event(event: dict):
    """Handle Dapr pub/sub events."""
    # Process event with AI if needed
    return {"status": "processed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
