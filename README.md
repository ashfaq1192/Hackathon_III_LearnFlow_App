# LearnFlow

AI-Powered Python Learning Platform built entirely by AI agents using reusable Skills.

**Live Demo: [http://35.222.110.147](http://35.222.110.147)**

## What is LearnFlow?

LearnFlow is a cloud-native, event-driven platform for learning Python. Students write code in a Monaco Editor, get AI-powered explanations, debugging help, code reviews, and personalized exercise recommendations - all powered by 7 microservices communicating through Kafka and Dapr, deployed on Google Kubernetes Engine (GKE).

## Architecture

```
Browser → Kong API Gateway (LoadBalancer) → Microservices (with Dapr sidecars)
                                              ├── triage-service          (AI question routing)
                                              ├── concepts-service        (AI explanations)
                                              ├── exercise-service        (exercises + quizzes)
                                              ├── code-execution-service  (sandboxed Python)
                                              ├── debug-service           (AI error analysis)
                                              ├── code-review-service     (AI code quality)
                                              └── progress-service        (mastery tracking)
                                            ↕ Dapr ↕
                                  State: Neon PostgreSQL    Pub/Sub: Kafka
```

### Event Flow
1. Student submits a question → **triage-service** analyzes via OpenAI → routes to the correct service
2. Services publish events to Kafka topics via Dapr pub/sub:
   - `learning.events` - concept explanations, progress updates
   - `code.submitted` - code submissions for execution and review
   - `struggle.detected` - detected learning difficulties

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 14 + Monaco Editor + Better Auth |
| Backend | FastAPI + OpenAI SDK (7 microservices) |
| Service Mesh | Dapr (state management, pub/sub, service invocation) |
| Messaging | Apache Kafka on Kubernetes (Strimzi + KRaft) |
| Database | Neon PostgreSQL |
| API Gateway | Kong Ingress Controller on Kubernetes |
| Auth | Better Auth (email/password + role-based) |
| Orchestration | Google Kubernetes Engine (GKE) |
| Documentation | Docusaurus |

## Live Deployment

The application is deployed on **GKE Standard** cluster in `us-central1`:

| Component | URL |
|-----------|-----|
| Frontend | [http://35.222.110.147](http://35.222.110.147) |
| API Gateway | http://35.222.110.147/api/* |
| Triage API | `POST http://35.222.110.147/api/triage` |
| Concepts API | `POST http://35.222.110.147/api/concepts/explain` |
| Execute API | `POST http://35.222.110.147/api/execute` |
| Debug API | `POST http://35.222.110.147/api/debug/analyze` |
| Code Review API | `POST http://35.222.110.147/api/review` |
| Progress API | `GET http://35.222.110.147/api/progress/{user_id}` |
| Curriculum API | `GET http://35.222.110.147/api/curriculum` |

## Services

| Service | Port | AI | Description |
|---------|------|-----|-------------|
| triage-service | 8000 | OpenAI | Analyzes student questions and routes to the correct service |
| concepts-service | 8000 | OpenAI | Explains Python concepts with examples, analogies, and code samples |
| exercise-service | 8000 | OpenAI | Exercise CRUD, quiz generation, and auto-grading |
| code-execution-service | 8000 | No | Executes Python code in a sandboxed environment with security checks |
| debug-service | 8000 | OpenAI | Analyzes errors and provides hints, root cause, and solutions |
| code-review-service | 8000 | OpenAI | Reviews code for correctness, style, efficiency, and readability |
| progress-service | 8000 | No | Tracks student mastery across 8 curriculum modules |
| frontend | 3000 | - | Next.js app with Monaco Editor, AI chat, dashboard, and exercise browser |

All backend services run with Dapr sidecars (2/2 containers per pod) for pub/sub and state management.

## Quick Start

### Prerequisites

- Docker
- kubectl
- Helm
- `gcloud` CLI (for GKE deployment)
- `dapr` CLI

### Local Development (Docker Compose)

```bash
cp .env.example .env
# Edit .env with your OPENAI_API_KEY, DATABASE_URL, and AUTH_SECRET
docker compose up
```

Frontend: http://localhost:3000

### GKE Deployment

```bash
# Set environment variables
source .env

# Run the full deployment (cluster + operators + secrets + services + ingress)
./k8s/deploy-gke.sh

# Or run individual phases
./k8s/deploy-gke.sh phase2_secrets
./k8s/deploy-gke.sh phase4_services

# Verify deployment
./k8s/verify-gke.sh
```

### Kubernetes Deployment (Minikube)

```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=8192 --driver=docker

# 2. Create secrets
source .env
./scripts/create-k8s-secrets.sh

# 3. Deploy everything
./scripts/deploy.sh

# 4. Access the app
kubectl port-forward -n learnflow svc/learnflow-frontend 3000:80
```

## Project Structure

```
learnflow-app/
├── AGENTS.md                           # Agent guidelines and conventions
├── README.md                           # This file
├── docker-compose.yml                  # Local development
├── .env.example                        # Environment template
├── .claude/skills/                     # Reusable skills (Claude Code + Goose)
│   ├── gke-fullstack-deployment/       # GKE deployment skill
│   ├── kafka-k8s-setup/               # Kafka deployment skill
│   ├── kong-gateway-setup/            # Kong API Gateway skill
│   └── ...                            # 11+ total skills
├── src/
│   ├── frontend/                       # Next.js 14 + Monaco Editor + Better Auth
│   └── services/
│       ├── triage-service/             # AI question routing
│       ├── concepts-service/           # AI concept explanations
│       ├── exercise-service/           # Exercises + quizzes + grading
│       ├── code-execution-service/     # Sandboxed Python execution
│       ├── debug-service/              # AI error analysis
│       ├── code-review-service/        # AI code quality review
│       └── progress-service/           # Mastery tracking + curriculum
├── k8s/
│   ├── deploy-gke.sh                  # Full GKE deployment script
│   ├── verify-gke.sh                  # Deployment verification
│   ├── namespaces.yaml                # K8s namespaces
│   ├── services/                      # Service deployment manifests
│   ├── dapr/components.yaml           # Dapr state store + pub/sub
│   ├── kafka/                         # Strimzi Kafka cluster + topics
│   └── kong/ingress.yaml              # Kong ingress routing
└── docs/                              # Docusaurus documentation site
```

## Testing

```bash
# Run tests per-service (avoids module name collisions)
cd src/services/triage-service && OPENAI_API_KEY=test-key pytest tests/ -v
cd src/services/concepts-service && OPENAI_API_KEY=test-key pytest tests/ -v
cd src/services/exercise-service && OPENAI_API_KEY=test-key pytest tests/ -v
cd src/services/code-execution-service && pytest tests/ -v
cd src/services/debug-service && OPENAI_API_KEY=test-key pytest tests/ -v
cd src/services/code-review-service && OPENAI_API_KEY=test-key pytest tests/ -v
cd src/services/progress-service && pytest tests/ -v
```

## Built With Skills

This application was built entirely by AI agents (Claude Code and Goose) using reusable skills from the [skills-library](https://github.com/Ashfaq-Ahmed-Mohammed/skills-library) repository. Skills follow the MCP Code Execution pattern for token-efficient AI agent automation.

| Skill | Purpose |
|-------|---------|
| gke-fullstack-deployment | Deploy full-stack apps to GKE |
| kafka-k8s-setup | Deploy Kafka with Strimzi operator |
| neon-postgres-setup | Configure Neon PostgreSQL |
| dapr-setup | Install Dapr runtime on K8s |
| fastapi-dapr-agent | Generate FastAPI microservices |
| nextjs-k8s-deploy | Deploy Next.js to K8s |
| better-auth-setup | Configure Better Auth |
| kong-gateway-setup | Deploy Kong API Gateway |
| k8s-foundation | Kubernetes health checks |
| mcp-code-execution | MCP Code Execution pattern |
| docusaurus-deploy | Deploy documentation site |

See [AGENTS.md](AGENTS.md) for full details on skills, conventions, and architecture.

## License

Built for Hackathon III - Reusable Intelligence and Cloud-Native Mastery.
