# Code Execution Service API

The Code Execution Service safely runs Python code in a sandboxed environment.

## Base URL
```
http://code-execution-service.learnflow.svc.cluster.local
```

Via Kong Gateway:
```
http://kong-gateway/api/execute
```

## Endpoints

### Execute Code

**POST** `/items`

Execute Python code and return the output.

**Request Body:**
```json
{
  "name": "execution-request",
  "data": {
    "code": "print('Hello, World!')",
    "timeout": 5
  }
}
```

**Successful Response:**
```json
{
  "id": "execution-id",
  "name": "execution-request",
  "data": {
    "output": "Hello, World!\n",
    "error": null,
    "execution_time_ms": 42
  }
}
```

**Error Response (Runtime Error):**
```json
{
  "id": "execution-id",
  "name": "execution-request",
  "data": {
    "output": "",
    "error": "NameError: name 'undefined_var' is not defined",
    "execution_time_ms": 15
  }
}
```

**Error Response (Timeout):**
```json
{
  "detail": "Execution timed out after 5 seconds"
}
```

### Health Check

**GET** `/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "code-execution-service"
}
```

## Security Restrictions

The sandbox environment enforces the following restrictions:

### Blocked Imports
```python
# These modules are blocked
import os          # ❌
import subprocess  # ❌
import sys         # ❌ (limited)
import socket      # ❌
import requests    # ❌
```

### Resource Limits
| Resource | Limit |
|----------|-------|
| Execution time | 10 seconds |
| Memory | 128 MB |
| Output size | 1 MB |
| File system | Read-only |
| Network | Disabled |

### Allowed Operations
```python
# Safe operations allowed
print("output")           # ✅
x = [1, 2, 3]            # ✅
def my_function():       # ✅
    pass
import math              # ✅
import json              # ✅
import collections       # ✅
```

## Usage Examples

### Basic Execution

```bash
curl -X POST http://localhost:8000/api/execute/items \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test",
    "data": {
      "code": "for i in range(5):\n    print(i)"
    }
  }'
```

**Output:**
```json
{
  "data": {
    "output": "0\n1\n2\n3\n4\n",
    "error": null
  }
}
```

### With User Input Simulation

```bash
curl -X POST http://localhost:8000/api/execute/items \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test",
    "data": {
      "code": "name = \"Alice\"\nprint(f\"Hello, {name}!\")"
    }
  }'
```

### Testing a Function

```bash
curl -X POST http://localhost:8000/api/execute/items \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test",
    "data": {
      "code": "def add(a, b):\n    return a + b\n\nprint(add(2, 3))\nprint(add(10, 20))"
    }
  }'
```

## Error Handling

### Syntax Errors
```python
# Code with syntax error
for i in range(10)  # Missing colon
    print(i)
```
**Response:**
```json
{
  "data": {
    "output": "",
    "error": "SyntaxError: expected ':' (line 1)"
  }
}
```

### Runtime Errors
```python
# Code with runtime error
x = 1 / 0
```
**Response:**
```json
{
  "data": {
    "output": "",
    "error": "ZeroDivisionError: division by zero"
  }
}
```
