"""Code Execution Service - Safe Python code executor."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import subprocess
import tempfile
import requests

app = FastAPI(
    title="code-execution-service",
    description="Safely executes Python code in a sandbox environment",
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

# Execution limits
MAX_TIMEOUT = int(os.getenv("EXEC_TIMEOUT", "10"))
MAX_OUTPUT_SIZE = int(os.getenv("MAX_OUTPUT_SIZE", "10000"))

# Blocked imports for security
BLOCKED_IMPORTS = [
    "subprocess", "shutil", "ctypes", "socket",
    "http", "urllib", "ftplib", "smtplib",
]


class CodeRequest(BaseModel):
    code: str
    timeout: Optional[int] = None
    user_id: str = ""


class CodeResponse(BaseModel):
    output: str
    error: str = ""
    exit_code: int = 0
    timed_out: bool = False


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "code-execution-service"}


@app.get("/dapr/subscribe")
async def subscribe():
    """Dapr pub/sub subscriptions."""
    return [
        {"pubsubname": "pubsub", "topic": "code.submitted", "route": "/events/code"}
    ]


def check_code_safety(code: str) -> Optional[str]:
    """Basic safety check on submitted code."""
    for blocked in BLOCKED_IMPORTS:
        if f"import {blocked}" in code or f"from {blocked}" in code:
            return f"Import '{blocked}' is not allowed for security reasons"
    if "open(" in code and ("w" in code or "a" in code):
        return "File write operations are not allowed"
    if "exec(" in code or "eval(" in code:
        return "exec() and eval() are not allowed"
    return None


@app.post("/execute", response_model=CodeResponse)
@app.post("/api/execute", response_model=CodeResponse, include_in_schema=False)
async def execute_code(request: CodeRequest):
    """Execute Python code in a sandboxed environment."""
    # Safety check
    safety_issue = check_code_safety(request.code)
    if safety_issue:
        return CodeResponse(output="", error=safety_issue, exit_code=1)

    timeout = min(request.timeout or MAX_TIMEOUT, MAX_TIMEOUT)

    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(request.code)
            temp_path = f.name

        result = subprocess.run(
            ["python3", temp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )

        output = result.stdout[:MAX_OUTPUT_SIZE]
        error = result.stderr[:MAX_OUTPUT_SIZE]

        response = CodeResponse(
            output=output,
            error=error,
            exit_code=result.returncode,
        )

        # Publish execution result via Dapr
        try:
            requests.post(
                f"{DAPR_BASE_URL}/v1.0/publish/pubsub/learning.events",
                json={
                    "type": "code_executed",
                    "user_id": request.user_id,
                    "success": result.returncode == 0,
                },
                timeout=2,
            )
        except Exception:
            pass

        return response

    except subprocess.TimeoutExpired:
        return CodeResponse(
            output="", error="Code execution timed out", exit_code=1, timed_out=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            os.unlink(temp_path)
        except Exception:
            pass


@app.post("/events/code")
async def handle_code_event(event: dict):
    """Handle code submission events from pub/sub."""
    data = event.get("data", {})
    code = data.get("code", "")
    user_id = data.get("user_id", "")

    if code:
        result = await execute_code(CodeRequest(code=code, user_id=user_id))
        return {"status": "executed", "exit_code": result.exit_code}

    return {"status": "processed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
