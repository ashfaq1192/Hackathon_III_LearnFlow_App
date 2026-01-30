# Triage Service API

The Triage Service analyzes learner code and patterns to detect struggles and provide guidance.

## Base URL
```
http://triage-service.learnflow.svc.cluster.local
```

Via Kong Gateway:
```
http://kong-gateway/api/triage
```

## Endpoints

### Process Request

Analyze code for issues and provide guidance.

**POST** `/process`

**Request Body:**
```json
{
  "prompt": "I'm getting an error with this code",
  "context": {
    "code": "for i in range(10)\n  print(i)",
    "exercise_id": "uuid",
    "attempts": 3
  }
}
```

**Response:**
```json
{
  "response": "I see a syntax error in your code. The `for` loop is missing a colon at the end. It should be:\n\n```python\nfor i in range(10):\n    print(i)\n```\n\nAlso, make sure to use proper indentation (4 spaces).",
  "tokens_used": 156
}
```

**Error Responses:**
- `400` - Invalid request body
- `500` - AI service error
- `503` - Service unavailable

### Health Check

**GET** `/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "triage-service"
}
```

### Dapr Subscription

**GET** `/dapr/subscribe`

Returns pub/sub subscriptions for Dapr sidecar.

**Response:**
```json
[
  {
    "pubsubname": "pubsub",
    "topic": "triage_service",
    "route": "/events"
  }
]
```

### Handle Events

**POST** `/events`

Handles incoming events from Kafka via Dapr.

**Request Body (CloudEvent):**
```json
{
  "specversion": "1.0",
  "type": "learning.event",
  "source": "frontend",
  "id": "uuid",
  "data": {
    "userId": "uuid",
    "eventType": "help.requested",
    "code": "..."
  }
}
```

**Response:**
```json
{
  "status": "processed"
}
```

## Usage Examples

### cURL

```bash
curl -X POST http://localhost:8000/api/triage/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Why is my loop not working?",
    "context": {
      "code": "while True\n  print(x)"
    }
  }'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/triage/process",
    json={
        "prompt": "Help me fix this error",
        "context": {"code": "print(undefined_var)"}
    }
)
print(response.json())
```

### JavaScript

```javascript
const response = await fetch('/api/triage/process', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: "What's wrong with my code?",
    context: { code: "if x = 5:" }
  })
});
const data = await response.json();
```
