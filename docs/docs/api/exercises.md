# Exercise Service API

The Exercise Service provides CRUD operations for the exercise library.

## Base URL
```
http://exercise-service.learnflow.svc.cluster.local
```

Via Kong Gateway:
```
http://kong-gateway/api/exercises
```

## Endpoints

### Create Exercise

**POST** `/items`

**Request Body:**
```json
{
  "name": "Hello World",
  "data": {
    "title": "Hello World",
    "description": "Print 'Hello, World!' to the console",
    "difficulty": "easy",
    "starter_code": "# Write your code here\n",
    "solution": "print('Hello, World!')",
    "tests": ["output == 'Hello, World!'"],
    "hints": ["Use the print() function"]
  }
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Hello World",
  "data": {...}
}
```

### Get Exercise

**GET** `/items/{item_id}`

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Hello World",
  "data": {
    "title": "Hello World",
    "description": "Print 'Hello, World!' to the console",
    "difficulty": "easy",
    "starter_code": "# Write your code here\n",
    "solution": "print('Hello, World!')"
  }
}
```

**Error Response (404):**
```json
{
  "detail": "Item not found"
}
```

### Health Check

**GET** `/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "exercise-service"
}
```

## Exercise Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Exercise identifier |
| data.title | string | Yes | Display title |
| data.description | string | Yes | Exercise instructions |
| data.difficulty | enum | Yes | easy, medium, hard |
| data.starter_code | string | No | Initial code template |
| data.solution | string | No | Reference solution |
| data.tests | array | No | Test assertions |
| data.hints | array | No | Progressive hints |

## Usage Examples

### Create an Exercise

```bash
curl -X POST http://localhost:8000/api/exercises/items \
  -H "Content-Type: application/json" \
  -d '{
    "name": "fibonacci",
    "data": {
      "title": "Fibonacci Sequence",
      "description": "Write a function that returns the nth Fibonacci number",
      "difficulty": "medium",
      "starter_code": "def fibonacci(n):\n    # Your code here\n    pass",
      "solution": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
      "tests": ["fibonacci(0) == 0", "fibonacci(1) == 1", "fibonacci(10) == 55"]
    }
  }'
```

### Retrieve an Exercise

```bash
curl http://localhost:8000/api/exercises/items/550e8400-e29b-41d4-a716-446655440000
```
