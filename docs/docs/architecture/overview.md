# Architecture Overview

LearnFlow uses a cloud-native, event-driven microservices architecture designed for scalability, resilience, and AI-powered learning experiences.

## Design Principles

1. **Stateless Services**: All services are stateless; state is managed by Dapr
2. **Event-Driven**: Asynchronous communication via Kafka pub/sub
3. **AI-First**: OpenAI integration in triage and concepts services
4. **Cloud-Native**: Kubernetes-native with Dapr service mesh

## Component Diagram

```
                                    ┌─────────────────┐
                                    │    Browser      │
                                    │  (Next.js SPA)  │
                                    └────────┬────────┘
                                             │
                                             ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                           Kong API Gateway                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │JWT Plugin│  │Rate Limit│  │   CORS   │  │ Logging  │                   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘                   │
└────────────────────────────────────────────────────────────────────────────┘
                                             │
        ┌────────────────┬───────────────────┼───────────────────┬──────────────┐
        │                │                   │                   │              │
        ▼                ▼                   ▼                   ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Triage     │ │   Concepts   │ │   Exercise   │ │   Code       │ │   Frontend   │
│   Service    │ │   Service    │ │   Service    │ │   Execution  │ │   (Next.js)  │
│  ┌────────┐  │ │  ┌────────┐  │ │  ┌────────┐  │ │  ┌────────┐  │ │              │
│  │OpenAI  │  │ │  │OpenAI  │  │ │  │ CRUD   │  │ │  │Sandbox │  │ │              │
│  │ Agent  │  │ │  │ Agent  │  │ │  │  API   │  │ │  │Executor│  │ │              │
│  └────────┘  │ │  └────────┘  │ │  └────────┘  │ │  └────────┘  │ │              │
│  ┌────────┐  │ │  ┌────────┐  │ │  ┌────────┐  │ │  ┌────────┐  │ │              │
│  │ Dapr   │  │ │  │ Dapr   │  │ │  │ Dapr   │  │ │  │ Dapr   │  │ │              │
│  │Sidecar │  │ │  │Sidecar │  │ │  │Sidecar │  │ │  │Sidecar │  │ │              │
│  └────────┘  │ │  └────────┘  │ │  └────────┘  │ │  └────────┘  │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        │                │                   │                   │
        └────────────────┴───────────────────┼───────────────────┘
                                             │
                                             ▼
                              ┌──────────────────────────┐
                              │      Dapr Building Blocks │
                              │  ┌────────┐ ┌─────────┐  │
                              │  │ State  │ │ Pub/Sub │  │
                              │  │ Store  │ │         │  │
                              │  └───┬────┘ └────┬────┘  │
                              └──────┼───────────┼───────┘
                                     │           │
                                     ▼           ▼
                              ┌──────────┐ ┌──────────┐
                              │   Neon   │ │  Kafka   │
                              │PostgreSQL│ │ Cluster  │
                              └──────────┘ └──────────┘
```

## Data Flow

### Learning Flow
1. User writes code in Monaco Editor
2. Code submitted to code-execution-service
3. Result displayed; learning event published to Kafka
4. Triage service analyzes patterns for struggles

### Help Request Flow
1. User clicks "Get Help"
2. Request sent to triage-service
3. AI analyzes code and context
4. Response returns with guidance
5. If needed, concepts-service provides detailed explanation

## Technology Choices

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Service Mesh | Dapr | Abstracts state/pub-sub, polyglot support |
| Message Broker | Kafka | High throughput, event sourcing capable |
| Database | Neon PostgreSQL | Serverless, auto-scaling, branching |
| API Gateway | Kong | Rich plugin ecosystem, K8s native |
| Auth | Better Auth | Modern, Next.js optimized |
