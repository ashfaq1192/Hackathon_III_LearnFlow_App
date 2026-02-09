# LearnFlow

AI-Powered Python Learning Platform built entirely by AI agents using reusable Skills.

## What is LearnFlow?

LearnFlow is a cloud-native, event-driven platform for learning Python. Students write code in a Monaco Editor, get AI-powered explanations, and receive personalized exercise recommendations - all powered by microservices communicating through Kafka and Dapr.

## Architecture

```
Browser → Kong API Gateway → Microservices (with Dapr sidecars)
                                ├── triage-service      (AI routing via OpenAI)
                                ├── concepts-service    (AI explanations via OpenAI)
                                ├── exercise-service    (CRUD + Dapr state store)
                                └── code-execution-service (sandboxed Python)
                              ↕ Dapr ↕
                    State: Neon PostgreSQL    Pub/Sub: Kafka
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 14 + Monaco Editor + Better Auth |
| Backend | FastAPI + OpenAI SDK |
| Service Mesh | Dapr (state management, pub/sub) |
| Messaging | Apache Kafka on Kubernetes (Strimzi) |
| Database | Neon PostgreSQL |
| API Gateway | Kong on Kubernetes |
| Orchestration | Kubernetes (Minikube) |
| Documentation | Docusaurus |

## Quick Start

### Prerequisites

- Docker
- Minikube (`minikube start --cpus=4 --memory=8192 --driver=docker`)
- kubectl
- Helm

### Local Development (Docker Compose)

```bash
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and DATABASE_URL
docker compose up
```

### Kubernetes Deployment

```bash
# 1. Create secrets
export OPENAI_API_KEY="sk-..."
export DATABASE_URL="postgresql://..."
./scripts/create-k8s-secrets.sh

# 2. Deploy everything
./scripts/deploy.sh

# 3. Access the app
kubectl port-forward -n learnflow svc/learnflow-frontend 3000:80
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| triage-service | 8000 | Analyzes student questions via OpenAI and routes to the correct service |
| concepts-service | 8000 | Explains Python concepts with examples and analogies using AI |
| exercise-service | 8000 | CRUD API for coding exercises with Dapr state management |
| code-execution-service | 8000 | Executes Python code in a sandboxed environment with security checks |
| frontend | 3000 | Next.js app with Monaco Editor, AI chat, and exercise browser |

## Testing

```bash
# Run all service tests
OPENAI_API_KEY=test-key pytest src/services/triage-service/tests/ -v
OPENAI_API_KEY=test-key pytest src/services/concepts-service/tests/ -v
pytest src/services/exercise-service/tests/ -v
pytest src/services/code-execution-service/tests/ -v
```

## Built With Skills

This application was built entirely by AI agents (Claude Code and Goose) using reusable skills from the skills-library. See [AGENTS.md](AGENTS.md) for details on available skills and conventions.

## License

Built for Hackathon III - Reusable Intelligence and Cloud-Native Mastery.
