# LearnFlow Application - Development Constitution

## Project Overview

**LearnFlow** is an AI-powered Python learning platform built using cloud-native, event-driven architecture with skills from the skills-library repository.

## Architecture Principles

1. **Microservices**: Each service has a single responsibility
2. **Event-Driven**: Services communicate via Kafka pub/sub
3. **Dapr Integration**: Use Dapr for state management and service invocation
4. **AI-Powered**: OpenAI integration for intelligent features
5. **Cloud-Native**: Kubernetes-first deployment

## Tech Stack (Non-Negotiable)

- **Frontend**: Next.js 14+ with Monaco Editor + Better Auth
- **Backend**: FastAPI + OpenAI SDK (Python 3.9+)
- **Service Mesh**: Dapr
- **Messaging**: Kafka on Kubernetes
- **Database**: Neon PostgreSQL (serverless)
- **API Gateway**: Kong Gateway
- **Orchestration**: Kubernetes (Minikube for dev)
- **Documentation**: Docusaurus

## Code Standards

### Python (FastAPI Services)
- Use async/await for I/O operations
- Pydantic models for validation
- Type hints everywhere
- FastAPI dependency injection
- Health check endpoint at `/health`

### TypeScript (Next.js Frontend)
- Use TypeScript strict mode
- Server components by default
- Client components only when needed
- Monaco Editor for code editing

### Kubernetes
- All manifests in `k8s/` directory
- Use Dapr annotations for sidecars
- Resource limits defined
- Health checks configured

## Service Structure

Each microservice follows this pattern:
```
service-name/
├── app/
│   ├── main.py              # FastAPI app
│   ├── models/              # Pydantic models
│   ├── services/            # Business logic
│   └── dapr/                # Dapr handlers
├── Dockerfile
├── requirements.txt
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
└── tests/
```

## Development Workflow

1. Use skills from `.claude/skills/` directory
2. Generate services with `fastapi-dapr-agent` skill
3. Deploy infrastructure in order: PostgreSQL → Kafka → Dapr → Services → Frontend → Gateway
4. Validate each component before proceeding

## Security

- Never commit secrets to git
- Use Kubernetes Secrets for credentials
- Environment variables for configuration
- JWT authentication via Better Auth
- Rate limiting via Kong Gateway

## Testing

- Unit tests for business logic
- Integration tests with Dapr
- End-to-end tests for critical flows
- Load testing before production

## Deployment

- Use skills for autonomous deployment
- Validate health checks after each deployment
- Rollback on failure
- Monitor logs and metrics

---

**Built with**: Claude Code + Goose using MCP Code Execution pattern
