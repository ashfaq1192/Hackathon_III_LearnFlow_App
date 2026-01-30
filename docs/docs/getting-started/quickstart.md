# Quickstart

Get LearnFlow running in your environment.

## Prerequisites

- Kubernetes cluster (Minikube, Kind, or cloud provider)
- kubectl configured
- Helm 3 installed
- Claude Code or Goose AI agent

## Deploy with Skills

LearnFlow is built using AI agents and reusable skills. Deploy the entire application with a single command:

```bash
claude "Deploy LearnFlow using skills in .claude/skills/"
```

This will:
1. Setup Neon PostgreSQL database
2. Deploy Kafka for event streaming
3. Install Dapr service mesh
4. Generate and deploy 4 microservices
5. Deploy Next.js frontend
6. Configure Kong API Gateway

## Manual Deployment

If you prefer manual control:

### 1. Setup Infrastructure

```bash
# Create namespace
kubectl create namespace learnflow

# Deploy Kafka
kubectl apply -f k8s/kafka/

# Install Dapr
dapr init --kubernetes --wait

# Deploy Dapr components
kubectl apply -f k8s/dapr/
```

### 2. Build Services

```bash
# Build microservices
cd src/services/triage-service
docker build -t triage-service:latest .

# Repeat for other services
```

### 3. Deploy to Kubernetes

```bash
# Deploy all services
kubectl apply -f src/services/triage-service/k8s/
kubectl apply -f src/services/concepts-service/k8s/
kubectl apply -f src/services/exercise-service/k8s/
kubectl apply -f src/services/code-execution-service/k8s/
kubectl apply -f src/frontend/k8s/
```

### 4. Configure Gateway

```bash
kubectl apply -f k8s/kong/
```

## Access the Application

```bash
# Port-forward Kong proxy
kubectl port-forward -n kong svc/kong-kong-proxy 8000:80

# Access LearnFlow
open http://localhost:8000
```

## Verify Deployment

Check all components are running:

```bash
kubectl get pods -n learnflow
kubectl get pods -n kafka
kubectl get pods -n kong
kubectl get pods -n dapr-system
```
