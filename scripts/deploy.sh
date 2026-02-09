#!/bin/bash
# Full deployment script for LearnFlow on Kubernetes (Minikube)
# Usage: ./scripts/deploy.sh
#
# Prerequisites:
#   - minikube running: minikube start --cpus=4 --memory=8192 --driver=docker
#   - K8s secrets created: ./scripts/create-k8s-secrets.sh
#   - Strimzi operator installed: kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka'
#   - Dapr installed: dapr init -k
#   - Kong installed: helm install kong kong/ingress -n kong --create-namespace

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Image registry prefix (set to empty for local-only builds)
REGISTRY="${REGISTRY:-ashfaq1192}"
TAG="${TAG:-latest}"

echo "=== LearnFlow Deployment ==="
echo "Project: $PROJECT_DIR"
echo "Registry: $REGISTRY"
echo ""

# Step 1: Build Docker images in Minikube's Docker environment
echo "--- Step 1: Building Docker images ---"
eval $(minikube docker-env)

for service in triage-service concepts-service exercise-service code-execution-service; do
    IMAGE_NAME="${REGISTRY}/learnflow-${service}:${TAG}"
    echo "  Building $IMAGE_NAME..."
    docker build -t "$IMAGE_NAME" "$PROJECT_DIR/src/services/$service/"
done

echo "  Building ${REGISTRY}/learnflow-frontend:v5..."
docker build -t "${REGISTRY}/learnflow-frontend:v5" "$PROJECT_DIR/src/frontend/"

echo "  Building ${REGISTRY}/learnflow-docs:v5..."
docker build -t "${REGISTRY}/learnflow-docs:v5" "$PROJECT_DIR/docs/"

echo "  All images built."
echo ""

# Step 2: Deploy Kafka
echo "--- Step 2: Deploying Kafka ---"
kubectl apply -f "$PROJECT_DIR/k8s/kafka/kafka-cluster.yaml"
kubectl apply -f "$PROJECT_DIR/k8s/kafka/kafka-topics.yaml"
echo "  Kafka cluster and topics applied."
echo ""

# Step 3: Deploy Dapr components
echo "--- Step 3: Deploying Dapr components ---"
kubectl apply -f "$PROJECT_DIR/k8s/dapr/components.yaml"
echo "  Dapr state store and pub/sub configured."
echo ""

# Step 4: Deploy microservices
echo "--- Step 4: Deploying microservices ---"
for service in triage-service concepts-service exercise-service code-execution-service; do
    kubectl apply -f "$PROJECT_DIR/src/services/$service/k8s/deployment.yaml"
    echo "  $service deployed."
done
echo ""

# Step 5: Deploy frontend
echo "--- Step 5: Deploying frontend ---"
kubectl apply -f "$PROJECT_DIR/src/frontend/k8s/deployment.yaml"
echo "  Frontend deployed."
echo ""

# Step 6: Deploy documentation site
echo "--- Step 6: Deploying documentation ---"
kubectl apply -f "$PROJECT_DIR/docs/k8s/deployment.yaml"
echo "  Documentation site deployed."
echo ""

# Step 7: Deploy Kong ingress
echo "--- Step 7: Deploying Kong ingress ---"
kubectl apply -f "$PROJECT_DIR/k8s/kong/ingress.yaml"
echo "  Kong ingress configured."
echo ""

# Step 8: Wait for pods
echo "--- Step 8: Waiting for pods to be ready ---"
echo "  Waiting for services in learnflow namespace..."
kubectl wait --namespace=learnflow --for=condition=Ready pod --all --timeout=120s 2>/dev/null || true

echo ""
echo "=== Deployment Status ==="
kubectl get pods -n learnflow 2>/dev/null || echo "  No pods in learnflow namespace yet"
echo ""
kubectl get pods -n kafka 2>/dev/null || echo "  No pods in kafka namespace yet"
echo ""
echo "=== Services ==="
kubectl get svc -n learnflow 2>/dev/null || true
echo ""
echo "To access the frontend:"
echo "  kubectl port-forward -n learnflow svc/learnflow-frontend 3000:80"
echo "  Then open: http://localhost:3000"
echo ""
echo "To access the documentation:"
echo "  kubectl port-forward -n learnflow svc/learnflow-docs 3001:80"
echo "  Then open: http://localhost:3001"
echo ""
echo "Deployment complete."
