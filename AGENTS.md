# AGENTS.md

**Project**: LearnFlow - AI-Powered Python Learning Platform
**Built By**: AI Agents (Claude Code + Goose) using reusable Skills
**Stack**: FastAPI + Dapr + Kafka + Neon PostgreSQL + Next.js + Monaco Editor + Kong + Better Auth

## Architecture

```
Browser → Kong API Gateway → Microservices (with Dapr sidecars)
                                ├── triage-service          (AI routing)
                                ├── concepts-service        (AI explanations)
                                ├── exercise-service        (CRUD + quizzes + grading)
                                ├── code-execution-service  (sandbox)
                                ├── debug-service           (AI error analysis)
                                ├── code-review-service     (AI code quality review)
                                └── progress-service        (student tracking + curriculum)
                              ↕ Dapr ↕
                    State: Neon PostgreSQL    Pub/Sub: Kafka
```

### Event Flow
1. Student submits question → triage-service analyzes via OpenAI → routes to appropriate service
2. Services publish events to Kafka topics via Dapr pub/sub:
   - `learning.events` - concept explanations, code execution results
   - `code.submitted` - code submissions for execution
   - `struggle.detected` - detected learning difficulties

## Repository Structure

```
learnflow-app/
├── AGENTS.md                           # This file
├── docker-compose.yml                  # Local development
├── .env.example                        # Environment template
├── scripts/
│   ├── create-k8s-secrets.sh           # K8s secrets setup
│   └── deploy.sh                       # Full K8s deployment
├── .claude/skills/                     # Reusable skills (both agents)
├── src/
│   ├── frontend/                       # Next.js 14 + Monaco Editor
│   │   ├── src/app/                    # Pages (home, login, signup, dashboard, learn, teacher)
│   │   ├── src/components/             # CodeEditor, AIAssistant, ExercisePanel, QuizModal, UserMenu
│   │   ├── lib/auth.ts                 # Better Auth configuration (Neon PostgreSQL)
│   │   ├── lib/auth-client.ts          # Better Auth React client
│   │   └── k8s/deployment.yaml
│   └── services/
│       ├── triage-service/             # Port 8000 | AI question routing
│       ├── concepts-service/           # Port 8000 | AI concept explanations
│       ├── exercise-service/           # Port 8000 | Exercise CRUD + quizzes + auto-grading
│       ├── code-execution-service/     # Port 8000 | Sandboxed Python execution
│       ├── debug-service/              # Port 8000 | AI error analysis and debugging
│       ├── code-review-service/        # Port 8000 | AI code quality review
│       └── progress-service/           # Port 8000 | Student mastery tracking + curriculum
├── k8s/
│   ├── dapr/components.yaml            # State store (PostgreSQL) + Pub/Sub (Kafka)
│   ├── kafka/                          # Strimzi Kafka cluster + topics
│   └── kong/ingress.yaml               # API Gateway routing
└── docs/                               # Docusaurus documentation site
```

## Service Details

| Service | Purpose | AI? | Dapr | Key Endpoints |
|---------|---------|-----|------|---------------|
| triage-service | Routes learner questions to correct service | OpenAI GPT | pub/sub | `POST /api/triage/route`, `POST /events/struggle` |
| concepts-service | Explains Python concepts with examples | OpenAI GPT | pub/sub | `POST /api/concepts/explain`, `POST /events/learning` |
| exercise-service | Exercise CRUD, quizzes, auto-grading | OpenAI GPT | state + pub/sub | `POST /api/exercises`, `GET /api/exercises`, `POST /api/exercises/{id}/submit`, `GET /api/quizzes/generate` |
| code-execution-service | Runs Python code in sandbox | No | pub/sub | `POST /api/execute/run`, `POST /events/code` |
| debug-service | AI-powered error analysis and fix suggestions | OpenAI GPT | pub/sub | `POST /api/debug/analyze`, `POST /events/debug` |
| code-review-service | AI code quality review and feedback | OpenAI GPT | pub/sub | `POST /api/review/analyze`, `POST /events/review` |
| progress-service | Student mastery tracking and curriculum | OpenAI GPT | state + pub/sub | `GET /api/progress/{user}`, `GET /api/curriculum/modules`, `POST /events/progress` |

All services expose `GET /health` and `GET /dapr/subscribe`.

## Conventions for AI Agents

### Code Style
- **Python**: FastAPI with Pydantic models, async endpoints, type hints
- **TypeScript**: Next.js App Router, React functional components, Tailwind CSS
- **Naming**: kebab-case for services/files, camelCase for TypeScript, snake_case for Python

### Dapr Integration Pattern
```python
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"

# Publish event
requests.post(f"{DAPR_BASE_URL}/v1.0/publish/pubsub/{topic}", json=data)

# Save state
requests.post(f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE}", json=[{"key": k, "value": v}])
```

### Kubernetes
- All services deploy to `learnflow` namespace
- Kafka deploys to `kafka` namespace
- Images use `IfNotPresent` pull policy (built locally with `eval $(minikube docker-env)`)
- All deployments include liveness/readiness probes on `/health`
- Resource limits: 256Mi-512Mi memory, 100m-500m CPU

### Testing
- pytest with FastAPI TestClient
- Mock OpenAI client and Dapr HTTP calls
- Tests in `services/{name}/tests/test_main.py`

## Skills Available

Skills in `.claude/skills/` can be used by both Claude Code and Goose:

| Skill | Purpose |
|-------|---------|
| agents-md-gen | Generate this AGENTS.md file |
| k8s-foundation | Kubernetes cluster health checks |
| kafka-k8s-setup | Deploy Kafka with Strimzi operator |
| neon-postgres-setup | Configure Neon PostgreSQL schemas |
| dapr-setup | Install Dapr runtime on K8s |
| fastapi-dapr-agent | Generate FastAPI microservices |
| mcp-code-execution | MCP Code Execution pattern |
| nextjs-k8s-deploy | Deploy Next.js to K8s |
| better-auth-setup | Configure Better Auth |
| kong-gateway-setup | Deploy Kong API Gateway |
| docusaurus-deploy | Deploy documentation site |

## Deployment

### Live (GKE)
**URL: http://35.222.110.147**

Deployed on GKE Standard cluster (`us-central1`) with Kong LoadBalancer ingress.

```bash
source .env
./k8s/deploy-gke.sh        # Full deployment
./k8s/verify-gke.sh        # Verification
```

### Local (Docker Compose)
```bash
cp .env.example .env  # Fill in OPENAI_API_KEY, DATABASE_URL, AUTH_SECRET
docker compose up
```

### Kubernetes (Minikube)
```bash
minikube start --cpus=4 --memory=8192 --driver=docker
source .env
./scripts/create-k8s-secrets.sh
./scripts/deploy.sh
```

---
*This application was built entirely by AI agents using reusable skills from the skills-library repository.*
