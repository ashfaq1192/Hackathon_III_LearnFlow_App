# Welcome to LearnFlow

LearnFlow is an **AI-powered Python learning platform** that helps developers learn Python through interactive exercises, real-time code execution, and intelligent tutoring.

## Features

- **Monaco Code Editor** - VS Code-like editing experience in your browser
- **AI-Powered Tutoring** - Get help when you're stuck with intelligent analysis
- **Real-time Code Execution** - Run Python code safely in the cloud
- **Exercise Library** - Practice with curated exercises at all skill levels
- **Event-Driven Architecture** - Modern cloud-native microservices design

## Architecture Overview

LearnFlow uses a cloud-native microservices architecture:

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────┐
│          Kong API Gateway                        │
│  (JWT Auth, Rate Limiting, CORS)                │
└──────┬──────────────────────────────────────────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       │              │              │              │
       ▼              ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Triage   │   │ Concepts │   │ Exercise │   │   Code   │
│ Service  │   │ Service  │   │ Service  │   │ Execution│
│ (AI)     │   │ (AI)     │   │ (CRUD)   │   │ Service  │
└────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │              │
     └──────────────┴──────────────┴──────────────┘
                    │
                    ▼
     ┌─────────────────────────────────┐
     │         Dapr Sidecars            │
     │  (State, Pub/Sub, Invocation)   │
     └──────────────┬──────────────────┘
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
     ┌─────────┐         ┌─────────┐
     │  Neon   │         │  Kafka  │
     │PostgreSQL│        │(Events) │
     └─────────┘         └─────────┘
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js 14 + Monaco Editor |
| Authentication | Better Auth |
| Backend | FastAPI + OpenAI SDK |
| Service Mesh | Dapr |
| Messaging | Apache Kafka |
| Database | Neon PostgreSQL |
| API Gateway | Kong |
| Orchestration | Kubernetes |

## Quick Start

Get started with LearnFlow in minutes:

```bash
# Clone the repository
git clone https://github.com/learnflow/learnflow-app.git

# Deploy using skills
claude "Deploy LearnFlow using skills"
```

See the [Quickstart Guide](/docs/getting-started/quickstart) for detailed instructions.
