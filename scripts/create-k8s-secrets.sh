#!/bin/bash
# Create Kubernetes secrets for LearnFlow deployment
# Usage: ./scripts/create-k8s-secrets.sh
#
# Requires environment variables:
#   OPENAI_API_KEY   - OpenAI API key for AI services
#   DATABASE_URL     - Neon PostgreSQL connection string
#   AUTH_SECRET      - Secret for Better Auth session signing (optional, auto-generated if missing)

set -euo pipefail

NAMESPACE="${NAMESPACE:-learnflow}"

echo "Creating K8s secrets for LearnFlow in namespace: $NAMESPACE"

# Create namespace if it doesn't exist
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -

# Validate required env vars
if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo "ERROR: OPENAI_API_KEY is not set"
    echo "  export OPENAI_API_KEY='sk-...'"
    exit 1
fi

if [ -z "${DATABASE_URL:-}" ]; then
    echo "ERROR: DATABASE_URL is not set"
    echo "  export DATABASE_URL='postgresql://user:pass@host/db?sslmode=require'"
    exit 1
fi

# Auto-generate AUTH_SECRET if not provided
AUTH_SECRET="${AUTH_SECRET:-$(openssl rand -base64 32)}"

# Create OpenAI credentials secret
kubectl create secret generic openai-credentials \
    --namespace="$NAMESPACE" \
    --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
    --dry-run=client -o yaml | kubectl apply -f -

echo "  openai-credentials created"

# Create PostgreSQL credentials secret
kubectl create secret generic postgres-credentials \
    --namespace="$NAMESPACE" \
    --from-literal=DATABASE_URL="$DATABASE_URL" \
    --dry-run=client -o yaml | kubectl apply -f -

echo "  postgres-credentials created"

# Create auth secret
kubectl create secret generic auth-credentials \
    --namespace="$NAMESPACE" \
    --from-literal=AUTH_SECRET="$AUTH_SECRET" \
    --dry-run=client -o yaml | kubectl apply -f -

echo "  auth-credentials created"

echo ""
echo "All secrets created successfully in namespace '$NAMESPACE'"
echo "Secrets: openai-credentials, postgres-credentials, auth-credentials"
