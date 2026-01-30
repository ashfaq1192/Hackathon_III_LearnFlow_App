# Event-Driven Architecture

LearnFlow uses Apache Kafka for asynchronous event-driven communication between services.

## Kafka Topics

| Topic | Purpose | Producers | Consumers |
|-------|---------|-----------|-----------|
| `learning-events` | User learning activities | Frontend, All services | Triage service |
| `code-submitted` | Code execution requests | Frontend | Code execution service |
| `struggle-detected` | AI-detected learning issues | Triage service | Concepts service |

## Event Schemas

### Learning Event
```json
{
  "eventId": "uuid",
  "userId": "uuid",
  "eventType": "exercise.started | exercise.completed | help.requested",
  "timestamp": "2026-01-27T10:00:00Z",
  "data": {
    "exerciseId": "uuid",
    "duration": 120,
    "attempts": 3
  }
}
```

### Code Submitted Event
```json
{
  "eventId": "uuid",
  "userId": "uuid",
  "eventType": "code.submitted",
  "timestamp": "2026-01-27T10:00:00Z",
  "data": {
    "exerciseId": "uuid",
    "code": "print('hello')",
    "language": "python"
  }
}
```

### Struggle Detected Event
```json
{
  "eventId": "uuid",
  "userId": "uuid",
  "eventType": "struggle.detected",
  "timestamp": "2026-01-27T10:00:00Z",
  "data": {
    "struggleType": "syntax_error | logic_error | concept_confusion",
    "concept": "list_comprehension",
    "confidence": 0.85,
    "suggestedAction": "explain_concept"
  }
}
```

## Dapr Pub/Sub Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: learnflow
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "learnflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
    - name: authType
      value: "none"
    - name: consumerGroup
      value: "learnflow-group"
```

## Event Flow Diagrams

### Code Execution Flow
```
┌──────────┐    ┌─────────┐    ┌───────────────────┐    ┌─────────────┐
│ Frontend │───>│  Kafka  │───>│ Code Execution    │───>│   Triage    │
│          │    │code.sub │    │ Service           │    │   Service   │
└──────────┘    └─────────┘    └───────────────────┘    └─────────────┘
     │                                   │                      │
     │                                   ▼                      ▼
     │                            ┌───────────┐          ┌───────────┐
     │<───────────────────────────│  Result   │          │ Analysis  │
     │        (direct response)   └───────────┘          │  (async)  │
     │                                                   └───────────┘
```

### Struggle Detection Flow
```
┌─────────────┐    ┌─────────────┐    ┌────────────────┐    ┌──────────────┐
│   Triage    │───>│    Kafka    │───>│    Concepts    │───>│   Proactive  │
│   Service   │    │struggle.det │    │    Service     │    │    Help      │
└─────────────┘    └─────────────┘    └────────────────┘    └──────────────┘
      ▲                                        │
      │                                        ▼
┌─────────────┐                         ┌──────────────┐
│  Learning   │                         │ Explanation  │
│   Events    │                         │   (pushed)   │
└─────────────┘                         └──────────────┘
```

## Error Handling

### Dead Letter Queue
Failed events are sent to `{topic}.dlq` for later processing:
- `learning-events.dlq`
- `code-submitted.dlq`
- `struggle-detected.dlq`

### Retry Policy
- Max retries: 3
- Backoff: exponential (1s, 2s, 4s)
- After max retries: send to DLQ

## Monitoring

Kafka metrics exposed via Prometheus:
- `kafka_consumer_lag` - Consumer lag per topic
- `kafka_messages_per_second` - Throughput
- `kafka_consumer_errors` - Error count
