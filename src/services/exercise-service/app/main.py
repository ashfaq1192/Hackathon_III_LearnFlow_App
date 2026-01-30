"""FastAPI application with Dapr integration."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI(
    title="exercise-service",
    description="Exercise Service microservice",
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


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "exercise-service"}

@app.get("/dapr/subscribe")
async def subscribe():
    """Dapr pub/sub subscriptions."""
    return [
        {"pubsubname": "pubsub", "topic": "exercise_service", "route": "/events"}
    ]


from typing import List, Optional

class Item(BaseModel):
    id: Optional[str] = None
    name: str
    data: dict = {}

@app.post("/items")
async def create_item(item: Item):
    """Create new item with Dapr state store."""
    import requests
    import uuid

    item_id = str(uuid.uuid4())
    item.id = item_id

    # Save to Dapr state store
    response = requests.post(
        f"{DAPR_BASE_URL}/v1.0/state/statestore",
        json=[{"key": item_id, "value": item.dict()}]
    )

    if response.status_code != 204:
        raise HTTPException(status_code=500, detail="Failed to save item")

    return item

@app.get("/items/{item_id}")
async def get_item(item_id: str):
    """Get item from Dapr state store."""
    import requests

    response = requests.get(f"{DAPR_BASE_URL}/v1.0/state/statestore/{item_id}")

    if response.status_code == 204:
        raise HTTPException(status_code=404, detail="Item not found")

    return response.json()

@app.post("/events")
async def handle_event(event: dict):
    """Handle Dapr pub/sub events."""
    return {"status": "processed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
