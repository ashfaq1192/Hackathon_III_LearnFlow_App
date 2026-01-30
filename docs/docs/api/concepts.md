# Concepts Service API

The Concepts Service provides AI-powered explanations of Python programming concepts.

## Base URL
```
http://concepts-service.learnflow.svc.cluster.local
```

Via Kong Gateway:
```
http://kong-gateway/api/concepts
```

## Endpoints

### Process Request

Get an AI-generated explanation of a concept.

**POST** `/process`

**Request Body:**
```json
{
  "prompt": "Explain list comprehensions in Python with examples",
  "context": {
    "skill_level": "intermediate",
    "preferred_style": "concise"
  }
}
```

**Response:**
```json
{
  "response": "List comprehensions are a concise way to create lists in Python.\n\n**Basic Syntax:**\n```python\n[expression for item in iterable]\n```\n\n**Examples:**\n\n1. Create a list of squares:\n```python\nsquares = [x**2 for x in range(10)]\n# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]\n```\n\n2. Filter with condition:\n```python\nevens = [x for x in range(20) if x % 2 == 0]\n# [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]\n```\n\nList comprehensions are faster than loops and more Pythonic!",
  "tokens_used": 245
}
```

### Health Check

**GET** `/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "concepts-service"
}
```

## Usage Examples

### Common Concept Requests

**Variables and Types:**
```json
{"prompt": "Explain Python variable types and type hints"}
```

**Functions:**
```json
{"prompt": "How do default arguments work in Python functions?"}
```

**Classes:**
```json
{"prompt": "Explain Python class inheritance with a practical example"}
```

**Error Handling:**
```json
{"prompt": "How should I handle exceptions in Python?"}
```

### cURL Example

```bash
curl -X POST http://localhost:8000/api/concepts/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What are decorators in Python?",
    "context": {"skill_level": "intermediate"}
  }'
```
