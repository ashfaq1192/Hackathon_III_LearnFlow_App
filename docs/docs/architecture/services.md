# Microservices

LearnFlow consists of 4 backend microservices plus a frontend application.

## Service Overview

| Service | Type | Purpose | AI Integration |
|---------|------|---------|----------------|
| triage-service | AI Agent | Analyzes learner struggles | GPT-4 |
| concepts-service | AI Agent | Explains Python concepts | GPT-4 |
| exercise-service | CRUD API | Manages exercise library | None |
| code-execution-service | Executor | Runs Python code safely | None |

## Triage Service

Analyzes student code and learning patterns to detect struggles.

**Endpoints:**
- `POST /process` - Analyze code for issues
- `POST /events` - Handle learning events
- `GET /health` - Health check

**AI Prompt Template:**
```
You are a Python learning assistant. Analyze this code for:
1. Syntax errors
2. Logic issues
3. Best practice violations
4. Potential confusion points

Code: {code}
Context: {context}
```

## Concepts Service

Provides on-demand explanations of Python concepts.

**Endpoints:**
- `POST /process` - Explain a concept
- `POST /events` - Handle concept requests
- `GET /health` - Health check

**Example Request:**
```json
{
  "prompt": "Explain list comprehensions in Python",
  "context": {
    "skill_level": "intermediate"
  }
}
```

## Exercise Service

CRUD operations for the exercise library.

**Endpoints:**
- `GET /items` - List all exercises
- `GET /items/{id}` - Get exercise by ID
- `POST /items` - Create exercise
- `PUT /items/{id}` - Update exercise
- `DELETE /items/{id}` - Delete exercise

**Exercise Schema:**
```json
{
  "id": "uuid",
  "title": "Hello World",
  "description": "Print Hello World",
  "difficulty": "easy",
  "starter_code": "# Your code here",
  "solution": "print('Hello, World!')",
  "tests": ["output == 'Hello, World!'"]
}
```

## Code Execution Service

Safely executes Python code in a sandboxed environment.

**Endpoints:**
- `POST /execute` - Execute Python code
- `GET /health` - Health check

**Security Measures:**
- Timeout limits (10 seconds max)
- Memory limits (128MB max)
- Network isolation
- Filesystem restrictions
- Blocked imports (os, subprocess, etc.)

**Request:**
```json
{
  "code": "print('Hello')",
  "timeout": 5
}
```

**Response:**
```json
{
  "output": "Hello\n",
  "error": null,
  "execution_time_ms": 42
}
```

## Dapr Integration

All services use Dapr sidecars for:

### State Management
```python
# Save state
requests.post(
    f"{DAPR_BASE_URL}/v1.0/state/statestore",
    json=[{"key": item_id, "value": data}]
)

# Get state
response = requests.get(
    f"{DAPR_BASE_URL}/v1.0/state/statestore/{item_id}"
)
```

### Pub/Sub
```python
# Publish event
requests.post(
    f"{DAPR_BASE_URL}/v1.0/publish/pubsub/learning.events",
    json={"eventType": "code.submitted", "data": {...}}
)

# Subscribe (in FastAPI app)
@app.get("/dapr/subscribe")
async def subscribe():
    return [{"pubsubname": "pubsub", "topic": "learning.events", "route": "/events"}]
```

### Service Invocation
```python
# Call another service
response = requests.get(
    f"{DAPR_BASE_URL}/v1.0/invoke/concepts-service/method/health"
)
```
