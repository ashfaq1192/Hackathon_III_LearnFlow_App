# Contributing

Thank you for your interest in contributing to LearnFlow!

## Development Setup

### Prerequisites

1. Fork and clone the repository
2. Install dependencies (see [Installation](/docs/getting-started/installation))
3. Start Minikube cluster
4. Deploy infrastructure

### Local Development

**Backend Services:**
```bash
cd src/services/triage-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd src/frontend
npm install
npm run dev
```

## Code Style

### Python (Backend)

- Use `black` for formatting
- Type hints required
- Async for I/O operations
- Pydantic for validation

```python
from pydantic import BaseModel

class RequestModel(BaseModel):
    prompt: str
    context: dict = {}

async def process(request: RequestModel) -> dict:
    """Process the request."""
    return {"status": "ok"}
```

### TypeScript (Frontend)

- Use Prettier for formatting
- Strict mode enabled
- Server components by default

```typescript
interface Props {
  code: string;
  onChange: (code: string) => void;
}

export default function CodeEditor({ code, onChange }: Props) {
  return <Editor value={code} onChange={onChange} />;
}
```

## Git Workflow

### Branch Naming
- `feat/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code refactoring

### Commit Messages

```
<type>: <description>

Claude: <skill used if applicable>

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

**Types:** feat, fix, docs, refactor, test, chore

### Example
```
feat: add exercise validation endpoint

Claude: Extended exercise-service using fastapi-dapr-agent skill
- Added validation endpoint for code submissions
- Integrated with code-execution-service

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

## Pull Request Process

1. Create a feature branch
2. Make your changes
3. Run tests locally
4. Create PR with description
5. Wait for review
6. Address feedback
7. Merge when approved

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
```

## Testing

### Unit Tests
```bash
cd src/services/triage-service
pytest tests/
```

### Integration Tests
```bash
# With Dapr sidecar
dapr run --app-id test-service --app-port 8000 -- pytest tests/integration/
```

### End-to-End Tests
```bash
# Requires full deployment
npm run test:e2e
```

## Documentation

- Update docs in `docs/docs/`
- API changes require API doc updates
- Architecture changes require diagram updates
- New features need getting started updates

## Getting Help

- GitHub Issues for bugs
- Discussions for questions
- Discord for real-time chat
